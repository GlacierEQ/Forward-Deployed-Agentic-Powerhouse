"""Shared fail-closed authentication for local APEX command bridges."""

import hmac
import os
from typing import Any


TOKEN_ENV = "APEX_RUNTIME_API_TOKEN"


def configured_token() -> str:
    return os.environ.get(TOKEN_ENV, "")


def is_authorized(headers: Any) -> bool:
    token = configured_token()
    if not token:
        return False
    supplied = headers.get("Authorization", "")
    if supplied.startswith("Bearer "):
        supplied = supplied[7:]
    return bool(supplied) and hmac.compare_digest(supplied, token)


def authorization_error() -> dict:
    return {
        "success": False,
        "error": "APEX_RUNTIME_API_TOKEN is required for command execution",
        "auth_required": True,
    }
