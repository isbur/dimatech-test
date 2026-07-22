"""Request dependencies (stubs for next implementation step).

TODO:
- get_session: yield AsyncSession from app.ctx.sessionmaker
- get_current_user: decode JWT from Authorization header
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sanic import Request
    from sqlalchemy.ext.asyncio import AsyncSession

    from dimatech.models.user import User


async def get_session() -> AsyncSession:
    raise NotImplementedError("DB session dependency not implemented yet")


async def get_current_user(_request: Request) -> User:
    raise NotImplementedError("JWT auth dependency not implemented yet")
