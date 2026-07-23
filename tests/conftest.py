from __future__ import annotations

import asyncio
import os
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest
from sanic import Sanic
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url

from dimatech.config import settings
from dimatech.main import create_app

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE_NAME = "dimatech_test"

# bcrypt hash for password: password1 (same as seed migration)
_PASSWORD_HASH = "$2b$12$gIXwMzgnjyW30eHHL3MtP.6fhQ3CO4F./7oMZUcs9P4Vg7LabFbs2"


def _admin_url(database_url: str) -> URL:
    return make_url(database_url).set(database="postgres")


def _test_url(database_url: str) -> URL:
    return make_url(database_url).set(database=TEST_DATABASE_NAME)


def _run_alembic_upgrade(database_url: str) -> None:
    env = {**os.environ, "DATABASE_URL": database_url}
    subprocess.run(
        ["alembic", "upgrade", "head"],
        check=True,
        cwd=PROJECT_ROOT,
        env=env,
    )


def _terminate_and_drop(admin_url: URL, database_name: str) -> None:
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE datname = :name AND pid <> pg_backend_pid()"
                ),
                {"name": database_name},
            )
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))
    finally:
        engine.dispose()


def _create_database(admin_url: URL, database_name: str) -> None:
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    finally:
        engine.dispose()


def reset_and_reseed(database_url: str) -> None:
    """Wipe app tables and restore seed user/admin/account."""
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "TRUNCATE TABLE payments, accounts, users "
                    "RESTART IDENTITY CASCADE"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO users (id, email, password_hash, full_name, role) "
                    "VALUES "
                    "(1, 'user@example.com', :hash, 'Test User', 'user'), "
                    "(2, 'admin@example.com', :hash, 'Test Admin', 'admin')"
                ),
                {"hash": _PASSWORD_HASH},
            )
            connection.execute(
                text(
                    "INSERT INTO accounts (id, user_id, balance) "
                    "VALUES (1, 1, 0.00)"
                )
            )
            connection.execute(
                text("SELECT setval(pg_get_serial_sequence('users', 'id'), 2)")
            )
            connection.execute(
                text("SELECT setval(pg_get_serial_sequence('accounts', 'id'), 1)")
            )
    finally:
        engine.dispose()


async def _dispose_app_engine() -> None:
    from dimatech.db import session as db_session

    await db_session.close_engine()


@pytest.fixture(scope="session")
def database_url() -> Iterator[str | None]:
    """Ephemeral Postgres DB for the test session, or None if Postgres is down."""
    base_url = settings.database_url
    admin_url = _admin_url(base_url)
    test_url = _test_url(base_url)
    test_url_str = test_url.render_as_string(hide_password=False)

    probe = create_engine(admin_url)
    try:
        with probe.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        probe.dispose()
        yield None
        return
    probe.dispose()

    _terminate_and_drop(admin_url, TEST_DATABASE_NAME)
    _create_database(admin_url, TEST_DATABASE_NAME)
    try:
        _run_alembic_upgrade(test_url_str)
    except Exception:
        _terminate_and_drop(admin_url, TEST_DATABASE_NAME)
        raise

    original_override = settings.database_url_override
    settings.database_url_override = test_url_str
    try:
        yield test_url_str
    finally:
        settings.database_url_override = original_override
        try:
            asyncio.run(_dispose_app_engine())
        except Exception:
            pass
        _terminate_and_drop(admin_url, TEST_DATABASE_NAME)


@pytest.fixture(autouse=True)
def _integration_database(
    request: pytest.FixtureRequest,
    database_url: str | None,
) -> Iterator[None]:
    marker = request.node.get_closest_marker("integration")
    if marker is None:
        yield
        return

    if database_url is None:
        pytest.skip("Postgres unavailable")

    settings.database_url_override = database_url
    yield
    reset_and_reseed(database_url)


@pytest.fixture
def app(database_url: str | None) -> Iterator[Sanic]:
    """App pointed at the ephemeral test DB when Postgres is available."""
    if database_url is not None:
        settings.database_url_override = database_url

    Sanic.test_mode = True
    application = create_app()
    yield application

    try:
        asyncio.run(_dispose_app_engine())
    except Exception:
        pass
