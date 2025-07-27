# tests/test_domain_constraints.py

import pytest
from src.domain_definition_writer import validate_domain_bounds, DomainValidationError


def test_valid_domain_bounds():
    domain = {
        "min_x": 0.0, "max_x": 1.0,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0
    }
    # Should not raise
    validate_domain_bounds(domain)


@pytest.mark.parametrize("axis, min_val, max_val", [
    ("x", 1.0, 0.5),
    ("y", 2.0, 1.0),
    ("z", 10.0, 5.0)
])
def test_invalid_bounds_trigger_exception(axis, min_val, max_val):
    domain = {
        f"min_{axis}": min_val,
        f"max_{axis}": max_val,
        # include valid placeholders for other axes
        "min_x": 0.0, "max_x": 1.0,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0
    }
    # Patch in bad axis values
    domain[f"min_{axis}"] = min_val
    domain[f"max_{axis}"] = max_val

    with pytest.raises(DomainValidationError) as exc:
        validate_domain_bounds(domain)
    assert axis in str(exc.value)


@pytest.mark.parametrize("missing_key", [
    "min_x", "max_x", "min_y", "max_y", "min_z", "max_z"
])
def test_missing_keys_raise_exception(missing_key):
    domain = {
        "min_x": 0.0, "max_x": 1.0,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0
    }
    domain.pop(missing_key)

    with pytest.raises(DomainValidationError) as exc:
        validate_domain_bounds(domain)
    assert missing_key in str(exc.value)



