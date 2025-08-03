# tests/utils/test_domain_loader_geometry_detection.py

import gmsh
import pytest
from pathlib import Path
from src.utils.domain_loader import DomainLoader

# Paths to STEP fixtures
BASE_PATH = Path("test_models")
VALID_STEP = BASE_PATH / "test.step"
INVALID_STEP = BASE_PATH / "mock_invalid_geometry.step"
EMPTY_STEP = BASE_PATH / "empty.step"

@pytest.mark.parametrize("step_file,expected", [
    (VALID_STEP, True),       # FreeCAD generated file with BREP surface/solid
    (INVALID_STEP, False),    # Degenerate or malformed geometry
    (EMPTY_STEP, False)       # Truly empty or wireframe-only input
])
def test_has_geometry_detection(step_file, expected):
    """
    Validate that DomainLoader correctly identifies geometry presence
    across diverse STEP files.
    """
    loader = DomainLoader.from_step(step_file)
    assert loader.has_geometry() is expected

def test_surface_count_nonzero_for_valid_step():
    """
    Ensure valid geometry file exposes surface entities.
    """
    loader = DomainLoader.from_step(VALID_STEP)
    assert loader.surface_count > 0

def test_bounding_box_extraction_matches_expected_keys():
    """
    Validate bounding box dictionary structure for valid inputs.
    """
    loader = DomainLoader.from_step(VALID_STEP)
    bbox = loader.bounding_box
    expected_keys = {"xmin", "ymin", "zmin", "xmax", "ymax", "zmax"}
    assert set(bbox.keys()) == expected_keys

def test_bounding_box_empty_for_invalid_and_empty():
    """
    Verify that malformed and empty STEP files yield no bbox.
    """
    for step_file in [INVALID_STEP, EMPTY_STEP]:
        loader = DomainLoader.from_step(step_file)
        assert loader.bounding_box == {}

def test_surface_count_zero_for_invalid_inputs():
    """
    Ensure surface count is correctly reported as zero where applicable.
    """
    for step_file in [INVALID_STEP, EMPTY_STEP]:
        loader = DomainLoader.from_step(step_file)
        assert loader.surface_count == 0



