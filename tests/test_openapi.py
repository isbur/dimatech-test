import pytest
from sanic import Sanic

from dimatech.api import openapi_examples as ex

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


def _example(spec: dict, path: str, method: str, status: str):
    return spec["paths"][path][method]["responses"][status]["content"][
        "application/json"
    ]["example"]


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
async def test_openapi_me_requires_bearer_auth(app: Sanic) -> None:
    _request, response = await app.asgi_client.get("/docs/openapi.json")
    assert response.status_code == 200
    assert response.json is not None

    schemes = response.json["components"]["securitySchemes"]
    assert schemes["BearerAuth"]["type"] == "http"
    assert schemes["BearerAuth"]["scheme"] == "bearer"

    me = response.json["paths"]["/api/v1/users/me"]["get"]
    assert {"BearerAuth": []} in me["security"]


@pytest.mark.asyncio
async def test_openapi_decimal_fields_are_strings(app: Sanic) -> None:
    _request, response = await app.asgi_client.get("/docs/openapi.json")
    assert response.status_code == 200
    assert response.json is not None
    spec = response.json

    webhook = spec["paths"]["/api/v1/webhooks/payment"]["post"]
    amount = webhook["requestBody"]["content"]["application/json"]["schema"][
        "properties"
    ]["amount"]
    assert amount["type"] == "string"
    assert "properties" not in amount
    assert amount["examples"] == ["100.00"]

    pay_media = spec["paths"]["/api/v1/users/me/payments"]["get"]["responses"][
        "200"
    ]["content"]["application/json"]
    pay_amount = pay_media["schema"]["items"]["properties"]["amount"]
    assert pay_amount["type"] == "string"
    assert "properties" not in pay_amount
    assert pay_media["example"][0]["amount"] == "100.00"

    accounts = spec["paths"]["/api/v1/users/me/accounts"]["get"]
    acc_media = accounts["responses"]["200"]["content"]["application/json"]
    assert acc_media["example"] == [{"id": 1, "balance": "0.00"}]
    assert acc_media["schema"]["items"]["properties"]["balance"]["examples"] == [
        "0.00"
    ]


@pytest.mark.asyncio
async def test_openapi_response_examples_are_concrete(app: Sanic) -> None:
    _request, response = await app.asgi_client.get("/docs/openapi.json")
    assert response.status_code == 200
    assert response.json is not None
    spec = response.json

    assert _example(spec, "/health", "get", "200") == ex.HEALTH

    assert _example(spec, "/api/v1/auth/login", "post", "200") == ex.TOKEN_RESPONSE
    assert (
        _example(spec, "/api/v1/auth/login", "post", "401")
        == ex.UNAUTHORIZED_CREDENTIALS
    )
    assert (
        _example(spec, "/api/v1/auth/login", "post", "422")
        == ex.VALIDATION_INVALID_EMAIL
    )

    assert _example(spec, "/api/v1/users/me", "get", "200") == ex.USER_PUBLIC
    assert (
        _example(spec, "/api/v1/users/me", "get", "401")
        == ex.UNAUTHORIZED_MISSING_AUTH
    )
    assert (
        _example(spec, "/api/v1/users/me/accounts", "get", "200") == ex.ACCOUNT_LIST
    )
    assert (
        _example(spec, "/api/v1/users/me/payments", "get", "200") == ex.PAYMENT_LIST
    )

    assert (
        _example(spec, "/api/v1/admin/users", "get", "200")
        == ex.USERS_WITH_ACCOUNTS
    )
    assert (
        _example(spec, "/api/v1/admin/users", "get", "403") == ex.FORBIDDEN_ADMIN
    )
    assert (
        _example(spec, "/api/v1/admin/users", "post", "201") == ex.USER_CREATED
    )
    assert (
        _example(spec, "/api/v1/admin/users", "post", "409") == ex.CONFLICT_EMAIL
    )
    assert (
        _example(spec, "/api/v1/admin/users", "post", "422")
        == ex.VALIDATION_SHORT_PASSWORD
    )
    assert (
        _example(spec, "/api/v1/admin/users/{user_id}", "patch", "200")
        == ex.USER_UPDATED
    )
    assert (
        _example(spec, "/api/v1/admin/users/{user_id}", "patch", "404")
        == ex.NOT_FOUND_USER
    )
    assert (
        _example(spec, "/api/v1/admin/users/{user_id}", "delete", "200")
        == ex.USER_DELETED
    )
    assert (
        _example(spec, "/api/v1/admin/users/{user_id}", "delete", "403")
        == ex.FORBIDDEN_SELF_DELETE
    )

    assert _example(spec, "/api/v1/webhooks/payment", "post", "200") == ex.PAYMENT
    assert (
        _example(spec, "/api/v1/webhooks/payment", "post", "400")
        == ex.INVALID_SIGNATURE
    )
    assert (
        _example(spec, "/api/v1/webhooks/payment", "post", "403")
        == ex.FORBIDDEN_ACCOUNT_OWNER
    )
    assert (
        _example(spec, "/api/v1/webhooks/payment", "post", "409")
        == ex.CONFLICT_TRANSACTION
    )
    assert (
        _example(spec, "/api/v1/webhooks/payment", "post", "422")
        == ex.VALIDATION_NON_POSITIVE_AMOUNT
    )
