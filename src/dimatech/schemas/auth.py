from pydantic import BaseModel, EmailStr

from dimatech.schemas.types import Password


class LoginRequest(BaseModel):
    email: EmailStr
    password: Password


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
