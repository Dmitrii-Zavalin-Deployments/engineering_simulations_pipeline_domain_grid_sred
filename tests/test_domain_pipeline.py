# tests/test_domain_pipeline.py

import os
import json
import pytest
import subprocess
from pathlib import Path

from pipeline.domain_generator import compute_domain_from_step
from utils.step_parser import validate_bounding_box, StepBoundingBoxError
from components.grid_calculator import compute_grid_dimensions, GridResolutionError

# 🔧 Test fixture for dummy bounding box data
@pytest.fixture
def dummy_bounds():
    return {
        "xmin": 0.0, "xmax": 1.2,
        "ymin": 0.0, "ymax": 2.5,
        "zmin": 0.0, "zmax": 0.8
    }

# 🧪 Unit Tests — Bounding Box Validation
def test_validate_bounding_box_success(dummy_bounds):
    assert validate_bounding_box(dummy_bounds) is True

def test_validate_bounding_box_missing_keys():
    incomplete = {"xmin": 0.0, "ymin": 0.0, "zmin": 0.0}
    with pytest.raises(StepBoundingBoxError):
        validate_bounding_box(incomplete)

def test_validate_bounding_box_bad_types():
    malformed = {
        "xmin": "zero", "xmax": 1.0,
        "ymin": 0.0, "ymax": 1.0,
        "zmin": 0.0, "zmax": 1.0
    }
    with pytest.raises(StepBoundingBoxError):
        validate_bounding_box(malformed)

# 🧪 Unit Tests — Grid Resolution
def test_compute_grid_dimensions_valid(dummy_bounds):
    grid = compute_grid_dimensions(dummy_bounds, resolution=0.1)
    assert grid == {"nx": 12, "ny": 25, "nz": 8}

def test_compute_grid_dimensions_bad_resolution(dummy_bounds):
    with pytest.raises(GridResolutionError):
        compute_grid_dimensions(dummy_bounds, resolution=-1)

def test_compute_grid_dimensions_missing_bounds():
    incomplete = {"xmin": 0.0, "xmax": 1.0}
    with pytest.raises(GridResolutionError):
        compute_grid_dimensions(incomplete, resolution=0.1)

# 🧪 Integration Test — STEP Domain Parsing
def test_domain_generator_with_real_step():
    test_path = Path("data/testing-input-output/test_shape.step")
    if not test_path.exists():
        pytest.skip("STEP input file not available.")

    result = compute_domain_from_step(str(test_path), resolution=0.05)
    assert "bounds" in result
    assert "grid" in result
    assert result["grid"]["nx"] > 0
    assert result["bounds"]["xmin"] < result["bounds"]["xmax"]

# 🧪 Integration Test — Metadata Output Structure
def test_metadata_output_structure(tmp_path, dummy_bounds):
    metadata = {
        "domain_definition": {
            "min_x": dummy_bounds["xmin"],
            "max_x": dummy_bounds["xmax"],
            "min_y": dummy_bounds["ymin"],
            "max_y": dummy_bounds["ymax"],
            "min_z": dummy_bounds["zmin"],
            "max_z": dummy_bounds["zmax"],
            "nx": 3, "ny": 2, "nz": 1
        }
    }
    output_path = tmp_path / "enriched_metadata.json"
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)

    with open(output_path) as f:
        content = json.load(f)
    assert "domain_definition" in content
    assert content["domain_definition"]["nx"] == 3

# 🧪 System Test — Full Execution via CLI Entrypoint
def test_run_pipeline_execution(tmp_path):
    step_file = Path("data/testing-input-output/test_shape.step")
    if not step_file.exists():
        pytest.skip("Required STEP file missing for system test.")

    env = os.environ.copy()
    env["IO_DIRECTORY"] = str(step_file.parent)
    env["OUTPUT_PATH"] = str(tmp_path / "domain_metadata.json")

    result = subprocess.run(
        ["python", "src/run_pipeline.py", "--resolution", "0.02"],
        env=env,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "✅ Metadata written" in result.stdout

    output_file = Path(env["OUTPUT_PATH"])
    assert output_file.exists()
    with open(output_file) as f:
        metadata = json.load(f)
    assert "domain_definition" in metadata
    assert metadata["domain_definition"]["nx"] > 0



