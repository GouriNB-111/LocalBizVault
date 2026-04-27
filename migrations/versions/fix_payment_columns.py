"""fix payment column sizes

Revision ID: fix_payment_cols
Revises: 
Create Date: 2026-04-27

"""
from alembic import op
import sqlalchemy as sa

# Replace this with your actual latest revision ID
# Find it by looking at the most recent file in migrations/versions/
revision = 'fix_payment_cols'
down_revision = None  # ← PUT YOUR LATEST REVISION ID HERE e.g. 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('order', 'payment_status',
                    existing_type=sa.String(20),
                    type_=sa.String(100),
                    existing_nullable=True)
    op.alter_column('order', 'payment_method',
                    existing_type=sa.String(20),
                    type_=sa.String(50),
                    existing_nullable=True)


def downgrade():
    op.alter_column('order', 'payment_status',
                    existing_type=sa.String(100),
                    type_=sa.String(20),
                    existing_nullable=True)
    op.alter_column('order', 'payment_method',
                    existing_type=sa.String(50),
                    type_=sa.String(20),
                    existing_nullable=True)