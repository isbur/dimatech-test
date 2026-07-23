from __future__ import annotations

import hashlib
from decimal import Decimal

from sanic.exceptions import Forbidden, InvalidUsage, NotFound
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dimatech.api.errors import Conflict
from dimatech.config import settings
from dimatech.models.account import Account
from dimatech.models.payment import Payment
from dimatech.models.user import User
from dimatech.schemas.payment import WebhookPaymentIn


def amount_for_signature(amount: Decimal) -> str:
    """Format amount the way the TZ signature example expects (no trailing zeros)."""
    quantized = amount.quantize(Decimal("0.01"))
    if quantized == quantized.to_integral_value():
        return str(int(quantized))
    return format(quantized, "f").rstrip("0").rstrip(".")


def build_signature(
    *,
    account_id: int,
    amount: Decimal,
    transaction_id: str,
    user_id: int,
    secret: str,
) -> str:
    payload = (
        f"{account_id}"
        f"{amount_for_signature(amount)}"
        f"{transaction_id}"
        f"{user_id}"
        f"{secret}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_signature(data: WebhookPaymentIn, secret: str | None = None) -> None:
    expected = build_signature(
        account_id=data.account_id,
        amount=data.amount,
        transaction_id=data.transaction_id,
        user_id=data.user_id,
        secret=secret if secret is not None else settings.webhook_secret,
    )
    if data.signature != expected:
        raise InvalidUsage("Invalid signature")


async def _sync_accounts_id_sequence(session: AsyncSession) -> None:
    await session.execute(
        text(
            "SELECT setval("
            "pg_get_serial_sequence('accounts', 'id'), "
            "COALESCE((SELECT MAX(id) FROM accounts), 1))"
        )
    )


async def _get_or_create_account(
    session: AsyncSession,
    *,
    account_id: int,
    user_id: int,
) -> Account:
    """Lock existing account, or create it; recover from concurrent INSERT race."""
    account = await session.scalar(
        select(Account).where(Account.id == account_id).with_for_update()
    )
    if account is None:
        try:
            # SAVEPOINT: failed INSERT must not abort the outer payment transaction.
            async with session.begin_nested():
                account = Account(
                    id=account_id,
                    user_id=user_id,
                    balance=Decimal("0.00"),
                )
                session.add(account)
                await session.flush()
                await _sync_accounts_id_sequence(session)
        except IntegrityError:
            account = await session.scalar(
                select(Account)
                .where(Account.id == account_id)
                .with_for_update()
            )
            if account is None:
                raise Conflict("Could not create account") from None

    if account.user_id != user_id:
        raise Forbidden("Account does not belong to user")
    return account


async def process_webhook_payment(
    session: AsyncSession,
    data: WebhookPaymentIn,
) -> Payment:
    verify_signature(data)

    existing = await session.scalar(
        select(Payment).where(Payment.transaction_id == data.transaction_id)
    )
    if existing is not None:
        if (
            existing.account_id != data.account_id
            or existing.user_id != data.user_id
            or existing.amount != data.amount.quantize(Decimal("0.01"))
        ):
            raise Conflict("Transaction already processed with different payload")
        return existing

    user = await session.scalar(select(User).where(User.id == data.user_id))
    if user is None:
        raise NotFound("User not found")

    account = await _get_or_create_account(
        session,
        account_id=data.account_id,
        user_id=data.user_id,
    )

    payment = Payment(
        transaction_id=data.transaction_id,
        account_id=account.id,
        user_id=data.user_id,
        amount=data.amount.quantize(Decimal("0.01")),
    )
    account.balance = account.balance + payment.amount
    session.add(payment)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raced = await session.scalar(
            select(Payment).where(Payment.transaction_id == data.transaction_id)
        )
        if raced is not None:
            return raced
        raise Conflict("Could not process payment") from exc

    await session.refresh(payment)
    return payment
