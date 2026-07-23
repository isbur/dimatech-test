from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi, validate
from sqlalchemy.ext.asyncio import AsyncSession

from dimatech.api import openapi_examples as ex
from dimatech.api.openapi_body import json_body, json_content
from dimatech.deps import Admin
from dimatech.schemas.errors import MessageResponse, ValidationErrorResponse
from dimatech.schemas.user import UserCreate, UserPublic, UserUpdate, UserWithAccounts
from dimatech.services import users as users_service

bp = Blueprint("admin", url_prefix="/admin")


@bp.get("/users")
@openapi.summary("List users")
@openapi.description("Admin: list users with their accounts and balances.")
@openapi.secured("BearerAuth")
@openapi.response(
    200,
    json_content(list[UserWithAccounts], example=ex.USERS_WITH_ACCOUNTS),
    "OK",
)
@openapi.response(
    401,
    json_content(MessageResponse, example=ex.UNAUTHORIZED_MISSING_AUTH),
    "Unauthorized",
)
@openapi.response(
    403,
    json_content(MessageResponse, example=ex.FORBIDDEN_ADMIN),
    "Forbidden",
)
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
@openapi.response(
    201,
    json_content(UserPublic, example=ex.USER_CREATED),
    "Created",
)
@openapi.response(
    401,
    json_content(MessageResponse, example=ex.UNAUTHORIZED_MISSING_AUTH),
    "Unauthorized",
)
@openapi.response(
    403,
    json_content(MessageResponse, example=ex.FORBIDDEN_ADMIN),
    "Forbidden",
)
@openapi.response(
    409,
    json_content(MessageResponse, example=ex.CONFLICT_EMAIL),
    "Conflict",
)
@openapi.response(
    422,
    json_content(ValidationErrorResponse, example=ex.VALIDATION_SHORT_PASSWORD),
    "Validation error",
)
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
@openapi.response(
    200,
    json_content(UserPublic, example=ex.USER_UPDATED),
    "OK",
)
@openapi.response(
    401,
    json_content(MessageResponse, example=ex.UNAUTHORIZED_MISSING_AUTH),
    "Unauthorized",
)
@openapi.response(
    403,
    json_content(MessageResponse, example=ex.FORBIDDEN_ADMIN),
    "Forbidden",
)
@openapi.response(
    404,
    json_content(MessageResponse, example=ex.NOT_FOUND_USER),
    "Not found",
)
@openapi.response(
    409,
    json_content(MessageResponse, example=ex.CONFLICT_EMAIL),
    "Conflict",
)
@openapi.response(
    422,
    json_content(ValidationErrorResponse, example=ex.VALIDATION_SHORT_PASSWORD),
    "Validation error",
)
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
@openapi.response(
    200,
    json_content(MessageResponse, example=ex.USER_DELETED),
    "Deleted",
)
@openapi.response(
    401,
    json_content(MessageResponse, example=ex.UNAUTHORIZED_MISSING_AUTH),
    "Unauthorized",
)
@openapi.response(
    403,
    json_content(MessageResponse, example=ex.FORBIDDEN_SELF_DELETE),
    "Forbidden",
)
@openapi.response(
    404,
    json_content(MessageResponse, example=ex.NOT_FOUND_USER),
    "Not found",
)
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
