# tests/conftest.py

import sys
import pathlib
import pytest
import gmsh

# Adds src/ directory to sys.path for all tests
SRC_PATH = pathlib.Path(__file__).resolve().parents[1] / "src"
if SRC_PATH.exists():
    sys.path.insert(0, str(SRC_PATH))


@pytest.fixture(scope="function")
def gmsh_session():
    """
    Provides an initialized and finalized Gmsh session around each test.

    Usage:
        def test_something(gmsh_session):
            # Gmsh is initialized here
            ...
            # Gmsh will finalize automatically after test
    """
    gmsh.initialize()
    yield
    gmsh.finalize()


# 🧪 Utility: Expression Payload Factory
def get_payload_with_defaults(overrides=None):
    """
    Generates a baseline payload structure with common default keys and values,
    optionally overridden for edge-case expression tests.

    Parameters:
        overrides (dict): Dictionary of values to override or inject into the default payload.

    Returns:
        dict: Merged payload structure suitable for expression-based validation.
    """
    base = {
        "hello": "world",
        "flag": True,
        "thresholds": {"warn_val": 150, "max_val": 150},
        "limits": {"upper": 10.0, "lower": 5.0},
        "metrics": {"score": 0.3},
        "values": {"x": 5},
        "system": {"subsystem": {"value": 42}},
        "expected": {"value": 42},
        "config": {"enabled": "true"},
        "domain_definition": {"max_z": 100.0, "min_z": 90.5},
        "a": {"b": 10},
        "x": {"y": 10},
        "rules": {"status_code": "not_a_number", "expected_code": 200},
    }

    if overrides:
        for key, value in overrides.items():
            # ✅ Defensive check: ensure override types match expected dict structure
            if key in base and isinstance(base[key], dict):
                if isinstance(value, dict):
                    base[key].update(value)
                else:
                    raise TypeError(f"Override for '{key}' must be a dict, got {type(value)}")
            else:
                base[key] = value
    return base



