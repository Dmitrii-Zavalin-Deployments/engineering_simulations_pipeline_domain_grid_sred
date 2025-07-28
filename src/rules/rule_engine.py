# 📄 src/rules/rule_engine.py

from src.validation.expression_utils import parse_literal
from src.validation.validation_profile_expressions import _evaluate_expression

class RuleEvaluationError(Exception):
    """Raised when a rule evaluation fails due to missing keys or invalid logic."""
    pass

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
        # Rule is malformed or missing; considered safe to skip
        return True

    # Use rule-level override if provided
    strict_override = rule.get("strict_type_check")
    if isinstance(strict_override, bool):
        strict_type_check = strict_override

    try:
        return _evaluate_expression(expression, payload, strict_type_check=strict_type_check)
    except KeyError as e:
        raise RuleEvaluationError(f"Missing key in expression: {e}")
    except ValueError as e:
        raise RuleEvaluationError(f"Expression evaluation error: {e}")
    except Exception as e:
        raise RuleEvaluationError(f"Unexpected evaluation failure: {e}")



