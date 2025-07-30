import ast

def normalize_quotes(expr: str) -> str:
    """
    Cleans up deeply nested or redundant quote tokens.

    Examples:
        normalize_quotes("'''hello'''") ➝ "'hello'"
        normalize_quotes("''world''") ➝ "'world'"
    """
    return expr.strip().replace("'''", "'").replace("''", "'")

def parse_literal(value: str):
    """
    Safely converts a string representation into its Python literal equivalent.

    Uses layered logic:
      - Handles canonical JSON-style literals explicitly
      - Detects quoted string literals
      - Attempts safe literal evaluation with ast.literal_eval
      - Falls back to raw string if evaluation fails

    Supported conversions:
    - 'null', 'None' ➝ None
    - 'true', 'false' ➝ bool
    - Padded integers ➝ int
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
        parse_literal("00123") ➝ 123
    """
    if not isinstance(value, str):
        return value  # Already parsed

    val = normalize_quotes(value)  # ✅ Safety wrapper applied
    val = val.strip()
    val_lower = val.lower()

    # ✅ Explicit JSON-style literal handling
    if val_lower == "true":
        return True
    if val_lower == "false":
        return False
    if val_lower in {"null", "none"}:
        return None

    # ✅ Handle quoted string literals before coercion
    if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
        return val[1:-1]

    # ✅ Leading-zero-safe integer fallback
    if val.isdigit():
        return int(val)

    # ✅ Attempt literal evaluation (floats, objects, etc.)
    try:
        return ast.literal_eval(val)
    except Exception:
        return val  # Fallback to raw string



