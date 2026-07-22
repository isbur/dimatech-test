from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from dimatech.config import settings

ALGORITHM = "HS256"


def create_access_token(*, user_id: int, role: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
