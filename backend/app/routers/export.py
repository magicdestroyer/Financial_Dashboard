"""
Data export/import — full JSON dump for backup or migration.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.budget import BudgetYear
from app.models.hysa import HysaAccount
from app.models.stock import StockHolding, PortfolioSnapshot
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("/export")
async def export_all_data(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export all user data as a single JSON document."""

    # Budgets
    budgets_result = await db.execute(
        select(BudgetYear)
        .where(BudgetYear.user_id == user.id)
        .options(selectinload(BudgetYear.items), selectinload(BudgetYear.buckets))
    )
    budget_years = budgets_result.scalars().all()

    budgets_data = {}
    for by in budget_years:
        budgets_data[str(by.year)] = {
            "roth": float(by.roth_contribution),
            "income": [
                {"label": i.label, "amount": float(i.amount), "type": i.frequency, "date": str(i.start_date) if i.start_date else ""}
                for i in by.items if i.category == "income"
            ],
            "expenses": [
                {"label": i.label, "amount": float(i.amount), "type": i.frequency, "date": str(i.start_date) if i.start_date else ""}
                for i in by.items if i.category == "expense"
            ],
            "savingsBuckets": [
                {"label": b.label, "target": float(b.target), "saved": float(b.saved), "color": b.color}
                for b in by.buckets
            ],
        }

    # HYSA
    hysa_result = await db.execute(
        select(HysaAccount)
        .where(HysaAccount.user_id == user.id)
        .options(selectinload(HysaAccount.logs), selectinload(HysaAccount.snapshots))
    )
    hysa_accounts = hysa_result.scalars().all()

    hysa_data = [
        {
            "ticker": a.ticker, "name": a.name,
            "currentBalance": float(a.current_balance),
            "rate": float(a.apy_rate), "compounding": a.compounding,
            "frequency": a.frequency,
            "contributionTarget": float(a.contribution_target),
            "nextContributionDate": str(a.next_contribution_date) if a.next_contribution_date else "",
            "contributionLog": [
                {"date": str(l.log_date), "amount": float(l.amount), "type": l.log_type, "note": l.note or ""}
                for l in a.logs
            ],
            "balanceSnapshots": [
                {"date": str(s.snapshot_date), "balance": float(s.balance)}
                for s in a.snapshots
            ],
        }
        for a in hysa_accounts
    ]

    # Stocks
    stocks_result = await db.execute(
        select(StockHolding)
        .where(StockHolding.user_id == user.id)
        .options(selectinload(StockHolding.lots), selectinload(StockHolding.price_history))
    )
    stock_holdings = stocks_result.scalars().all()

    stocks_data = []
    for h in stock_holdings:
        total_shares = sum(float(l.shares) for l in h.lots)
        total_cost = sum(float(l.amount_spent) for l in h.lots)
        avg_price = (total_cost / total_shares) if total_shares else 0
        stocks_data.append({
            "ticker": h.ticker, "name": h.name, "account": h.account_type,
            "shares": total_shares, "buyPrice": round(avg_price, 4),
            "totalCost": round(total_cost, 2),
            "lots": [
                {"date": str(l.purchase_date) if l.purchase_date else "", "shares": float(l.shares),
                 "pricePerShare": float(l.price_per_share), "amountSpent": float(l.amount_spent)}
                for l in h.lots
            ],
            "priceHistory": [
                {"date": str(p.price_date), "price": float(p.price)}
                for p in h.price_history
            ],
        })

    # Snapshots
    snap_result = await db.execute(
        select(PortfolioSnapshot)
        .where(PortfolioSnapshot.user_id == user.id)
        .order_by(PortfolioSnapshot.snapshot_date)
    )
    snapshots = {str(s.snapshot_date): float(s.total_value) for s in snap_result.scalars().all()}

    return {
        "username": user.username,
        "exportDate": str(user.updated_at),
        "budgets": budgets_data,
        "hysa": hysa_data,
        "stocks": stocks_data,
        "snapshots": snapshots,
    }