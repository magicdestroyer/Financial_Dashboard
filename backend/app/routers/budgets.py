"""
Budget CRUD.

The PUT endpoint accepts the full budget year (income, expenses, buckets)
and replaces all items — this matches how the frontend saves: it sends
the entire budget state at once.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.budget import BudgetYear, BudgetItem, SavingsBucket
from app.schemas.budget import (
    BudgetYearResponse, BudgetYearCreateRequest,
    BudgetYearUpdateRequest, BudgetItemSchema, SavingsBucketSchema,
)
from app.middleware.auth import get_current_user

router = APIRouter()


def budget_to_response(by: BudgetYear) -> BudgetYearResponse:
    """Convert ORM BudgetYear → response schema the frontend expects."""
    income = [BudgetItemSchema.model_validate(i) for i in by.items if i.category == "income"]
    expenses = [BudgetItemSchema.model_validate(i) for i in by.items if i.category == "expense"]
    buckets = [SavingsBucketSchema.model_validate(b) for b in by.buckets]
    return BudgetYearResponse(
        year=by.year,
        roth=by.roth_contribution,
        income=income,
        expenses=expenses,
        buckets=buckets,
    )


@router.get("", response_model=list[BudgetYearResponse])
async def get_all_budgets(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BudgetYear)
        .where(BudgetYear.user_id == user.id)
        .options(selectinload(BudgetYear.items), selectinload(BudgetYear.buckets))
        .order_by(BudgetYear.year)
    )
    years = result.scalars().all()
    return [budget_to_response(by) for by in years]


@router.get("/{year}", response_model=BudgetYearResponse)
async def get_budget_year(
    year: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BudgetYear)
        .where(BudgetYear.user_id == user.id, BudgetYear.year == year)
        .options(selectinload(BudgetYear.items), selectinload(BudgetYear.buckets))
    )
    by = result.scalar_one_or_none()
    if not by:
        raise HTTPException(status_code=404, detail="Budget year not found")
    return budget_to_response(by)


@router.post("", response_model=BudgetYearResponse, status_code=201)
async def create_budget_year(
    req: BudgetYearCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check if year already exists
    existing = await db.execute(
        select(BudgetYear).where(
            BudgetYear.user_id == user.id, BudgetYear.year == req.year
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Budget year already exists")

    by = BudgetYear(user_id=user.id, year=req.year)
    db.add(by)
    await db.flush()
    return budget_to_response(by)


@router.put("/{year}", response_model=BudgetYearResponse)
async def update_budget_year(
    year: int,
    req: BudgetYearUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Full replace of a budget year's data.
    The frontend sends all income, expenses, and buckets at once.
    We delete existing items and recreate them — simplest approach
    that avoids complex diffing logic.
    """
    result = await db.execute(
        select(BudgetYear)
        .where(BudgetYear.user_id == user.id, BudgetYear.year == year)
        .options(selectinload(BudgetYear.items), selectinload(BudgetYear.buckets))
    )
    by = result.scalar_one_or_none()
    if not by:
        # Auto-create if it doesn't exist
        by = BudgetYear(user_id=user.id, year=year)
        db.add(by)
        await db.flush()

    if req.roth is not None:
        by.roth_contribution = req.roth

    # Replace income + expense items
    if req.income is not None or req.expenses is not None:
        # Delete all existing items
        for item in list(by.items):
            await db.delete(item)
        await db.flush()

        # Recreate income
        for i, item in enumerate(req.income or []):
            db.add(BudgetItem(
                budget_year_id=by.id,
                category="income",
                label=item.label,
                amount=item.amount,
                frequency=item.frequency,
                start_date=item.start_date,
                sort_order=i,
            ))

        # Recreate expenses
        for i, item in enumerate(req.expenses or []):
            db.add(BudgetItem(
                budget_year_id=by.id,
                category="expense",
                label=item.label,
                amount=item.amount,
                frequency=item.frequency,
                start_date=item.start_date,
                sort_order=i,
            ))

    # Replace buckets
    if req.buckets is not None:
        for bucket in list(by.buckets):
            await db.delete(bucket)
        await db.flush()

        for i, b in enumerate(req.buckets):
            db.add(SavingsBucket(
                budget_year_id=by.id,
                label=b.label,
                target=b.target,
                saved=b.saved,
                color=b.color,
                sort_order=i,
            ))

    await db.flush()

    # Re-fetch with relationships loaded
    result = await db.execute(
        select(BudgetYear)
        .where(BudgetYear.id == by.id)
        .options(selectinload(BudgetYear.items), selectinload(BudgetYear.buckets))
    )
    by = result.scalar_one()
    return budget_to_response(by)


@router.delete("/{year}")
async def delete_budget_year(
    year: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BudgetYear).where(
            BudgetYear.user_id == user.id, BudgetYear.year == year
        )
    )
    by = result.scalar_one_or_none()
    if not by:
        raise HTTPException(status_code=404, detail="Budget year not found")
    await db.delete(by)
    return {"message": f"Budget year {year} deleted"}