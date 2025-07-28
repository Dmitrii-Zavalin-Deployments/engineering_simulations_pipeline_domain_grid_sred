# tests/test_payload_factory.py

import pytest
from src.run_pipeline import sanitize_payload
from tests.helpers.payload_factory import (
    valid_domain_payload,
    empty_domain_payload,
    non_numeric_domain_payload,
    mixed_schema_payload
)

EXPECTED_KEYS = ["x", "y", "z", "width", "height", "depth"]

def test_valid_domain_payload_sanitization():
    payload = valid_domain_payload()
    sanitized = sanitize_payload(payload)
    domain = sanitized["domain_definition"]

    for key in EXPECTED_KEYS:
        assert key in domain, f"Missing key: {key}"
        assert isinstance(domain[key], float), f"{key} should be float"

def test_empty_domain_payload_fallback():
    payload = empty_domain_payload()
    sanitized = sanitize_payload(payload)
    domain = sanitized["domain_definition"]

    for key in EXPECTED_KEYS:
        assert key in domain
        assert isinstance(domain[key], float)

def test_non_numeric_domain_payload_graceful_handling():
    payload = non_numeric_domain_payload()
    sanitized = sanitize_payload(payload)
    domain = sanitized.get("domain_definition")

    assert isinstance(domain, dict)
    for key in EXPECTED_KEYS:
        assert key in domain
        assert isinstance(domain[key], float)

def test_mixed_schema_payload_sanitization():
    payload = mixed_schema_payload()
    sanitized = sanitize_payload(payload)
    domain = sanitized["domain_definition"]

    # Assert legacy keys were dropped and normalized keys preserved
    for key in EXPECTED_KEYS:
        assert key in domain
        assert isinstance(domain[key], float)

    # Assert no unexpected fields leaked in
    unexpected_keys = ["min_x", "max_y", "min_z", "extra"]
    for key in unexpected_keys:
        assert key not in domain



