from pydantic import BaseModel, ConfigDict, Field

from dimatech.schemas.types import PositiveMoney


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: str
    account_id: int
    user_id: int
    amount: PositiveMoney


class WebhookPaymentIn(BaseModel):
    """Payload from the emulated payment-system webhook."""

    transaction_id: str = Field(min_length=1)
    account_id: int
    user_id: int
    amount: PositiveMoney
    signature: str = Field(min_length=1)
