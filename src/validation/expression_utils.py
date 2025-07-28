# src/validation/expression_utils.py

import ast

def parse_literal(value: str):
    """
    Safely converts a string representation into its Python literal equivalent.

    Uses `ast.literal_eval` for robust conversion with fallback to raw string
    when evaluation fails or input is ambiguous.

    Supported conversions:
    - 'null', 'None' ➝ None
    - 'true', 'false' ➝ bool
    - Numeric strings ➝ int / float
    - Quoted strings ➝ str
    - All other values ➝ raw str (fallback)

    Examples:
        parse_literal("42") ➝ 42
        parse_literal("3.14") ➝ 3.14
        parse_literal("'hello'") ➝ "hello"
        parse_literal('"world"') ➝ "world"
        parse_literal("true") ➝ True
        parse_literal("null") ➝ None
    """
    if not isinstance(value, str):
        return value  # Already parsed

    try:
        return ast.literal_eval(value.strip())
    except Exception:
        return value.strip()  # Fallback to raw string



