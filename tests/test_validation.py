import pytest
from sanic import Sanic


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_short_password_is_unauthorized(app: Sanic) -> None:
    _request, response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 401
    assert response.json == {"detail": "Invalid email or password"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_password_with_whitespace_is_unauthorized(app: Sanic) -> None:
    _request, response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "has space1",
        },
    )
    assert response.status_code == 401
    assert response.json == {"detail": "Invalid email or password"}


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
async def test_login_rejects_missing_body(app: Sanic) -> None:
    _request, response = await app.asgi_client.post("/api/v1/auth/login")
    assert response.status_code == 422
    assert response.json == {
        "detail": [
            {
                "loc": ["body"],
                "msg": "Request body is required",
                "type": "missing",
            }
        ]
    }


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_create_rejects_short_password(app: Sanic) -> None:
    _request, login = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "password1"},
    )
    assert login.status_code == 200
    assert login.json is not None
    token = login.json["access_token"]

    _request, response = await app.asgi_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "short.pass@example.com",
            "password": "short",
            "full_name": "Short",
            "role": "user",
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
