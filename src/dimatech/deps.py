from __future__ import annotations

from dataclasses import dataclass

from sanic import Request
from sanic.exceptions import Forbidden, Unauthorized
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dimatech.models.user import User, UserRole
from dimatech.security.jwt import decode_access_token


@dataclass(frozen=True, slots=True)
class Admin:
    """Authenticated admin principal for DI into admin-only routes."""

    user: User


async def get_session(request: Request) -> AsyncSession:
    session = getattr(request.ctx, "db_session", None)
    if session is not None:
        return session

    sessionmaker = request.app.ctx.sessionmaker
    session = sessionmaker()
    request.ctx.db_session = session
    return session


async def get_current_user(request: Request, session: AsyncSession) -> User:
    header = request.headers.get("authorization")
    if header is None or not header.lower().startswith("bearer "):
        raise Unauthorized("Missing or invalid Authorization header")

    token = header.split(" ", 1)[1].strip()
    if not token:
        raise Unauthorized("Missing or invalid Authorization header")

    try:
        payload = decode_access_token(token)
    except Exception as exc:
        raise Unauthorized("Invalid or expired token") from exc

    subject = payload.get("sub")
    if subject is None:
        raise Unauthorized("Invalid token payload")

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise Unauthorized("Invalid token payload") from exc

    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise Unauthorized("User not found")
    return user


async def get_current_admin(request: Request, user: User) -> Admin:
    _ = request
    if user.role != UserRole.ADMIN:
        raise Forbidden("Admin access required")
    return Admin(user=user)
