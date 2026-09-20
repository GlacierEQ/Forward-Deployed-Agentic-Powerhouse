#!/usr/bin/env python3
"""Shared security runtime for the APEX estate — single source of truth for TLS, secrets, retries, auth, and atomic I/O."""

import os
import ssl
import time
import json
import hashlib
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, TypeVar
from functools import wraps

T = TypeVar('T')


def secure_tls_context() -> ssl.SSLContext:
    """Return a TLS context with full verification enabled. Never disable verification."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx


def require_env(name: str) -> str:
    """Fail closed if required environment variable is not set."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable is not set: {name}")
    return value


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get secret from environment. No hardcoded fallbacks anywhere."""
    return os.environ.get(name, default)


class RetryPolicy:
    """Bounded exponential backoff with jitter for idempotent operations."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 8.0,
        jitter: float = 0.1,
        retryable_statuses: Optional[List[int]] = None,
        retryable_exceptions: Optional[List[type]] = None,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.retryable_statuses = retryable_statuses or [429, 500, 502, 503, 504]
        self.retryable_exceptions = retryable_exceptions or [
            urllib.error.URLError,
            TimeoutError,
            ConnectionError,
            OSError,
        ]

    def should_retry(self, attempt: int, exc: Optional[Exception] = None, status: Optional[int] = None) -> bool:
        if attempt >= self.max_attempts:
            return False
        if status and status in self.retryable_statuses:
            return True
        if exc and any(isinstance(exc, t) for t in self.retryable_exceptions):
            return True
        return False

    def delay(self, attempt: int) -> float:
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        jitter_range = delay * self.jitter
        return delay + (hash(str(attempt)) % 1000) / 1000 * jitter_range * 2 - jitter_range


def with_retry(policy: RetryPolicy):
    """Decorator that applies the retry policy to a function."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exc = None
            for attempt in range(policy.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if not policy.should_retry(attempt, exc=exc):
                        raise
                    time.sleep(policy.delay(attempt))
            raise last_exc
        return wrapper
    return decorator


def verify_bearer_token(headers: Dict[str, str]) -> bool:
    """Verify Authorization: Bearer <token> against APEX_RUNTIME_API_TOKEN."""
    token = os.environ.get("APEX_RUNTIME_API_TOKEN")
    if not token:
        return False
    supplied = headers.get("Authorization", "")
    if supplied.startswith("Bearer "):
        supplied = supplied[7:]
    import hmac
    return bool(supplied) and hmac.compare_digest(supplied, token)


def auth_required(handler_method: Callable) -> Callable:
    """Decorator for HTTP handlers that require bearer auth."""
    @wraps(handler_method)
    def wrapper(self, *args, **kwargs):
        if not verify_bearer_token(dict(self.headers)):
            self._send_json({
                "success": False,
                "error": "APEX_RUNTIME_API_TOKEN is required",
                "auth_required": True,
            }, status=401)
            return
        return handler_method(self, *args, **kwargs)
    return wrapper


def atomic_write(path: Path, data: Any, mode: int = 0o600, serialize: Callable = json.dumps) -> None:
    """Atomic write with fsync: temp file → fsync → rename → dir fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    content = serialize(data) + "\n"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    os.chmod(path, mode)
    # fsync parent directory for durability
    try:
        dir_fd = os.open(str(path.parent), os.O_DIRECTORY)
        os.fsync(dir_fd)
        os.close(dir_fd)
    except OSError:
        pass


def atomic_read(path: Path, deserialize: Callable = json.loads, default: Any = None) -> Any:
    """Atomic read with fallback to default."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return deserialize(f.read())
    except (OSError, ValueError, TypeError):
        return default


def sha256_digest(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


# Shared retry policies
DEFAULT_RETRY = RetryPolicy()
IDEMPOTENT_RETRY = RetryPolicy(max_attempts=3, base_delay=0.5)
AUTH_RETRY = RetryPolicy(max_attempts=2, base_delay=1.0, retryable_statuses=[429, 503])


__all__ = [
    "secure_tls_context",
    "require_env",
    "get_secret",
    "RetryPolicy",
    "with_retry",
    "verify_bearer_token",
    "auth_required",
    "atomic_write",
    "atomic_read",
    "sha256_digest",
    "DEFAULT_RETRY",
    "IDEMPOTENT_RETRY",
    "AUTH_RETRY",
]