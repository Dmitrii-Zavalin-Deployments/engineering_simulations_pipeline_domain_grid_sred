# src/utils/validation_helpers.py

"""
Validation helper routines for input consistency and rule safety.

Includes reusable logic to pre-check values before coercion, casting, or expression evaluation.
Use these to avoid runtime errors and enforce reliable type handling across the system.
"""

from typing import Any


def is_valid_numeric_string(s: Any) -> bool:
    """
    Returns True if the input can be safely parsed as a float.

    Accepts int, float, str-representations of numeric values, or boolean primitives.
    Returns False for malformed strings, collections, or incompatible types.
    """
    try:
        # Defensive: skip types that shouldn't be coerced
        if isinstance(s, (list, dict, set, tuple)):
            return False
        float(s)
        return True
    except (ValueError, TypeError):
        return False



