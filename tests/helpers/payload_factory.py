# tests/helpers/payload_factory.py

"""
Payload factory fixtures for domain sanitizer tests.

These are raw input payloads meant to test pre-sanitization behavior.
They intentionally include legacy keys (e.g. min_x, nx) and malformed values
to validate sanitizer robustness and fallback logic.
"""

def valid_domain_payload():
    """Structured geometry definition using legacy keys, before sanitization."""
    return {
        "domain_definition": {
            "min_x": 0.0, "max_x": 3.0,
            "min_y": 0.0, "max_y": 2.0,
            "min_z": 0.0, "max_z": 1.0,
            "nx": 3, "ny": 2, "nz": 1
        }
    }

def empty_domain_payload():
    """Edge case: empty domain section — sanitizer should inject defaults."""
    return {
        "domain_definition": {}
    }

def non_numeric_domain_payload():
    """Invalid values simulating corrupted or misconfigured input."""
    return {
        "domain_definition": {
            "min_x": "left", "max_x": "right",
            "min_y": None, "max_y": True,
            "min_z": [], "max_z": {}
        }
    }

def mixed_schema_payload():
    """Combines stringified floats, incorrect types, and extra metadata."""
    return {
        "domain_definition": {
            "min_x": "0.0", "max_x": 3.0,
            "min_y": 0.0, "max_y": "2.0",
            "min_z": "invalid_float", "max_z": 1.0
        },
        "extra": {
            "notes": "spatial context",
            "version": "1.0.3"
        }
    }



