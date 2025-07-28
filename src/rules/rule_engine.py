# src/rules/rule_engine.py

import logging
from configs.rule_engine_defaults import get_type_check_mode
from src.validation.expression_utils import parse_literal
from src.rules.operators import resolve_operator, OperatorError

logger = logging.getLogger(__name__)

class RuleEvaluationError(Exception):
    """Raised when a rule evaluation fails due to missing keys or invalid logic."""
    pass

def _get_nested_value(payload: dict, key_path: str):
    """
    Resolves a dotted key path into a nested value from the payload dictionary.

    Example:
        payload = {"a": {"b": {"c": 5}}}
        key_path = "a.b.c" → returns 5

    Raises:
        KeyError: If any key along the path is missing
    """
    keys = key_path.split(".")
    value = payload
    for k in keys:
        value = value[k]
    return value

def _evaluate_expression(expression: str, payload: dict, *, strict_type_check: bool = False, relaxed_type_check: bool = False) -> bool:
    """
    Evaluates an expression like "a.b == 5" against the payload using parsed literals and operator resolution.

    Supports:
      - Comparison operators: ==, !=, >, <, >=, <=, in, not in, matches
      - Literal parsing and type coercion
      - Strict/Relaxed type enforcement toggle

    Raises:
        ValueError, KeyError, OperatorError
    """
    parts = expression.strip().split(" ", 2)
    if len(parts) != 3:
        raise ValueError(f"Unsupported expression format: '{expression}'")

    lhs_path, operator_str, rhs_literal = parts

    try:
        compare_fn = resolve_operator(operator_str)
    except OperatorError as err:
        raise ValueError(str(err))  # Short-circuit evaluation if operator is invalid

    lhs_value = _get_nested_value(payload, lhs_path)
    rhs_value = parse_literal(rhs_literal)

    if strict_type_check:
        if type(lhs_value) != type(rhs_value):
            raise ValueError(f"Incompatible types: {type(lhs_value)} vs {type(rhs_value)}")
    elif relaxed_type_check:
        try:
            if isinstance(rhs_value, int):
                lhs_value = int(lhs_value)
            elif isinstance(rhs_value, float):
                lhs_value = float(lhs_value)
            elif isinstance(rhs_value, bool):
                if str(lhs_value).lower() in ["true", "false"]:
                    lhs_value = str(lhs_value).lower() == "true"
        except Exception as e:
            raise ValueError(f"Coercion failed: {e}")

    return compare_fn(lhs_value, rhs_value)

def evaluate_rule(rule: dict, payload: dict, *, strict_type_check: bool = False, relaxed_type_check: bool = False) -> bool:
    """
    Evaluates a validation rule expression against a payload.

    Parameters:
        rule (dict): Rule definition containing 'if' and optionally 'type_check_mode'
        payload (dict): Input data structure for rule evaluation
        strict_type_check (bool): If True, enforces exact type alignment in comparisons
        relaxed_type_check (bool): If True, attempts type coercion where safe

    Returns:
        bool: True if the rule passes, False if it fails

    Raises:
        RuleEvaluationError: If the rule expression is malformed or cannot be resolved
    """
    expression = rule.get("if")
    if not expression or not isinstance(expression, str):
        return True  # Consider blank or malformed rules safe to ignore

    try:
        type_mode = get_type_check_mode(rule.get("type_check_mode"))
    except Exception as config_error:
        logger.warning(f"Invalid type check mode override: {config_error}")
        type_mode = "strict"

    strict_type_check = type_mode == "strict"
    relaxed_type_check = type_mode == "relaxed"

    try:
        return _evaluate_expression(expression, payload,
                                    strict_type_check=strict_type_check,
                                    relaxed_type_check=relaxed_type_check)
    except KeyError as e:
        logger.warning(f"Missing key path in rule expression: {e}")
        raise RuleEvaluationError(f"Missing key in expression: {e}")
    except (ValueError, OperatorError) as e:
        logger.warning(f"Rule evaluation failed: {e}")
        raise RuleEvaluationError(f"Expression evaluation error: {e}")
    except Exception as e:
        logger.error(f"Unexpected evaluation failure: {e}")
        raise RuleEvaluationError(f"Unexpected evaluation failure: {e}")



