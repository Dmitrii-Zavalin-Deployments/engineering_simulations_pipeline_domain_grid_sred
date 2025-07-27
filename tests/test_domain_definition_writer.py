# tests/test_domain_definition_writer.py

import pytest
from src.domain_definition_writer import validate_domain_bounds, DomainValidationError


def test_valid_domain_bounds():
    domain = {
        "min_x": 0.0, "max_x": 1.0,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0
    }
    validate_domain_bounds(domain)  # Should pass silently


@pytest.mark.parametrize("axis, min_val, max_val", [
    ("x", 5.0, 1.0),
    ("y", 2.0, 1.5),
    ("z", 10.0, 0.0),
])
def test_invalid_bounds_trigger_exception(axis, min_val, max_val):
    domain = {
        "min_x": 0.0, "max_x": 1.0,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0
    }
    domain[f"min_{axis}"] = min_val
    domain[f"max_{axis}"] = max_val

    with pytest.raises(DomainValidationError) as exc:
        validate_domain_bounds(domain)
    assert axis in str(exc.value)


@pytest.mark.parametrize("missing_key", [
    "min_x", "max_x", "min_y", "max_y", "min_z", "max_z"
])
def test_missing_keys_trigger_exception(missing_key):
    domain = {
        "min_x": 0.0, "max_x": 1.0,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0
    }
    domain.pop(missing_key)

    with pytest.raises(DomainValidationError) as exc:
        validate_domain_bounds(domain)
    assert missing_key in str(exc.value)


def test_non_numeric_values_are_invalid():
    domain = {
        "min_x": "zero", "max_x": 5.0,
        "min_y": 0.0, "max_y": "five",
        "min_z": None, "max_z": 3.0
    }
    with pytest.raises(DomainValidationError):
        validate_domain_bounds(domain)


def test_extremely_large_float_bounds():
    domain = {
        "min_x": -1e300, "max_x": 1e300,
        "min_y": -1e-12, "max_y": 1e-12,
        "min_z": 0.0, "max_z": 1.0
    }
    validate_domain_bounds(domain)  # Should pass



