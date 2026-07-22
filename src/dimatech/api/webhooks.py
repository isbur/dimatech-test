from sanic import Blueprint, Request
from sanic.response import JSONResponse, json
from sanic_ext import openapi, validate

from dimatech.schemas.payment import WebhookPaymentIn

bp = Blueprint("webhooks", url_prefix="/webhooks")


def _not_implemented() -> JSONResponse:
    return json({"detail": "not implemented"}, status=501)


@bp.post("/payment")
@openapi.summary("Payment webhook")
@openapi.description("Emulated payment-system webhook for balance top-up.")
@openapi.response(422, {"application/json": dict}, "Validation error")
@openapi.response(501, {"application/json": dict}, "Not implemented")
@validate(json=WebhookPaymentIn)
async def payment_webhook(
    _request: Request,
    body: WebhookPaymentIn,
) -> JSONResponse:
    _ = body
    return _not_implemented()
