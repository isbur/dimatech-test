import uuid
from decimal import Decimal

import pytest
from sanic import Sanic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dimatech.config import settings
from dimatech.models.account import Account


async def _admin_headers(app: Sanic) -> dict[str, str]:
    _request, response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "password1"},
    )
    assert response.status_code == 200
    assert response.json is not None
    return {"Authorization": f"Bearer {response.json['access_token']}"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_account_create_list_get_delete(app: Sanic) -> None:
    headers = await _admin_headers(app)
    email = f"account-owner-{uuid.uuid4().hex}@example.com"

    _request, owner = await app.asgi_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": email,
            "password": "password1",
            "full_name": "Account Owner",
            "role": "user",
        },
    )
    assert owner.status_code == 201
    assert owner.json is not None
    user_id = owner.json["id"]

    _request, created = await app.asgi_client.post(
        "/api/v1/admin/accounts",
        headers=headers,
        json={"user_id": user_id},
    )
    assert created.status_code == 201
    assert created.json is not None
    account_id = created.json["id"]
    assert created.json == {
        "id": account_id,
        "user_id": user_id,
        "balance": "0.00",
    }

    _request, listed = await app.asgi_client.get(
        "/api/v1/admin/accounts",
        headers=headers,
    )
    assert listed.status_code == 200
    assert listed.json is not None
    assert any(item["id"] == account_id for item in listed.json)

    _request, fetched = await app.asgi_client.get(
        f"/api/v1/admin/accounts/{account_id}",
        headers=headers,
    )
    assert fetched.status_code == 200
    assert fetched.json == {
        "id": account_id,
        "user_id": user_id,
        "balance": "0.00",
    }

    _request, deleted = await app.asgi_client.delete(
        f"/api/v1/admin/accounts/{account_id}",
        headers=headers,
    )
    assert deleted.status_code == 200
    assert deleted.json == {"detail": "Account deleted"}

    _request, _ = await app.asgi_client.delete(
        f"/api/v1/admin/users/{user_id}",
        headers=headers,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_cannot_delete_account_with_balance(app: Sanic) -> None:
    headers = await _admin_headers(app)
    email = f"funded-{uuid.uuid4().hex}@example.com"

    _request, owner = await app.asgi_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": email,
            "password": "password1",
            "full_name": "Funded Owner",
            "role": "user",
        },
    )
    assert owner.status_code == 201
    assert owner.json is not None
    user_id = owner.json["id"]

    _request, created = await app.asgi_client.post(
        "/api/v1/admin/accounts",
        headers=headers,
        json={"user_id": user_id},
    )
    assert created.status_code == 201
    assert created.json is not None
    account_id = created.json["id"]

    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        account = await session.scalar(select(Account).where(Account.id == account_id))
        assert account is not None
        account.balance = Decimal("10.00")
        await session.commit()
    await engine.dispose()

    _request, response = await app.asgi_client.delete(
        f"/api/v1/admin/accounts/{account_id}",
        headers=headers,
    )
    assert response.status_code == 403
    assert response.json == {"detail": "Cannot delete account with non-zero balance"}

    # reset balance via DB so cleanup delete works, then remove user
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        account = await session.scalar(select(Account).where(Account.id == account_id))
        assert account is not None
        account.balance = Decimal("0.00")
        await session.commit()
    await engine.dispose()

    _request, _ = await app.asgi_client.delete(
        f"/api/v1/admin/users/{user_id}",
        headers=headers,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_create_account_unknown_user(app: Sanic) -> None:
    headers = await _admin_headers(app)
    _request, response = await app.asgi_client.post(
        "/api/v1/admin/accounts",
        headers=headers,
        json={"user_id": 999999},
    )
    assert response.status_code == 404
    assert response.json == {"detail": "User not found"}
