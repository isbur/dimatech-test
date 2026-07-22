from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi, validate

from dimatech.schemas.auth import LoginRequest, TokenResponse

bp = Blueprint("auth", url_prefix="/auth")


def _not_implemented() -> JSONResponse:
    return json({"detail": "not implemented"}, status=501)


@bp.post("/login")
@openapi.summary("Login")
@openapi.description("Authenticate user or admin by email/password.")
@openapi.response(200, {"application/json": TokenResponse}, "OK")
@openapi.response(422, {"application/json": dict}, "Validation error")
@openapi.response(501, {"application/json": dict}, "Not implemented")
@validate(json=LoginRequest)
async def login(_request: Request, body: LoginRequest) -> JSONResponse:
    _ = body
    return _not_implemented()
