from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dimatech.api.openapi_body import json_content
from dimatech.models.payment import Payment
from dimatech.models.user import User
from dimatech.schemas.account import AccountOut
from dimatech.schemas.errors import MessageResponse
from dimatech.schemas.payment import PaymentOut
from dimatech.schemas.user import UserPublic

bp = Blueprint("users", url_prefix="/users")


@bp.get("/me")
@openapi.summary("Current user")
@openapi.description("Return id, email, full_name of the authenticated user.")
@openapi.secured("BearerAuth")
@openapi.response(200, json_content(UserPublic), "OK")
@openapi.response(401, json_content(MessageResponse), "Unauthorized")
async def get_me(_request: Request, user: User) -> JSONResponse:
    return json(UserPublic.model_validate(user).model_dump(mode="json"))


@bp.get("/me/accounts")
@openapi.summary("Current user accounts")
@openapi.description("Return accounts and balances of the authenticated user.")
@openapi.secured("BearerAuth")
@openapi.response(
    200,
    json_content(
        list[AccountOut],
        example=[{"id": 1, "balance": "0.00"}],
    ),
    "OK",
)
@openapi.response(401, json_content(MessageResponse), "Unauthorized")
async def get_my_accounts(
    _request: Request,
    user: User,
    session: AsyncSession,
) -> JSONResponse:
    loaded = await session.scalar(
        select(User)
        .where(User.id == user.id)
        .options(selectinload(User.accounts))
    )
    assert loaded is not None
    return json(
        [
            AccountOut.model_validate(account).model_dump(mode="json")
            for account in loaded.accounts
        ]
    )


@bp.get("/me/payments")
@openapi.summary("Current user payments")
@openapi.description("Return payments of the authenticated user.")
@openapi.secured("BearerAuth")
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
@openapi.response(401, json_content(MessageResponse), "Unauthorized")
async def get_my_payments(
    _request: Request,
    user: User,
    session: AsyncSession,
) -> JSONResponse:
    result = await session.scalars(
        select(Payment).where(Payment.user_id == user.id).order_by(Payment.id)
    )
    return json(
        [
            PaymentOut.model_validate(payment).model_dump(mode="json")
            for payment in result.all()
        ]
    )
