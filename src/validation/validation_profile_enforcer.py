# 📄 src/validation/validation_profile_enforcer.py

try:
    import yaml
except ImportError:
    raise ImportError("Missing PyYAML. Install with: pip install PyYAML")

from src.rules.rule_engine import evaluate_rule, RuleEvaluationError


class ValidationProfileError(Exception):
    """Raised when a validation profile rule fails."""
    pass


def enforce_profile(profile_path: str, payload: dict):
    """
    Parse a validation YAML profile and enforce its rules on the given payload.

    Each rule must include:
      - if: <expression>
      - raise: <error message>
      - Optional: strict_type_check: <bool>
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
            triggered = evaluate_rule(rule, payload)
        except RuleEvaluationError as err:
            raise ValidationProfileError(
                f"[Rule {i}] {message} — Evaluation error for '{condition}': {err}"
            )

        if triggered:
            raise ValidationProfileError(f"[Rule {i}] {message}")



