# src/rules/utils/coercion.py

"""
Type coercion helpers tailored for rule evaluation.

Used to convert raw values during expression parsing and logical comparisons.
Ensures safety and consistency for numeric and boolean operations under strict or relaxed modes.

Available Methods:
- coerce_numeric(value)
- coerce_boolean(value)
- coerce_string(value)
- safe_float(value)
- relaxed_cast(value, target_type)  # ✅ Strategic Addition
"""

from typing import Any, Union, Optional
from src.rules.config import debug_log


def coerce_numeric(value: Any) -> Optional[float]:
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
    try:
        result = value.strip() if isinstance(value, str) else str(value)
        debug_log(f"[string] Coerced '{value}' → '{result}'")
        return result
    except Exception as e:
        debug_log(f"[string] Failed to coerce '{value}' → fallback: '' | {e}")
        return ""


def safe_float(value: Any) -> Optional[float]:
    try:
        result = float(value)
        debug_log(f"[safe_float] Parsed '{value}' → {result}")
        return result
    except Exception as e:
        debug_log(f"[safe_float] Failed to parse '{value}' → None | {e}")
        return None


def relaxed_cast(value: Any, target_type: type) -> Optional[Any]:
    """
    Defensive relaxed-mode type casting.
    Handles common encodings like "true", "123", etc. without raising.
    Returns None for unsafe or unrecognized cases.
    """
    try:
        if isinstance(value, target_type):
            debug_log(f"[relaxed_cast] Native {target_type.__name__} detected → {value}")
            return value

        if isinstance(value, str):
            stripped = value.strip().lower()
            if target_type == bool:
                if stripped in ("true", "1"):
                    debug_log(f"[relaxed_cast] Interpreted '{value}' → True")
                    return True
                elif stripped in ("false", "0"):
                    debug_log(f"[relaxed_cast] Interpreted '{value}' → False")
                    return False
            elif target_type == int and stripped.isdigit():
                result = int(stripped)
                debug_log(f"[relaxed_cast] Parsed '{value}' → {result}")
                return result
            elif target_type == float:
                try:
                    result = float(stripped)
                    debug_log(f"[relaxed_cast] Parsed '{value}' → {result}")
                    return result
                except ValueError:
                    pass

        # Fallback for generic casting attempt
        result = target_type(value)
        debug_log(f"[relaxed_cast] Fallback cast '{value}' → {result}")
        return result
    except Exception as e:
        debug_log(f"[relaxed_cast] Failed to cast '{value}' to {target_type.__name__} → None | {e}")
        return None



