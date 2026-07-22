from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    loc: list[str | int] = Field(default_factory=list)
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: list[ErrorDetail]


class MessageResponse(BaseModel):
    detail: str
