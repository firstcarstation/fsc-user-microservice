"""user_db: add company trade license + landline fields.

Revision ID: c3a7f2b1d901
Revises: 002_seed_roles_widen_logins
Create Date: 2026-04-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c3a7f2b1d901"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("roles", sa.Column("company_trade_license_number", sa.Text(), nullable=True))
    op.add_column("roles", sa.Column("company_landline_number", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("roles", "company_landline_number")
    op.drop_column("roles", "company_trade_license_number")

