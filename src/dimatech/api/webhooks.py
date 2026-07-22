from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi, validate

from dimatech.api.openapi_body import json_body, json_content
from dimatech.schemas.errors import MessageResponse, ValidationErrorResponse
from dimatech.schemas.payment import WebhookPaymentIn

bp = Blueprint("webhooks", url_prefix="/webhooks")


def _not_implemented() -> JSONResponse:
    return json({"detail": "not implemented"}, status=501)


@bp.post("/payment")
@openapi.summary("Payment webhook")
@openapi.description("Emulated payment-system webhook for balance top-up.")
@openapi.body(
    json_body(
        WebhookPaymentIn,
        example={
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1,
            "account_id": 1,
            "amount": "100.00",
            "signature": "abc123",
        },
    ),
    required=True,
)
@openapi.response(422, json_content(ValidationErrorResponse), "Validation error")
@openapi.response(501, json_content(MessageResponse), "Not implemented")
@validate(json=WebhookPaymentIn)
async def payment_webhook(
    _request: Request,
    body: WebhookPaymentIn,
) -> JSONResponse:
    _ = body
    return _not_implemented()
