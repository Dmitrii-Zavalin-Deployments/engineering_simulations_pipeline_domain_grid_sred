# tests/rules/test_type_compatibility_utils.py

import pytest
from src.rules.type_compatibility_utils import (
    are_types_comparable,
    STRICT_MODE,
    RELAXED_MODE,
    _is_numeric_str,  # ✅ Added for direct testing
)

# --- STRICT MODE TESTS ---

@pytest.mark.parametrize("lhs, rhs, expected", [
    (5, 10, True),
    (3.14, 2.71, True),
    ("hello", "world", True),
    (True, False, True),
    (5, "5", False),
    ("True", True, False),
    (5, 5.0, False),
])
def test_strict_mode_comparisons(lhs, rhs, expected):
    assert are_types_comparable(lhs, rhs, STRICT_MODE) is expected


# --- RELAXED MODE TESTS ---

@pytest.mark.parametrize("lhs, rhs, expected", [
    ("42", 42, True),
    ("3.14", 3.14, True),
    ("100", 100, True),
    ("not_found", 404, False),
    ("1", 1, True),
    ("abc", 5, False),
    (42, "42", True),
    (3.14, "3.14", True),
    ("true", True, True),
    ("False", False, True),
    ("yes", True, True),
    ("no", False, True),
    ("true", 1, False),
    (True, "yes", True),
    (3.0, 3, True),
    (0, 0.0, True),
    ("text", "text", True),
    (False, False, True),
])
def test_relaxed_mode_comparisons(lhs, rhs, expected):
    assert are_types_comparable(lhs, rhs, RELAXED_MODE) is expected


# --- UNKNOWN MODE TESTS ---

@pytest.mark.parametrize("lhs, rhs, mode", [
    (5, 5, "mystery"),
    (1, 1, "unsupported"),
])
def test_unknown_mode_is_rejected(lhs, rhs, mode):
    assert are_types_comparable(lhs, rhs, mode) is False


# --- EDGE CASES & PERFORMANCE GUARDS ---

@pytest.mark.parametrize("value", [
    "", " ", "not a number", "Trueish", "maybe", "1e309",
])
def test_relaxed_mode_false_on_ambiguous_strings(value):
    assert not are_types_comparable(value, 10, RELAXED_MODE)
    assert not are_types_comparable(10, value, RELAXED_MODE)
    assert not are_types_comparable(value, True, RELAXED_MODE)
    assert not are_types_comparable(True, value, RELAXED_MODE)


def test_relaxed_mode_handles_large_numbers():
    big_number_str = str(2 ** 128)
    big_number_int = 2 ** 128
    assert are_types_comparable(big_number_str, big_number_int, RELAXED_MODE) is True

def test_strict_mode_identity_vs_equivalence():
    assert are_types_comparable(True, 1, STRICT_MODE) is False
    assert are_types_comparable(False, 0, STRICT_MODE) is False


# --- NEW SAFETY VALIDATIONS ---

@pytest.mark.parametrize("val", [
    None,
    {},
    [],
    set(),
    tuple(),
    "1e309",
    "NaN",
    "inf",
    "-inf",
])
def test_is_numeric_str_defensive_falses(val):
    assert not _is_numeric_str(val)

@pytest.mark.parametrize("lhs, rhs", [
    (None, 1),
    (1, None),
    (None, None),
    ({}, 1),
    ([1], 2),
])
def test_are_types_comparable_handles_non_scalars(lhs, rhs):
    assert not are_types_comparable(lhs, rhs, RELAXED_MODE)
    assert not are_types_comparable(lhs, rhs, STRICT_MODE)



