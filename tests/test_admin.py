import uuid

import pytest
from sanic import Sanic


async def _admin_token(app: Sanic) -> str:
    _request, response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "password1"},
    )
    assert response.status_code == 200
    assert response.json is not None
    return response.json["access_token"]


async def _user_token(app: Sanic) -> str:
    _request, response = await app.asgi_client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "password1"},
    )
    assert response.status_code == 200
    assert response.json is not None
    return response.json["access_token"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_list_users_forbidden_for_user(app: Sanic) -> None:
    token = await _user_token(app)
    _request, response = await app.asgi_client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_list_users(app: Sanic) -> None:
    token = await _admin_token(app)
    _request, response = await app.asgi_client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json is not None
    emails = {item["email"] for item in response.json}
    assert "user@example.com" in emails
    assert "admin@example.com" in emails
    user_row = next(item for item in response.json if item["email"] == "user@example.com")
    assert len(user_row["accounts"]) == 1
    assert user_row["accounts"][0]["balance"] == "0.00"
    assert isinstance(user_row["accounts"][0]["id"], int)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_create_update_delete_user(app: Sanic) -> None:
    token = await _admin_token(app)
    headers = {"Authorization": f"Bearer {token}"}
    email = f"crud-{uuid.uuid4().hex}@example.com"

    _request, created = await app.asgi_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": email,
            "password": "password1",
            "full_name": "CRUD User",
            "role": "user",
        },
    )
    assert created.status_code == 201
    assert created.json is not None
    user_id = created.json["id"]
    assert created.json == {
        "id": user_id,
        "email": email,
        "full_name": "CRUD User",
    }

    _request, updated = await app.asgi_client.patch(
        f"/api/v1/admin/users/{user_id}",
        headers=headers,
        json={"full_name": "CRUD User Updated"},
    )
    assert updated.status_code == 200
    assert updated.json is not None
    assert updated.json["full_name"] == "CRUD User Updated"

    _request, deleted = await app.asgi_client.delete(
        f"/api/v1/admin/users/{user_id}",
        headers=headers,
    )
    assert deleted.status_code == 200
    assert deleted.json == {"detail": "User deleted"}

    _request, missing = await app.asgi_client.patch(
        f"/api/v1/admin/users/{user_id}",
        headers=headers,
        json={"full_name": "Gone"},
    )
    assert missing.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_cannot_delete_self(app: Sanic) -> None:
    token = await _admin_token(app)
    _request, me = await app.asgi_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    assert me.json is not None
    admin_id = me.json["id"]

    _request, response = await app.asgi_client.delete(
        f"/api/v1/admin/users/{admin_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json == {"detail": "Cannot delete your own account"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_create_duplicate_email(app: Sanic) -> None:
    token = await _admin_token(app)
    _request, response = await app.asgi_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "user@example.com",
            "password": "password1",
            "full_name": "Dup",
            "role": "user",
        },
    )
    assert response.status_code == 409
    assert response.json == {"detail": "Email already registered"}
