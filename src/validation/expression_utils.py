# src/validation/expression_utils.py

def parse_literal(value: str):
    """
    Safely converts a string representation into its Python literal equivalent.

    Supported conversions:
    - 'null', 'None' ➝ None
    - 'true', 'false' ➝ bool
    - Integers ➝ int
    - Floats ➝ float
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

    val = value.strip()

    # Boolean literals
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False

    # Null / None literals
    if val.lower() in {"null", "none"}:
        return None

    # Quoted strings
    if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
        return val[1:-1]

    # Integer and float conversion
    try:
        if '.' in val:
            return float(val)
        return int(val)
    except ValueError:
        return val  # Fallback to string



