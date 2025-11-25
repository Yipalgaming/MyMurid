"""add student_id to transaction table

Revision ID: fd8bf217d324
Revises: 9f1b2a7c2c3a
Create Date: 2025-11-25 16:10:44.365983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd8bf217d324'
down_revision = '9f1b2a7c2c3a'
branch_labels = None
depends_on = None


def upgrade():
    # Add student_id column if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'transaction'
              AND column_name = 'student_id'
        ) THEN
            ALTER TABLE transaction
            ADD COLUMN student_id INTEGER;
        END IF;
    END $$;
    """)

    # Add FK constraint if not exists
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints
            WHERE constraint_name = 'transaction_student_id_fkey'
              AND table_name = 'transaction'
        ) THEN
            ALTER TABLE transaction
            ADD CONSTRAINT transaction_student_id_fkey
            FOREIGN KEY (student_id) REFERENCES student_info (id);
        END IF;
    END $$;
    """)

    # Add index for faster lookups
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_indexes
            WHERE tablename = 'transaction'
              AND indexname = 'ix_transaction_student_id'
        ) THEN
            CREATE INDEX ix_transaction_student_id
                ON transaction (student_id);
        END IF;
    END $$;
    """)


def downgrade():
    # Remove FK constraint
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM information_schema.table_constraints
            WHERE constraint_name = 'transaction_student_id_fkey'
              AND table_name = 'transaction'
        ) THEN
            ALTER TABLE transaction
            DROP CONSTRAINT transaction_student_id_fkey;
        END IF;
    END $$;
    """)

    # Drop index
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM pg_indexes
            WHERE tablename = 'transaction'
              AND indexname = 'ix_transaction_student_id'
        ) THEN
            DROP INDEX ix_transaction_student_id;
        END IF;
    END $$;
    """)

    # Drop column
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'transaction'
              AND column_name = 'student_id'
        ) THEN
            ALTER TABLE transaction
            DROP COLUMN student_id;
        END IF;
    END $$;
    """)
