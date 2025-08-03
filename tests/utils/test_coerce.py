# tests/utils/test_coerce.py

import unittest
from src.utils.coercion import coerce_numeric, coerce_boolean, coerce_string, relaxed_equals


class TestCoerceNumeric(unittest.TestCase):

    def test_valid_float_string(self):
        self.assertEqual(coerce_numeric("3.14"), 3.14)

    def test_valid_integer_string(self):
        self.assertEqual(coerce_numeric("42"), 42.0)

    def test_negative_float_string(self):
        self.assertEqual(coerce_numeric("-2.5"), -2.5)

    def test_negative_integer_string(self):
        self.assertEqual(coerce_numeric("-10"), -10.0)

    def test_string_with_spaces(self):
        self.assertEqual(coerce_numeric("  7.0  "), 7.0)

    def test_leading_zeros(self):
        self.assertEqual(coerce_numeric("000123"), 123.0)

    def test_non_numeric_string(self):
        self.assertIsNone(coerce_numeric("not_a_number"))

    def test_empty_string(self):
        self.assertIsNone(coerce_numeric(""))

    def test_none_input(self):
        self.assertIsNone(coerce_numeric(None))

    def test_boolean_true(self):
        self.assertEqual(coerce_numeric(True), 1.0)

    def test_boolean_false(self):
        self.assertEqual(coerce_numeric(False), 0.0)

    def test_float_input(self):
        self.assertEqual(coerce_numeric(8.9), 8.9)

    def test_int_input(self):
        self.assertEqual(coerce_numeric(100), 100.0)

    def test_list_input(self):
        self.assertIsNone(coerce_numeric([1, 2]))

    def test_dict_input(self):
        self.assertIsNone(coerce_numeric({"x": 5}))

    def test_numeric_string_with_suffix(self):
        self.assertIsNone(coerce_numeric("10kg"))

    def test_scientific_notation(self):
        self.assertEqual(coerce_numeric("1e3"), 1000.0)

    def test_overflow_value(self):
        self.assertIsNone(coerce_numeric("1e1000"))  # ✅ Updated: inf should yield None

    # ✅ NEW: Relaxed equality behavior with malformed inputs
    def test_relaxed_equals_nan_behavior(self):
        self.assertFalse(relaxed_equals("not_a_number", 0))
        self.assertFalse(relaxed_equals("NaN", 42))
        self.assertTrue(relaxed_equals("false", False))
        self.assertFalse(relaxed_equals("false", True))


class TestCoerceBoolean(unittest.TestCase):

    def test_boolean_true_string(self):
        self.assertEqual(coerce_boolean("true"), True)

    def test_boolean_false_string(self):
        self.assertEqual(coerce_boolean("false"), False)

    def test_numeric_truthy(self):
        self.assertEqual(coerce_boolean("1"), True)
        self.assertEqual(coerce_boolean("0"), False)

    def test_unrecognized_string(self):
        self.assertEqual(coerce_boolean("maybe"), "maybe")

    def test_none_input(self):
        self.assertIsNone(coerce_boolean(None))

    def test_bad_str_object(self):
        class BadStr:
            def __str__(self): raise ValueError("bad")

        self.assertIsNone(coerce_boolean(BadStr()))  # ✅ Updated: should recover safely


class TestCoerceString(unittest.TestCase):

    def test_basic_string(self):
        self.assertEqual(coerce_string("hello"), "hello")

    def test_trimmed_string(self):
        self.assertEqual(coerce_string("  spaced  "), "spaced")

    def test_int_input(self):
        self.assertEqual(coerce_string(123), "123")

    def test_none_input(self):
        self.assertEqual(coerce_string(None), "None")  # ✅ Defensive fallback preserved

    def test_bad_str_object(self):
        class Bad:
            def __str__(self): raise ValueError("fail")

        self.assertEqual(coerce_string(Bad()), "")  # ✅ Updated: fallback to empty string




