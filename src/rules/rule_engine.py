# src/rules/rule_engine.py

import logging
from configs.rule_engine_defaults import get_type_check_mode
from src.validation.expression_utils import parse_literal, is_literal
from src.rules.operators import resolve_operator, OperatorError, SUPPORTED_OPERATORS
from src.rules.config import debug_log
from src.rules.rule_engine_utils import (
    RuleEvaluationError,
    is_symbolic_reference,
    get_nested_value
)

logger = logging.getLogger(__name__)

def _coerce_types_for_comparison(left, right):
    try:
        debug_log(f"Attempting type coercion: left={left} ({type(left)}), right={right} ({type(right)})")

        if is_symbolic_reference(right):
            raise RuleEvaluationError(f"Cannot coerce unresolved reference: {right}")

        if isinstance(left, bool) or isinstance(right, bool):
            coerced = bool(left), bool(right)
            debug_log(f"Coerced to boolean: {coerced}")
            return coerced
        if isinstance(left, (int, float)) and isinstance(right, str):
            right_coerced = type(left)(right)
            debug_log(f"Coerced right str to numeric: {right_coerced}")
            return left, right_coerced
        if isinstance(right, (int, float)) and isinstance(left, str):
            left_coerced = type(right)(left)
            debug_log(f"Coerced left str to numeric: {left_coerced}")
            return left_coerced, right
        if isinstance(left, str) and isinstance(right, str):
            for num_type in (int, float):
                try:
                    left_num = num_type(left)
                    right_num = num_type(right)
                    debug_log(f"Coerced both strings to {num_type}: {left_num}, {right_num}")
                    return left_num, right_num
                except Exception:
                    continue
        debug_log("Coercion fallback: using original values")
        return left, right
    except Exception as e:
        raise RuleEvaluationError(f"Type coercion failed in relaxed mode: {e}")

def _evaluate_expression(
    expression: str,
    payload: dict,
    *,
    strict_type_check: bool = False,
    relaxed_type_check: bool = False
) -> bool:
    debug_log(f"Evaluating expression: {expression}")
    parts = expression.strip().split(" ", 3)
    if len(parts) != 3:
        raise RuleEvaluationError(f"Unsupported expression format: '{expression}'")

    lhs_path, operator_str, rhs_literal = parts
    debug_log(f"Parsed expression: lhs='{lhs_path}', operator='{operator_str}', rhs='{rhs_literal}'")

    if operator_str not in SUPPORTED_OPERATORS:
        raise RuleEvaluationError(f"Unsupported operator: '{operator_str}'")

    if not payload and all(is_literal(x) for x in [lhs_path, rhs_literal]):
        lhs_val = parse_literal(lhs_path)
        rhs_val = parse_literal(rhs_literal)
        try:
            compare_fn = resolve_operator(operator_str)
            debug_log(f"Literal-only fast-path → {lhs_val} {operator_str} {rhs_val}")
            return compare_fn(lhs_val, rhs_val)
        except Exception as e:
            raise RuleEvaluationError(f"Literal comparison failed: {e}")

    if not "." in lhs_path and lhs_path.strip().lower() in ["true", "false", "null"] or lhs_path.isnumeric():
        lhs_value = parse_literal(lhs_path)
        debug_log(f"Parsed literal lhs: {lhs_value}")
    else:
        try:
            lhs_value = get_nested_value(payload, lhs_path)
        except RuleEvaluationError as e:
            if relaxed_type_check:
                lhs_value = None
                logger.debug(f"Relaxed mode fallback for missing key '{lhs_path}': {e}")
                debug_log(f"Relaxed fallback: missing key '{lhs_path}', using None")
            else:
                raise

    try:
        compare_fn = resolve_operator(operator_str)
        debug_log(f"Resolved operator '{operator_str}' → {compare_fn}")
    except OperatorError:
        raise RuleEvaluationError(f"Operator resolution failed: {operator_str}")

    rhs_resolved_from_payload = False

    try:
        rhs_value = parse_literal(rhs_literal)
        debug_log(f"Parsed rhs literal: {rhs_value}")
    except ValueError as rhs_error:
        debug_log(f"Literal parsing failed for RHS: '{rhs_literal}' → {rhs_error}")
        if relaxed_type_check:
            debug_log(f"Attempting to resolve RHS path: {rhs_literal}")
            try:
                rhs_value = get_nested_value(payload, rhs_literal)
                rhs_resolved_from_payload = True
                debug_log(f"Fallback: Resolved RHS from payload key path '{rhs_literal}' → {rhs_value}")
            except RuleEvaluationError as e:
                logger.debug(f"Relaxed RHS fallback key resolution failed: {e}")
                rhs_value = None
                debug_log(f"Fallback: Using None for RHS '{rhs_literal}' due to resolution failure")
        else:
            raise RuleEvaluationError(f"Invalid RHS literal: '{rhs_literal}'")

    # ✅ Defensive bypass: skip coercion if unresolved values present in relaxed mode
    if relaxed_type_check and (lhs_value is None or rhs_value is None):
        debug_log("Skipping coercion: unresolved key in relaxed mode")
        result = lhs_value == rhs_value
        debug_log(f"Relaxed comparison: {lhs_value} == {rhs_value} → {result}")
        return result

    try:
        if strict_type_check:
            debug_log("Strict type check enabled")
            if type(lhs_value) != type(rhs_value):
                raise RuleEvaluationError(f"Incompatible types: {type(lhs_value)} vs {type(rhs_value)}")
        elif relaxed_type_check:
            debug_log("Relaxed type check enabled")
            if not rhs_resolved_from_payload:
                lhs_value, rhs_value = _coerce_types_for_comparison(lhs_value, rhs_value)
            else:
                debug_log("RHS was resolved from payload — skipping coercion on original string")
        else:
            debug_log("Default strict check")
            if type(lhs_value) != type(rhs_value):
                raise RuleEvaluationError(f"Type mismatch (default strict): {type(lhs_value)} vs {type(rhs_value)}")
    except Exception as e:
        raise RuleEvaluationError(f"Coercion error: {e}")

    try:
        result = compare_fn(lhs_value, rhs_value)
        debug_log(f"Comparison result: {lhs_value} {operator_str} {rhs_value} → {result}")
        return result
    except Exception as e:
        raise RuleEvaluationError(f"Comparison failed: {e}")

def evaluate_rule(rule: dict, payload: dict, *, strict_type_check: bool = False, relaxed_type_check: bool = False) -> bool:
    expression = rule.get("if")
    if not expression or not isinstance(expression, str):
        debug_log("Empty or malformed rule expression; returning True")
        return True

    if not (strict_type_check or relaxed_type_check):
        try:
            type_mode = get_type_check_mode(rule.get("type_check_mode"))
            debug_log(f"Resolved type check mode: {type_mode}")
        except Exception as config_error:
            logger.warning(f"Invalid type check mode override: {config_error}")
            type_mode = "strict"
            debug_log("Fallback type check mode: strict")

        strict_type_check = type_mode == "strict"
        relaxed_type_check = type_mode == "relaxed"

    return _evaluate_expression(
        expression,
        payload,
        strict_type_check=strict_type_check,
        relaxed_type_check=relaxed_type_check
    )



