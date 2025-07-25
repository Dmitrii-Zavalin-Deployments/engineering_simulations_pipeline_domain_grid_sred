# tests/pipeline/test_domain_generator.py

import pytest
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepBndLib import BRepBndLib_Add
from OCP.Bnd import Bnd_Box
from pipeline.domain_generator import compute_domain_from_step

TEST_RESOLUTION = 0.01  # meters

def get_dummy_shape():
    # Creates a solid box shape: dimensions 1x1x1 meters
    return BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape()

def test_bounding_box_add():
    shape = get_dummy_shape()
    bbox = Bnd_Box()
    BRepBndLib_Add(shape, bbox)

    # Validate bounding box is correctly populated
    assert not bbox.IsVoid(), "Bounding box should not be void after shape addition"
    bounds = bbox.Get()
    assert all(isinstance(v, float) for v in bounds), "All bound values must be floats"
    assert bounds[3] > bounds[0] and bounds[4] > bounds[1] and bounds[5] > bounds[2], \
        "Max bounds must be greater than min bounds"

def test_domain_computation_from_dummy_shape(tmp_path):
    # Create a temporary STEP file from the dummy shape
    # Instead of writing a STEP, mock the domain computation directly
    import os
    import json
    from pathlib import Path

    # This test assumes a known dummy STEP file is already available
    # Replace with dynamic creation if STEP writer is accessible
    step_path = Path("data/testing-input-output/test.step")
    if not step_path.exists():
        pytest.skip("STEP test fixture not found")

    result = compute_domain_from_step(str(step_path), resolution=TEST_RESOLUTION)

    # Validation guards
    assert "bounds" in result
    assert "grid" in result
    assert "resolution" in result

    nx, ny, nz = result["grid"].values()
    assert nx > 0 and ny > 0 and nz > 0, "Grid dimensions must be positive"
    assert result["bounds"]["xmax"] > result["bounds"]["xmin"]
    assert result["bounds"]["ymax"] > result["bounds"]["ymin"]
    assert result["bounds"]["zmax"] > result["bounds"]["zmin"]



