"""
Shared utilities for the MCP server, modeled after the Binance MCP server pattern.
Provides standardized response builders, input validators, and rate limiting.
"""
import json
import time
import logging
from typing import Any, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)


# ── Standardized response builders ────────────────────────────────

def create_success_response(
    data: Any,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized success response.

    Returns:
        {"success": True, "data": ..., "timestamp": ..., "metadata": ...}
    """
    response: Dict[str, Any] = {
        "success": True,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    if metadata:
        response["metadata"] = metadata
    return response


def create_error_response(
    error_type: str,
    message: str,
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Returns:
        {"success": False, "error": {"type": ..., "message": ..., "timestamp": ...}}
    """
    return {
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "timestamp": int(time.time() * 1000),
        },
    }


# ── Input validators ──────────────────────────────────────────────

def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize a cryptocurrency symbol.

    Accepts formats like BTC, ETH, BTC/USDT and normalizes them.
    Raises ValueError on invalid input.
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string")

    symbol = symbol.upper().strip()

    if len(symbol) < 2:
        raise ValueError("Symbol must be at least 2 characters long")
    if len(symbol) > 20:
        raise ValueError("Symbol must be less than 20 characters long")

    # Allow alphanumeric and / for pairs like BTC/USDT
    sanitized = "".join(c for c in symbol if c.isalnum() or c == "/")
    if not sanitized or sanitized.startswith("/") or sanitized.endswith("/"):
        raise ValueError(f"Invalid symbol format: {symbol}")

    return sanitized


def validate_positive_number(
    value: float,
    field_name: str,
    min_value: float = 0.0,
) -> float:
    """Validate that a numeric value is positive."""
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number")
    if value <= min_value:
        raise ValueError(f"{field_name} must be greater than {min_value}")
    if value > 1e15:
        raise ValueError(f"{field_name} value is unreasonably large")
    return float(value)


# ── Rate limiter ──────────────────────────────────────────────────

class RateLimiter:
    """
    Sliding-window rate limiter for API calls.
    Default: 1200 requests per 60-second window (matches Binance limits).
    """

    def __init__(self, max_calls: int = 1200, window: int = 60):
        self.max_calls = max_calls
        self.window = window
        self.calls: list[float] = []

    def can_proceed(self) -> bool:
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.window]
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False


def rate_limited(limiter: Optional[RateLimiter] = None):
    """Decorator that applies rate limiting to a function."""
    if limiter is None:
        limiter = RateLimiter()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not limiter.can_proceed():
                return create_error_response(
                    "rate_limit_exceeded",
                    "API rate limit exceeded. Please try again later.",
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global rate limiter for exchange API calls
exchange_rate_limiter = RateLimiter(max_calls=1200, window=60)


# ── Display formatting ────────────────────────────────────────────

def format_for_display(result: Dict[str, Any]) -> str:
    """
    Convert a structured handler response to a display string
    suitable for LLM consumption and UI display.
    """
    if not result.get("success"):
        err = result.get("error", {})
        return f"Error ({err.get('type', 'unknown')}): {err.get('message', 'Unknown error')}"

    data = result.get("data", {})
    if isinstance(data, str):
        return data
    return json.dumps(data, indent=2, default=str)
