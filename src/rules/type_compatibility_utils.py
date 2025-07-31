# src/rules/type_compatibility_utils.py

from typing import Any
import math

# Supported comparison modes
STRICT_MODE = "strict"
RELAXED_MODE = "relaxed"


def are_types_comparable(lhs: Any, rhs: Any, mode: str) -> bool:
    """
    Determines whether two values are semantically comparable
    under the given type check mode.

    Modes:
        - 'strict': types must match exactly.
        - 'relaxed': allows coercible comparisons like str ↔ int/float/bool.

    Args:
        lhs: Left-hand-side value.
        rhs: Right-hand-side value.
        mode: Type check mode.

    Returns:
        bool: True if values are comparable under mode rules, False otherwise.
    """

    if lhs is None or rhs is None:
        return False

    if mode == STRICT_MODE:
        return type(lhs) == type(rhs)

    if mode == RELAXED_MODE:
        return _relaxed_type_match(lhs, rhs)

    # Unknown mode → reject by default
    return False


def _relaxed_type_match(lhs: Any, rhs: Any) -> bool:
    """
    Implements relaxed coercion rules:
    - str ↔ int/float if string is numeric
    - str ↔ bool if string is boolean-like
    - float ↔ int always allowed
    """

    lhs_type = type(lhs)
    rhs_type = type(rhs)

    # Numeric string ↔ numeric types
    if isinstance(lhs, str) and _is_numeric_str(lhs):
        if rhs_type in (int, float):
            return True
    if isinstance(rhs, str) and _is_numeric_str(rhs):
        if lhs_type in (int, float):
            return True

    # Boolean-like strings
    if isinstance(lhs, str) and _is_boolean_str(lhs):
        if isinstance(rhs, bool):
            return True
    if isinstance(rhs, str) and _is_boolean_str(rhs):
        if isinstance(lhs, bool):
            return True

    # float ↔ int always allowed
    if (lhs_type, rhs_type) in [(int, float), (float, int)]:
        return True

    # Default: fallback to type equality
    return lhs_type == rhs_type


def _is_numeric_str(s: Any) -> bool:
    if not isinstance(s, str):
        return False
    try:
        return math.isfinite(float(s))
    except (ValueError, OverflowError):
        return False


def _is_boolean_str(s: str) -> bool:
    return s.lower() in {"true", "false", "yes", "no", "0", "1"}



