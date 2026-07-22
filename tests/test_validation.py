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
    assert response.json == {
        "detail": [
            {
                "loc": ["password"],
                "msg": "password must be at least 8 characters long",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_login_rejects_password_with_whitespace(app: Sanic) -> None:
    _request, response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "has space1",
        },
    )
    assert response.status_code == 422
    assert response.json == {
        "detail": [
            {
                "loc": ["password"],
                "msg": "password must not contain whitespace",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_login_rejects_invalid_email(app: Sanic) -> None:
    _request, response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={
            "email": "not-an-email",
            "password": "longenough",
        },
    )
    assert response.status_code == 422
    assert response.json is not None
    detail = response.json["detail"]
    assert len(detail) == 1
    assert detail[0]["loc"] == ["email"]
    assert "email" in detail[0]["msg"].lower()


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
    detail = response.json["detail"]
    assert len(detail) == 1
    assert detail[0]["loc"] == ["amount"]
    assert detail[0]["type"] == "greater_than"
