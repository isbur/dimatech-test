from __future__ import annotations

import asyncio
from decimal import Decimal

import pytest
from sanic import Sanic

from dimatech.config import settings
from dimatech.services.payments import amount_for_signature, build_signature


def test_tz_example_signature() -> None:
    signature = build_signature(
        account_id=1,
        amount=Decimal("100"),
        transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
        user_id=1,
        secret="gfdmhghif38yrf9ew0jkf32",
    )
    assert signature == (
        "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
    )


def test_amount_for_signature_strips_zeros() -> None:
    assert amount_for_signature(Decimal("100.00")) == "100"
    assert amount_for_signature(Decimal("10.50")) == "10.5"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_webhook_credits_seed_account(app: Sanic) -> None:
    transaction_id = "5eae174f-7cd0-472c-bd36-35660f00132b"
    amount = Decimal("100.00")
    signature = build_signature(
        account_id=1,
        amount=amount,
        transaction_id=transaction_id,
        user_id=1,
        secret=settings.webhook_secret,
    )

    _request, response = await app.asgi_client.post(
        "/api/v1/webhooks/payment",
        json={
            "transaction_id": transaction_id,
            "user_id": 1,
            "account_id": 1,
            "amount": "100.00",
            "signature": signature,
        },
    )
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["transaction_id"] == transaction_id
    assert response.json["account_id"] == 1
    assert response.json["user_id"] == 1
    assert response.json["amount"] == "100.00"

    login = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "password1"},
    )
    token = login[1].json["access_token"]
    accounts = await app.asgi_client.get(
        "/api/v1/users/me/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert accounts[1].status_code == 200
    assert accounts[1].json == [{"id": 1, "balance": "100.00"}]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_webhook_idempotent_on_transaction_id(app: Sanic) -> None:
    transaction_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    amount = Decimal("25.50")
    payload = {
        "transaction_id": transaction_id,
        "user_id": 1,
        "account_id": 1,
        "amount": "25.50",
        "signature": build_signature(
            account_id=1,
            amount=amount,
            transaction_id=transaction_id,
            user_id=1,
            secret=settings.webhook_secret,
        ),
    }

    first = await app.asgi_client.post("/api/v1/webhooks/payment", json=payload)
    second = await app.asgi_client.post("/api/v1/webhooks/payment", json=payload)
    assert first[1].status_code == 200
    assert second[1].status_code == 200
    assert first[1].json == second[1].json

    login = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "password1"},
    )
    token = login[1].json["access_token"]
    accounts = await app.asgi_client.get(
        "/api/v1/users/me/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert accounts[1].json[0]["balance"] == "25.50"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_webhook_creates_missing_account(app: Sanic) -> None:
    transaction_id = "11111111-2222-3333-4444-555555555555"
    amount = Decimal("10")
    payload = {
        "transaction_id": transaction_id,
        "user_id": 1,
        "account_id": 42,
        "amount": "10",
        "signature": build_signature(
            account_id=42,
            amount=amount,
            transaction_id=transaction_id,
            user_id=1,
            secret=settings.webhook_secret,
        ),
    }

    _request, response = await app.asgi_client.post(
        "/api/v1/webhooks/payment",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json["account_id"] == 42

    login = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "password1"},
    )
    token = login[1].json["access_token"]
    accounts = await app.asgi_client.get(
        "/api/v1/users/me/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )
    balances = {row["id"]: row["balance"] for row in accounts[1].json}
    assert balances[1] == "0.00"
    assert balances[42] == "10.00"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_webhook_concurrent_create_same_new_account(app: Sanic) -> None:
    """Two different payments racing to create the same missing account."""
    account_id = 77
    payloads = []
    for transaction_id, amount in (
        ("c1111111-1111-1111-1111-111111111111", Decimal("10.00")),
        ("c2222222-2222-2222-2222-222222222222", Decimal("20.00")),
    ):
        payloads.append(
            {
                "transaction_id": transaction_id,
                "user_id": 1,
                "account_id": account_id,
                "amount": str(amount),
                "signature": build_signature(
                    account_id=account_id,
                    amount=amount,
                    transaction_id=transaction_id,
                    user_id=1,
                    secret=settings.webhook_secret,
                ),
            }
        )

    results = await asyncio.gather(
        *(
            app.asgi_client.post("/api/v1/webhooks/payment", json=payload)
            for payload in payloads
        )
    )
    statuses = sorted(response.status_code for _request, response in results)
    assert statuses == [200, 200]

    login = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "password1"},
    )
    token = login[1].json["access_token"]
    accounts = await app.asgi_client.get(
        "/api/v1/users/me/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )
    balances = {row["id"]: row["balance"] for row in accounts[1].json}
    assert balances[account_id] == "30.00"

    payments = await app.asgi_client.get(
        "/api/v1/users/me/payments",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert {row["transaction_id"] for row in payments[1].json} == {
        payloads[0]["transaction_id"],
        payloads[1]["transaction_id"],
    }


@pytest.mark.integration
@pytest.mark.asyncio
async def test_webhook_rejects_bad_signature(app: Sanic) -> None:
    _request, response = await app.asgi_client.post(
        "/api/v1/webhooks/payment",
        json={
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1,
            "account_id": 1,
            "amount": "100.00",
            "signature": "00" * 32,
        },
    )
    assert response.status_code == 400
    assert response.json == {"detail": "Invalid signature"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_webhook_rejects_account_owned_by_other_user(app: Sanic) -> None:
    transaction_id = "99999999-9999-9999-9999-999999999999"
    amount = Decimal("5")
    # account 1 belongs to user 1; claim it for admin (user 2)
    _request, response = await app.asgi_client.post(
        "/api/v1/webhooks/payment",
        json={
            "transaction_id": transaction_id,
            "user_id": 2,
            "account_id": 1,
            "amount": "5",
            "signature": build_signature(
                account_id=1,
                amount=amount,
                transaction_id=transaction_id,
                user_id=2,
                secret=settings.webhook_secret,
            ),
        },
    )
    assert response.status_code == 403
    assert response.json == {"detail": "Account does not belong to user"}
