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


@pytest.mark.asyncio
async def test_openapi_login_has_request_body_example(app: Sanic) -> None:
    _request, response = await app.asgi_client.get("/docs/openapi.json")
    assert response.status_code == 200
    assert response.json is not None

    login = response.json["paths"]["/api/v1/auth/login"]["post"]
    media = login["requestBody"]["content"]["application/json"]
    assert media["example"] == {
        "email": "user@example.com",
        "password": "password1",
    }
    assert "schema" in media
    assert "properties" in media["schema"] or "$ref" in media["schema"]


@pytest.mark.asyncio
async def test_openapi_decimal_fields_are_strings(app: Sanic) -> None:
    _request, response = await app.asgi_client.get("/docs/openapi.json")
    assert response.status_code == 200
    assert response.json is not None

    webhook = response.json["paths"]["/api/v1/webhooks/payment"]["post"]
    amount = webhook["requestBody"]["content"]["application/json"]["schema"][
        "properties"
    ]["amount"]
    assert amount["type"] == "string"
    assert "properties" not in amount
    assert amount["examples"] == ["100.00"]

    payments = response.json["paths"]["/api/v1/users/me/payments"]["get"]
    pay_media = payments["responses"]["200"]["content"]["application/json"]
    pay_amount = pay_media["schema"]["items"]["properties"]["amount"]
    assert pay_amount["type"] == "string"
    assert "properties" not in pay_amount
    assert pay_media["example"][0]["amount"] == "100.00"

    accounts = response.json["paths"]["/api/v1/users/me/accounts"]["get"]
    acc_media = accounts["responses"]["200"]["content"]["application/json"]
    assert acc_media["example"] == [{"id": 1, "balance": "0.00"}]
    assert acc_media["schema"]["items"]["properties"]["balance"]["examples"] == [
        "0.00"
    ]
