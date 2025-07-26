# tests/pipeline/test_domain_generator.py

import pytest
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from pipeline.domain_generator import compute_domain_from_step

TEST_RESOLUTION = 0.01  # meters

def get_dummy_shape():
    # Creates a solid box shape: dimensions 1x1x1 meters
    return BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape()

def test_bounding_box_add_method():
    shape = get_dummy_shape()
    bbox = Bnd_Box()
    BRepBndLib.Add(shape, bbox)

    # Validate bounding box is correctly populated
    assert not bbox.IsVoid(), "Bounding box should not be void after shape addition"
    bounds = bbox.Get()
    assert all(isinstance(v, float) for v in bounds), "All bound values must be floats"
    assert bounds[3] > bounds[0] and bounds[4] > bounds[1] and bounds[5] > bounds[2], \
        "Max bounds must be greater than min bounds"

def test_domain_computation_from_dummy_shape(tmp_path):
    import os
    from pathlib import Path

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

def test_bounding_box_parsing_sample_step():
    import os
    from pathlib import Path

    sample_path = Path("data/testing-input-output/sample.step")
    if not sample_path.exists():
        pytest.skip("Sample STEP file missing")

    result = compute_domain_from_step(str(sample_path), resolution=TEST_RESOLUTION)

    # Validate bounding box length in at least one axis is nonzero
    xlen = result["bounds"]["xmax"] - result["bounds"]["xmin"]
    ylen = result["bounds"]["ymax"] - result["bounds"]["ymin"]
    zlen = result["bounds"]["zmax"] - result["bounds"]["zmin"]
    assert max(xlen, ylen, zlen) > 0.0, "Bounding box dimensions must be greater than zero"



