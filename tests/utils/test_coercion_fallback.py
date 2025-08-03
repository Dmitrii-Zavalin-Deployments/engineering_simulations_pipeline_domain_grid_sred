# tests/utils/test_coercion_fallback.py

import pytest
from src.utils.coercion import (
    coerce_numeric,
    coerce_boolean,
    coerce_string,
    safe_float,
    relaxed_cast,
    relaxed_equals
)

# 🔹 Numeric Coercion Edge Cases
def test_numeric_overflow_string():
    assert coerce_numeric("1e10000") is None

def test_numeric_infinite_object():
    assert coerce_numeric(float("inf")) is None

def test_numeric_nan_input():
    assert coerce_numeric(float("nan")) is None

def test_numeric_weird_format():
    assert coerce_numeric("3.14.15") is None

def test_numeric_utf8_like_string():
    assert coerce_numeric("３．１４") is None  # Unicode full-width digits

def test_numeric_zero_string():
    assert coerce_numeric("0") == 0.0


# 🔹 Boolean Coercion Edge Cases
def test_boolean_integer_zero_one():
    assert coerce_boolean(0) == False
    assert coerce_boolean(1) == True

def test_boolean_uppercase_strings():
    assert coerce_boolean("TRUE") == True
    assert coerce_boolean("FALSE") == False

def test_boolean_weird_string():
    assert coerce_boolean("yes") == "yes"
    assert coerce_boolean("nope") == "nope"

def test_boolean_bad_str_object():
    class BadStr:
        def __str__(self): raise ValueError("bad-str")

    assert coerce_boolean(BadStr()) is None


# 🔹 String Coercion Edge Cases
def test_string_int_input():
    assert coerce_string(123) == "123"

def test_string_none_input():
    assert coerce_string(None) == "None"

def test_string_bad_object():
    class Bad:
        def __str__(self): raise ValueError("fail")
    assert coerce_string(Bad()) == ""

def test_string_unicode_object():
    class UnicodeObj:
        def __str__(self): return "Ω≈ç√∫˜µ≤≥÷"
    assert coerce_string(UnicodeObj()) == "Ω≈ç√∫˜µ≤≥÷"


# 🔹 Safe Float Cases
def test_safe_float_valid_input():
    assert safe_float("3.1415") == pytest.approx(3.1415)

def test_safe_float_invalid_string():
    assert safe_float("not-a-float") is None

def test_safe_float_none():
    assert safe_float(None) is None


# 🔹 Relaxed Casting Robustness
@pytest.mark.parametrize("value,target,expected", [
    ("true", bool, True),
    ("FALSE", bool, False),
    ("yes", bool, None),
    ("123", int, 123),
    ("3.14", float, pytest.approx(3.14)),
    ("NaN", float, None),
    ("inf", float, None),
    (None, str, "None"),
    (object(), str, str(object())),
])
def test_relaxed_cast_defensive(value, target, expected):
    result = relaxed_cast(value, target)
    if expected is None:
        assert result is None
    elif isinstance(expected, float):
        assert result == pytest.approx(expected)
    else:
        assert result == expected


# 🔹 Relaxed Equals Corner Cases
def test_relaxed_equals_malformed_strings():
    assert not relaxed_equals("not_a_number", 0)
    assert not relaxed_equals("NaN", 5)

def test_relaxed_equals_equivalent_values():
    assert relaxed_equals("true", True)
    assert relaxed_equals("1", True)
    assert relaxed_equals("0", False)
    assert relaxed_equals("False", False)
    assert relaxed_equals("  123  ", 123)

def test_relaxed_equals_non_equivalent():
    assert not relaxed_equals("true", 1.0)
    assert not relaxed_equals("False", "true")



