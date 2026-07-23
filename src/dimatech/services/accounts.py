from __future__ import annotations

from decimal import Decimal

from sanic.exceptions import Forbidden, NotFound
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dimatech.models.account import Account
from dimatech.models.user import User
from dimatech.schemas.account import AccountCreate


async def list_accounts(session: AsyncSession) -> list[Account]:
    result = await session.scalars(select(Account).order_by(Account.id))
    return list(result.all())


async def get_account(session: AsyncSession, account_id: int) -> Account:
    account = await session.scalar(select(Account).where(Account.id == account_id))
    if account is None:
        raise NotFound("Account not found")
    return account


async def create_account(session: AsyncSession, data: AccountCreate) -> Account:
    user = await session.scalar(select(User).where(User.id == data.user_id))
    if user is None:
        raise NotFound("User not found")

    account = Account(user_id=data.user_id, balance=Decimal("0.00"))
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account


async def delete_account(session: AsyncSession, account_id: int) -> None:
    account = await session.scalar(
        select(Account)
        .where(Account.id == account_id)
        .options(selectinload(Account.payments))
    )
    if account is None:
        raise NotFound("Account not found")
    if account.balance != 0:
        raise Forbidden("Cannot delete account with non-zero balance")

    await session.delete(account)
    await session.commit()
