"""Initial database schema for Financial Dashboard.

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Accounts table (for different investment accounts)
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('account_type', sa.String(50), nullable=False),  # e.g., 'brokerage', '401k', 'ira'
        sa.Column('initial_balance', sa.Numeric(12, 2), nullable=False),
        sa.Column('current_balance', sa.Numeric(12, 2), nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Holdings table (stocks/bonds held in accounts)
    op.create_table(
        'holdings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer, sa.ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('quantity', sa.Numeric(12, 4), nullable=False),
        sa.Column('average_cost', sa.Numeric(12, 4), nullable=False),
        sa.Column('current_price', sa.Numeric(12, 4), nullable=True),
        sa.Column('current_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_holdings_symbol', 'holdings', ['symbol'])

    # Transactions table (buy/sell history)
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer, sa.ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('transaction_type', sa.String(20), nullable=False),  # 'buy' or 'sell'
        sa.Column('quantity', sa.Numeric(12, 4), nullable=False),
        sa.Column('price_per_unit', sa.Numeric(12, 4), nullable=False),
        sa.Column('total_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('fees', sa.Numeric(10, 2), default=0, nullable=False),
        sa.Column('transaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_transactions_symbol', 'transactions', ['symbol'])
    op.create_index('ix_transactions_date', 'transactions', ['transaction_date'])

    # Price history table (for charting)
    op.create_table(
        'price_history',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('symbol', sa.String(20), nullable=False, index=True),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('open', sa.Numeric(12, 4), nullable=True),
        sa.Column('high', sa.Numeric(12, 4), nullable=True),
        sa.Column('low', sa.Numeric(12, 4), nullable=True),
        sa.Column('close', sa.Numeric(12, 4), nullable=False),
        sa.Column('volume', sa.BigInteger, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('symbol', 'date', name='uq_price_symbol_date'),
    )

    # Audit log table (for compliance and debugging)
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('resource', sa.String(255), nullable=False),
        sa.Column('details', sa.JSON, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('price_history')
    op.drop_table('transactions')
    op.drop_table('holdings')
    op.drop_table('accounts')
    op.drop_table('users')
