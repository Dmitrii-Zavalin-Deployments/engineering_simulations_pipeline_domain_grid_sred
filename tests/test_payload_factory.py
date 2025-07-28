# tests/test_payload_factory.py

import pytest
from src.run_pipeline import sanitize_payload
from tests.helpers.payload_factory import (
    valid_domain_payload,
    empty_domain_payload,
    non_numeric_domain_payload,
    mixed_schema_payload
)


def test_valid_domain_payload_sanitization():
    payload = valid_domain_payload()
    sanitized = sanitize_payload(payload)
    assert isinstance(sanitized["domain_definition"]["min_x"], float)
    assert sanitized["domain_definition"]["max_z"] == 1.0


def test_empty_domain_payload_fallback():
    payload = empty_domain_payload()
    sanitized = sanitize_payload(payload)
    assert all(k in sanitized["domain_definition"] for k in [
        "x", "y", "z", "width", "height", "depth"
    ])
    assert all(isinstance(v, float) for v in sanitized["domain_definition"].values())


def test_non_numeric_domain_payload_graceful_handling():
    payload = non_numeric_domain_payload()
    sanitized = sanitize_payload(payload)
    assert "domain_definition" in sanitized
    # Invalid values should fallback or be excluded safely
    assert isinstance(sanitized["domain_definition"], dict)


def test_mixed_schema_payload_sanitization():
    payload = mixed_schema_payload()
    sanitized = sanitize_payload(payload)

    assert "domain_definition" in sanitized
    assert isinstance(sanitized["domain_definition"]["min_x"], float)
    assert isinstance(sanitized["domain_definition"]["max_y"], float)
    assert sanitized["domain_definition"]["min_z"] == "invalid_float"  # Preserved as-is

    assert "extra" not in sanitized  # Outside schema scope



