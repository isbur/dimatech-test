import pytest
from sanic import Sanic


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_success(app: Sanic) -> None:
    _request, response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "password1",
        },
    )
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["token_type"] == "bearer"
    assert isinstance(response.json["access_token"], str)
    assert response.json["access_token"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_rejects_wrong_password(app: Sanic) -> None:
    _request, response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "wrongpass",
        },
    )
    assert response.status_code == 401
    assert response.json == {"detail": "Invalid email or password"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_me_requires_auth(app: Sanic) -> None:
    _request, response = await app.asgi_client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_me_with_token(app: Sanic) -> None:
    _request, login_response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "password1",
        },
    )
    assert login_response.status_code == 200
    assert login_response.json is not None
    token = login_response.json["access_token"]

    _request, response = await app.asgi_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json == {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Test User",
    }


@pytest.mark.integration
@pytest.mark.asyncio
async def test_me_accounts_with_token(app: Sanic) -> None:
    _request, login_response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "password1",
        },
    )
    assert login_response.status_code == 200
    assert login_response.json is not None
    token = login_response.json["access_token"]

    _request, response = await app.asgi_client.get(
        "/api/v1/users/me/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json == [{"id": 1, "balance": "0.00"}]
