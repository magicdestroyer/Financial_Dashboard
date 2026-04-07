"""
Stock portfolio models.

Hierarchy:
  User → StockHolding → StockLot
                       → StockPriceHistory
  User → PortfolioSnapshot (daily total portfolio value)
"""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import ForeignKey, String, Integer, Date, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StockHolding(Base):
    __tablename__ = "stock_holdings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str | None] = mapped_column(String(200))
    account_type: Mapped[str] = mapped_column(String(50), default="Roth IRA")
    exchange: Mapped[str | None] = mapped_column(String(50))
    quote_type: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="stock_holdings")
    lots: Mapped[list["StockLot"]] = relationship(
        back_populates="holding", cascade="all, delete-orphan",
        order_by="StockLot.purchase_date"
    )
    price_history: Mapped[list["StockPriceHistory"]] = relationship(
        back_populates="holding", cascade="all, delete-orphan",
        order_by="StockPriceHistory.price_date"
    )


class StockLot(Base):
    __tablename__ = "stock_lots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    holding_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stock_holdings.id", ondelete="CASCADE")
    )
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    shares: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    price_per_share: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    amount_spent: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    holding: Mapped["StockHolding"] = relationship(back_populates="lots")


class StockPriceHistory(Base):
    __tablename__ = "stock_price_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    holding_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stock_holdings.id", ondelete="CASCADE")
    )
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)

    holding: Mapped["StockHolding"] = relationship(back_populates="price_history")

    __table_args__ = (
        UniqueConstraint("holding_id", "price_date", name="uq_stock_price_date"),
    )


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    user: Mapped["User"] = relationship(back_populates="portfolio_snapshots")

    __table_args__ = (
        UniqueConstraint("user_id", "snapshot_date", name="uq_portfolio_snap_date"),
    )
