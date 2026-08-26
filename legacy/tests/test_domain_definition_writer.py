# tests/test_domain_definition_writer.py

import pytest
from src.domain_definition_writer import validate_domain_bounds, DomainValidationError

# ✅ Valid domain should pass
def test_valid_domain_bounds():
    domain = {
        "min_x": 0.0, "max_x": 1.0,
        "min_y": -1.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 5.0
    }
    validate_domain_bounds(domain)  # Should not raise

# ❌ Missing keys
@pytest.mark.parametrize("missing_key", [
    "min_x", "max_x", "min_y", "max_y", "min_z", "max_z"
])
def test_missing_keys(missing_key):
    domain = {
        "min_x": 0.0, "max_x": 1.0,
        "min_y": -1.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 5.0
    }
    domain.pop(missing_key)
    with pytest.raises(DomainValidationError) as exc:
        validate_domain_bounds(domain)
    assert f"Missing domain bounds for axis" in str(exc.value)

# ❌ Non-numeric values and missing detection
@pytest.mark.parametrize("bad_value,expected_message", [
    ("abc", "Non-numeric bounds for axis 'x'"),
    (None, "Missing domain bounds for axis 'x'"),
    ({}, "Non-numeric bounds for axis 'x'"),
    ([], "Non-numeric bounds for axis 'x'")
])
def test_non_numeric_bounds(bad_value, expected_message):
    domain = {
        "min_x": bad_value, "max_x": 1.0,
        "min_y": -1.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 5.0
    }
    with pytest.raises(DomainValidationError) as exc:
        validate_domain_bounds(domain)
    assert expected_message in str(exc.value)

# ❌ Logical inconsistency: max < min
def test_max_less_than_min():
    domain = {
        "min_x": 5.0, "max_x": 2.0,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0
    }
    with pytest.raises(DomainValidationError) as exc:
        validate_domain_bounds(domain)
    assert "Invalid domain: max_x (2.0) < min_x (5.0)" in str(exc.value)

# ✅ String-castable numeric values should pass
def test_string_castable_values():
    domain = {
        "min_x": "0.0", "max_x": "1.0",
        "min_y": "-1.0", "max_y": "1.0",
        "min_z": "0.0", "max_z": "5.0"
    }
    validate_domain_bounds(domain)  # Should not raise

# ❌ Performance guard: extremely large values
def test_extreme_values():
    domain = {
        "min_x": -1e308, "max_x": 1e308,
        "min_y": -1e308, "max_y": 1e308,
        "min_z": -1e308, "max_z": 1e308
    }
    validate_domain_bounds(domain)  # Should not raise (but test performance edge)

# ❌ Performance guard: extremely small delta
def test_near_zero_delta():
    domain = {
        "min_x": 1.0000001, "max_x": 1.0000002,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0
    }
    validate_domain_bounds(domain)  # Should not raise




