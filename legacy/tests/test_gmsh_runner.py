# tests/test_gmsh_runner.py

import pytest
import json
import os
from src.gmsh_runner import compute_resolution, round2, extract_domain_definition, load_schema, SCHEMA_PATH
from jsonschema import validate, ValidationError

# ✅ Resolution logic
def test_compute_resolution_basic():
    assert compute_resolution(0.0, 10.0, 1.0) == 10
    assert compute_resolution(0.0, 10.0, 0.5) == 20
    assert compute_resolution(0.0, 0.1, 0.2) == 1  # Enforces minimum of 1

# ✅ Rounding logic
@pytest.mark.parametrize("value,expected", [
    (1.2345, 1.23),
    (1.2399, 1.24),
    (-0.005, -0.01),
    (0.0, 0.0)
])
def test_round2(value, expected):
    assert round2(value) == expected

# ✅ Schema loading
def test_load_schema_success():
    schema = load_schema(SCHEMA_PATH)
    assert isinstance(schema, dict)
    assert "type" in schema

def test_load_schema_missing(tmp_path):
    fake_path = tmp_path / "missing_schema.json"
    with pytest.raises(FileNotFoundError):
        load_schema(str(fake_path))

# ✅ Domain extraction (mocked)
@pytest.mark.skip(reason="Requires Gmsh and STEP file — covered by integration tests")
def test_extract_domain_definition_real_file():
    # This test is covered in integration tests with actual STEP files
    pass

# ✅ Schema validation on known good domain
def test_schema_validation_passes():
    schema = load_schema(SCHEMA_PATH)
    domain = {
        "domain_definition": {
            "min_x": 0.0, "max_x": 1.0,
            "min_y": 0.0, "max_y": 1.0,
            "min_z": 0.0, "max_z": 1.0,
            "nx": 10, "ny": 10, "nz": 10
        }
    }
    validate(instance=domain, schema=schema)

# ❌ Schema validation fails on missing keys
def test_schema_validation_fails_missing_key():
    schema = load_schema(SCHEMA_PATH)
    domain = {
        "domain_definition": {
            "min_x": 0.0, "max_x": 1.0,
            "min_y": 0.0, "max_y": 1.0,
            "nx": 10, "ny": 10, "nz": 10  # Missing z bounds
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=domain, schema=schema)

# ❌ Schema validation fails on wrong types
def test_schema_validation_fails_wrong_type():
    schema = load_schema(SCHEMA_PATH)
    domain = {
        "domain_definition": {
            "min_x": "zero", "max_x": 1.0,
            "min_y": 0.0, "max_y": 1.0,
            "min_z": 0.0, "max_z": 1.0,
            "nx": 10, "ny": 10, "nz": 10
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=domain, schema=schema)

# ✅ Performance guard: large bounds
def test_compute_resolution_large_bounds():
    assert compute_resolution(-1e6, 1e6, 1000) == 2000

# ✅ Performance guard: small delta
def test_compute_resolution_small_delta():
    assert compute_resolution(0.0, 0.0001, 0.00001) == 10

# ✅ CLI entry point is covered by integration tests
@pytest.mark.skip(reason="CLI tested via GitHub Actions integration workflow")
def test_main_cli_entry():
    pass




