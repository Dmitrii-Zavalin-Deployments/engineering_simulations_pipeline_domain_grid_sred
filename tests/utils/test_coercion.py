# tests/unit/test_coercion.py

import pytest
import math
from unittest.mock import patch, MagicMock
from typing import Any, Optional, Union

# --- Import Functions to Test ---
# IMPORTANT: This assumes 'src.utils.coercion' is importable in your test environment.
# Ensure your PYTHONPATH is configured correctly or run pytest from your project root.
from src.utils.coercion import (
    coerce_numeric, coerce_boolean, coerce_string,
    safe_float, safe_int, relaxed_cast, relaxed_equals
)
# We still need to import and mock the internal dependencies of coercion.py
from src.rules.config import debug_log
from src.rules.type_compatibility_utils import _is_numeric_str

# --- Mocking Dependencies for Isolated Testing ---
mock_debug_log = MagicMock()

# Simplified mock for _is_numeric_str, assuming its core behavior
def _mock_is_numeric_str(value: Any) -> bool:
    if not isinstance(value, str): return False
    try: float(value.strip()); return True
    except ValueError: return False

# Apply patches globally for the module under test during the test session
patch_debug_log = patch('src.rules.config.debug_log', mock_debug_log)
patch_is_numeric_str = patch('src.rules.type_compatibility_utils._is_numeric_str', _mock_is_numeric_str)

class TestCoercion:
    @pytest.fixture(autouse=True)
    def setup_patches(self):
        """Start and stop patches, and reset mock_debug_log for each test."""
        patch_debug_log.start()
        patch_is_numeric_str.start()
        mock_debug_log.reset_mock()
        yield # Yield control to the test function
        patch_debug_log.stop()
        patch_is_numeric_str.stop()

    # --- Test Cases for coerce_numeric ---
    @pytest.mark.parametrize("value, expected", [
        (10, 10.0), (10.5, 10.5), ("123", 123.0), (" 45.67 ", 45.67),
        ("-5", -5.0), ("0", 0.0), ("", None), ("abc", None),
        ("123a", None), (None, None), ([], None), ({}, None),
        (True, 1.0), (False, 0.0),
    ])
    def test_coerce_numeric(self, value, expected):
        assert coerce_numeric(value) == expected

    # --- Test Cases for coerce_boolean ---
    @pytest.mark.parametrize("value, expected", [
        (True, True), (False, False), ("true", True), ("1", True),
        ("false", False), ("0", False), ("yes", "yes"), ("abc", "abc"),
        ("", ""), (None, "None"), (1, "1"), (0, "0"), (5, "5"),
        ([], "[]"), ({}, "{}"), (" True ", True), (" False ", False),
    ])
    def test_coerce_boolean(self, value, expected):
        assert coerce_boolean(value) == expected

    # --- Test Cases for coerce_string ---
    @pytest.mark.parametrize("value, expected", [
        ("hello", "hello"), ("  world  ", "world"), (123, "123"),
        (123.45, "123.45"), (True, "True"), (False, "False"),
        (None, "None"), ([], "[]"), ({'a': 1}, "{'a': 1}"),
        (math.inf, "inf"), (math.nan, "nan"),
    ])
    def test_coerce_string(self, value, expected):
        assert coerce_string(value) == expected

    # --- Test Cases for safe_float ---
    @pytest.mark.parametrize("value, expected", [
        (10.5, 10.5), (10, 10.0), ("123.45", 123.45), ("-50", -50.0),
        (" 7.89 ", 7.89), (True, 1.0), (False, 0.0), (None, None),
        ([], None), ({}, None), ((), None), (set(), None),
        ("abc", None), ("1.2.3", None),
        (math.inf, None), (-math.inf, None), (math.nan, None), # Non-finite values
        ("inf", None), ("-inf", None), ("nan", None), # String representations of non-finite
    ])
    def test_safe_float(self, value, expected):
        assert safe_float(value) == expected

    # --- Test Cases for safe_int ---
    @pytest.mark.parametrize("value, expected", [
        (10, 10), ("123", 123), ("-50", -50), (" 7 ", 7),
        (10.0, 10), ("10.0", 10), (True, 1), (False, 0),
        (None, None), ([], None), ({}, None), ("abc", None),
        ("10.5", None), (10.5, None), (math.inf, None), (math.nan, None),
    ])
    def test_safe_int(self, value, expected):
        assert safe_int(value) == expected

    # --- Test Cases for relaxed_cast ---
    @pytest.mark.parametrize("value, target_type, expected", [
        # To bool
        (True, bool, True), (False, bool, False), ("true", bool, True), ("1", bool, True),
        ("false", bool, False), ("0", bool, False), ("yes", bool, None), (1, bool, True),
        (0, bool, False), (None, bool, None), ([], bool, None),
        # To int
        (10, int, 10), ("123", int, 123), (" 45 ", int, 45), (10.0, int, 10),
        ("10.0", int, 10), (10.5, int, None), ("10.5", int, None), (True, int, 1),
        (False, int, 0), ("abc", int, None), (None, int, None), ([], int, None),
        # To float
        (10.5, float, 10.5), (10, float, 10.0), ("123.45", float, 123.45), (" 67.8 ", float, 67.8),
        (True, float, 1.0), (False, float, 0.0), ("abc", float, None), (None, float, None),
        ([], float, None), (math.inf, float, None), ("inf", float, None),
        # To str
        ("hello", str, "hello"), (123, str, "123"), (True, str, "True"), (None, str, "None"),
    ])
    def test_relaxed_cast(self, value, target_type, expected):
        assert relaxed_cast(value, target_type) == expected

    # --- Test Cases for relaxed_equals ---
    @pytest.mark.parametrize("lhs, rhs, expected", [
        # Numeric equality
        (1, 1, True), (1, 2, False), (1, "1", True), ("1", 1.0, True),
        (1.0, "1.0", True), (1.23, "1.23", True), ("1.23", 1.23, True),
        (10, "10.0", True), ("10.0", 10, True), (0, False, True),
        (False, 0, True), (1, True, True), (True, 1, True),
        # Boolean equality
        (True, True, True), (False, False, True), (True, False, False),
        ("true", True, True), ("false", False, True), ("1", True, True),
        ("0", False, True), ("TRUE", "true", True), ("FALSE", "false", True),
        # String equality (after other coercions fail)
        ("hello", "hello", True), ("hello", "world", False), ("1", "2", False),
        ("abc", "abc", True), ("abc", "def", False),
        # Mixed types, no match
        ("hello", 123, False), (True, "abc", False), (None, 0, False),
        (None, False, False), (None, "None", True), ("None", None, True),
        # Edge cases: NaN, Inf (explicitly rejected by relaxed_equals or safe_float/int)
        ("nan", 1, False), (1, "nan", False), ("not_a_number", 5, False),
        (5, "not_a_number", False), (math.nan, math.nan, False),
        (math.inf, math.inf, False), ("inf", "inf", True), ("inf", math.inf, False),
        # Empty strings and spaces
        ("", "", True), (" ", "", False), (" ", " ", True), ("  ", " ", True),
        ("  1  ", "1", True), ("  True  ", "true", True),
    ])
    def test_relaxed_equals(self, lhs, rhs, expected):
        assert relaxed_equals(lhs, rhs) == expected



