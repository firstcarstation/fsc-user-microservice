"""Add optional geo fields to addresses (lat/lng/place_id).

Revision ID: a4_addresses_geo
Revises: c3a7f2b1d901
Create Date: 2026-04-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a4_addresses_geo"
down_revision: Union[str, Sequence[str], None] = "c3a7f2b1d901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("addresses", sa.Column("lat", sa.Float(), nullable=True))
    op.add_column("addresses", sa.Column("lng", sa.Float(), nullable=True))
    op.add_column("addresses", sa.Column("place_id", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("addresses", "place_id")
    op.drop_column("addresses", "lng")
    op.drop_column("addresses", "lat")

