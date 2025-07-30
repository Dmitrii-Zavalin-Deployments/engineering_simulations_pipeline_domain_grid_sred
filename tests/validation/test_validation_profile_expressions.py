# tests/validation/test_validation_profile_expressions.py

import os
import pytest

# ✅ Test Enhancement: Enable debug mode globally during expression tests
os.environ["ENABLE_RULE_DEBUG"] = "true"

from src.rules.rule_engine import (
    get_nested_value,
    _evaluate_expression,
    RuleEvaluationError
)

from tests.conftest import get_payload_with_defaults  # 🔧 Added fixture import

# 🔍 Nested Key Access
def test_get_nested_value_success():
    payload = {"a": {"b": {"c": 42}}}
    assert get_nested_value(payload, "a.b.c") == 42

def test_get_nested_value_missing_key():
    payload = {"a": {"b": {"c": 42}}}
    with pytest.raises(RuleEvaluationError) as e:
        get_nested_value(payload, "a.x.c")
    assert "Missing key" in str(e.value)

# 🔧 Expression Evaluation — Core
@pytest.mark.parametrize("expr, payload, expected", [
    ("values.x == 5", {"values": {"x": 5}}, True),
    ("data.flag != \"true\"", {"data": {"flag": "true"}}, False),
    ("limits.upper > 5.0", {"limits": {"upper": 10.0, "lower": 5.0}}, True),
    ("metrics.score < 0.5", {"metrics": {"score": "0.3"}}, True),
    ("config.enabled == \"true\"", {"config": {"enabled": "true"}}, True),
])
def test_evaluate_expression_basic(expr, payload, expected):
    assert _evaluate_expression(expr, payload, relaxed_type_check=True) is expected

# 🧪 Type Coercion
def test_expression_evaluation_type_coercion_float_str():
    payload = get_payload_with_defaults()
    assert _evaluate_expression("domain_definition.max_z >= domain_definition.min_z", payload, relaxed_type_check=True)

def test_expression_evaluation_type_coercion_int_str():
    payload = get_payload_with_defaults()
    assert _evaluate_expression("thresholds.max_val == thresholds.warn_val", payload, relaxed_type_check=True)

def test_expression_evaluation_type_coercion_mixed_types():
    payload = get_payload_with_defaults()
    assert _evaluate_expression("a.b == x.y", payload, relaxed_type_check=True)

# 🚫 Failure & Exceptions
def test_expression_evaluation_incompatible_types():
    payload = get_payload_with_defaults()
    with pytest.raises(RuleEvaluationError) as err:
        _evaluate_expression("rules.status_code == rules.expected_code", payload, strict_type_check=True)
    assert "Incompatible types" in str(err.value)

def test_expression_evaluation_unsupported_operator():
    payload = {"meta": {"score": 85}}
    with pytest.raises(RuleEvaluationError) as err:
        _evaluate_expression("meta.score %% 80", payload)
    assert "Unsupported operator" in str(err.value)

def test_expression_evaluation_missing_key_path():
    payload = {"data": {"valid": True}}
    with pytest.raises(RuleEvaluationError) as err:
        _evaluate_expression("data.missing_key == true", payload)
    assert "Missing key" in str(err.value)

# 🧪 Mixed Mode Fallbacks and Missing Keys
def test_expression_evaluation_missing_key_relaxed_fallback():
    payload = {"a": {"x": "value"}}
    assert _evaluate_expression("a.missing == null", payload, relaxed_type_check=True)

def test_expression_evaluation_nested_key_resolution():
    payload = get_payload_with_defaults()
    assert _evaluate_expression("system.subsystem.value == expected.value", payload, relaxed_type_check=True)

# 🔍 Literal Edge Cases and Strict Type Toggle
def test_literal_vs_native_equivalence():
    payload = {"flag": True, "count": 123}
    assert _evaluate_expression("flag == true", payload, relaxed_type_check=True)
    assert _evaluate_expression("count == 123", payload, relaxed_type_check=True)

def test_literal_comparison_strict_type_enabled():
    payload = {"flag": "true", "count": "123"}
    assert not _evaluate_expression("flag == true", payload, strict_type_check=True)
    assert not _evaluate_expression("count == 123", payload, strict_type_check=True)

def test_literal_comparison_strict_type_disabled():
    payload = {"flag": "true", "count": "123"}
    assert _evaluate_expression("flag == \"true\"", payload, strict_type_check=False, relaxed_type_check=True)
    assert _evaluate_expression("count == 123", payload, strict_type_check=False, relaxed_type_check=True)

# 🧪 Strictness Mode Matrix
@pytest.mark.parametrize("expression,payload,strict,expected", [
    ("x.val == 100", {"x": {"val": 100}}, True, True),
    ("x.val == 100", {"x": {"val": "100"}}, False, True),
    ("x.flag == true", {"x": {"flag": True}}, True, True),
    ("x.flag == true", {"x": {"flag": "true"}}, False, True),
])
def test_strict_vs_relaxed_behavior(expression, payload, strict, expected):
    result = _evaluate_expression(expression, payload, strict_type_check=strict, relaxed_type_check=not strict)
    assert result is expected

# 🔤 Literal Matching and Fallbacks
def test_non_expression_literal_equality():
    payload = get_payload_with_defaults()
    assert _evaluate_expression("123 == 123", payload) is True
    assert _evaluate_expression("'hello' == 'hello'", payload) is True

def test_literal_mismatch_fallback():
    payload = get_payload_with_defaults()
    assert _evaluate_expression("'hello' == 100", payload, relaxed_type_check=True) is False
    with pytest.raises(RuleEvaluationError):
        _evaluate_expression("true == \"true\"", payload, strict_type_check=True)

def test_invalid_operator_literal_case():
    with pytest.raises(RuleEvaluationError) as err:
        _evaluate_expression("false %% true", {})
    assert "Unsupported operator" in str(err.value)



