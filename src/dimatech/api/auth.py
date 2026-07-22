from sanic import Blueprint, Request
from sanic.exceptions import Unauthorized
from sanic.response import JSONResponse, json
from sanic_ext import openapi, validate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dimatech.api.openapi_body import json_body, json_content
from dimatech.models.user import User
from dimatech.schemas.auth import LoginRequest, TokenResponse
from dimatech.schemas.errors import MessageResponse, ValidationErrorResponse
from dimatech.security.jwt import create_access_token
from dimatech.security.passwords import verify_password

bp = Blueprint("auth", url_prefix="/auth")


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
@openapi.response(401, json_content(MessageResponse), "Invalid credentials")
@openapi.response(422, json_content(ValidationErrorResponse), "Validation error")
@validate(json=LoginRequest)
async def login(
    _request: Request,
    body: LoginRequest,
    session: AsyncSession,
) -> JSONResponse:
    user = await session.scalar(select(User).where(User.email == body.email))
    if user is None or not verify_password(body.password, user.password_hash):
        raise Unauthorized("Invalid email or password")

    token = create_access_token(user_id=user.id, role=user.role.value)
    return json(
        TokenResponse(access_token=token).model_dump(),
        status=200,
    )
