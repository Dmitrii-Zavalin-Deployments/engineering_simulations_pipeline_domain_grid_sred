# tests/validation/test_validation_profile_enforcer.py

import pytest
import tempfile
import yaml
from src.validation.validation_profile_enforcer import (
    _get_nested_value,
    _evaluate_expression,
    enforce_profile,
    ValidationProfileError
)


# 🔍 Nested Key Access
def test_get_nested_value_success():
    payload = {"a": {"b": {"c": 42}}}
    assert _get_nested_value(payload, "a.b.c") == 42

def test_get_nested_value_missing_key():
    payload = {"a": {"b": {"c": 42}}}
    with pytest.raises(KeyError):
        _get_nested_value(payload, "a.x.c")


# 🔧 Expression Evaluation — Core
@pytest.mark.parametrize("expr, payload, expected", [
    ("values.x == 5", {"values": {"x": 5}}, True),
    ("data.flag != false", {"data": {"flag": True}}, True),
    ("limits.upper > limits.lower", {"limits": {"upper": 10, "lower": 5}}, True),
    ("metrics.score < 0.5", {"metrics": {"score": 0.3}}, True),
    ("config.enabled == true", {"config": {"enabled": "true"}}, False),
])
def test_evaluate_expression_basic(expr, payload, expected):
    assert _evaluate_expression(expr, payload) is expected


# 🧪 Type Coercion
def test_expression_evaluation_type_coercion_float_str():
    payload = {
        "domain_definition": {
            "max_z": 100.0,
            "min_z": "90.5"
        }
    }
    assert _evaluate_expression("domain_definition.max_z >= domain_definition.min_z", payload)

def test_expression_evaluation_type_coercion_int_str():
    payload = {
        "thresholds": {
            "max_val": 150,
            "warn_val": "150"
        }
    }
    assert _evaluate_expression("thresholds.max_val == thresholds.warn_val", payload)

def test_expression_evaluation_type_coercion_mixed_types():
    payload = {"a": {"b": "10"}, "x": {"y": 10}}
    assert _evaluate_expression("a.b == x.y", payload)


# 🚫 Failure & Exceptions
def test_expression_evaluation_incompatible_types():
    payload = {
        "rules": {
            "status_code": "not_a_number",
            "expected_code": 200
        }
    }
    with pytest.raises(ValueError) as err:
        _evaluate_expression("rules.status_code == rules.expected_code", payload)
    assert "Incompatible types" in str(err.value)

def test_expression_evaluation_unsupported_operator():
    payload = {"meta": {"score": 85}}
    with pytest.raises(ValueError) as err:
        _evaluate_expression("meta.score %% 80", payload)
    assert "Unsupported expression format" in str(err.value)

def test_expression_evaluation_missing_key_path():
    payload = {"data": {"valid": True}}
    with pytest.raises(KeyError):
        _evaluate_expression("data.missing_key == True", payload)


# 🧩 Nested Key Resolution
def test_expression_evaluation_nested_key_resolution():
    payload = {
        "system": {"subsystem": {"value": 42}},
        "expected": {"value": 42}
    }
    assert _evaluate_expression("system.subsystem.value == expected.value", payload)


# 📜 Profile Enforcement Logic
def test_enforce_profile_success():
    profile = {
        "rules": [{"if": "metrics.accuracy < 0.8", "raise": "Accuracy too low"}]
    }
    payload = {"metrics": {"accuracy": 0.95}}
    with tempfile.NamedTemporaryFile("w+", suffix=".yaml") as f:
        yaml.dump(profile, f)
        f.flush()
        enforce_profile(f.name, payload)  # No error expected

def test_enforce_profile_triggered_error():
    profile = {
        "rules": [{"if": "metrics.accuracy < 0.8", "raise": "Accuracy too low"}]
    }
    payload = {"metrics": {"accuracy": 0.7}}
    with tempfile.NamedTemporaryFile("w+", suffix=".yaml") as f:
        yaml.dump(profile, f)
        f.flush()
        with pytest.raises(ValidationProfileError) as err:
            enforce_profile(f.name, payload)
        assert "Accuracy too low" in str(err.value)

def test_enforce_profile_missing_file():
    with pytest.raises(RuntimeError):
        enforce_profile("nonexistent.yaml", {})

def test_enforce_profile_expression_failure():
    profile = {
        "rules": [{"if": "a.b == x.y", "raise": "Comparison failed"}]
    }
    payload = {"a": {"b": "abc"}, "x": {"y": 123}}
    with tempfile.NamedTemporaryFile("w+", suffix=".yaml") as f:
        yaml.dump(profile, f)
        f.flush()
        with pytest.raises(ValidationProfileError) as err:
            enforce_profile(f.name, payload)
        assert "Comparison failed" in str(err.value)



