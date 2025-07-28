# 📄 src/rules/operators.py

import re

class OperatorError(Exception):
    """Raised when an unsupported operator is invoked."""
    pass

def op_eq(a, b): return a == b
def op_ne(a, b): return a != b
def op_lt(a, b): return a < b
def op_le(a, b): return a <= b
def op_gt(a, b): return a > b
def op_ge(a, b): return a >= b
def op_in(a, b): return a in b
def op_not_in(a, b): return a not in b

def op_matches(a, b):
    """Regex match — assumes 'b' is a regex pattern"""
    if not isinstance(b, str):
        raise TypeError("Regex pattern must be a string")
    return re.fullmatch(b, str(a)) is not None

# 🔗 Operator registry
OPS = {
    "==": op_eq,
    "!=": op_ne,
    "<": op_lt,
    "<=": op_le,
    ">": op_gt,
    ">=": op_ge,
    "in": op_in,
    "not in": op_not_in,
    "matches": op_matches,
}

def resolve_operator(op: str):
    """
    Retrieve the comparison function associated with a given operator.

    Parameters:
        op (str): Symbolic or semantic operator string

    Returns:
        function: Callable that accepts two arguments and returns a bool

    Raises:
        OperatorError: If operator is not supported
    """
    if op not in OPS:
        raise OperatorError(f"Unsupported comparison operator: '{op}'")
    return OPS[op]



