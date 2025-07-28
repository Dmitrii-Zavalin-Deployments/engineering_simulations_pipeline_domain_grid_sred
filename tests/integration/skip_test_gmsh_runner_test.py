import pytest
from pathlib import Path
from gmsh_runner import extract_bounding_box_with_gmsh

# 📁 Test STEP file must exist at this location
TEST_STEP_PATH = Path("test_models/test.step")


@pytest.mark.integration
def test_domain_extraction_valid_geometry(gmsh_session):
    """Validates correct bounding box and grid from test STEP."""
    if not TEST_STEP_PATH.exists():
        pytest.skip("STEP file missing")

    result = extract_bounding_box_with_gmsh(TEST_STEP_PATH, resolution=0.01)

    # Bounding box sanity check
    assert result["max_x"] > result["min_x"]
    assert result["max_y"] > result["min_y"]
    assert result["max_z"] > result["min_z"]

    # Grid resolution check
    assert result["nx"] > 0
    assert result["ny"] > 0
    assert result["nz"] > 0

    # Optional surface tag validation (if included)
    if "surface_tags" in result:
        assert isinstance(result["surface_tags"], list)


@pytest.mark.integration
def test_missing_file_raises_exception(gmsh_session):
    """Asserts missing STEP file triggers FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        extract_bounding_box_with_gmsh(Path("nonexistent_model.step"))


@pytest.mark.integration
def test_empty_geometry_triggers_exception(gmsh_session, tmp_path):
    """Simulates a malformed STEP and validates geometry detection."""
    fake_step = tmp_path / "empty.step"
    fake_step.write_text("")  # Dummy empty file

    with pytest.raises(Exception):  # Could be EmptyGeometryException or gmsh error
        extract_bounding_box_with_gmsh(fake_step)


@pytest.mark.integration
def test_resolution_scaling_effect(gmsh_session):
    """Checks grid size scaling based on resolution change."""
    if not TEST_STEP_PATH.exists():
        pytest.skip("STEP file missing")

    coarse = extract_bounding_box_with_gmsh(TEST_STEP_PATH, resolution=0.05)
    fine = extract_bounding_box_with_gmsh(TEST_STEP_PATH, resolution=0.005)

    # Finer resolution should yield more grid cells
    assert fine["nx"] > coarse["nx"]
    assert fine["ny"] > coarse["ny"]
    assert fine["nz"] > coarse["nz"]



