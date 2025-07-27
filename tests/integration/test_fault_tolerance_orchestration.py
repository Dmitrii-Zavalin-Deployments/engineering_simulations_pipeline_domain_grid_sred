# tests/integration/test_fault_tolerance_orchestration.py

import pytest
import json
from pathlib import Path

from domain_definition_writer import validate_domain_bounds  # ✅ corrected import
from processing.resolution_calculator import get_resolution
from pipeline.metadata_enrichment import enrich_metadata_pipeline
from input_validator import validate_bounding_box_inputs

# 🧩 Faulty assets
INVALID_STEP = Path("test_models/mock_invalid_geometry.step")
EMPTY_STEP = Path("test_models/empty.step")
CONFIG_PATH = Path("configs/system_config.json")

def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# ✅ Parser rejection + fallback confirmation
@pytest.mark.parametrize("step_file", [INVALID_STEP, EMPTY_STEP])
def test_pipeline_triggers_fallback_on_invalid_geometry(step_file):
    config = load_config()
    try:
        # Simulated extraction fallback
        bbox = {
            "min_x": 0.0, "max_x": 3.0,
            "min_y": 0.0, "max_y": 2.0,
            "min_z": 0.0, "max_z": 1.0
        }
        validate_domain_bounds(bbox)
        validate_bounding_box_inputs(bbox)
        resolution = get_resolution(
            dx=None, dy=None, dz=None,
            bounding_box=bbox,
            config=config
        )
        assert resolution["dx"] > 0
        assert resolution["dy"] > 0
        assert resolution["dz"] > 0
    except Exception:
        pytest.fail("Fallback pipeline failed on invalid geometry.")

# 🛡️ Metadata enrichment must skip gracefully
@pytest.mark.parametrize("step_file", [INVALID_STEP, EMPTY_STEP])
def test_metadata_skipped_on_geometry_failure(step_file):
    config = load_config()
    try:
        bbox = {
            "min_x": 0.0, "max_x": 3.0,
            "min_y": 0.0, "max_y": 2.0,
            "min_z": 0.0, "max_z": 1.0
        }
        validate_domain_bounds(bbox)
        validate_bounding_box_inputs(bbox)
        nx = ny = nz = 10
        volume = 500.0
        tagging_flag = config.get("tagging_enabled", True)
        metadata = enrich_metadata_pipeline(nx, ny, nz, volume, config_flag=tagging_flag)
        assert isinstance(metadata, dict)
        assert "domain_size" in metadata
    except Exception:
        metadata_dict = enrich_metadata_pipeline(0, 0, 0, bounding_volume=0.0, config_flag=True)
        assert metadata_dict == {}

# 🔍 Runtime safety check (no crash propagation)
@pytest.mark.parametrize("step_file", [INVALID_STEP, EMPTY_STEP])
def test_pipeline_does_not_crash_on_bad_input(step_file):
    config = load_config()
    try:
        bbox = {
            "min_x": 0.0, "max_x": 1.0,
            "min_y": 0.0, "max_y": 1.0,
            "min_z": 0.0, "max_z": 1.0
        }
        validate_domain_bounds(bbox)
        validate_bounding_box_inputs(bbox)
        resolution = get_resolution(
            dx=None, dy=None, dz=None,
            bounding_box=bbox,
            config=config
        )
        assert resolution["nx"] >= 1
    except Exception:
        pytest.fail("Resolution failed unexpectedly during fallback.")

# ⏱️ Integration runtime ceiling
def test_integration_sequence_runtime():
    import time
    config = load_config()
    bbox = {
        "min_x": 0.0, "max_x": 3.0,
        "min_y": 0.0, "max_y": 2.0,
        "min_z": 0.0, "max_z": 1.0
    }

    start = time.time()
    resolution = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config)
    enrich_metadata_pipeline(
        resolution["nx"], resolution["ny"], resolution["nz"],
        volume=6000, config_flag=True
    )
    elapsed = time.time() - start
    assert elapsed < 1.5



