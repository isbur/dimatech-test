from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi, validate

from dimatech.api.openapi_body import json_body, json_content
from dimatech.schemas.auth import LoginRequest, TokenResponse
from dimatech.schemas.errors import MessageResponse, ValidationErrorResponse

bp = Blueprint("auth", url_prefix="/auth")


def _not_implemented() -> JSONResponse:
    return json({"detail": "not implemented"}, status=501)


@bp.post("/login")
@openapi.summary("Login")
@openapi.description("Authenticate user or admin by email/password.")
@openapi.body(
    json_body(
        LoginRequest,
        example={
            "email": "user@example.com",
            "password": "password1",
        },
    ),
    required=True,
)
@openapi.response(200, json_content(TokenResponse), "OK")
@openapi.response(422, json_content(ValidationErrorResponse), "Validation error")
@openapi.response(501, json_content(MessageResponse), "Not implemented")
@validate(json=LoginRequest)
async def login(_request: Request, body: LoginRequest) -> JSONResponse:
    _ = body
    return _not_implemented()
