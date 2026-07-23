from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi, validate
from sqlalchemy.ext.asyncio import AsyncSession

from dimatech.api.openapi_body import json_body, json_content
from dimatech.deps import Admin
from dimatech.schemas.account import AccountCreate, AccountDetail
from dimatech.schemas.errors import MessageResponse, ValidationErrorResponse
from dimatech.schemas.user import UserCreate, UserPublic, UserUpdate, UserWithAccounts
from dimatech.services import accounts as accounts_service
from dimatech.services import users as users_service

bp = Blueprint("admin", url_prefix="/admin")


@bp.get("/users")
@openapi.summary("List users")
@openapi.description("Admin: list users with their accounts and balances.")
@openapi.secured("BearerAuth")
@openapi.response(200, json_content(list[UserWithAccounts]), "OK")
@openapi.response(401, json_content(MessageResponse), "Unauthorized")
@openapi.response(403, json_content(MessageResponse), "Forbidden")
async def list_users(
    _request: Request,
    admin: Admin,
    session: AsyncSession,
) -> JSONResponse:
    _ = admin
    users = await users_service.list_users_with_accounts(session)
    return json(
        [
            UserWithAccounts.model_validate(user).model_dump(mode="json")
            for user in users
        ]
    )


@bp.post("/users")
@openapi.summary("Create user")
@openapi.description("Admin: create a user.")
@openapi.secured("BearerAuth")
@openapi.body(
    json_body(
        UserCreate,
        example={
            "email": "new.user@example.com",
            "password": "password1",
            "full_name": "New User",
            "role": "user",
        },
    ),
    required=True,
)
@openapi.response(201, json_content(UserPublic), "Created")
@openapi.response(401, json_content(MessageResponse), "Unauthorized")
@openapi.response(403, json_content(MessageResponse), "Forbidden")
@openapi.response(409, json_content(MessageResponse), "Conflict")
@openapi.response(422, json_content(ValidationErrorResponse), "Validation error")
@validate(json=UserCreate)
async def create_user(
    _request: Request,
    body: UserCreate,
    admin: Admin,
    session: AsyncSession,
) -> JSONResponse:
    _ = admin
    user = await users_service.create_user(session, body)
    return json(
        UserPublic.model_validate(user).model_dump(mode="json"),
        status=201,
    )


@bp.patch("/users/<user_id:int>")
@openapi.summary("Update user")
@openapi.description("Admin: update a user.")
@openapi.secured("BearerAuth")
@openapi.body(
    json_body(
        UserUpdate,
        example={
            "full_name": "Updated Name",
        },
    ),
    required=True,
)
@openapi.response(200, json_content(UserPublic), "OK")
@openapi.response(401, json_content(MessageResponse), "Unauthorized")
@openapi.response(403, json_content(MessageResponse), "Forbidden")
@openapi.response(404, json_content(MessageResponse), "Not found")
@openapi.response(409, json_content(MessageResponse), "Conflict")
@openapi.response(422, json_content(ValidationErrorResponse), "Validation error")
@validate(json=UserUpdate)
async def update_user(
    _request: Request,
    body: UserUpdate,
    user_id: int,
    admin: Admin,
    session: AsyncSession,
) -> JSONResponse:
    _ = admin
    user = await users_service.update_user(session, user_id, body)
    return json(UserPublic.model_validate(user).model_dump(mode="json"))


@bp.delete("/users/<user_id:int>")
@openapi.summary("Delete user")
@openapi.description("Admin: delete a user.")
@openapi.secured("BearerAuth")
@openapi.response(200, json_content(MessageResponse), "Deleted")
@openapi.response(401, json_content(MessageResponse), "Unauthorized")
@openapi.response(403, json_content(MessageResponse), "Forbidden")
@openapi.response(404, json_content(MessageResponse), "Not found")
async def delete_user(
    _request: Request,
    user_id: int,
    admin: Admin,
    session: AsyncSession,
) -> JSONResponse:
    await users_service.delete_user(
        session,
        user_id,
        actor_user_id=admin.user.id,
    )
    return json({"detail": "User deleted"})


@bp.get("/accounts")
@openapi.summary("List accounts")
@openapi.description("Admin: list all accounts.")
@openapi.secured("BearerAuth")
@openapi.response(
    200,
    json_content(
        list[AccountDetail],
        example=[{"id": 1, "user_id": 1, "balance": "0.00"}],
    ),
    "OK",
)
@openapi.response(401, json_content(MessageResponse), "Unauthorized")
@openapi.response(403, json_content(MessageResponse), "Forbidden")
async def list_accounts(
    _request: Request,
    admin: Admin,
    session: AsyncSession,
) -> JSONResponse:
    _ = admin
    accounts = await accounts_service.list_accounts(session)
    return json(
        [
            AccountDetail.model_validate(account).model_dump(mode="json")
            for account in accounts
        ]
    )


@bp.get("/accounts/<account_id:int>")
@openapi.summary("Get account")
@openapi.description("Admin: get a single account.")
@openapi.secured("BearerAuth")
@openapi.response(
    200,
    json_content(
        AccountDetail,
        example={"id": 1, "user_id": 1, "balance": "0.00"},
    ),
    "OK",
)
@openapi.response(401, json_content(MessageResponse), "Unauthorized")
@openapi.response(403, json_content(MessageResponse), "Forbidden")
@openapi.response(404, json_content(MessageResponse), "Not found")
async def get_account(
    _request: Request,
    account_id: int,
    admin: Admin,
    session: AsyncSession,
) -> JSONResponse:
    _ = admin
    account = await accounts_service.get_account(session, account_id)
    return json(AccountDetail.model_validate(account).model_dump(mode="json"))


@bp.post("/accounts")
@openapi.summary("Create account")
@openapi.description("Admin: create an account for a user with zero balance.")
@openapi.secured("BearerAuth")
@openapi.body(
    json_body(
        AccountCreate,
        example={
            "user_id": 1,
        },
    ),
    required=True,
)
@openapi.response(
    201,
    json_content(
        AccountDetail,
        example={"id": 1, "user_id": 1, "balance": "0.00"},
    ),
    "Created",
)
@openapi.response(401, json_content(MessageResponse), "Unauthorized")
@openapi.response(403, json_content(MessageResponse), "Forbidden")
@openapi.response(404, json_content(MessageResponse), "Not found")
@openapi.response(422, json_content(ValidationErrorResponse), "Validation error")
@validate(json=AccountCreate)
async def create_account(
    _request: Request,
    body: AccountCreate,
    admin: Admin,
    session: AsyncSession,
) -> JSONResponse:
    _ = admin
    account = await accounts_service.create_account(session, body)
    return json(
        AccountDetail.model_validate(account).model_dump(mode="json"),
        status=201,
    )


@bp.delete("/accounts/<account_id:int>")
@openapi.summary("Delete account")
@openapi.description(
    "Admin: delete an account with zero balance (and its payments)."
)
@openapi.secured("BearerAuth")
@openapi.response(200, json_content(MessageResponse), "Deleted")
@openapi.response(401, json_content(MessageResponse), "Unauthorized")
@openapi.response(403, json_content(MessageResponse), "Forbidden")
@openapi.response(404, json_content(MessageResponse), "Not found")
async def delete_account(
    _request: Request,
    account_id: int,
    admin: Admin,
    session: AsyncSession,
) -> JSONResponse:
    _ = admin
    await accounts_service.delete_account(session, account_id)
    return json({"detail": "Account deleted"})
