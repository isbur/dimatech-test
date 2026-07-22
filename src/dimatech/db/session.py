from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sanic import Sanic
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from dimatech.config import settings

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def init_engine(database_url: str | None = None) -> async_sessionmaker[AsyncSession]:
    global _engine, _sessionmaker

    url = database_url or settings.database_url
    _engine = create_async_engine(url, pool_pre_ping=True)
    _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
    return _sessionmaker


async def close_engine() -> None:
    global _engine, _sessionmaker

    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _sessionmaker = None


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    if _sessionmaker is None:
        raise RuntimeError("Database engine is not initialized")
    return _sessionmaker


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session


def setup_db(app: Sanic) -> None:
    @app.before_server_start
    async def on_before_server_start(_app: Sanic) -> None:
        sessionmaker = init_engine()
        _app.ctx.sessionmaker = sessionmaker

    @app.after_server_stop
    async def on_after_server_stop(_app: Sanic) -> None:
        await close_engine()
