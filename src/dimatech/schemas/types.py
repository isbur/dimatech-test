from typing import Annotated

from pydantic import AfterValidator


def validate_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError("password must be at least 8 characters long")
    if any(ch.isspace() for ch in value):
        raise ValueError("password must not contain whitespace")
    return value


Password = Annotated[str, AfterValidator(validate_password)]
