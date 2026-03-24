"""Initial schema — all tables

Revision ID: 001_initial
Revises: None
Create Date: 2025-01-01
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Users ─────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("username", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(255), unique=True, nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("date_of_birth", sa.Date, nullable=True),
        sa.Column("risk_tolerance", sa.String(20), server_default="moderate"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint(
            "risk_tolerance IN ('conservative','moderate','aggressive','speculative')",
            name="ck_users_risk_tolerance",
        ),
    )

    # ── Settings ──────────────────────────────────────────
    op.create_table(
        "settings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True),
        sa.Column("theme_index", sa.Integer, server_default="0"),
        sa.Column("accent_color", sa.String(7), server_default="'#3cefb0'"),
        sa.Column("live_enabled", sa.Boolean, server_default="false"),
        sa.Column("extended_hours", sa.Boolean, server_default="false"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # ── Budget Years ──────────────────────────────────────
    op.create_table(
        "budget_years",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("roth_contribution", sa.Numeric(10, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "year", name="uq_budget_user_year"),
    )

    # ── Budget Items ──────────────────────────────────────
    op.create_table(
        "budget_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("budget_year_id", UUID(as_uuid=True), sa.ForeignKey("budget_years.id", ondelete="CASCADE")),
        sa.Column("category", sa.String(10), nullable=False),
        sa.Column("label", sa.String(100)),
        sa.Column("amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("frequency", sa.String(20), server_default="'monthly'"),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("sort_order", sa.Integer, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("category IN ('income','expense')", name="ck_budget_item_category"),
        sa.CheckConstraint(
            "frequency IN ('weekly','biweekly','monthly','quarterly','semiann','annually','onetime','capex')",
            name="ck_budget_item_frequency",
        ),
    )

    # ── Savings Buckets ───────────────────────────────────
    op.create_table(
        "savings_buckets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("budget_year_id", UUID(as_uuid=True), sa.ForeignKey("budget_years.id", ondelete="CASCADE")),
        sa.Column("label", sa.String(100)),
        sa.Column("target", sa.Numeric(12, 2), server_default="0"),
        sa.Column("saved", sa.Numeric(12, 2), server_default="0"),
        sa.Column("color", sa.String(7), server_default="'#3cefb0'"),
        sa.Column("sort_order", sa.Integer, server_default="0"),
    )

    # ── HYSA Accounts ─────────────────────────────────────
    op.create_table(
        "hysa_accounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("ticker", sa.String(20)),
        sa.Column("name", sa.String(100)),
        sa.Column("current_balance", sa.Numeric(14, 2), server_default="0"),
        sa.Column("apy_rate", sa.Numeric(6, 4), server_default="0.0450"),
        sa.Column("compounding", sa.Integer, server_default="12"),
        sa.Column("frequency", sa.String(20), server_default="'monthly'"),
        sa.Column("contribution_target", sa.Numeric(10, 2), server_default="0"),
        sa.Column("next_contribution_date", sa.Date, nullable=True),
        sa.Column("annual_deposit", sa.Numeric(12, 2), server_default="0"),
        sa.Column("sort_order", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # ── HYSA Logs ─────────────────────────────────────────
    op.create_table(
        "hysa_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("account_id", UUID(as_uuid=True), sa.ForeignKey("hysa_accounts.id", ondelete="CASCADE")),
        sa.Column("log_date", sa.Date, nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("log_type", sa.String(20), nullable=False),
        sa.Column("note", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("log_type IN ('deposit','withdrawal','interest')", name="ck_hysa_log_type"),
    )

    # ── HYSA Snapshots ────────────────────────────────────
    op.create_table(
        "hysa_snapshots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("account_id", UUID(as_uuid=True), sa.ForeignKey("hysa_accounts.id", ondelete="CASCADE")),
        sa.Column("snapshot_date", sa.Date, nullable=False),
        sa.Column("balance", sa.Numeric(14, 2), nullable=False),
        sa.UniqueConstraint("account_id", "snapshot_date", name="uq_hysa_snap_date"),
    )

    # ── Stock Holdings ────────────────────────────────────
    op.create_table(
        "stock_holdings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("name", sa.String(200)),
        sa.Column("account_type", sa.String(50), server_default="'Roth IRA'"),
        sa.Column("exchange", sa.String(50)),
        sa.Column("quote_type", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # ── Stock Lots ────────────────────────────────────────
    op.create_table(
        "stock_lots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("holding_id", UUID(as_uuid=True), sa.ForeignKey("stock_holdings.id", ondelete="CASCADE")),
        sa.Column("purchase_date", sa.Date),
        sa.Column("shares", sa.Numeric(14, 6), nullable=False),
        sa.Column("price_per_share", sa.Numeric(12, 4), nullable=False),
        sa.Column("amount_spent", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # ── Stock Price History ───────────────────────────────
    op.create_table(
        "stock_price_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("holding_id", UUID(as_uuid=True), sa.ForeignKey("stock_holdings.id", ondelete="CASCADE")),
        sa.Column("price_date", sa.Date, nullable=False),
        sa.Column("price", sa.Numeric(12, 4), nullable=False),
        sa.UniqueConstraint("holding_id", "price_date", name="uq_stock_price_date"),
    )

    # ── Portfolio Snapshots ───────────────────────────────
    op.create_table(
        "portfolio_snapshots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("snapshot_date", sa.Date, nullable=False),
        sa.Column("total_value", sa.Numeric(14, 2), nullable=False),
        sa.UniqueConstraint("user_id", "snapshot_date", name="uq_portfolio_snap_date"),
    )


def downgrade() -> None:
    op.drop_table("portfolio_snapshots")
    op.drop_table("stock_price_history")
    op.drop_table("stock_lots")
    op.drop_table("stock_holdings")
    op.drop_table("hysa_snapshots")
    op.drop_table("hysa_logs")
    op.drop_table("hysa_accounts")
    op.drop_table("savings_buckets")
    op.drop_table("budget_items")
    op.drop_table("budget_years")
    op.drop_table("settings")
    op.drop_table("users")