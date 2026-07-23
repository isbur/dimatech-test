from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from sanic import Request
from sanic.exceptions import HTTPException
from sanic_ext.exceptions import ValidationError

from dimatech.schemas.account import AccountCreate
from dimatech.schemas.auth import LoginRequest
from dimatech.schemas.payment import WebhookPaymentIn
from dimatech.schemas.user import UserCreate, UserUpdate

_BODY_MODEL_RE = re.compile(r"^Invalid request body: (\w+)\.")

_BODY_MODELS: dict[str, type[BaseModel]] = {
    "LoginRequest": LoginRequest,
    "UserCreate": UserCreate,
    "UserUpdate": UserUpdate,
    "AccountCreate": AccountCreate,
    "WebhookPaymentIn": WebhookPaymentIn,
}


class Conflict(HTTPException):
    status_code = 409
    quiet = True


def format_validation_detail(
    request: Request,
    exception: ValidationError,
) -> list[dict[str, Any]]:
    """Build a compact list of field errors from sanic-ext ValidationError."""
    model = _resolve_body_model(exception.message or "")
    body = request.json

    if model is not None and body is None:
        return [
            {
                "loc": ["body"],
                "msg": "Request body is required",
                "type": "missing",
            }
        ]

    if model is not None and isinstance(body, dict):
        try:
            model.model_validate(body)
        except PydanticValidationError as pydantic_error:
            return [
                {
                    "loc": list(error["loc"]),
                    "msg": _clean_msg(str(error["msg"])),
                    "type": error["type"],
                }
                for error in pydantic_error.errors()
            ]

    return [{"loc": [], "msg": exception.message or "Invalid request", "type": "value_error"}]

def _resolve_body_model(message: str) -> type[BaseModel] | None:
    match = _BODY_MODEL_RE.match(message)
    if match is None:
        return None
    return _BODY_MODELS.get(match.group(1))


def _clean_msg(message: str) -> str:
    prefix = "Value error, "
    if message.startswith(prefix):
        return message[len(prefix) :]
    return message
