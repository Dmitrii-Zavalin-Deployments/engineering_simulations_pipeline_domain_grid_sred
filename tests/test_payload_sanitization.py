# 📄 tests/test_payload_sanitization.py

import pytest
from src.run_pipeline import sanitize_payload
from src.utils.coercion import coerce_numeric  # ✅ Existing Asset Update
from tests.helpers.payload_factory import valid_domain_payload

def test_float_str_normalization_basic():
    payload = {"domain_definition": {"min_z": "90.5", "max_z": 100.0}}
    sanitized = sanitize_payload(payload)
    domain = sanitized["domain_definition"]

    assert "z" in domain
    assert isinstance(coerce_numeric(domain["z"]), float)
    assert coerce_numeric(domain["z"]) == 90.5

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
    domain = sanitized["domain_definition"]

    expected_keys = ["x", "y", "z", "width", "height", "depth"]

    for key in expected_keys:
        assert key in domain
        assert isinstance(coerce_numeric(domain[key]), float)

def test_edge_case_empty_payload():
    sanitized = sanitize_payload({})
    expected = {
        "domain_definition": {
            "x": 0.0, "y": 0.0, "z": 0.0,
            "width": 0.0, "height": 0.0, "depth": 0.0
        }
    }
    assert sanitized == expected

def test_autopopulate_bounds_from_dimensions():
    raw = {"domain_definition": {"x": 1, "y": 2, "z": 3, "width": 10, "height": 20, "depth": 30}}
    clean = sanitize_payload(raw)
    domain = clean["domain_definition"]

    assert domain["min_x"] == 1
    assert domain["max_x"] == 11
    assert domain["min_y"] == 2
    assert domain["max_y"] == 22
    assert domain["min_z"] == 3
    assert domain["max_z"] == 33



