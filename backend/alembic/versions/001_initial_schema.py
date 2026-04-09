"""Create initial schema matching current models.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('username', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('email', sa.String(255), unique=True, nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('date_of_birth', sa.Date, nullable=True),
        sa.Column('risk_tolerance', sa.String(20), default='moderate', nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Add check constraint for risk_tolerance
    op.create_check_constraint(
        'ck_users_risk_tolerance',
        'users',
        "risk_tolerance IN ('conservative', 'moderate', 'aggressive', 'speculative')"
    )


def downgrade() -> None:
    op.drop_table('users')
