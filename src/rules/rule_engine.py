# 📄 src/rules/rule_engine.py

from src.validation.expression_utils import parse_literal
from src.rules.operators import resolve_operator, OperatorError

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

def _evaluate_expression(expression: str, payload: dict, *, strict_type_check: bool = False) -> bool:
    """
    Evaluates an expression like "a.b == 5" against the payload using parsed literals and operator resolution.

    Supports:
      - Comparison operators: ==, !=, >, <, >=, <=, in, not in, matches
      - Literal parsing and type coercion
      - Strict type enforcement toggle

    Raises:
        ValueError, KeyError, OperatorError
    """
    parts = expression.strip().split(" ", 2)
    if len(parts) != 3:
        raise ValueError(f"Unsupported expression format: '{expression}'")

    lhs_path, operator_str, rhs_literal = parts

    lhs_value = _get_nested_value(payload, lhs_path)
    rhs_value = parse_literal(rhs_literal)

    if strict_type_check and type(lhs_value) != type(rhs_value):
        raise ValueError(f"Incompatible types: {type(lhs_value)} vs {type(rhs_value)}")

    try:
        compare_fn = resolve_operator(operator_str)
        return compare_fn(lhs_value, rhs_value)
    except OperatorError as err:
        raise ValueError(str(err))

def evaluate_rule(rule: dict, payload: dict, *, strict_type_check: bool = False) -> bool:
    """
    Evaluates a validation rule expression against a payload.

    Parameters:
        rule (dict): Rule definition containing 'if' and optionally 'strict_type_check'
        payload (dict): Input data structure for rule evaluation
        strict_type_check (bool): If True, enforces exact type alignment in comparisons

    Returns:
        bool: True if the rule passes, False if it fails

    Raises:
        RuleEvaluationError: If the rule expression is malformed or cannot be resolved
    """
    expression = rule.get("if")
    if not expression or not isinstance(expression, str):
        return True  # Consider blank or malformed rules safe to ignore

    strict_override = rule.get("strict_type_check")
    if isinstance(strict_override, bool):
        strict_type_check = strict_override

    try:
        return _evaluate_expression(expression, payload, strict_type_check=strict_type_check)
    except KeyError as e:
        raise RuleEvaluationError(f"Missing key in expression: {e}")
    except (ValueError, OperatorError) as e:
        raise RuleEvaluationError(f"Expression evaluation error: {e}")
    except Exception as e:
        raise RuleEvaluationError(f"Unexpected evaluation failure: {e}")



