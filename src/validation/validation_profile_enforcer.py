# src/validation/validation_profile_enforcer.py

try:
    import yaml
except ImportError:
    raise ImportError("Missing PyYAML. Install with: pip install PyYAML")

import operator
from validation.expression_utils import parse_literal  # ✅ Modular import added


class ValidationProfileError(Exception):
    """Raised when a validation profile rule fails."""
    pass


def _get_nested_value(payload: dict, key_path: str):
    """Traverse nested dict using dot-separated key path (e.g. 'a.b.c')."""
    keys = key_path.strip().split(".")
    value = payload
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            raise KeyError(f"Missing key in payload: '{key_path}'")
    return value


def _evaluate_expression(expr: str, payload: dict) -> bool:
    """
    Evaluate simple relational expression using payload values.
    Supported operators: ==, !=, >, <, >=, <=
    """
    ops = {
        "==": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        "<=": operator.le,
        ">": operator.gt,
        "<": operator.lt,
    }

    for symbol in sorted(ops.keys(), key=len, reverse=True):
        if symbol in expr:
            left, right = expr.split(symbol, 1)
            left_val = _get_nested_value(payload, left.strip())

            # Determine whether right side is a literal or key path
            try:
                right_val = parse_literal(right.strip())
            except Exception:
                right_val = _get_nested_value(payload, right.strip())

            # ✅ Type harmonization safeguard added
            if type(left_val) != type(right_val):
                try:
                    right_val = type(left_val)(right_val)
                except Exception:
                    pass  # keep original if coercion fails

            try:
                return ops[symbol](left_val, right_val)
            except TypeError as err:
                raise ValueError(
                    f"Incompatible types for operation '{symbol}': {type(left_val)} vs {type(right_val)}"
                ) from err

    raise ValueError(f"Unsupported expression format: '{expr}'")


def enforce_profile(profile_path: str, payload: dict):
    """
    Parse a validation YAML profile and enforce its rules on the given payload.

    Each rule must include:
      - if: <expression>
      - raise: <error message>
    """
    try:
        with open(profile_path, "r") as f:
            profile = yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load profile at '{profile_path}': {e}")

    rules = profile.get("rules", [])
    for i, rule in enumerate(rules):
        condition = rule.get("if")
        message = rule.get("raise", f"Validation rule {i} failed")

        if not condition:
            continue  # skip incomplete rule

        try:
            triggered = _evaluate_expression(condition, payload)
        except Exception as err:
            raise ValidationProfileError(
                f"[Rule {i}] Evaluation error for '{condition}': {err}"
            )

        if triggered:
            raise ValidationProfileError(f"[Rule {i}] {message}")



