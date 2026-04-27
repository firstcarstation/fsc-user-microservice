"""JSON list of extra saved addresses on persons.

Revision ID: a5_saved_addrs
Revises: a4_addresses_geo
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a5_saved_addrs"
down_revision: Union[str, Sequence[str], None] = "a4_addresses_geo"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("persons", sa.Column("saved_addresses", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("persons", "saved_addresses")
