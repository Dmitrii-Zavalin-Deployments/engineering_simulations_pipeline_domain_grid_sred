# 📄 src/rules/rule_config_parser.py

import yaml

class RuleConfigError(Exception):
    """Raised when validation rule configuration cannot be parsed properly."""
    pass

def load_rule_profile(path: str) -> list:
    """
    Loads a YAML-based validation profile and returns a list of normalized rule definitions.

    Each rule must contain:
        - "if": expression string
        - "raise": error message string
    Optional:
        - "strict_type_check": boolean flag (default: False)

    Parameters:
        path (str): Path to YAML file containing rule definitions

    Returns:
        list: List of validated and enriched rule dictionaries

    Raises:
        RuleConfigError: If the file cannot be read or is malformed
    """
    try:
        with open(path, "r") as f:
            content = yaml.safe_load(f)
    except Exception as e:
        raise RuleConfigError(f"Failed to load rule profile at '{path}': {e}")

    raw_rules = content.get("rules", [])
    if not isinstance(raw_rules, list):
        raise RuleConfigError(f"Invalid rule structure: expected list under 'rules' key")

    enriched_rules = []
    for i, rule in enumerate(raw_rules):
        expr = rule.get("if")
        msg = rule.get("raise", f"Rule {i} failed")
        strict = rule.get("strict_type_check", False)

        if not isinstance(expr, str):
            continue  # Skip malformed rule

        enriched_rules.append({
            "if": expr,
            "raise": msg,
            "strict_type_check": bool(strict),
        })

    return enriched_rules



