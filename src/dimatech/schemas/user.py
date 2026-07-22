from pydantic import BaseModel, ConfigDict, EmailStr, Field

from dimatech.models.user import UserRole
from dimatech.schemas.account import AccountOut
from dimatech.schemas.types import Password


class UserPublic(BaseModel):
    """Response for 'get me' and public user views"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str


class UserCreate(BaseModel):
    """Admin: create user."""

    email: EmailStr
    password: Password
    full_name: str = Field(min_length=1)
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    """Admin: partial update of a user."""

    email: EmailStr | None = None
    password: Password | None = None
    full_name: str | None = Field(default=None, min_length=1)
    role: UserRole | None = None


class UserWithAccounts(UserPublic):
    """Admin: user plus their accounts and balances."""

    accounts: list[AccountOut] = []
