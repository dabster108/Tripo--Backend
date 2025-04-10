"""Add reset_password_otp columns to users table

Revision ID: 5452a25e2c06
Revises: 
Create Date: 2025-04-10 21:58:33.708416

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '5452a25e2c06'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if the column already exists before adding it
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Get existing columns in the 'users' table
    existing_columns = [col["name"] for col in inspector.get_columns("users")]

    if "reset_password_otp" not in existing_columns:
        op.add_column('users', sa.Column('reset_password_otp', sa.String(length=6), nullable=True))
    if "reset_password_otp_expires" not in existing_columns:
        op.add_column('users', sa.Column('reset_password_otp_expires', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the columns if they exist
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Get existing columns in the 'users' table
    existing_columns = [col["name"] for col in inspector.get_columns("users")]

    if "reset_password_otp" in existing_columns:
        op.drop_column('users', 'reset_password_otp')
    if "reset_password_otp_expires" in existing_columns:
        op.drop_column('users', 'reset_password_otp_expires')