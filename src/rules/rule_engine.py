# 📄 src/rules/rule_engine.py

import logging
from configs.rule_engine_defaults import get_type_check_mode
from src.validation.expression_utils import parse_literal
from src.rules.operators import resolve_operator, OperatorError, SUPPORTED_OPERATORS

logger = logging.getLogger(__name__)

class RuleEvaluationError(Exception):
    """Raised when a rule evaluation fails due to missing keys or invalid logic."""
    pass

def get_nested_value(payload: dict, path: str):
    """
    Safely resolves a dotted key path into a nested value from the payload dictionary.

    Example:
        payload = {"a": {"b": {"c": 5}}}
        path = "a.b.c" → returns 5

    Raises:
        RuleEvaluationError: If path is missing or value is None
    """
    keys = path.split(".")
    value = payload
    for k in keys:
        if not isinstance(value, dict):
            raise RuleEvaluationError(f"Expected dict at '{k}' in path '{path}', but got {type(value)}")
        if k not in value:
            raise RuleEvaluationError(f"Missing key in expression: {path}")
        value = value[k]
        if value is None:
            raise RuleEvaluationError(f"Null value encountered at '{k}' in path '{path}'")
    return value

def _evaluate_expression(expression: str, payload: dict, *, strict_type_check: bool = False, relaxed_type_check: bool = False) -> bool:
    """
    Evaluates an expression like "a.b == 5" against the payload using parsed literals and operator resolution.

    Supports:
      - Comparison operators: ==, !=, >, <, >=, <=, in, not in, matches
      - Literal parsing and type coercion
      - Strict/Relaxed type enforcement toggle

    Raises:
        RuleEvaluationError: On malformed expression, operator errors, missing keys, or coercion failure
    """
    parts = expression.strip().split(" ", 2)
    if len(parts) != 3:
        raise RuleEvaluationError(f"Unsupported expression format: '{expression}'")

    lhs_path, operator_str, rhs_literal = parts

    if operator_str not in SUPPORTED_OPERATORS:
        raise RuleEvaluationError(f"Unsupported operator: '{operator_str}'")

    # 🔓 Relaxed literal guard: allow literal-only comparisons
    if not "." in lhs_path and lhs_path.strip().lower() in ["true", "false", "null"] or lhs_path.isnumeric():
        lhs_value = parse_literal(lhs_path)
    else:
        lhs_value = get_nested_value(payload, lhs_path)

    try:
        compare_fn = resolve_operator(operator_str)
    except OperatorError:
        raise RuleEvaluationError(f"Operator resolution failed: {operator_str}")

    rhs_value = parse_literal(rhs_literal)

    try:
        if strict_type_check:
            if type(lhs_value) != type(rhs_value):
                raise RuleEvaluationError(f"Incompatible types: {type(lhs_value)} vs {type(rhs_value)}")
        elif relaxed_type_check:
            if isinstance(rhs_value, bool):
                if str(lhs_value).lower() in ["true", "false"]:
                    lhs_value = str(lhs_value).lower() == "true"
                else:
                    raise RuleEvaluationError(f"Cannot coerce non-boolean string: {lhs_value}")
            elif isinstance(rhs_value, (int, float)):
                try:
                    lhs_value = type(rhs_value)(lhs_value)
                except Exception as e:
                    raise RuleEvaluationError(f"Numeric coercion failed: {e}")
        else:
            # default strict behavior if no mode specified
            if type(lhs_value) != type(rhs_value):
                raise RuleEvaluationError(f"Type mismatch (default strict): {type(lhs_value)} vs {type(rhs_value)}")
    except Exception as e:
        raise RuleEvaluationError(f"Coercion error: {e}")

    try:
        return compare_fn(lhs_value, rhs_value)
    except Exception as e:
        raise RuleEvaluationError(f"Comparison failed: {e}")

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
        RuleEvaluationError: If rule evaluation fails due to invalid configuration or logic
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

    return _evaluate_expression(
        expression,
        payload,
        strict_type_check=strict_type_check,
        relaxed_type_check=relaxed_type_check
    )



