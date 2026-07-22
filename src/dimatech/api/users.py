from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi

from dimatech.api.openapi_body import json_content
from dimatech.schemas.account import AccountOut
from dimatech.schemas.errors import MessageResponse
from dimatech.schemas.payment import PaymentOut
from dimatech.schemas.user import UserPublic

bp = Blueprint("users", url_prefix="/users")


def _not_implemented() -> JSONResponse:
    return json({"detail": "not implemented"}, status=501)


@bp.get("/me")
@openapi.summary("Current user")
@openapi.description("Return id, email, full_name of the authenticated user.")
@openapi.response(200, json_content(UserPublic), "OK")
@openapi.response(501, json_content(MessageResponse), "Not implemented")
async def get_me(_request: Request) -> JSONResponse:
    return _not_implemented()


@bp.get("/me/accounts")
@openapi.summary("Current user accounts")
@openapi.description("Return accounts and balances of the authenticated user.")
@openapi.response(
    200,
    json_content(
        list[AccountOut],
        example=[{"id": 1, "balance": "0.00"}],
    ),
    "OK",
)
@openapi.response(501, json_content(MessageResponse), "Not implemented")
async def get_my_accounts(_request: Request) -> JSONResponse:
    return _not_implemented()


@bp.get("/me/payments")
@openapi.summary("Current user payments")
@openapi.description("Return payments of the authenticated user.")
@openapi.response(
    200,
    json_content(
        list[PaymentOut],
        example=[
            {
                "id": 1,
                "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
                "account_id": 1,
                "user_id": 1,
                "amount": "100.00",
            }
        ],
    ),
    "OK",
)
@openapi.response(501, json_content(MessageResponse), "Not implemented")
async def get_my_payments(_request: Request) -> JSONResponse:
    return _not_implemented()
