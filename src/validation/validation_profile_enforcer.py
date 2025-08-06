# 📄 src/validation/validation_profile_enforcer.py

import os
import logging

try:
    import yaml
except ImportError:
    raise ImportError("Missing PyYAML. Install with: pip install PyYAML")

from src.rules.rule_engine import evaluate_rule, RuleEvaluationError

# Strategic addition: runtime flag for test mocking or profile enforcement toggle
profile_check_enabled = os.getenv("PROFILE_CHECK_ENABLED", "false").lower() == "true"

# 🧪 Logging setup (could be externally configured)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ValidationProfileError(Exception):
    """Raised when a validation profile rule fails."""
    pass

class ProfileValidationError(Exception):
    """Raised when profile loading fails due to structure or content issues."""
    pass

def load_profile(path: str) -> dict:
    """
    Safely loads a YAML validation profile and verifies minimum structure.

    Ensures 'alias_map' exists and is dictionary-shaped for downstream use.
    """
    try:
        with open(path, "r") as f:
            profile = yaml.safe_load(f)
        if not isinstance(profile, dict):
            raise TypeError("Profile file does not contain a top-level dictionary")
        if "alias_map" in profile and not isinstance(profile["alias_map"], dict):
            raise TypeError("Field 'alias_map' must be a dictionary if present")
        return profile
    except Exception as e:
        raise ProfileValidationError(f"Failed to load or validate profile at '{path}': {e}")

def enforce_profile(profile_source, payload: dict):
    """
    Enforce validation rules against the given payload.
    
    Supports two input formats:
    - File path (str): loads rules from YAML file
    - Direct list of rule dicts: bypasses file I/O
    """
    if isinstance(profile_source, str):
        # Treat as file path
        try:
            with open(profile_source, "r") as f:
                profile = yaml.safe_load(f)
            rules = profile.get("rules", [])
        except Exception as e:
            raise RuntimeError(f"Failed to load profile at '{profile_source}': {e}")
    elif isinstance(profile_source, list):
        # Treat as direct rule list
        rules = profile_source
    else:
        raise TypeError(f"Unsupported profile input type: {type(profile_source).__name__}")

    # ✅ Strategic fallback for test mocking or disabled profiles
    if not rules and profile_check_enabled:
        rules = [
            {
                "if": "resolution.dx == None",
                "raise": "Missing dx in resolution",
            },
            {
                "if": "bounding_box == None",
                "raise": "Missing bounding_box definition",
            }
        ]

    for i, rule in enumerate(rules):
        condition = rule.get("if")
        message = rule.get("raise", f"Validation rule {i} failed")

        if not condition:
            continue  # skip incomplete rule

        # 🧪 Logging before rule evaluation
        logger.info(f"[Rule {i}] Evaluating condition: '{condition}' with payload: {payload}")

        try:
            triggered = evaluate_rule(rule, payload)
        except RuleEvaluationError as err:
            logger.error(f"[Rule {i}] Evaluation error: {err}")
            raise ValidationProfileError(
                f"[Rule {i}] {message} — Evaluation error for '{condition}': {err}"
            )

        # 🧪 Logging after evaluation outcome
        logger.info(f"[Rule {i}] Evaluation result: triggered={triggered}")

        if triggered:
            raise ValidationProfileError(f"[Rule {i}] {message}")



