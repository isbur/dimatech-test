from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi, validate

from dimatech.api.openapi_body import json_body, json_content
from dimatech.schemas.errors import MessageResponse, ValidationErrorResponse
from dimatech.schemas.user import UserCreate, UserPublic, UserUpdate, UserWithAccounts

bp = Blueprint("admin", url_prefix="/admin")


def _not_implemented() -> JSONResponse:
    return json({"detail": "not implemented"}, status=501)


@bp.get("/users")
@openapi.summary("List users")
@openapi.description("Admin: list users with their accounts and balances.")
@openapi.response(200, json_content(list[UserWithAccounts]), "OK")
@openapi.response(501, json_content(MessageResponse), "Not implemented")
async def list_users(_request: Request) -> JSONResponse:
    return _not_implemented()


@bp.post("/users")
@openapi.summary("Create user")
@openapi.description("Admin: create a user.")
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
@openapi.response(200, json_content(UserPublic), "OK")
@openapi.response(422, json_content(ValidationErrorResponse), "Validation error")
@openapi.response(501, json_content(MessageResponse), "Not implemented")
@validate(json=UserCreate)
async def create_user(_request: Request, body: UserCreate) -> JSONResponse:
    _ = body
    return _not_implemented()


@bp.patch("/users/<user_id:int>")
@openapi.summary("Update user")
@openapi.description("Admin: update a user.")
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
@openapi.response(422, json_content(ValidationErrorResponse), "Validation error")
@openapi.response(501, json_content(MessageResponse), "Not implemented")
@validate(json=UserUpdate)
async def update_user(
    _request: Request,
    body: UserUpdate,
    user_id: int,
) -> JSONResponse:
    _ = (body, user_id)
    return _not_implemented()


@bp.delete("/users/<user_id:int>")
@openapi.summary("Delete user")
@openapi.description("Admin: delete a user.")
@openapi.response(204, description="Deleted")
@openapi.response(501, json_content(MessageResponse), "Not implemented")
async def delete_user(_request: Request, user_id: int) -> JSONResponse:
    _ = user_id
    return _not_implemented()
