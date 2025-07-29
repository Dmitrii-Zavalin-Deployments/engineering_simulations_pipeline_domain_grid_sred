# 📄 src/rules/utils/coercion.py

"""
Type coercion helpers tailored for rule evaluation.

Used to convert raw values during expression parsing and logical comparisons.
Ensures safety and consistency for numeric and boolean operations under strict or relaxed modes.

Available Methods:
- coerce_numeric(value)
- coerce_boolean(value)
- coerce_string(value)
"""

from typing import Any, Union


def coerce_numeric(value: Any) -> Union[int, float, str]:
    """
    Attempt to coerce a value into int or float. Falls back to string on failure.
    Used when comparing numeric payload fields with mixed representations.
    """
    if isinstance(value, (int, float)):
        return value
    try:
        str_value = str(value).strip()
        if '.' in str_value:
            return float(str_value)
        return int(str_value)
    except (ValueError, TypeError):
        return str(value)


def coerce_boolean(value: Any) -> Union[bool, str]:
    """
    Normalize common truthy and falsy string representations.
    e.g. "true", "1", "false", "0" → True/False
    Falls back to string if unrecognized.
    """
    if isinstance(value, bool):
        return value
    try:
        str_value = str(value).strip().lower()
        if str_value in ("true", "1"):
            return True
        elif str_value in ("false", "0"):
            return False
        return str_value
    except Exception:
        return str(value)


def coerce_string(value: Any) -> str:
    """
    Coerces value to a trimmed string representation.
    """
    try:
        return value.strip() if isinstance(value, str) else str(value)
    except Exception:
        return ""



