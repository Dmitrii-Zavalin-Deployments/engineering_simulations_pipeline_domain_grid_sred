# tests/test_validation_profile_enforcer.py

import pytest
from validation.validation_profile_enforcer import enforce_profile, ValidationProfileError

# Utility: in-memory profile for testing without file I/O
def enforce_profile_from_dict(profile_dict, payload):
    import tempfile, yaml
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(profile_dict, f)
        f.flush()
        return enforce_profile(f.name, payload)

def test_passes_when_rule_does_not_trigger():
    payload = {"domain_definition": {"nx": 5}}
    profile = {
        "rules": [
            {"if": "domain_definition.nx == 0", "raise": "nx must be zero"}
        ]
    }
    enforce_profile_from_dict(profile, payload)  # No exception expected

def test_triggers_validation_error_on_literal_match():
    payload = {"domain_definition": {"nx": 0}}
    profile = {
        "rules": [
            {"if": "domain_definition.nx == 0", "raise": "nx must be zero"}
        ]
    }
    with pytest.raises(ValidationProfileError, match="nx must be zero"):
        enforce_profile_from_dict(profile, payload)

def test_floats_handled_as_literals():
    payload = {"domain_definition": {"max_x": 40.5}}
    profile = {
        "rules": [
            {"if": "domain_definition.max_x >= 100.0", "raise": "Too wide"}
        ]
    }
    enforce_profile_from_dict(profile, payload)  # Should pass

def test_malformed_expression_raises():
    payload = {"domain_definition": {"nx": 0}}
    profile = {
        "rules": [
            {"if": "domain_definition.nx =", "raise": "Invalid expression"}
        ]
    }
    with pytest.raises(ValidationProfileError, match="Unsupported expression"):
        enforce_profile_from_dict(profile, payload)

def test_missing_key_triggers_key_error():
    payload = {"domain_definition": {"ny": 1}}  # 'nx' is missing
    profile = {
        "rules": [
            {"if": "domain_definition.nx == 0", "raise": "Missing nx"}
        ]
    }
    with pytest.raises(ValidationProfileError, match="Missing key in payload"):
        enforce_profile_from_dict(profile, payload)

def test_string_literal_evaluated_correctly():
    payload = {"domain_definition": {"material": "aluminum"}}
    profile = {
        "rules": [
            {"if": "domain_definition.material == 'steel'", "raise": "Wrong material"}
        ]
    }
    enforce_profile_from_dict(profile, payload)  # Should pass

def test_boolean_literal_parsing():
    payload = {"domain_definition": {"enabled": False}}
    profile = {
        "rules": [
            {"if": "domain_definition.enabled == true", "raise": "Feature must be enabled"}
        ]
    }
    enforce_profile_from_dict(profile, payload)  # Should pass since enabled == False

def test_null_literal_handling():
    payload = {"domain_definition": {"bbox": None}}
    profile = {
        "rules": [
            {"if": "domain_definition.bbox == null", "raise": "Bounding box missing"}
        ]
    }
    with pytest.raises(ValidationProfileError, match="Bounding box missing"):
        enforce_profile_from_dict(profile, payload)

def test_rule_missing_condition_is_skipped():
    payload = {"domain_definition": {"nx": 3}}
    profile = {
        "rules": [
            {"raise": "This rule has no condition"}
        ]
    }
    enforce_profile_from_dict(profile, payload)  # Should silently skip

def test_multiple_rules_trigger_only_first():
    payload = {"domain_definition": {"nx": 0, "max_z": 0, "min_z": 10}}
    profile = {
        "rules": [
            {"if": "domain_definition.nx == 0", "raise": "nx must be > 0"},
            {"if": "domain_definition.max_z <= domain_definition.min_z", "raise": "max_z must be above min_z"}
        ]
    }
    with pytest.raises(ValidationProfileError, match="nx must be > 0"):
        enforce_profile_from_dict(profile, payload)



