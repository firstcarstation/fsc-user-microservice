"""Add recovery_on_duty flag on users (recovery agent availability).

Revision ID: a7_recovery_on_duty
Revises: a6_saved_addrs_default
Create Date: 2026-04-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a7_recovery_on_duty"
down_revision: Union[str, Sequence[str], None] = "a6_saved_addrs_default"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("recovery_on_duty", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("users", "recovery_on_duty")
