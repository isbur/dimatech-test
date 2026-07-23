from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi, validate
from sqlalchemy.ext.asyncio import AsyncSession

from dimatech.api import openapi_examples as ex
from dimatech.api.openapi_body import json_body, json_content
from dimatech.schemas.errors import MessageResponse, ValidationErrorResponse
from dimatech.schemas.payment import PaymentOut, WebhookPaymentIn
from dimatech.services import payments as payments_service

bp = Blueprint("webhooks", url_prefix="/webhooks")


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
            "signature": (
                "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
            ),
        },
    ),
    required=True,
)
@openapi.response(
    200,
    json_content(PaymentOut, example=ex.PAYMENT),
    "Payment applied",
)
@openapi.response(
    400,
    json_content(MessageResponse, example=ex.INVALID_SIGNATURE),
    "Invalid signature",
)
@openapi.response(
    403,
    json_content(MessageResponse, example=ex.FORBIDDEN_ACCOUNT_OWNER),
    "Account/user mismatch",
)
@openapi.response(
    404,
    json_content(MessageResponse, example=ex.NOT_FOUND_USER),
    "User not found",
)
@openapi.response(
    409,
    json_content(MessageResponse, example=ex.CONFLICT_TRANSACTION),
    "Conflicting transaction",
)
@openapi.response(
    422,
    json_content(
        ValidationErrorResponse,
        example=ex.VALIDATION_NON_POSITIVE_AMOUNT,
    ),
    "Validation error",
)
@validate(json=WebhookPaymentIn)
async def payment_webhook(
    _request: Request,
    body: WebhookPaymentIn,
    session: AsyncSession,
) -> JSONResponse:
    payment = await payments_service.process_webhook_payment(session, body)
    return json(PaymentOut.model_validate(payment).model_dump(mode="json"))
