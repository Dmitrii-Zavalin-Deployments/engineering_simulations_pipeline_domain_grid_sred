# 📄 src/validation/validation_profile_expressions.py

def _evaluate_expression(lhs, rhs, operator: str, *, strict_type_check: bool = False):
    """
    Evaluates binary expressions with type safety and controlled fallback.

    Parameters:
        lhs (Any): Left-hand side value
        rhs (Any): Right-hand side value
        operator (str): Comparison operator (e.g., '==', '!=', '<', '>', '<=', '>=')
        strict_type_check (bool): Enforces strict type alignment if True; else allows coercion

    Returns:
        bool: Result of the comparison; False if type mismatch or operator error

    Examples:
        _evaluate_expression("123", 123, '==') ➝ True
        _evaluate_expression("hello", 100, '<') ➝ False
    """
    # Define supported operators
    ops = {
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        "<":  lambda a, b: a < b,
        ">":  lambda a, b: a > b,
        "<=": lambda a, b: a <= b,
        ">=": lambda a, b: a >= b,
    }

    # Optional strict type enforcement
    if strict_type_check and type(lhs) != type(rhs):
        return False

    # Attempt coercion if types mismatch and not strict
    if type(lhs) != type(rhs and not strict_type_check):
        try:
            # Prefer numeric coercion
            if isinstance(lhs, (int, float)) or isinstance(rhs, (int, float)):
                lhs = float(lhs)
                rhs = float(rhs)
            else:
                lhs = str(lhs)
                rhs = str(rhs)
        except Exception:
            return False  # Coercion failed

    # Perform comparison with fallback
    try:
        comparison_func = ops.get(operator)
        if not comparison_func:
            return False  # Unsupported operator
        return comparison_func(lhs, rhs)
    except Exception:
        return False



