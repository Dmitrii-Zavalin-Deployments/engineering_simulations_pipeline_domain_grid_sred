# 📄 tests/validation/test_validation_profile_expressions.py

import pytest
from src.rules.rule_engine import (
    _get_nested_value,
    _evaluate_expression
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
    ("data.flag != true", {"data": {"flag": True}}, False),
    ("limits.upper > limits.lower", {"limits": {"upper": 10.0, "lower": 5.0}}, True),
    ("metrics.score < 0.5", {"metrics": {"score": 0.3}}, True),
    ("config.enabled == true", {"config": {"enabled": "true"}}, True),
])
def test_evaluate_expression_basic(expr, payload, expected):
    assert _evaluate_expression(expr, payload) is expected

# 🧪 Type Coercion
def test_expression_evaluation_type_coercion_float_str():
    payload = {"domain_definition": {"max_z": 100.0, "min_z": "90.5"}}
    assert _evaluate_expression("domain_definition.max_z >= domain_definition.min_z", payload)

def test_expression_evaluation_type_coercion_int_str():
    payload = {"thresholds": {"max_val": 150, "warn_val": "150"}}
    assert _evaluate_expression("thresholds.max_val == thresholds.warn_val", payload)

def test_expression_evaluation_type_coercion_mixed_types():
    payload = {"a": {"b": "10"}, "x": {"y": 10}}
    assert _evaluate_expression("a.b == x.y", payload)

# 🚫 Failure & Exceptions
def test_expression_evaluation_incompatible_types():
    payload = {"rules": {"status_code": "not_a_number", "expected_code": 200}}
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

def test_expression_evaluation_nested_key_resolution():
    payload = {"system": {"subsystem": {"value": 42}}, "expected": {"value": 42}}
    assert _evaluate_expression("system.subsystem.value == expected.value", payload)

# 🔍 New Tests — Literal Edge Cases and Strict Type Toggle
def test_literal_vs_native_equivalence():
    payload = {"flag": "true", "count": "123"}
    assert _evaluate_expression("flag == true", payload)  # parsed as True
    assert _evaluate_expression("count == 123", payload)  # parsed as int

def test_literal_comparison_strict_type_enabled():
    payload = {"flag": "true", "count": "123"}
    assert not _evaluate_expression("flag == true", payload, strict_type_check=True)
    assert not _evaluate_expression("count == 123", payload, strict_type_check=True)

def test_literal_comparison_strict_type_disabled():
    payload = {"flag": "true", "count": "123"}
    assert _evaluate_expression("flag == true", payload, strict_type_check=False)
    assert _evaluate_expression("count == 123", payload, strict_type_check=False)

def test_non_expression_literal_equality():
    assert _evaluate_expression("123 == 123", {}) is True
    assert _evaluate_expression("'hello' == \"hello\"", {}) is True

def test_literal_mismatch_fallback():
    assert _evaluate_expression("hello == 100", {}) is False
    assert not _evaluate_expression("true == 'true'", {}, strict_type_check=True)

def test_invalid_operator_literal_case():
    with pytest.raises(ValueError) as err:
        _evaluate_expression("false %% true", {})
    assert "Unsupported expression format" in str(err.value)



