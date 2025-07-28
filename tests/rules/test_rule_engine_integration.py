# tests/rules/test_rule_engine_integration.py

import pytest
from src.rules.rule_engine import evaluate_rule

# 🧪 Basic Pass-through Enforcement (Relaxed)
def test_numeric_string_equals_float_relaxed():
    rule = {
        "if": "values.height == 50.0",
        "raise": "Height mismatch",
        "strict_type_check": False,
    }
    payload = {"values": {"height": "50.0"}}
    assert evaluate_rule(rule, payload) is True

def test_boolean_string_equals_true_relaxed():
    rule = {
        "if": "flags.active == true",
        "raise": "Active flag failure",
        "strict_type_check": False,
    }
    payload = {"flags": {"active": "true"}}
    assert evaluate_rule(rule, payload) is True

# 🚫 Strict Type Enforcement (Should Fail)
def test_boolean_string_equals_true_strict():
    rule = {
        "if": "flags.active == true",
        "raise": "Strict active flag mismatch",
        "strict_type_check": True,
    }
    payload = {"flags": {"active": "true"}}  # string, not bool
    assert evaluate_rule(rule, payload) is False

def test_int_string_strict_comparison_failure():
    rule = {
        "if": "metrics.score == 85",
        "raise": "Score mismatch",
        "strict_type_check": True,
    }
    payload = {"metrics": {"score": "85"}}
    assert evaluate_rule(rule, payload) is False

# ✅ Matching Native Types
def test_native_int_match_strict():
    rule = {
        "if": "metrics.score == 85",
        "raise": "Score mismatch",
        "strict_type_check": True,
    }
    payload = {"metrics": {"score": 85}}
    assert evaluate_rule(rule, payload) is True

# 🧪 Nested Field Access
def test_nested_value_strict_match():
    rule = {
        "if": "domain.bounds.max_z == 100.0",
        "raise": "max_z mismatch",
        "strict_type_check": True,
    }
    payload = {"domain": {"bounds": {"max_z": 100.0}}}
    assert evaluate_rule(rule, payload) is True

def test_nested_string_coercion_relaxed():
    rule = {
        "if": "domain.bounds.max_z == 100.0",
        "raise": "max_z mismatch",
        "strict_type_check": False,
    }
    payload = {"domain": {"bounds": {"max_z": "100.0"}}}
    assert evaluate_rule(rule, payload) is True

# 🚫 Edge Case: incompatible fallback
def test_invalid_string_comparison_relaxed():
    rule = {
        "if": "values.status == 404",
        "raise": "Invalid fallback mismatch",
        "strict_type_check": False,
    }
    payload = {"values": {"status": "not_found"}}
    assert evaluate_rule(rule, payload) is False

# 🔍 Literal expression fallback (no payload needed)
def test_direct_literal_comparison_strict_pass():
    rule = {
        "if": "123 == 123",
        "raise": "Should pass",
        "strict_type_check": True,
    }
    assert evaluate_rule(rule, {}) is True

def test_direct_literal_comparison_strict_fail():
    rule = {
        "if": "true == 'true'",
        "raise": "Mismatch literal strict",
        "strict_type_check": True,
    }
    assert evaluate_rule(rule, {}) is False



