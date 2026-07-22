import pytest
from sanic import Sanic


@pytest.mark.asyncio
async def test_login_rejects_short_password(app: Sanic) -> None:
    _request, response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 422
    assert response.json is not None
    assert response.json["status"] == 422


@pytest.mark.asyncio
async def test_webhook_rejects_non_positive_amount(app: Sanic) -> None:
    _request, response = await app.asgi_client.post(
        "/api/v1/webhooks/payment",
        json={
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1,
            "account_id": 1,
            "amount": 0,
            "signature": "abc",
        },
    )
    assert response.status_code == 422
    assert response.json is not None
    assert response.json["status"] == 422
