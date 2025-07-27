import pytest
import json
from jsonschema import validate, ValidationError
from pathlib import Path

# 📍 Define schema load path
SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "domain_schema.json"

def load_schema():
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)

@pytest.fixture(scope="module")
def domain_schema():
    return load_schema()

def test_payload_matches_schema(domain_schema):
    payload = {
        "domain_definition": {
            "min_x": 0.0, "max_x": 3.0,
            "min_y": 0.0, "max_y": 1.0,
            "min_z": 0.0, "max_z": 1.0,
            "nx": 3, "ny": 2, "nz": 1
        }
    }

    # Should validate without error
    validate(instance=payload, schema=domain_schema)

@pytest.mark.parametrize("key", [
    "min_x", "max_x", "min_y", "max_y", "min_z", "max_z", "nx", "ny", "nz"
])
def test_missing_keys_trigger_validation_error(domain_schema, key):
    domain = {
        "min_x": 0.0, "max_x": 3.0,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0,
        "nx": 3, "ny": 2, "nz": 1
    }
    domain.pop(key)
    payload = { "domain_definition": domain }

    with pytest.raises(ValidationError) as exc:
        validate(instance=payload, schema=domain_schema)
    assert key in str(exc.value)

def test_flat_payload_structure_rejected(domain_schema):
    # Domain values provided at root level — should fail
    flat_payload = {
        "min_x": 0.0, "max_x": 3.0,
        "min_y": 0.0, "max_y": 1.0,
        "min_z": 0.0, "max_z": 1.0,
        "nx": 3, "ny": 2, "nz": 1
    }

    with pytest.raises(ValidationError):
        validate(instance=flat_payload, schema=domain_schema)

def test_extra_properties_rejected(domain_schema):
    payload = {
        "domain_definition": {
            "min_x": 0.0, "max_x": 3.0,
            "min_y": 0.0, "max_y": 1.0,
            "min_z": 0.0, "max_z": 1.0,
            "nx": 3, "ny": 2, "nz": 1,
            "extra": 99  # 🚫 not allowed
        }
    }

    with pytest.raises(ValidationError):
        validate(instance=payload, schema=domain_schema)



