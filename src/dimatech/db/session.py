from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sanic import Request, Sanic
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from dimatech.config import settings
from dimatech.deps import get_current_user, get_session
from dimatech.models.user import User

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
    sessionmaker = init_engine()
    app.ctx.sessionmaker = sessionmaker
    app.ext.add_dependency(AsyncSession, get_session)
    app.ext.add_dependency(User, get_current_user)

    @app.after_server_stop
    async def on_after_server_stop(_app: Sanic) -> None:
        await close_engine()

    @app.middleware("response")
    async def close_db_session(request: Request, _response) -> None:
        session = getattr(request.ctx, "db_session", None)
        if session is not None:
            await session.close()
