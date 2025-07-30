# src/validation/expression_utils.py

import ast

__all__ = ["parse_literal", "is_literal"]

def normalize_quotes(expr: str) -> str:
    """
    Cleans up deeply nested or redundant quote tokens.

    Examples:
        normalize_quotes("'''hello'''") returns "'hello'"
        normalize_quotes("''string''") returns "'string'"
        normalize_quotes('""data""') returns '"data"'
    """
    expr = expr.strip()
    expr = expr.replace("'''", "'").replace('"""', '"')
    expr = expr.replace("''", "'").replace('""', '"')
    return expr

def parse_literal(value: str):
    """
    Safely converts a string representation into its Python literal equivalent.

    Uses layered logic:
      - Handles canonical JSON-style literals explicitly
      - Detects quoted string literals
      - Attempts safe literal evaluation with ast.literal_eval
      - Falls back to raw string if evaluation fails

    Supported conversions:
    - 'null', 'None' are converted to None
    - 'true', 'false' are converted to boolean
    - Padded integers are converted to int
    - Floats are converted to float
    - Quoted strings are converted to str
    - All other values are returned as raw str

    Examples:
        parse_literal("42") returns 42
        parse_literal("3.14") returns 3.14
        parse_literal("'hello'") returns "hello"
        parse_literal('"world"') returns "world"
        parse_literal("true") returns True
        parse_literal("null") returns None
        parse_literal("00123") returns 123
    """
    if not isinstance(value, str):
        return value  # Already parsed

    val = normalize_quotes(value)
    val = val.strip()
    val_lower = val.lower()

    if val_lower == "true":
        return True
    if val_lower == "false":
        return False
    if val_lower in {"null", "none"}:
        return None

    if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
        return val[1:-1]

    if val.isdigit():
        return int(val)

    try:
        return ast.literal_eval(val)
    except Exception:
        return val

def is_literal(token: str) -> bool:
    """
    Determines whether the token represents a primitive literal.

    Supported types:
    - Boolean strings like 'true', 'false'
    - Null representations like 'null', 'none'
    - Numeric literals
    - Quoted string literals

    Examples:
        is_literal("true") returns True
        is_literal("'abc'") returns True
        is_literal("123") returns True
        is_literal("not_a_literal") returns False
    """
    token = token.strip().lower()
    if token in {"true", "false", "null", "none"}:
        return True
    if token.isnumeric():
        return True
    if (token.startswith("'") and token.endswith("'")) or (token.startswith('"') and token.endswith('"')):
        return True
    return False



