"""Portfolio snapshots — daily total portfolio value."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.stock import PortfolioSnapshot
from app.schemas.stock import SnapshotRequest
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("")
async def get_snapshots(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return snapshots as { "YYYY-MM-DD": value } dict — matches frontend."""
    result = await db.execute(
        select(PortfolioSnapshot)
        .where(PortfolioSnapshot.user_id == user.id)
        .order_by(PortfolioSnapshot.snapshot_date)
    )
    snapshots = result.scalars().all()
    return {str(s.snapshot_date): float(s.total_value) for s in snapshots}


@router.post("", status_code=201)
async def create_snapshot(
    req: SnapshotRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upsert a daily portfolio snapshot."""
    existing = await db.execute(
        select(PortfolioSnapshot).where(
            PortfolioSnapshot.user_id == user.id,
            PortfolioSnapshot.snapshot_date == req.date,
        )
    )
    snap = existing.scalar_one_or_none()
    if snap:
        snap.total_value = req.value
    else:
        snap = PortfolioSnapshot(
            user_id=user.id,
            snapshot_date=req.date,
            total_value=req.value,
        )
        db.add(snap)

    return {"date": str(req.date), "value": float(req.value)}