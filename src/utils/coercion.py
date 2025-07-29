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
from src.rules.config import debug_log  # ✅ Strategic Addition


def coerce_numeric(value: Any) -> Union[int, float, str]:
    """
    Attempt to coerce a value into int or float. Falls back to string on failure.
    Used when comparing numeric payload fields with mixed representations.
    """
    if isinstance(value, (int, float)):
        debug_log(f"[numeric] Native numeric detected → {value}")
        return value
    try:
        str_value = str(value).strip()
        if '.' in str_value:
            result = float(str_value)
        else:
            result = int(str_value)
        debug_log(f"[numeric] Coerced '{value}' → {result}")
        return result
    except (ValueError, TypeError) as e:
        fallback = str(value)
        debug_log(f"[numeric] Coercion failed for '{value}' ({type(value).__name__}) → fallback: '{fallback}' | {e}")
        return fallback


def coerce_boolean(value: Any) -> Union[bool, str]:
    """
    Normalize common truthy and falsy string representations.
    e.g. "true", "1", "false", "0" → True/False
    Falls back to string if unrecognized.
    """
    if isinstance(value, bool):
        debug_log(f"[boolean] Native bool detected → {value}")
        return value
    try:
        str_value = str(value).strip().lower()
        if str_value in ("true", "1"):
            debug_log(f"[boolean] Interpreted '{value}' → True")
            return True
        elif str_value in ("false", "0"):
            debug_log(f"[boolean] Interpreted '{value}' → False")
            return False
        debug_log(f"[boolean] Unrecognized form '{value}' → fallback: '{str_value}'")
        return str_value
    except Exception as e:
        fallback = str(value)
        debug_log(f"[boolean] Coercion error for '{value}' ({type(value).__name__}) → fallback: '{fallback}' | {e}")
        return fallback


def coerce_string(value: Any) -> str:
    """
    Coerces value to a trimmed string representation.
    """
    try:
        result = value.strip() if isinstance(value, str) else str(value)
        debug_log(f"[string] Coerced '{value}' → '{result}'")
        return result
    except Exception as e:
        debug_log(f"[string] Failed to coerce '{value}' → fallback: '' | {e}")
        return ""



