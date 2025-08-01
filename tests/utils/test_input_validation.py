# tests/utils/test_input_validation.py

import os
import pytest
import tempfile
import pathlib
from utils.gmsh_input_check import validate_step_has_volumes
from src.utils.input_validation import validate_step_file

# ------------------------------------------------------------------------------------
# 🧪 Volume Validation Tests — validate_step_has_volumes
# ------------------------------------------------------------------------------------

def step_with_volume():
    return { "solids": [ {"id": 101}, {"id": 202} ] }

def step_empty():
    return { "solids": [] }

def test_step_with_volume_passes():
    validate_step_has_volumes(step_with_volume())

def test_step_missing_solids_key_raises():
    invalid = { "shells": [] }
    with pytest.raises(KeyError):
        validate_step_has_volumes(invalid)

def test_step_with_no_volumes_raises():
    with pytest.raises(ValueError):
        validate_step_has_volumes(step_empty())

@pytest.mark.parametrize("bad_input", [None, "step", 42, ["solids"], {"solids": None}])
def test_invalid_step_types_raise_typeerror(bad_input):
    with pytest.raises(TypeError):
        validate_step_has_volumes(bad_input)

def test_volume_validator_runtime_safe():
    import time
    start = time.time()
    validate_step_has_volumes(step_with_volume())
    assert time.time() - start < 0.2

# ------------------------------------------------------------------------------------
# 🧪 STEP File Path Validation Tests — validate_step_file
# ------------------------------------------------------------------------------------

@pytest.mark.parametrize("invalid_input", [42, {}, None, [], set(), object()])
def test_invalid_step_types_raise_typeerror_or_file_not_found(invalid_input):
    with pytest.raises((TypeError, FileNotFoundError)):
        validate_step_file(invalid_input)

@pytest.mark.parametrize("bad_path", ["nonexistent.step", "/fake/dir/file.step"])
def test_nonexistent_file_raises_file_not_found(bad_path):
    with pytest.raises(FileNotFoundError):
        validate_step_file(bad_path)

def test_valid_step_file_passes():
    with tempfile.NamedTemporaryFile(suffix=".step") as temp_file:
        assert validate_step_file(temp_file.name)

def test_valid_pathlike_step_file_passes():
    with tempfile.NamedTemporaryFile(suffix=".step") as temp_file:
        path_obj = pathlib.Path(temp_file.name)
        assert validate_step_file(path_obj)

def test_non_step_extension_still_passes_if_file_exists():
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        assert validate_step_file(temp_file.name)



