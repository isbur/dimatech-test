from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi, validate

from dimatech.schemas.user import UserCreate, UserPublic, UserUpdate, UserWithAccounts

bp = Blueprint("admin", url_prefix="/admin")


def _not_implemented() -> JSONResponse:
    return json({"detail": "not implemented"}, status=501)


@bp.get("/users")
@openapi.summary("List users")
@openapi.description("Admin: list users with their accounts and balances.")
@openapi.response(200, {"application/json": list[UserWithAccounts]}, "OK")
@openapi.response(501, {"application/json": dict}, "Not implemented")
async def list_users(_request: Request) -> JSONResponse:
    return _not_implemented()


@bp.post("/users")
@openapi.summary("Create user")
@openapi.description("Admin: create a user.")
@openapi.response(200, {"application/json": UserPublic}, "OK")
@openapi.response(422, {"application/json": dict}, "Validation error")
@openapi.response(501, {"application/json": dict}, "Not implemented")
@validate(json=UserCreate)
async def create_user(_request: Request, body: UserCreate) -> JSONResponse:
    _ = body
    return _not_implemented()


@bp.patch("/users/<user_id:int>")
@openapi.summary("Update user")
@openapi.description("Admin: update a user.")
@openapi.response(200, {"application/json": UserPublic}, "OK")
@openapi.response(422, {"application/json": dict}, "Validation error")
@openapi.response(501, {"application/json": dict}, "Not implemented")
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
@openapi.response(501, {"application/json": dict}, "Not implemented")
async def delete_user(_request: Request, user_id: int) -> JSONResponse:
    _ = user_id
    return _not_implemented()
