# src/rules/rule_engine.py

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

def _coerce_types_for_comparison(left, right):
    """
    Attempts to coerce left/right values to compatible types for comparison in relaxed mode.
    """
    try:
        if isinstance(left, bool) or isinstance(right, bool):
            return bool(left), bool(right)
        if isinstance(left, (int, float)) and isinstance(right, str):
            right_coerced = type(left)(right)
            return left, right_coerced
        if isinstance(right, (int, float)) and isinstance(left, str):
            left_coerced = type(right)(left)
            return left_coerced, right
        if isinstance(left, str) and isinstance(right, str):
            for num_type in (int, float):
                try:
                    left_num = num_type(left)
                    right_num = num_type(right)
                    return left_num, right_num
                except:
                    continue
        return left, right
    except Exception as e:
        raise RuleEvaluationError(f"Type coercion failed in relaxed mode: {e}")

def _evaluate_expression(expression: str, payload: dict, *, strict_type_check: bool = False, relaxed_type_check: bool = False) -> bool:
    """
    Evaluates an expression like "a.b == 5" against the payload using parsed literals and operator resolution.
    """
    parts = expression.strip().split(" ", 2)
    if len(parts) != 3:
        raise RuleEvaluationError(f"Unsupported expression format: '{expression}'")

    lhs_path, operator_str, rhs_literal = parts

    if operator_str not in SUPPORTED_OPERATORS:
        raise RuleEvaluationError(f"Unsupported operator: '{operator_str}'")

    if not "." in lhs_path and lhs_path.strip().lower() in ["true", "false", "null"] or lhs_path.isnumeric():
        lhs_value = parse_literal(lhs_path)
    else:
        try:
            lhs_value = get_nested_value(payload, lhs_path)
        except RuleEvaluationError as e:
            if relaxed_type_check:
                lhs_value = None
                logger.debug(f"Relaxed mode fallback for missing key '{lhs_path}': {e}")
            else:
                raise

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
            lhs_value, rhs_value = _coerce_types_for_comparison(lhs_value, rhs_value)
        else:
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
    """
    expression = rule.get("if")
    if not expression or not isinstance(expression, str):
        return True

    if not (strict_type_check or relaxed_type_check):
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



