"""
Stock holdings CRUD + lots + price history.

When adding a stock that already exists (same ticker), we add
a new lot to the existing holding and recompute the averages.
"""

from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.stock import StockHolding, StockLot, StockPriceHistory
from app.schemas.stock import (
    StockHoldingResponse, StockCreateRequest, StockUpdateRequest,
    LotCreateRequest, LotUpdateRequest, PriceCreateRequest,
    StockLotSchema,
)
from app.middleware.auth import get_current_user

router = APIRouter()


def compute_holding_summary(holding: StockHolding) -> dict:
    """Compute aggregated shares, avg price, total cost from lots."""
    total_shares = sum(lot.shares for lot in holding.lots)
    total_cost = sum(lot.amount_spent for lot in holding.lots)
    avg_price = (total_cost / total_shares) if total_shares else Decimal("0")
    return {
        "shares": total_shares,
        "buy_price": round(avg_price, 4),
        "total_cost": round(total_cost, 2),
    }


def holding_to_response(h: StockHolding) -> StockHoldingResponse:
    summary = compute_holding_summary(h)
    resp = StockHoldingResponse.model_validate(h)
    resp.shares = summary["shares"]
    resp.buy_price = summary["buy_price"]
    resp.total_cost = summary["total_cost"]
    return resp


@router.get("", response_model=list[StockHoldingResponse])
async def get_all_stocks(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StockHolding)
        .where(StockHolding.user_id == user.id)
        .options(
            selectinload(StockHolding.lots),
            selectinload(StockHolding.price_history),
        )
    )
    holdings = result.scalars().all()
    return [holding_to_response(h) for h in holdings]


@router.post("", response_model=StockHoldingResponse, status_code=201)
async def create_stock(
    req: StockCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a stock. If the ticker already exists for this user,
    add a new lot to the existing holding.
    """
    # Check for existing holding with same ticker
    result = await db.execute(
        select(StockHolding)
        .where(StockHolding.user_id == user.id, StockHolding.ticker == req.ticker.upper())
        .options(selectinload(StockHolding.lots), selectinload(StockHolding.price_history))
    )
    holding = result.scalar_one_or_none()

    if holding:
        # Add lot to existing holding
        lot = StockLot(
            holding_id=holding.id,
            purchase_date=req.purchase_date,
            shares=req.shares,
            price_per_share=req.price_per_share,
            amount_spent=req.amount_spent,
        )
        db.add(lot)
        # Update name/account if provided
        if req.name:
            holding.name = req.name
    else:
        # Create new holding + first lot
        holding = StockHolding(
            user_id=user.id,
            ticker=req.ticker.upper(),
            name=req.name or req.ticker.upper(),
            account_type=req.account_type,
            exchange=req.exchange,
            quote_type=req.quote_type,
        )
        db.add(holding)
        await db.flush()

        lot = StockLot(
            holding_id=holding.id,
            purchase_date=req.purchase_date,
            shares=req.shares,
            price_per_share=req.price_per_share,
            amount_spent=req.amount_spent,
        )
        db.add(lot)

        # Add initial price history entry
        if req.purchase_date and req.price_per_share:
            db.add(StockPriceHistory(
                holding_id=holding.id,
                price_date=req.purchase_date,
                price=req.price_per_share,
            ))

    await db.flush()

    # Re-fetch with relationships
    result = await db.execute(
        select(StockHolding)
        .where(StockHolding.id == holding.id)
        .options(selectinload(StockHolding.lots), selectinload(StockHolding.price_history))
    )
    holding = result.scalar_one()
    return holding_to_response(holding)


@router.put("/{holding_id}", response_model=StockHoldingResponse)
async def update_stock(
    holding_id: UUID,
    req: StockUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StockHolding)
        .where(StockHolding.id == holding_id, StockHolding.user_id == user.id)
        .options(selectinload(StockHolding.lots), selectinload(StockHolding.price_history))
    )
    holding = result.scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    if req.name is not None:
        holding.name = req.name
    if req.account_type is not None:
        holding.account_type = req.account_type

    return holding_to_response(holding)


@router.delete("/{holding_id}")
async def delete_stock(
    holding_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StockHolding).where(
            StockHolding.id == holding_id, StockHolding.user_id == user.id
        )
    )
    holding = result.scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    await db.delete(holding)
    return {"message": f"{holding.ticker} deleted"}


# ── LOTS ──────────────────────────────────────────────────

@router.post("/{holding_id}/lots", response_model=StockLotSchema, status_code=201)
async def create_lot(
    holding_id: UUID,
    req: LotCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StockHolding).where(
            StockHolding.id == holding_id, StockHolding.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Holding not found")

    lot = StockLot(
        holding_id=holding_id,
        purchase_date=req.purchase_date,
        shares=req.shares,
        price_per_share=req.price_per_share,
        amount_spent=req.amount_spent,
    )
    db.add(lot)
    await db.flush()
    return StockLotSchema.model_validate(lot)


@router.put("/{holding_id}/lots/{lot_id}", response_model=StockLotSchema)
async def update_lot(
    holding_id: UUID,
    lot_id: UUID,
    req: LotUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    h_result = await db.execute(
        select(StockHolding).where(
            StockHolding.id == holding_id, StockHolding.user_id == user.id
        )
    )
    if not h_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Holding not found")

    result = await db.execute(
        select(StockLot).where(StockLot.id == lot_id, StockLot.holding_id == holding_id)
    )
    lot = result.scalar_one_or_none()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(lot, field, value)

    return StockLotSchema.model_validate(lot)


@router.delete("/{holding_id}/lots/{lot_id}")
async def delete_lot(
    holding_id: UUID,
    lot_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    h_result = await db.execute(
        select(StockHolding).where(
            StockHolding.id == holding_id, StockHolding.user_id == user.id
        ).options(selectinload(StockHolding.lots))
    )
    holding = h_result.scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    result = await db.execute(
        select(StockLot).where(StockLot.id == lot_id, StockLot.holding_id == holding_id)
    )
    lot = result.scalar_one_or_none()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    await db.delete(lot)
    await db.flush()

    # If no lots remain, delete the entire holding
    remaining = await db.execute(
        select(StockLot).where(StockLot.holding_id == holding_id)
    )
    if not remaining.scalars().first():
        await db.delete(holding)

    return {"message": "Lot deleted"}


# ── PRICE HISTORY ─────────────────────────────────────────

@router.post("/{holding_id}/prices", status_code=201)
async def add_price(
    holding_id: UUID,
    req: PriceCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    h_result = await db.execute(
        select(StockHolding).where(
            StockHolding.id == holding_id, StockHolding.user_id == user.id
        )
    )
    if not h_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Holding not found")

    # Upsert — update if date exists, insert if not
    existing = await db.execute(
        select(StockPriceHistory).where(
            StockPriceHistory.holding_id == holding_id,
            StockPriceHistory.price_date == req.date,
        )
    )
    price_entry = existing.scalar_one_or_none()
    if price_entry:
        price_entry.price = req.price
    else:
        price_entry = StockPriceHistory(
            holding_id=holding_id,
            price_date=req.date,
            price=req.price,
        )
        db.add(price_entry)

    return {"date": str(req.date), "price": float(req.price)}