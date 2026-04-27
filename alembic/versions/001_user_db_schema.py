"""user_db: addresses, roles, persons, hubs, users, logins.

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2025-03-05

All PKs/FKs varchar(36). Enums: user_status_enum, role_type_enum.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_status_enum = postgresql.ENUM("active", "inactive", "pending", "suspended", name="user_status_enum", create_type=True)
    user_status_enum.create(op.get_bind(), checkfirst=True)

    role_type_enum = postgresql.ENUM(
        "customer", "agent", "mechanic", "admin", "hub_manager", "technician",
        name="role_type_enum", create_type=True
    )
    role_type_enum.create(op.get_bind(), checkfirst=True)
    # Prevent SQLAlchemy from attempting to CREATE TYPE again during table creation.
    user_status_enum.create_type = False
    role_type_enum.create_type = False

    op.create_table(
        "addresses",
        sa.Column("address_id", sa.String(36), nullable=False),
        sa.Column("address_line_1", sa.Text(), nullable=False),
        sa.Column("address_line_2", sa.Text(), nullable=True),
        sa.Column("country", sa.Text(), nullable=False),
        sa.Column("city", sa.Text(), nullable=False),
        sa.Column("zip_code", sa.String(10), nullable=False),
        sa.Column("address_type", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("address_id"),
    )

    op.create_table(
        "roles",
        sa.Column("role_id", sa.String(36), nullable=False),
        sa.Column("role_type", role_type_enum, nullable=False),
        sa.Column("company_name", sa.Text(), nullable=True),
        sa.Column("company_tin_number", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("role_id"),
    )

    op.create_table(
        "persons",
        sa.Column("person_id", sa.String(36), nullable=False),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("alternate_mobile_no", sa.String(15), nullable=True),
        sa.Column("permanent_address_id", sa.String(36), nullable=True),
        sa.Column("current_address_id", sa.String(36), nullable=True),
        sa.Column("dob", sa.Date(), nullable=True),
        sa.Column("image_path", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["current_address_id"], ["addresses.address_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["permanent_address_id"], ["addresses.address_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("person_id"),
    )
    op.create_index("idx_persons_email", "persons", ["email"])
    op.create_index("idx_persons_permanent_address_id", "persons", ["permanent_address_id"])
    op.create_index("idx_persons_current_address_id", "persons", ["current_address_id"])

    op.create_table(
        "hubs",
        sa.Column("hub_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("city", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("hub_id"),
    )

    op.create_table(
        "users",
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("person_id", sa.String(36), nullable=True),
        sa.Column("mobile_no", sa.String(15), nullable=False),
        sa.Column("role_id", sa.String(36), nullable=False),
        sa.Column("city", sa.Text(), nullable=False),
        sa.Column("status", user_status_enum, nullable=False),
        sa.Column("hub_id", sa.String(36), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["hub_id"], ["hubs.hub_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["person_id"], ["persons.person_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.role_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("mobile_no", name="users_mobile_no_key"),
    )
    op.create_index("idx_users_person_id", "users", ["person_id"])
    op.create_index("idx_users_role_id", "users", ["role_id"])
    op.create_index("idx_users_hub_id", "users", ["hub_id"])
    op.create_index("idx_users_status", "users", ["status"])
    op.create_index("idx_users_created_at", "users", ["created_at"])

    op.create_table(
        "logins",
        sa.Column("login_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("login_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("firebase_uid", sa.String(128), nullable=True),
        sa.Column("token", sa.Text(), nullable=True),
        sa.Column("device_id", sa.Text(), nullable=False),
        sa.Column("device_type", sa.String(50), nullable=True),
        sa.Column("fcm_token", sa.Text(), nullable=False),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("is_logout", sa.Boolean(), nullable=True),
        sa.Column("logout_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("login_id"),
    )
    op.create_index("ix_logins_user_id", "logins", ["user_id"])
    op.create_index("idx_logins_user_login_at", "logins", ["user_id", "login_at"])


def downgrade() -> None:
    op.drop_index("idx_logins_user_login_at", "logins")
    op.drop_index("ix_logins_user_id", "logins")
    op.drop_table("logins")
    op.drop_index("idx_users_created_at", "users")
    op.drop_index("idx_users_status", "users")
    op.drop_index("idx_users_hub_id", "users")
    op.drop_index("idx_users_role_id", "users")
    op.drop_index("idx_users_person_id", "users")
    op.drop_table("users")
    op.drop_table("hubs")
    op.drop_index("idx_persons_current_address_id", "persons")
    op.drop_index("idx_persons_permanent_address_id", "persons")
    op.drop_index("idx_persons_email", "persons")
    op.drop_table("persons")
    op.drop_table("roles")
    op.drop_table("addresses")
    op.execute("DROP TYPE IF EXISTS role_type_enum")
    op.execute("DROP TYPE IF EXISTS user_status_enum")
