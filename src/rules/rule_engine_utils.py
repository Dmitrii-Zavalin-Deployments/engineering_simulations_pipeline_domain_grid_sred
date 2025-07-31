# src/rules/rule_engine_utils.py

import logging
from src.rules.config import debug_log
from src.utils.coercion import relaxed_equals, relaxed_cast

logger = logging.getLogger(__name__)

STRICT_MODE = "strict"
RELAXED_MODE = "relaxed"
DEFAULT_MODE = "default"

class RuleEvaluationError(Exception):
    """Raised when a rule evaluation fails due to missing keys or invalid logic."""
    pass

def is_symbolic_reference(val: str) -> bool:
    return isinstance(val, str) and '.' in val and not val.replace('.', '', 1).isdigit()

def get_nested_value(payload: dict, path: str):
    keys = path.split(".")
    value = payload
    for k in keys:
        if not isinstance(value, dict):
            raise RuleEvaluationError(
                f"Expected dict at '{k}' in path '{path}', but got {type(value)}"
            )
        if k not in value:
            raise RuleEvaluationError(f"Missing key in expression: {path}")
        value = value[k]
        if value is None and k != keys[-1]:
            raise RuleEvaluationError(
                f"Null value encountered at '{k}' in path '{path}'"
            )
        debug_log(f"Resolved key '{k}' → {value}")
    return value

def resolve_comparable(lhs, rhs, strict_check=False, relaxed_check=False):
    mode = STRICT_MODE if strict_check else RELAXED_MODE if relaxed_check else DEFAULT_MODE
    debug_log(f"Applying comparison mode: {mode}")

    try:
        if mode == STRICT_MODE:
            return lhs == rhs
        elif mode == RELAXED_MODE:
            return relaxed_equals(lhs, rhs)
        else:
            # Attempt type normalization with fallback
            lhs_cast = relaxed_cast(lhs, type(rhs)) if rhs is not None else lhs
            rhs_cast = relaxed_cast(rhs, type(lhs)) if lhs is not None else rhs
            if lhs_cast is not None and rhs_cast is not None:
                return lhs_cast == rhs_cast
            return lhs == rhs
    except Exception as e:
        debug_log(f"Comparison failed for '{lhs}' vs '{rhs}' → False | {e}")
        return False



