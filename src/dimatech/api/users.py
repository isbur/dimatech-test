from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi

from dimatech.schemas.account import AccountOut
from dimatech.schemas.payment import PaymentOut
from dimatech.schemas.user import UserPublic

bp = Blueprint("users", url_prefix="/users")


def _not_implemented() -> JSONResponse:
    return json({"detail": "not implemented"}, status=501)


@bp.get("/me")
@openapi.summary("Current user")
@openapi.description("Return id, email, full_name of the authenticated user.")
@openapi.response(200, {"application/json": UserPublic}, "OK")
@openapi.response(501, {"application/json": dict}, "Not implemented")
async def get_me(_request: Request) -> JSONResponse:
    return _not_implemented()


@bp.get("/me/accounts")
@openapi.summary("Current user accounts")
@openapi.description("Return accounts and balances of the authenticated user.")
@openapi.response(200, {"application/json": list[AccountOut]}, "OK")
@openapi.response(501, {"application/json": dict}, "Not implemented")
async def get_my_accounts(_request: Request) -> JSONResponse:
    return _not_implemented()


@bp.get("/me/payments")
@openapi.summary("Current user payments")
@openapi.description("Return payments of the authenticated user.")
@openapi.response(200, {"application/json": list[PaymentOut]}, "OK")
@openapi.response(501, {"application/json": dict}, "Not implemented")
async def get_my_payments(_request: Request) -> JSONResponse:
    return _not_implemented()
