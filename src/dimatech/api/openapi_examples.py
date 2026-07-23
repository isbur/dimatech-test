"""Concrete OpenAPI response examples matching real API payloads."""

from __future__ import annotations

from typing import Any

# --- success payloads ---

TOKEN_RESPONSE: dict[str, Any] = {
    "access_token": (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxIiwicm9sZSI6InVzZXIifQ."
        "example-signature"
    ),
    "token_type": "bearer",
}

USER_PUBLIC: dict[str, Any] = {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Test User",
}

USER_CREATED: dict[str, Any] = {
    "id": 3,
    "email": "new.user@example.com",
    "full_name": "New User",
}

USER_UPDATED: dict[str, Any] = {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Updated Name",
}

USERS_WITH_ACCOUNTS: list[dict[str, Any]] = [
    {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Test User",
        "accounts": [{"id": 1, "balance": "0.00"}],
    },
    {
        "id": 2,
        "email": "admin@example.com",
        "full_name": "Test Admin",
        "accounts": [],
    },
]

ACCOUNT_LIST: list[dict[str, Any]] = [{"id": 1, "balance": "0.00"}]

PAYMENT: dict[str, Any] = {
    "id": 1,
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "account_id": 1,
    "user_id": 1,
    "amount": "100.00",
}

PAYMENT_LIST: list[dict[str, Any]] = [PAYMENT]

HEALTH: dict[str, Any] = {"status": "ok"}

USER_DELETED: dict[str, Any] = {"detail": "User deleted"}

# --- error payloads (real handler / service messages) ---

UNAUTHORIZED_CREDENTIALS: dict[str, Any] = {
    "detail": "Invalid email or password",
}
UNAUTHORIZED_MISSING_AUTH: dict[str, Any] = {
    "detail": "Missing or invalid Authorization header",
}
FORBIDDEN_ADMIN: dict[str, Any] = {"detail": "Admin access required"}
FORBIDDEN_SELF_DELETE: dict[str, Any] = {
    "detail": "Cannot delete your own account",
}
FORBIDDEN_ACCOUNT_OWNER: dict[str, Any] = {
    "detail": "Account does not belong to user",
}
NOT_FOUND_USER: dict[str, Any] = {"detail": "User not found"}
CONFLICT_EMAIL: dict[str, Any] = {"detail": "Email already registered"}
CONFLICT_TRANSACTION: dict[str, Any] = {
    "detail": "Transaction already processed with different payload",
}
INVALID_SIGNATURE: dict[str, Any] = {"detail": "Invalid signature"}

VALIDATION_INVALID_EMAIL: dict[str, Any] = {
    "detail": [
        {
            "loc": ["email"],
            "msg": (
                "value is not a valid email address: "
                "An email address must have an @-sign."
            ),
            "type": "value_error",
        }
    ]
}

VALIDATION_SHORT_PASSWORD: dict[str, Any] = {
    "detail": [
        {
            "loc": ["password"],
            "msg": "password must be at least 8 characters long",
            "type": "value_error",
        }
    ]
}

VALIDATION_NON_POSITIVE_AMOUNT: dict[str, Any] = {
    "detail": [
        {
            "loc": ["amount"],
            "msg": "Input should be greater than 0",
            "type": "greater_than",
        }
    ]
}
