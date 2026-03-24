"""
Budget models: years → items (income/expense) + savings buckets.

Hierarchy:
  User → BudgetYear → BudgetItem
                     → SavingsBucket
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, String, Integer, Date, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BudgetYear(Base):
    __tablename__ = "budget_years"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    roth_contribution: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="budget_years")
    items: Mapped[list["BudgetItem"]] = relationship(
        back_populates="budget_year", cascade="all, delete-orphan",
        order_by="BudgetItem.sort_order"
    )
    buckets: Mapped[list["SavingsBucket"]] = relationship(
        back_populates="budget_year", cascade="all, delete-orphan",
        order_by="SavingsBucket.sort_order"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "year", name="uq_budget_user_year"),
    )


class BudgetItem(Base):
    __tablename__ = "budget_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    budget_year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("budget_years.id", ondelete="CASCADE")
    )
    category: Mapped[str] = mapped_column(String(10), nullable=False)  # 'income' | 'expense'
    label: Mapped[str | None] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    frequency: Mapped[str] = mapped_column(String(20), default="monthly")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    budget_year: Mapped["BudgetYear"] = relationship(back_populates="items")

    __table_args__ = (
        CheckConstraint("category IN ('income', 'expense')", name="ck_budget_item_category"),
        CheckConstraint(
            "frequency IN ('weekly','biweekly','monthly','quarterly','semiann','annually','onetime','capex')",
            name="ck_budget_item_frequency",
        ),
    )


class SavingsBucket(Base):
    __tablename__ = "savings_buckets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    budget_year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("budget_years.id", ondelete="CASCADE")
    )
    label: Mapped[str | None] = mapped_column(String(100))
    target: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    saved: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    color: Mapped[str] = mapped_column(String(7), default="#3cefb0")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    budget_year: Mapped["BudgetYear"] = relationship(back_populates="buckets")