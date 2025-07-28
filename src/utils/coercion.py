# src/utils/coercion.py

"""
Safe coercion utilities for fault-tolerant data normalization.

These helpers ensure robust type conversion of legacy or malformed metadata values.
Used across sanitizers, validators, and payload normalizers.

Available Methods:
- safe_float(value, default=0.0)
- safe_int(value, default=0)
- safe_str(value, default="")
"""

from typing import Any


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value)) if isinstance(value, str) else int(value)
    except (TypeError, ValueError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    try:
        if isinstance(value, str):
            return value.strip()
        return str(value)
    except Exception:
        return default



