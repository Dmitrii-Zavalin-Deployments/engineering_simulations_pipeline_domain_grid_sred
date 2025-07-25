# tests/test_expression_evaluator.py

import pytest
from validation.validation_profile_enforcer import _evaluate_expression, ValidationProfileError


def test_expression_evaluation_type_coercion_float_str():
    payload = {
        "domain_definition": {
            "max_z": 100.0,
            "min_z": "90.5"
        }
    }
    assert _evaluate_expression("domain_definition.max_z >= domain_definition.min_z", payload) is True


def test_expression_evaluation_type_coercion_int_str():
    payload = {
        "thresholds": {
            "max_val": 150,
            "warn_val": "150"
        }
    }
    assert _evaluate_expression("thresholds.max_val == thresholds.warn_val", payload) is True


def test_expression_evaluation_str_int_coercion_failure():
    payload = {
        "rules": {
            "status_code": "not_a_number",
            "expected_code": 200
        }
    }
    with pytest.raises(ValueError) as err:
        _evaluate_expression("rules.status_code == rules.expected_code", payload)
    assert "Incompatible types" in str(err.value)


def test_expression_evaluation_nested_key_resolution():
    payload = {
        "system": {
            "subsystem": {
                "value": 42
            }
        },
        "expected": {
            "value": 42
        }
    }
    assert _evaluate_expression("system.subsystem.value == expected.value", payload) is True


def test_expression_evaluation_literal_vs_payload_key():
    payload = {
        "config": {
            "enabled": "true"
        }
    }
    # Right side should be parsed as literal boolean
    assert _evaluate_expression("config.enabled == true", payload) is False


def test_expression_evaluation_unsupported_operator():
    payload = {
        "meta": {
            "score": 85
        }
    }
    with pytest.raises(ValueError) as err:
        _evaluate_expression("meta.score %% 80", payload)
    assert "Unsupported expression format" in str(err.value)


def test_expression_evaluation_missing_key_path():
    payload = {
        "data": {
            "valid": True
        }
    }
    with pytest.raises(KeyError):
        _evaluate_expression("data.missing_key == True", payload)



