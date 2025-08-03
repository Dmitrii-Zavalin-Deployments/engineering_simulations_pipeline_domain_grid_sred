# tests/test_pipeline_payload.py

import unittest
from unittest.mock import patch
from src.run_pipeline import sanitize_payload
from src.utils.coercion import coerce_numeric


class TestSanitizePayload(unittest.TestCase):
    def test_complete_domain(self):
        raw = {"domain_definition": {"x": "1", "y": "2", "z": "3", "width": "4", "height": "5", "depth": "6"}}
        expected = {
            "domain_definition": {
                "x": 1.0, "y": 2.0, "z": 3.0,
                "width": 4.0, "height": 5.0, "depth": 6.0
            }
        }
        self.assertEqual(sanitize_payload(raw), expected)

    def test_missing_fields(self):
        raw = {"domain_definition": {"x": "1"}}
        expected = {
            "domain_definition": {
                "x": 1.0, "y": 0.0, "z": 0.0,
                "width": 0.0, "height": 0.0, "depth": 0.0
            }
        }
        self.assertEqual(sanitize_payload(raw), expected)

    def test_empty_metadata(self):
        expected = {
            "domain_definition": {
                "x": 0.0, "y": 0.0, "z": 0.0,
                "width": 0.0, "height": 0.0, "depth": 0.0
            }
        }
        self.assertEqual(sanitize_payload({}), expected)

    def test_width_clamping_on_misaligned_bounds(self):
        raw = {"domain_definition": {"min_x": "1.0", "max_x": "0.0"}}
        domain = sanitize_payload(raw)["domain_definition"]
        self.assertEqual(coerce_numeric(domain["width"]), 0.0)

    def test_fallback_on_invalid_width(self):
        raw = {"domain_definition": {"x": "1", "max_x": "5", "width": "invalid"}}
        domain = sanitize_payload(raw)["domain_definition"]
        self.assertEqual(domain["width"], 4.0)

    @patch("src.run_pipeline.coerce_numeric", side_effect=lambda val: None if val == "invalid" else float(val))
    def test_mocked_coercion_fallback(self, mock_coerce):
        raw = {
            "domain_definition": {
                "x": "1", "y": "0", "z": "0",
                "width": "invalid", "max_x": "5",
                "height": "0", "depth": "0"
            }
        }
        domain = sanitize_payload(raw)["domain_definition"]
        self.assertEqual(domain["width"], 4.0)
        mock_coerce.assert_any_call("invalid")



