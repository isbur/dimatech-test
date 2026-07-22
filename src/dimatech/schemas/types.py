from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, Field, WithJsonSchema

_MONEY_PATTERN = r"^-?(?:0|[1-9]\d*)(?:\.\d+)?$"
_POSITIVE_MONEY_PATTERN = r"^(?:0|[1-9]\d*)(?:\.\d+)?$"


def validate_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError("password must be at least 8 characters long")
    if any(ch.isspace() for ch in value):
        raise ValueError("password must not contain whitespace")
    return value


Password = Annotated[str, AfterValidator(validate_password)]

# Custom JSON schema so Swagger does not invent values from pydantic's
# default Decimal pattern (which produces absurd example strings).
Money = Annotated[
    Decimal,
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _MONEY_PATTERN,
            "examples": ["0.00"],
        }
    ),
]

PositiveMoney = Annotated[
    Decimal,
    Field(gt=0),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _POSITIVE_MONEY_PATTERN,
            "examples": ["100.00"],
        }
    ),
]
