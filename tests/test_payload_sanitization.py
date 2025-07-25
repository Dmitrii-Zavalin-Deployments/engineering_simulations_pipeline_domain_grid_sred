# tests/test_payload_sanitization.py

import pytest
from src.run_pipeline import sanitize_payload


def test_float_str_normalization_basic():
    payload = {"domain_definition": {"min_z": "90.5", "max_z": 100.0}}
    sanitized = sanitize_payload(payload)
    assert isinstance(sanitized["domain_definition"]["min_z"], float)
    assert sanitized["domain_definition"]["min_z"] == 90.5


def test_mixed_type_list_sanitization():
    payload = {"values": ["1.5", 2.0, "3.25", "not_a_float"]}
    sanitized = sanitize_payload(payload)
    assert sanitized["values"][0] == 1.5
    assert sanitized["values"][2] == 3.25
    assert sanitized["values"][3] == "not_a_float"


def test_nested_dict_and_list_normalization():
    payload = {
        "grid": {
            "points": [{"x": "0.0"}, {"x": "1.5"}],
            "spacing": "2.5"
        }
    }
    sanitized = sanitize_payload(payload)
    assert isinstance(sanitized["grid"]["spacing"], float)
    assert isinstance(sanitized["grid"]["points"][0]["x"], float)
    assert sanitized["grid"]["points"][1]["x"] == 1.5


def test_non_float_string_preservation():
    payload = {"metadata": {"label": "version_1.2"}}
    sanitized = sanitize_payload(payload)
    assert sanitized["metadata"]["label"] == "version_1.2"


def test_no_mutation_on_valid_input():
    original = {"domain": {"x": 1.0, "y": 2.0}}
    sanitized = sanitize_payload(original)
    assert sanitized == original


def test_edge_case_empty_payload():
    sanitized = sanitize_payload({})
    assert sanitized == {}



