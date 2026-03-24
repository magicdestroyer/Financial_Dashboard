from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BudgetItemSchema(BaseModel):
    id: Optional[UUID] = None
    category: str
    label: Optional[str] = ""
    amount: Decimal = Decimal("0")
    frequency: str = "monthly"
    start_date: Optional[date] = None
    sort_order: int = 0

    class Config:
        from_attributes = True


class SavingsBucketSchema(BaseModel):
    id: Optional[UUID] = None
    label: Optional[str] = ""
    target: Decimal = Decimal("0")
    saved: Decimal = Decimal("0")
    color: str = "#3cefb0"
    sort_order: int = 0

    class Config:
        from_attributes = True


class BudgetYearResponse(BaseModel):
    year: int
    roth: Decimal
    income: list[BudgetItemSchema]
    expenses: list[BudgetItemSchema]
    buckets: list[SavingsBucketSchema]

    class Config:
        from_attributes = True


class BudgetYearCreateRequest(BaseModel):
    year: int


class BudgetYearUpdateRequest(BaseModel):
    roth: Optional[Decimal] = None
    income: Optional[list[BudgetItemSchema]] = None
    expenses: Optional[list[BudgetItemSchema]] = None
    buckets: Optional[list[SavingsBucketSchema]] = None