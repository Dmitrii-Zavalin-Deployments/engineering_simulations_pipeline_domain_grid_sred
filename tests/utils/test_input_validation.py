# tests/utils/test_input_validation.py

import os
import pytest
import tempfile
import pathlib
from unittest.mock import patch
import src.utils.input_validation as iv
from utils.gmsh_input_check import validate_step_has_volumes


# ------------------------------------------------------------------------------------
# 🧪 Volume Validation Tests — validate_step_has_volumes
# ------------------------------------------------------------------------------------

def step_with_volume():
    return { "solids": [ {"id": 101}, {"id": 202} ] }

def step_empty():
    return { "solids": [] }


@patch("os.path.isfile", return_value=True)
@patch("src.utils.input_validation.validate_step_file", return_value=True)
def test_step_with_volume_passes(mock_validate_file, mock_isfile, mock_gmsh_volume):
    with mock_gmsh_volume:
        validate_step_has_volumes(step_with_volume())


@patch("os.path.isfile", return_value=True)
@patch("src.utils.input_validation.validate_step_file", return_value=True)
def test_step_missing_solids_key_raises(mock_validate_file, mock_isfile, mock_gmsh_volume):
    invalid = {}  # ❗ Updated to remove "solids" key entirely
    with mock_gmsh_volume:
        with pytest.raises(KeyError):
            validate_step_has_volumes(invalid)


@patch("os.path.isfile", return_value=True)
@patch("src.utils.input_validation.validate_step_file", return_value=True)
def test_step_with_no_volumes_raises(mock_validate_file, mock_isfile):
    with patch("gmsh.open", return_value=None), patch("gmsh.model.getEntities", return_value=[]):
        with pytest.raises(ValueError):
            validate_step_has_volumes(step_empty())


@patch("os.path.isfile", return_value=True)
@patch("src.utils.input_validation.validate_step_file", return_value=True)
@pytest.mark.parametrize("bad_input", [None, "step", 42, ["solids"], {"solids": None}])
def test_invalid_step_types_raise_typeerror_or_file_not_found(mock_validate_file, mock_isfile, mock_gmsh_volume, bad_input):
    with mock_gmsh_volume:
        with pytest.raises((TypeError, FileNotFoundError)):
            validate_step_has_volumes(bad_input)


@patch("os.path.isfile", return_value=True)
@patch("src.utils.input_validation.validate_step_file", return_value=True)
def test_volume_validator_runtime_safe(mock_validate_file, mock_isfile, mock_gmsh_volume):
    import time
    with mock_gmsh_volume:
        start = time.time()
        validate_step_has_volumes(step_with_volume())
        assert time.time() - start < 0.2


# ------------------------------------------------------------------------------------
# 🧪 STEP File Path Validation Tests — validate_step_file
# ------------------------------------------------------------------------------------

@pytest.mark.parametrize("invalid_input", [42, {}, None, [], set(), object()])
def test_invalid_step_types_raise_typeerror_or_file_not_found(invalid_input):
    with pytest.raises((TypeError, FileNotFoundError)):
        iv.validate_step_file(invalid_input)

@pytest.mark.parametrize("bad_path", ["nonexistent.step", "/fake/dir/file.step"])
def test_nonexistent_file_raises_file_not_found(bad_path):
    with pytest.raises(FileNotFoundError):
        iv.validate_step_file(bad_path)

def test_valid_step_file_passes():
    with tempfile.NamedTemporaryFile(suffix=".step") as temp_file:
        assert iv.validate_step_file(temp_file.name)

def test_valid_pathlike_step_file_passes():
    with tempfile.NamedTemporaryFile(suffix=".step") as temp_file:
        path_obj = pathlib.Path(temp_file.name)
        assert iv.validate_step_file(path_obj)

def test_non_step_extension_still_passes_if_file_exists():
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        assert iv.validate_step_file(temp_file.name)


# ------------------------------------------------------------------------------------
# 🧪 Mock Fixture Verification — validate_step_file
# ------------------------------------------------------------------------------------

def test_step_file_validation(mock_validate_step_file):
    result = iv.validate_step_file("fake/path/to/model.step")
    assert result is True
    mock_validate_step_file.assert_called_once()



