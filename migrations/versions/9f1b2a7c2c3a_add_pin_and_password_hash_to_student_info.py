"""add pin_hash and password_hash to student_info (idempotent)

Revision ID: 9f1b2a7c2c3a
Revises: d1b11d93ff51
Create Date: 2025-10-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f1b2a7c2c3a'
down_revision = 'd1b11d93ff51'
branch_labels = None
depends_on = None


def upgrade():
    # Use IF NOT EXISTS to make migration idempotent in PostgreSQL
    op.execute("""
        ALTER TABLE student_info
        ADD COLUMN IF NOT EXISTS pin_hash VARCHAR(255);
    """)
    op.execute("""
        ALTER TABLE student_info
        ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
    """)


def downgrade():
    # Safe downgrades (only drop if exists)
    op.execute("""
        ALTER TABLE student_info
        DROP COLUMN IF EXISTS password_hash;
    """)
    op.execute("""
        ALTER TABLE student_info
        DROP COLUMN IF EXISTS pin_hash;
    """)


