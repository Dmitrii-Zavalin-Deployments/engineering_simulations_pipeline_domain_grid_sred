# src/utils/validation_helpers.py

"""
Validation helper routines for input consistency and rule safety.

Includes reusable logic to pre-check values before coercion, casting, or expression evaluation.
Use these to avoid runtime errors and enforce reliable type handling across the system.
"""

# NOTE:
# The function `is_valid_numeric_string()` was deprecated in favor of `_is_numeric_str`
# in `src.rules.type_compatibility_utils`. Please update references accordingly.
# If still required elsewhere (e.g., external validation flows), move it to a local utility file.

# def is_valid_numeric_string(s: Any) -> bool:
#     """
#     Deprecated. Use _is_numeric_str in type_compatibility_utils instead.
#     """
#     try:
#         if isinstance(s, (list, dict, set, tuple)):
#             return False
#         float(s)
#         return True
#     except (ValueError, TypeError):
#         return False



