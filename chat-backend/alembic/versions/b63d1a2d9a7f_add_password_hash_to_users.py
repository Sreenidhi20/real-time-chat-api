"""add password_hash and created_at to users

Revision ID: b63d1a2d9a7f
Revises: 9c2d7a4e1f63
Create Date: 2026-10-03

"""

from alembic import op
import sqlalchemy as sa


revision = "b63d1a2d9a7f"
down_revision = "9c2d7a4e1f63"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=False, server_default=""),
    )
    op.add_column(
        "users",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.alter_column("users", "password_hash", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "created_at")
    op.drop_column("users", "password_hash")
