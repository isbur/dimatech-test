from __future__ import annotations

from sanic.exceptions import Forbidden, NotFound
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dimatech.api.errors import Conflict
from dimatech.models.account import Account
from dimatech.models.user import User
from dimatech.schemas.user import UserCreate, UserUpdate
from dimatech.security.passwords import hash_password


async def list_users_with_accounts(session: AsyncSession) -> list[User]:
    result = await session.scalars(
        select(User).options(selectinload(User.accounts)).order_by(User.id)
    )
    return list(result.all())


async def create_user(session: AsyncSession, data: UserCreate) -> User:
    user = User(
        email=str(data.email),
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise Conflict("Email already registered") from exc
    await session.refresh(user)
    return user


async def update_user(
    session: AsyncSession,
    user_id: int,
    data: UserUpdate,
) -> User:
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise NotFound("User not found")

    updates = data.model_dump(exclude_unset=True)
    if "password" in updates:
        password = updates.pop("password")
        if password is not None:
            user.password_hash = hash_password(password)
    if "email" in updates and updates["email"] is not None:
        user.email = str(updates.pop("email"))
    for field, value in updates.items():
        if value is not None:
            setattr(user, field, value)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise Conflict("Email already registered") from exc
    await session.refresh(user)
    return user


async def delete_user(
    session: AsyncSession,
    user_id: int,
    *,
    actor_user_id: int,
) -> None:
    if user_id == actor_user_id:
        raise Forbidden("Cannot delete your own account")

    user = await session.scalar(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.accounts).selectinload(Account.payments))
    )
    if user is None:
        raise NotFound("User not found")

    await session.delete(user)
    await session.commit()
