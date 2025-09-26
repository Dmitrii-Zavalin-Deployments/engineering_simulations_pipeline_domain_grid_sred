# tests/test_gmsh_runner.py

import pytest
from unittest.mock import patch, MagicMock
from src.gmsh_runner import extract_bounding_box_with_gmsh
from utils.gmsh_input_check import ValidationError

# 🧪 Success path — simulate valid geometry
@patch("src.gmsh_runner.gmsh")
@patch("os.path.isfile", return_value=True)
@patch("src.gmsh_runner.validate_step_has_volumes")
def test_successful_extraction(mock_validate, mock_isfile, mock_gmsh):
    mock_gmsh.model.getEntities.return_value = [(3, 42)]
    mock_gmsh.model.getBoundingBox.return_value = (0, 0, 0, 1, 1, 1)

    result = extract_bounding_box_with_gmsh("mock.step", resolution=0.1)

    assert result["nx"] == 10
    assert result["ny"] == 10
    assert result["nz"] == 10
    assert result["min_x"] == 0
    assert result["max_z"] == 1
    mock_gmsh.finalize.assert_called_once()

# 📂 Missing file trigger
@patch("os.path.isfile", return_value=False)
def test_missing_file_raises_file_error(mock_isfile):
    with pytest.raises(FileNotFoundError, match="STEP file not found"):
        extract_bounding_box_with_gmsh("missing.step")

# 🧠 Degenerate bounding box
@patch("src.gmsh_runner.gmsh")
@patch("os.path.isfile", return_value=True)
@patch("src.gmsh_runner.validate_step_has_volumes")
def test_empty_volume_raises_value_error(mock_validate, mock_isfile, mock_gmsh):
    mock_gmsh.model.getEntities.return_value = [(3, 7)]
    mock_gmsh.model.getBoundingBox.return_value = (0, 0, 0, 0, 0, 0)

    with pytest.raises(ValueError, match="bounding box has zero size"):
        extract_bounding_box_with_gmsh("degenerate.step")

# ❌ Internal validation failure
@patch("os.path.isfile", return_value=True)
@patch("src.gmsh_runner.gmsh")
@patch("src.gmsh_runner.validate_step_has_volumes", side_effect=ValidationError("No volumes found"))
def test_validation_check_failure_propagates(mock_validate, mock_gmsh, mock_isfile):
    with pytest.raises(ValidationError, match="No volumes found"):
        extract_bounding_box_with_gmsh("invalid.step")

# 🧮 Resolution calculation test
@patch("src.gmsh_runner.gmsh")
@patch("os.path.isfile", return_value=True)
@patch("src.gmsh_runner.validate_step_has_volumes")
def test_resolution_applies_correctly(mock_validate, mock_isfile, mock_gmsh):
    mock_gmsh.model.getEntities.return_value = [(3, 1)]
    mock_gmsh.model.getBoundingBox.return_value = (0.0, 0.0, 0.0, 0.5, 1.0, 1.5)

    result = extract_bounding_box_with_gmsh("geometry.step", resolution=0.25)
    assert result["nx"] == 2
    assert result["ny"] == 4
    assert result["nz"] == 6

# 🧪 Flow region: internal
@patch("src.gmsh_runner.gmsh")
@patch("os.path.isfile", return_value=True)
@patch("src.gmsh_runner.validate_step_has_volumes")
@patch("builtins.open")
def test_internal_flow_region_bounding_box(mock_open, mock_validate, mock_isfile, mock_gmsh):
    # Simulate flow_data.json with "internal"
    mock_open.return_value.__enter__.return_value.read.return_value = '''
    {
        "model_properties": {
            "flow_region": "internal"
        }
    }
    '''

    # Simulate physical groups with internal tags
    mock_gmsh.model.getPhysicalGroups.return_value = [(2, 21), (2, 22), (2, 23)]
    mock_gmsh.model.getPhysicalName.side_effect = lambda dim, tag: {
        21: "inlet", 22: "outlet", 23: "internal"
    }[tag]

    # Simulate bounding boxes for each surface
    mock_gmsh.model.getBoundingBox.side_effect = lambda dim, tag: {
        21: (0, 0, 0, 1, 1, 1),
        22: (1, 1, 1, 2, 2, 2),
        23: (2, 2, 2, 3, 3, 3)
    }[tag]

    result = extract_bounding_box_with_gmsh("internal.step", resolution=0.5)

    assert result["min_x"] == 0
    assert result["max_x"] == 3
    assert result["nx"] == 6  # (3 - 0) / 0.5

# 🧪 Flow region: external fallback
@patch("src.gmsh_runner.gmsh")
@patch("os.path.isfile", return_value=True)
@patch("src.gmsh_runner.validate_step_has_volumes")
@patch("builtins.open", side_effect=FileNotFoundError)
def test_external_flow_region_fallback(mock_open, mock_validate, mock_isfile, mock_gmsh):
    mock_gmsh.model.getEntities.return_value = [(3, 42)]
    mock_gmsh.model.getBoundingBox.return_value = (0, 0, 0, 1, 2, 3)

    result = extract_bounding_box_with_gmsh("external.step", resolution=0.1)

    assert result["min_x"] == 0
    assert result["max_z"] == 3
    assert result["nx"] == 10
    assert result["ny"] == 20
    assert result["nz"] == 30



