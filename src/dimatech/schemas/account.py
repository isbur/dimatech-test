from pydantic import BaseModel, ConfigDict

from dimatech.schemas.types import Money


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    balance: Money
