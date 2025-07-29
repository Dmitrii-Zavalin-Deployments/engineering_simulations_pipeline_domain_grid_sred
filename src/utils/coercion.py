# src/rules/utils/coercion.py

"""
Type coercion helpers tailored for rule evaluation.

Used to convert raw values during expression parsing and logical comparisons.
Ensures safety and consistency for numeric and boolean operations under strict or relaxed modes.

Available Methods:
- coerce_numeric(value)
- coerce_boolean(value)
- coerce_string(value)
- safe_float(value)  # ✅ Strategic Addition
"""

from typing import Any, Union, Optional
from src.rules.config import debug_log


def coerce_numeric(value: Any) -> Optional[float]:
    """
    Strict numeric coercion to float. Returns None on failure.
    Used in arithmetic logic to guarantee safe operation.
    """
    if isinstance(value, (int, float)):
        debug_log(f"[numeric] Native numeric detected → {value}")
        return float(value)
    try:
        result = float(str(value).strip())
        debug_log(f"[numeric] Coerced '{value}' → {result}")
        return result
    except (ValueError, TypeError) as e:
        debug_log(f"[numeric] Coercion failed for '{value}' ({type(value).__name__}) → None | {e}")
        return None


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


def safe_float(value: Any) -> Optional[float]:
    """
    Attempts to coerce value to float. Returns None on failure.
    Used for tolerant float parsing in pipeline and rule logic.
    """
    try:
        result = float(value)
        debug_log(f"[safe_float] Parsed '{value}' → {result}")
        return result
    except Exception as e:
        debug_log(f"[safe_float] Failed to parse '{value}' → None | {e}")
        return None



