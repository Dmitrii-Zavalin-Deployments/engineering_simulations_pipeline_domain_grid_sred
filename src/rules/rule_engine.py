# src/rules/rule_engine.py

import logging
from configs.rule_engine_defaults import get_type_check_mode
from src.validation.expression_utils import parse_literal
from src.rules.operators import resolve_operator, OperatorError, SUPPORTED_OPERATORS
from src.rules.config import debug_log

logger = logging.getLogger(__name__)

class RuleEvaluationError(Exception):
    """Raised when a rule evaluation fails due to missing keys or invalid logic."""
    pass

def get_nested_value(payload: dict, path: str):
    """
    Retrieves a nested value from a dictionary payload using a dot-separated path.
    Raises RuleEvaluationError if the path is invalid, a key is missing, or a null value is encountered.
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
        debug_log(f"Resolved key '{k}' → {value}")
    return value

def _coerce_types_for_comparison(left, right):
    """
    Coerces types for comparison in relaxed mode. Attempts to convert strings to numbers
    if one of the operands is numeric. Handles boolean coercion.
    """
    try:
        debug_log(f"Attempting type coercion: left={left} ({type(left)}), right={right} ({type(right)})")
        if isinstance(left, bool) or isinstance(right, bool):
            coerced = bool(left), bool(right)
            debug_log(f"Coerced to boolean: {coerced}")
            return coerced
        if isinstance(left, (int, float)) and isinstance(right, str):
            # Attempt to coerce string 'right' to the type of 'left'
            right_coerced = type(left)(right)
            debug_log(f"Coerced right str to numeric: {right_coerced}")
            return left, right_coerced
        if isinstance(right, (int, float)) and isinstance(left, str):
            # Attempt to coerce string 'left' to the type of 'right'
            left_coerced = type(right)(left)
            debug_log(f"Coerced left str to numeric: {left_coerced}")
            return left_coerced, right
        if isinstance(left, str) and isinstance(right, str):
            # If both are strings, try to coerce both to int, then float
            for num_type in (int, float):
                try:
                    left_num = num_type(left)
                    right_num = num_type(right)
                    debug_log(f"Coerced both strings to {num_type}: {left_num}, {right_num}")
                    return left_num, right_num
                except Exception:
                    # If coercion to current num_type fails, try next or fall through
                    continue
        debug_log("Coercion fallback: using original values")
        return left, right
    except Exception as e:
        # Catch any coercion errors and re-raise as RuleEvaluationError
        raise RuleEvaluationError(f"Type coercion failed in relaxed mode: {e}")

def _evaluate_expression(expression: str, payload: dict, *, strict_type_check: bool = False, relaxed_type_check: bool = False) -> bool:
    """
    Evaluates a single expression string against a given payload.
    Supports basic comparisons (e.g., 'path.to.value == literal').
    Handles strict and relaxed type checking modes.
    """
    debug_log(f"Evaluating expression: {expression}")
    parts = expression.strip().split(" ", 2)
    if len(parts) != 3:
        raise RuleEvaluationError(f"Unsupported expression format: '{expression}'")

    lhs_path, operator_str, rhs_literal = parts
    debug_log(f"Parsed expression: lhs='{lhs_path}', operator='{operator_str}', rhs='{rhs_literal}'")

    if operator_str not in SUPPORTED_OPERATORS:
        raise RuleEvaluationError(f"Unsupported operator: '{operator_str}'")

    # --- Determine LHS Value ---
    # Prioritize parsing as a literal, then fallback to payload path resolution
    lhs_value = None # Initialize to ensure scope
    try:
        lhs_value = parse_literal(lhs_path)
        debug_log(f"Parsed literal lhs: {lhs_value}")
    except ValueError: # If it's not a simple literal, try to resolve as a path
        try:
            lhs_value = get_nested_value(payload, lhs_path)
            debug_log(f"Resolved lhs from payload key path '{lhs_path}' → {lhs_value}")
        except RuleEvaluationError as e:
            if relaxed_type_check:
                lhs_value = None
                logger.debug(f"Relaxed mode fallback for missing key '{lhs_path}': {e}")
                debug_log(f"Relaxed fallback: missing key '{lhs_path}', using None")
            else:
                # Re-raise if not in relaxed mode and path resolution fails
                raise RuleEvaluationError(f"Invalid LHS: '{lhs_path}' - not a literal and not a valid payload path: {e}")

    # --- Resolve Operator ---
    try:
        compare_fn = resolve_operator(operator_str)
        debug_log(f"Resolved operator '{operator_str}' → {compare_fn}")
    except OperatorError:
        raise RuleEvaluationError(f"Operator resolution failed: {operator_str}")

    # --- Determine RHS Value ---
    # Prioritize parsing as a literal, then fallback to payload path resolution
    _temp_rhs_value = None # Use a temporary variable to ensure clear assignment
    try:
        _temp_rhs_value = parse_literal(rhs_literal)
        debug_log(f"Parsed rhs literal: {_temp_rhs_value}")
    except ValueError: # If not a simple literal, try to resolve as a path
        debug_log(f"Literal parsing failed for RHS: '{rhs_literal}' → {rhs_error}")
        if relaxed_type_check:
            debug_log(f"Attempting to resolve RHS path: {rhs_literal}")
            try:
                _temp_rhs_value = get_nested_value(payload, rhs_literal)
                debug_log(f"Fallback: Resolved RHS from payload key path '{rhs_literal}' → {_temp_rhs_value}")
            except RuleEvaluationError as e:
                logger.debug(f"Relaxed RHS fallback key resolution failed: {e}")
                _temp_rhs_value = None # Fallback to None if resolution fails
                debug_log(f"Fallback: Using None for RHS '{rhs_literal}' due to resolution failure")
        else:
            # Re-raise if not in relaxed mode and path resolution fails
            raise RuleEvaluationError(f"Invalid RHS: '{rhs_literal}' - not a literal and not a valid payload path: {e}")

    rhs_value = _temp_rhs_value # Ensure rhs_value is definitively set here for subsequent use

    # --- Type Checking and Coercion ---
    try:
        if strict_type_check:
            debug_log(f"Strict type check enabled")
            if type(lhs_value) != type(rhs_value):
                raise RuleEvaluationError(f"Incompatible types: {type(lhs_value)} vs {type(rhs_value)}")
        elif relaxed_type_check:
            debug_log(f"Relaxed type check enabled")
            # This call now receives the correctly resolved rhs_value (e.g., 42)
            lhs_value, rhs_value = _coerce_types_for_comparison(lhs_value, rhs_value)
        else:
            debug_log(f"Default strict check")
            if type(lhs_value) != type(rhs_value):
                raise RuleEvaluationError(f"Type mismatch (default strict): {type(lhs_value)} vs {type(rhs_value)}")
    except Exception as e:
        # Catch any errors during type checking/coercion
        raise RuleEvaluationError(f"Coercion error: {e}")

    # --- Perform Comparison ---
    try:
        result = compare_fn(lhs_value, rhs_value)
        debug_log(f"Comparison result: {lhs_value} {operator_str} {rhs_value} → {result}")
        return result
    except Exception as e:
        # Catch any errors during the final comparison
        raise RuleEvaluationError(f"Comparison failed: {e}")

def evaluate_rule(rule: dict, payload: dict, *, strict_type_check: bool = False, relaxed_type_check: bool = False) -> bool:
    """
    Evaluates a single rule dictionary against a given payload.
    Determines type checking mode based on rule configuration or defaults.
    """
    expression = rule.get("if")
    if not expression or not isinstance(expression, str):
        debug_log("Empty or malformed rule expression; returning True")
        return True

    # If type check flags are not explicitly provided, determine from rule config or default
    if not (strict_type_check or relaxed_type_check):
        try:
            type_mode = get_type_check_mode(rule.get("type_check_mode"))
            debug_log(f"Resolved type check mode: {type_mode}")
        except Exception as config_error:
            logger.warning(f"Invalid type check mode override: {config_error}")
            type_mode = "strict" # Fallback to strict if config is invalid
            debug_log(f"Fallback type check mode: strict")

        strict_type_check = type_mode == "strict"
        relaxed_type_check = type_mode == "relaxed"

    return _evaluate_expression(
        expression,
        payload,
        strict_type_check=strict_type_check,
        relaxed_type_check=relaxed_type_check
    )



