"""
HYSA (High-Yield Savings Account) models.

Hierarchy:
  User → HysaAccount → HysaLog
                      → HysaSnapshot
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, String, Integer, Date, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HysaAccount(Base):
    __tablename__ = "hysa_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    ticker: Mapped[str | None] = mapped_column(String(20))
    name: Mapped[str | None] = mapped_column(String(100))
    current_balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0.00")
    )
    apy_rate: Mapped[Decimal] = mapped_column(
        Numeric(6, 4), default=Decimal("0.0450")
    )
    compounding: Mapped[int] = mapped_column(Integer, default=12)
    frequency: Mapped[str] = mapped_column(String(20), default="monthly")
    contribution_target: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )
    next_contribution_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    annual_deposit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00")
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="hysa_accounts")
    logs: Mapped[list["HysaLog"]] = relationship(
        back_populates="account", cascade="all, delete-orphan",
        order_by="HysaLog.log_date"
    )
    snapshots: Mapped[list["HysaSnapshot"]] = relationship(
        back_populates="account", cascade="all, delete-orphan",
        order_by="HysaSnapshot.snapshot_date"
    )


class HysaLog(Base):
    __tablename__ = "hysa_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hysa_accounts.id", ondelete="CASCADE")
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    log_type: Mapped[str] = mapped_column(String(20), nullable=False)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    account: Mapped["HysaAccount"] = relationship(back_populates="logs")

    __table_args__ = (
        CheckConstraint(
            "log_type IN ('deposit', 'withdrawal', 'interest')",
            name="ck_hysa_log_type",
        ),
    )


class HysaSnapshot(Base):
    __tablename__ = "hysa_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hysa_accounts.id", ondelete="CASCADE")
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    account: Mapped["HysaAccount"] = relationship(back_populates="snapshots")

    __table_args__ = (
        UniqueConstraint("account_id", "snapshot_date", name="uq_hysa_snap_date"),
    )