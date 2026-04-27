"""Add saved_addresses_default_index to persons.

Revision ID: a6_saved_addrs_default
Revises: a5_saved_addrs
Create Date: 2026-04-23
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a6_saved_addrs_default"
down_revision: Union[str, Sequence[str], None] = "a5_saved_addrs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "persons",
        sa.Column("saved_addresses_default_index", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("persons", "saved_addresses_default_index")

