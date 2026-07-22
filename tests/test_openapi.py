import pytest
from sanic import Sanic

EXPECTED_PATHS = {
    "/health",
    "/api/v1/auth/login",
    "/api/v1/users/me",
    "/api/v1/users/me/accounts",
    "/api/v1/users/me/payments",
    "/api/v1/admin/users",
    "/api/v1/admin/users/{user_id}",
    "/api/v1/webhooks/payment",
}


@pytest.mark.asyncio
async def test_openapi_exposes_expected_paths(app: Sanic) -> None:
    _request, response = await app.asgi_client.get("/docs/openapi.json")
    assert response.status_code == 200
    assert response.json is not None

    paths = set(response.json.get("paths", {}).keys())
    missing = EXPECTED_PATHS - paths
    assert not missing, f"missing OpenAPI paths: {sorted(missing)}"
