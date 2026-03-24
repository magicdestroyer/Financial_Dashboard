"""
HYSA accounts CRUD + contribution logging.

When a log entry is created (deposit/withdrawal/interest),
the account balance auto-updates and a snapshot is recorded.
"""

from uuid import UUID
from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.hysa import HysaAccount, HysaLog, HysaSnapshot
from app.schemas.hysa import (
    HysaAccountResponse, HysaCreateRequest, HysaUpdateRequest,
    HysaLogCreateRequest, HysaLogSchema,
)
from app.middleware.auth import get_current_user

router = APIRouter()


def account_to_response(acct: HysaAccount) -> HysaAccountResponse:
    return HysaAccountResponse.model_validate(acct)


@router.get("", response_model=list[HysaAccountResponse])
async def get_all_hysa(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(HysaAccount)
        .where(HysaAccount.user_id == user.id)
        .options(selectinload(HysaAccount.logs), selectinload(HysaAccount.snapshots))
        .order_by(HysaAccount.sort_order)
    )
    accounts = result.scalars().all()
    return [account_to_response(a) for a in accounts]


@router.post("", response_model=HysaAccountResponse, status_code=201)
async def create_hysa(
    req: HysaCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    acct = HysaAccount(
        user_id=user.id,
        ticker=req.ticker,
        name=req.name,
        apy_rate=req.apy_rate,
        compounding=req.compounding,
        current_balance=req.current_balance,
        frequency=req.frequency,
        contribution_target=req.contribution_target,
        next_contribution_date=req.next_contribution_date,
        annual_deposit=req.annual_deposit,
    )
    db.add(acct)
    await db.flush()
    return account_to_response(acct)


@router.put("/{account_id}", response_model=HysaAccountResponse)
async def update_hysa(
    account_id: UUID,
    req: HysaUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(HysaAccount)
        .where(HysaAccount.id == account_id, HysaAccount.user_id == user.id)
        .options(selectinload(HysaAccount.logs), selectinload(HysaAccount.snapshots))
    )
    acct = result.scalar_one_or_none()
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found")

    # Update only provided fields
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(acct, field, value)

    return account_to_response(acct)


@router.delete("/{account_id}")
async def delete_hysa(
    account_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(HysaAccount).where(
            HysaAccount.id == account_id, HysaAccount.user_id == user.id
        )
    )
    acct = result.scalar_one_or_none()
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found")
    await db.delete(acct)
    return {"message": "Account deleted"}


@router.post("/{account_id}/logs", response_model=HysaLogSchema)
async def create_hysa_log(
    account_id: UUID,
    req: HysaLogCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Log a deposit, withdrawal, or interest entry.
    Auto-updates the account balance and creates a snapshot.
    """
    result = await db.execute(
        select(HysaAccount).where(
            HysaAccount.id == account_id, HysaAccount.user_id == user.id
        )
    )
    acct = result.scalar_one_or_none()
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found")

    if req.type not in ("deposit", "withdrawal", "interest"):
        raise HTTPException(status_code=422, detail="Invalid log type")

    log = HysaLog(
        account_id=acct.id,
        log_date=req.date,
        amount=req.amount,
        log_type=req.type,
        note=req.note,
    )
    db.add(log)

    # Update balance
    if req.type == "withdrawal":
        acct.current_balance = max(0, acct.current_balance - req.amount)
    else:
        acct.current_balance += req.amount

    # Record snapshot
    snapshot = HysaSnapshot(
        account_id=acct.id,
        snapshot_date=req.date,
        balance=acct.current_balance,
    )
    db.add(snapshot)

    await db.flush()
    return HysaLogSchema.model_validate(log)


@router.delete("/{account_id}/logs/{log_id}")
async def delete_hysa_log(
    account_id: UUID,
    log_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    result = await db.execute(
        select(HysaAccount).where(
            HysaAccount.id == account_id, HysaAccount.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Account not found")

    result = await db.execute(
        select(HysaLog).where(HysaLog.id == log_id, HysaLog.account_id == account_id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")

    await db.delete(log)
    return {"message": "Log entry deleted"}