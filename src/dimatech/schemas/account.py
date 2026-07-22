from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    balance: Decimal
