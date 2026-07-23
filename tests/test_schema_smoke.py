import uuid
from collections.abc import AsyncIterator
from decimal import Decimal

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from dimatech.models import Account, Payment, User, UserRole


@pytest.fixture
async def db_session(database_url: str | None) -> AsyncIterator[AsyncSession]:
    if database_url is None:
        pytest.skip("Postgres unavailable")

    engine = create_async_engine(database_url, pool_pre_ping=True)
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as exc:
        await engine.dispose()
        pytest.skip(f"database unavailable: {exc}")

    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        try:
            yield session
        finally:
            await session.rollback()

    await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_schema_smoke_insert_delete(db_session: AsyncSession) -> None:
    """Smoke: insert/delete a user → account → payment graph against live schema."""
    email = f"smoke-{uuid.uuid4().hex}@example.com"

    user = User(
        email=email,
        password_hash="not-a-real-hash",
        full_name="Smoke Test",
        role=UserRole.USER,
    )
    db_session.add(user)
    await db_session.flush()

    account = Account(user_id=user.id, balance=Decimal("0.00"))
    db_session.add(account)
    await db_session.flush()

    payment = Payment(
        transaction_id=str(uuid.uuid4()),
        account_id=account.id,
        user_id=user.id,
        amount=Decimal("100.00"),
    )
    db_session.add(payment)
    await db_session.flush()

    loaded_payment = await db_session.scalar(
        select(Payment).where(Payment.transaction_id == payment.transaction_id)
    )
    assert loaded_payment is not None
    assert loaded_payment.amount == Decimal("100.00")
    assert loaded_payment.account_id == account.id
    assert loaded_payment.user_id == user.id

    await db_session.delete(payment)
    await db_session.delete(account)
    await db_session.delete(user)
    await db_session.flush()

    assert (
        await db_session.scalar(select(User).where(User.email == email))
    ) is None
