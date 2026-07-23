from pydantic import BaseModel, ConfigDict, Field

from dimatech.schemas.types import Money


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    balance: Money


class AccountDetail(AccountOut):
    """Admin view of an account, including owner."""

    user_id: int


class AccountCreate(BaseModel):
    user_id: int = Field(gt=0)
