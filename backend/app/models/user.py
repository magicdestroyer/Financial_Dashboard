"""
User model.

This is the central table — every other table references users.id.
Passwords are never stored in plaintext; only bcrypt hashes.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    risk_tolerance: Mapped[str] = mapped_column(
        String(20), default="moderate"
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships (lazy="selectin" means they load in the same query)
    settings: Mapped["UserSettings"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    budget_years: Mapped[list["BudgetYear"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    hysa_accounts: Mapped[list["HysaAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    stock_holdings: Mapped[list["StockHolding"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    portfolio_snapshots: Mapped[list["PortfolioSnapshot"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "risk_tolerance IN ('conservative', 'moderate', 'aggressive', 'speculative')",
            name="ck_users_risk_tolerance",
        ),
    )

    def __repr__(self):
        return f"<User {self.username}>"