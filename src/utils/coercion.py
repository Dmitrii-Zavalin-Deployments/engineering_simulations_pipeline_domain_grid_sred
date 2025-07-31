# tests/utils/test_coercion.py

import pytest
import math
from unittest.mock import patch, MagicMock
from typing import Any

from src.utils.coercion import (
    coerce_numeric, coerce_boolean, coerce_string,
    safe_float, safe_int, relaxed_cast, relaxed_equals
)
from src.rules.config import debug_log
from src.rules.type_compatibility_utils import _is_numeric_str

mock_debug_log = MagicMock()

def _mock_is_numeric_str(value: Any) -> bool:
    if not isinstance(value, str): return False
    try: float(value.strip()); return True
    except ValueError: return False

patch_debug_log = patch('src.rules.config.debug_log', mock_debug_log)
patch_is_numeric_str = patch('src.rules.type_compatibility_utils._is_numeric_str', _mock_is_numeric_str)

class TestCoercionUtils:
    @pytest.fixture(autouse=True)
    def setup_patches(self):
        patch_debug_log.start()
        patch_is_numeric_str.start()
        mock_debug_log.reset_mock()
        yield
        patch_debug_log.stop()
        patch_is_numeric_str.stop()

    # coerce_numeric
    @pytest.mark.parametrize("value, expected", [
        (10, 10.0), (10.5, 10.5), ("123", 123.0), (" 45.67 ", 45.67),
        ("-5", -5.0), ("0", 0.0), ("", None), ("abc", None),
        ("123a", None), (None, None), ([], None), ({}, None),
        (True, 1.0), (False, 0.0),
    ])
    def test_coerce_numeric(self, value, expected):
        assert coerce_numeric(value) == expected

    # coerce_boolean
    @pytest.mark.parametrize("value, expected", [
        (True, True), (False, False), ("true", True), ("1", True),
        ("false", False), ("0", False), ("yes", "yes"), ("abc", "abc"),
        ("", ""), (None, "None"), (1, "1"), (0, "0"),
        ([], "[]"), ({}, "{}"), (" True ", True), (" False ", False),
    ])
    def test_coerce_boolean(self, value, expected):
        assert coerce_boolean(value) == expected

    # coerce_string
    @pytest.mark.parametrize("value, expected", [
        ("hello", "hello"), ("  world  ", "world"), (123, "123"),
        (123.45, "123.45"), (True, "True"), (False, "False"),
        (None, "None"), ([], "[]"), ({'a': 1}, "{'a': 1}"),
        (math.inf, "inf"), (math.nan, "nan"),
    ])
    def test_coerce_string(self, value, expected):
        assert coerce_string(value) == expected

    # safe_float
    @pytest.mark.parametrize("value, expected", [
        (10.5, 10.5), (10, 10.0), ("123.45", 123.45), ("-50", -50.0),
        (" 7.89 ", 7.89), (True, 1.0), (False, 0.0), (None, None),
        ([], None), ({}, None), ((), None), (set(), None),
        ("abc", None), ("1.2.3", None), (math.inf, None), (-math.inf, None), (math.nan, None),
        ("inf", None), ("-inf", None), ("nan", None),
    ])
    def test_safe_float(self, value, expected):
        assert safe_float(value) == expected

    @pytest.mark.parametrize("val", [None, {}, [], object()])
    def test_safe_float_rejects_bad_types(self, val):
        assert safe_float(val) is None

    # safe_int
    @pytest.mark.parametrize("value, expected", [
        (10, 10), ("123", 123), ("-50", -50), (" 7 ", 7),
        (10.0, 10), ("10.0", 10), (True, 1), (False, 0),
        (None, None), ([], None), ({}, None), ("abc", None),
        ("10.5", None), (10.5, None), (math.inf, None), (math.nan, None),
    ])
    def test_safe_int(self, value, expected):
        assert safe_int(value) == expected

    # relaxed_cast
    @pytest.mark.parametrize("value, target_type, expected", [
        (True, bool, True), ("true", bool, True), ("false", bool, False),
        ("1", bool, True), ("0", bool, False), ("yes", bool, None), (None, bool, None),
        (10, int, 10), ("123", int, 123), ("10.5", int, None), ("abc", int, None),
        (10.5, float, 10.5), ("123.45", float, 123.45), ("abc", float, None),
        ("hello", str, "hello"), (123, str, "123"), (None, str, "None"),
    ])
    def test_relaxed_cast(self, value, target_type, expected):
        assert relaxed_cast(value, target_type) == expected

    # relaxed_equals
    @pytest.mark.parametrize("lhs, rhs, expected", [
        (1, "1", True), ("1.0", 1.0, True), ("true", True, True), ("0", False, True),
        ("hello", "hello", True), ("abc", "def", False), (None, "None", True),
        ("nan", 1, False), (1, "nan", False), ("not_a_number", 5, False),
        ("", "", True), (" ", " ", True), ("  1  ", "1", True),
    ])
    def test_relaxed_equals(self, lhs, rhs, expected):
        assert relaxed_equals(lhs, rhs) == expected



