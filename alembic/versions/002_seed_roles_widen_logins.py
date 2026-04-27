"""Seed roles (one row per role_type) and widen logins.user_id to 128 chars.

Revision ID: b2c3d4e5f6a8
Revises: a1b2c3d4e5f6
Create Date: 2026-04-04
"""

from __future__ import annotations

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a8"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
_ROLE_LABELS = [
    ("role:customer", "customer"),
    ("role:agent", "agent"),
    ("role:mechanic", "mechanic"),
    ("role:admin", "admin"),
    ("role:hub_manager", "hub_manager"),
    ("role:technician", "technician"),
]


def upgrade() -> None:
    op.alter_column(
        "logins",
        "user_id",
        existing_type=sa.String(length=36),
        type_=sa.String(length=128),
        existing_nullable=False,
    )

    conn = op.get_bind()
    count = conn.execute(sa.text("SELECT COUNT(*) FROM roles")).scalar()
    if int(count or 0) == 0:
        for label, role_type in _ROLE_LABELS:
            rid = str(uuid.uuid5(_NS, label))
            conn.execute(
                sa.text(
                    """
                    INSERT INTO roles (role_id, role_type, company_name, company_tin_number, created_at)
                    VALUES (:rid, CAST(:rtype AS role_type_enum), NULL, NULL, NOW())
                    """
                ),
                {"rid": rid, "rtype": role_type},
            )


def downgrade() -> None:
    bind = op.get_bind()
    for label, _ in _ROLE_LABELS:
        rid = str(uuid.uuid5(_NS, label))
        bind.execute(sa.text("DELETE FROM roles WHERE role_id = :rid"), {"rid": rid})

    op.alter_column(
        "logins",
        "user_id",
        existing_type=sa.String(length=128),
        type_=sa.String(length=36),
        existing_nullable=False,
    )
