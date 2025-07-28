# ✅ tests/validation/test_validation_profile_enforcer.py

import pytest
import tempfile
import yaml
from src.validation.validation_profile_enforcer import (
    enforce_profile,
    ValidationProfileError
)

# 🔧 Profile helper
def _write_temp_profile(rules: list) -> str:
    """Write a validation profile (as YAML) to a temporary file for rule enforcement tests."""
    temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml")
    yaml.dump({"rules": rules}, temp_file)
    temp_file.close()
    return temp_file.name

# ✅ Rule passes
def test_valid_payload_passes():
    path = _write_temp_profile([
        {"if": "domain_definition.nx == 0", "raise": "Grid resolution nx must be nonzero"}
    ])
    payload = {"domain_definition": {"nx": 5, "min_x": 0, "max_x": 10}}
    enforce_profile(path, payload)
    assert True

def test_floats_handled_as_literals():
    path = _write_temp_profile([
        {"if": "domain_definition.max_x >= 100.0", "raise": "Too wide"}
    ])
    payload = {"domain_definition": {"max_x": 40.5}}
    enforce_profile(path, payload)
    assert True

def test_string_literal_evaluated_correctly():
    path = _write_temp_profile([
        {"if": "domain_definition.material == 'steel'", "raise": "Wrong material"}
    ])
    payload = {"domain_definition": {"material": "aluminum"}}
    enforce_profile(path, payload)
    assert True

def test_enforce_profile_success():
    path = _write_temp_profile([
        {"if": "metrics.accuracy < 0.8", "raise": "Accuracy too low"}
    ])
    payload = {"metrics": {"accuracy": 0.95}}
    enforce_profile(path, payload)
    assert True

# ❌ Rule triggers error
def test_invalid_payload_triggers_validation():
    path = _write_temp_profile([
        {"if": "domain_definition.nx == 0", "raise": "Grid resolution nx must be nonzero"}
    ])
    payload = {"domain_definition": {"nx": 0}}
    with pytest.raises(ValidationProfileError) as exc:
        enforce_profile(path, payload)
    assert str(exc.value).startswith("Grid resolution nx must be nonzero")

def test_enforce_profile_triggered_error():
    path = _write_temp_profile([
        {"if": "metrics.accuracy < 0.8", "raise": "Accuracy too low"}
    ])
    payload = {"metrics": {"accuracy": 0.7}}
    with pytest.raises(ValidationProfileError) as exc:
        enforce_profile(path, payload)
    assert str(exc.value).startswith("Accuracy too low")

def test_enforce_profile_expression_failure():
    path = _write_temp_profile([
        {"if": "a.b == 'xyz'", "raise": "Comparison failed"}
    ])
    payload = {"a": {"b": "abc"}}  # ✅ Literal string comparison to ensure failure
    with pytest.raises(ValidationProfileError) as exc:
        enforce_profile(path, payload)
    assert str(exc.value).startswith("Comparison failed")

def test_missing_keys_are_detected():
    path = _write_temp_profile([
        {"if": "domain_definition.max_z <= domain_definition.min_z", "raise": "max_z must exceed min_z"}
    ])
    payload = {"domain_definition": {"min_z": 10}}
    with pytest.raises(ValidationProfileError) as exc:
        enforce_profile(path, payload)
    assert "Expression evaluation error" in str(exc.value)
    assert "Missing key in expression" in str(exc.value)

def test_null_literal_handling():
    path = _write_temp_profile([
        {"if": "domain_definition.bbox == null", "raise": "Bounding box missing"}
    ])
    payload = {"domain_definition": {"bbox": None}}
    with pytest.raises(ValidationProfileError) as exc:
        enforce_profile(path, payload)
    assert str(exc.value).startswith("Bounding box missing")

# ⚠️ Skipped or malformed
def test_malformed_rule_is_ignored():
    path = _write_temp_profile([
        {"iff": "domain_definition.nx == 0", "raise": "Missing 'if' key"}
    ])
    payload = {"domain_definition": {"nx": 0}}
    enforce_profile(path, payload)
    assert True  # Rule skipped

def test_multiple_rules_trigger_only_first():
    path = _write_temp_profile([
        {"if": "domain_definition.nx == 0", "raise": "nx must be > 0"},
        {"if": "domain_definition.max_z <= domain_definition.min_z", "raise": "max_z must be above min_z"}
    ])
    payload = {"domain_definition": {"nx": 0, "max_z": 0, "min_z": 10}}
    with pytest.raises(ValidationProfileError) as exc:
        enforce_profile(path, payload)
    assert str(exc.value).startswith("nx must be > 0")

def test_enforce_profile_missing_file():
    with pytest.raises(RuntimeError):
        enforce_profile("nonexistent.yaml", {})

def test_unsupported_operator_raises_value_error():
    path = _write_temp_profile([
        {"if": "domain_definition.nx ++ domain_definition.ny", "raise": "Unsupported operator"}
    ])
    payload = {"domain_definition": {"nx": 1, "ny": 2}}
    with pytest.raises(ValidationProfileError) as exc:
        enforce_profile(path, payload)
    assert "Expression evaluation error" in str(exc.value)
    assert "Unsupported comparison operator" in str(exc.value)



