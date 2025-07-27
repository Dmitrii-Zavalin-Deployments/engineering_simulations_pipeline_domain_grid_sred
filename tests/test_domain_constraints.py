import pytest
from src.domain_definition_writer import validate_domain_bounds, DomainValidationError


def test_valid_domain_bounds():
    metadata = {
        "domain_definition": {
            "min_x": 0.0, "max_x": 1.0,
            "min_y": 0.0, "max_y": 1.0,
            "min_z": 0.0, "max_z": 1.0
        }
    }
    validate_domain_bounds(metadata["domain_definition"])  # Should not raise


@pytest.mark.parametrize("axis, min_val, max_val", [
    ("x", 1.0, 0.5),
    ("y", 2.0, 1.0),
    ("z", 10.0, 5.0)
])
def test_invalid_bounds_trigger_exception(axis, min_val, max_val):
    domain_definition = {
        "min_x": 0.0, "max_x": 1.0,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0
    }

    domain_definition[f"min_{axis}"] = min_val
    domain_definition[f"max_{axis}"] = max_val

    metadata = {"domain_definition": domain_definition}

    with pytest.raises(DomainValidationError) as exc:
        validate_domain_bounds(metadata["domain_definition"])
    assert axis in str(exc.value)


@pytest.mark.parametrize("missing_key", [
    "min_x", "max_x", "min_y", "max_y", "min_z", "max_z"
])
def test_missing_keys_raise_exception(missing_key):
    domain_definition = {
        "min_x": 0.0, "max_x": 1.0,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0
    }
    domain_definition.pop(missing_key)

    metadata = {"domain_definition": domain_definition}

    with pytest.raises(DomainValidationError) as exc:
        validate_domain_bounds(metadata["domain_definition"])
    assert missing_key in str(exc.value)



