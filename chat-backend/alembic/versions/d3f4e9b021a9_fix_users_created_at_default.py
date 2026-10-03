"""fix users created_at default

Revision ID: d3f4e9b021a9
Revises: b63d1a2d9a7f
Create Date: 2026-10-03

"""

from alembic import op
import sqlalchemy as sa


revision = "d3f4e9b021a9"
down_revision = "b63d1a2d9a7f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        op.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        return

    op.execute("UPDATE users SET created_at = NOW() WHERE created_at IS NULL")
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return

    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        nullable=False,
    )
