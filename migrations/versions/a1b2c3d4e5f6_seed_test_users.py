"""Seed test user, admin, and user account.

Revision ID: a1b2c3d4e5f6
Revises: f10d1bbe841e
Create Date: 2026-07-22 21:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f10d1bbe841e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# bcrypt hash for password: password1
_PASSWORD_HASH = "$2b$12$gIXwMzgnjyW30eHHL3MtP.6fhQ3CO4F./7oMZUcs9P4Vg7LabFbs2"


def upgrade() -> None:
    users = sa.table(
        "users",
        sa.column("id", sa.Integer),
        sa.column("email", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("full_name", sa.String),
        sa.column("role", sa.String),
    )
    accounts = sa.table(
        "accounts",
        sa.column("id", sa.Integer),
        sa.column("user_id", sa.Integer),
        sa.column("balance", sa.Numeric),
    )

    op.bulk_insert(
        users,
        [
            {
                "id": 1,
                "email": "user@example.com",
                "password_hash": _PASSWORD_HASH,
                "full_name": "Test User",
                "role": "user",
            },
            {
                "id": 2,
                "email": "admin@example.com",
                "password_hash": _PASSWORD_HASH,
                "full_name": "Test Admin",
                "role": "admin",
            },
        ],
    )
    op.bulk_insert(
        accounts,
        [
            {
                "id": 1,
                "user_id": 1,
                "balance": "0.00",
            },
        ],
    )
    op.execute(sa.text("SELECT setval(pg_get_serial_sequence('users', 'id'), 2)"))
    op.execute(sa.text("SELECT setval(pg_get_serial_sequence('accounts', 'id'), 1)"))


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM accounts WHERE id = 1"))
    op.execute(sa.text("DELETE FROM users WHERE id IN (1, 2)"))
