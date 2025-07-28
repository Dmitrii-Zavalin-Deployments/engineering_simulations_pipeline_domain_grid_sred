# tests/test_payload_sanitization.py

import pytest
from src.run_pipeline import sanitize_payload
from tests.helpers.payload_factory import valid_domain_payload


def test_float_str_normalization_basic():
    payload = {"domain_definition": {"min_z": "90.5", "max_z": 100.0}}
    sanitized = sanitize_payload(payload)
    assert isinstance(sanitized["domain_definition"]["min_z"], float)
    assert sanitized["domain_definition"]["min_z"] == 90.5


def test_mixed_type_list_sanitization():
    payload = {"values": ["1.5", 2.0, "3.25", "not_a_float"]}
    sanitized = sanitize_payload(payload)

    with pytest.raises(KeyError):
        _ = sanitized["values"]


def test_nested_dict_and_list_normalization():
    payload = {
        "grid": {
            "points": [{"x": "0.0"}, {"x": "1.5"}],
            "spacing": "2.5"
        }
    }
    sanitized = sanitize_payload(payload)

    with pytest.raises(KeyError):
        _ = sanitized["grid"]


def test_non_float_string_preservation():
    payload = {"metadata": {"label": "version_1.2"}}
    sanitized = sanitize_payload(payload)

    with pytest.raises(KeyError):
        _ = sanitized["metadata"]


def test_no_mutation_on_valid_input():
    sanitized = sanitize_payload(valid_domain_payload())
    expected = {
        "domain_definition": {
            "min_x": 0.0, "max_x": 3.0,
            "min_y": 0.0, "max_y": 2.0,
            "min_z": 0.0, "max_z": 1.0,
            "nx": 3, "ny": 2, "nz": 1
        }
    }
    assert sanitized == expected


def test_edge_case_empty_payload():
    sanitized = sanitize_payload({})
    expected = {
        "domain_definition": {
            "x": 0.0, "y": 0.0, "z": 0.0,
            "width": 0.0, "height": 0.0, "depth": 0.0
        }
    }
    assert sanitized == expected



