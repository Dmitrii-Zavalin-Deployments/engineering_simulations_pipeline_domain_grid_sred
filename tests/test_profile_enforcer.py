import pytest
import tempfile
import yaml
from validation.validation_profile_enforcer import enforce_profile, ValidationProfileError


def _write_temp_profile(rules: list) -> str:
    """Helper to write temporary profile YAML to disk."""
    temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml")
    yaml.dump({"rules": rules}, temp_file)
    temp_file.close()
    return temp_file.name


def test_valid_payload_passes():
    profile_path = _write_temp_profile([
        {
            "if": "domain_definition.nx == 0",
            "raise": "Grid resolution nx must be nonzero"
        }
    ])
    payload = {
        "domain_definition": {
            "nx": 5,
            "min_x": 0,
            "max_x": 10
        }
    }

    # Should not raise any errors
    enforce_profile(profile_path, payload)


def test_invalid_payload_triggers_validation():
    profile_path = _write_temp_profile([
        {
            "if": "domain_definition.nx == 0",
            "raise": "Grid resolution nx must be nonzero"
        }
    ])
    payload = {
        "domain_definition": {
            "nx": 0,
            "min_x": 0,
            "max_x": 10
        }
    }

    with pytest.raises(ValidationProfileError) as exc_info:
        enforce_profile(profile_path, payload)

    assert "Grid resolution nx must be nonzero" in str(exc_info.value)


def test_missing_keys_are_detected():
    profile_path = _write_temp_profile([
        {
            "if": "domain_definition.max_z <= domain_definition.min_z",
            "raise": "max_z must exceed min_z"
        }
    ])
    payload = {
        "domain_definition": {
            "min_z": 10  # max_z is missing
        }
    }

    with pytest.raises(ValidationProfileError) as exc_info:
        enforce_profile(profile_path, payload)

    assert "max_z" in str(exc_info.value)


def test_malformed_rule_is_ignored():
    profile_path = _write_temp_profile([
        {
            "iff": "domain_definition.nx == 0",  # malformed key
            "raise": "Missing 'if' key"
        }
    ])
    payload = {
        "domain_definition": {"nx": 0}
    }

    # Rule is skipped silently
    enforce_profile(profile_path, payload)


def test_unsupported_operator_raises_value_error():
    profile_path = _write_temp_profile([
        {
            "if": "domain_definition.nx ++ domain_definition.ny",
            "raise": "Unsupported operator"
        }
    ])
    payload = {
        "domain_definition": {"nx": 1, "ny": 2}
    }

    with pytest.raises(ValidationProfileError) as exc_info:
        enforce_profile(profile_path, payload)

    assert "Unsupported expression format" in str(exc_info.value)



