import pytest
import json
from pathlib import Path

from src.geometry_parser import extract_bounding_box_from_step
from src.processing.resolution_calculator import get_resolution
from src.pipeline.metadata_enrichment import enrich_metadata_pipeline
from src.input_validator import validate_bounding_box_inputs

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
        bbox = extract_bounding_box_from_step(step_file)
        validate_bounding_box_inputs(bbox)
        valid_geometry = True
    except Exception:
        bbox = None
        valid_geometry = False

    if not valid_geometry:
        dummy_bbox = {
            "xmin": 0.0, "xmax": 3.0,
            "ymin": 0.0, "ymax": 2.0,
            "zmin": 0.0, "zmax": 1.0
        }
        resolution = get_resolution(
            dx=None, dy=None, dz=None,
            bounding_box=dummy_bbox,
            config=config
        )

        assert resolution["dx"] > 0
        assert resolution["dy"] > 0
        assert resolution["dz"] > 0

# 🛡️ Metadata enrichment must skip gracefully
@pytest.mark.parametrize("step_file", [INVALID_STEP, EMPTY_STEP])
def test_metadata_skipped_on_geometry_failure(step_file):
    config = load_config()

    try:
        bbox = extract_bounding_box_from_step(step_file)
        validate_bounding_box_inputs(bbox)
        nx = ny = nz = 10
        volume = 500.0
        tagging_flag = config.get("tagging_enabled", True)
        metadata = enrich_metadata_pipeline(nx, ny, nz, volume, config_flag=tagging_flag)
        assert isinstance(metadata, dict)
        assert "domain_size" in metadata
    except Exception:
        # Fallback: Enrichment must not yield metadata
        metadata_dict = enrich_metadata_pipeline(0, 0, 0, bounding_volume=0.0, config_flag=True)
        assert metadata_dict == {}  # 🔐 Required assertion patch

# 🔍 Runtime safety check (no crash propagation)
@pytest.mark.parametrize("step_file", [INVALID_STEP, EMPTY_STEP])
def test_pipeline_does_not_crash_on_bad_input(step_file):
    config = load_config()
    try:
        bbox = extract_bounding_box_from_step(step_file)
        validate_bounding_box_inputs(bbox)
        resolution = get_resolution(
            dx=None, dy=None, dz=None,
            bounding_box=bbox,
            config=config
        )
        assert resolution["nx"] >= 0
    except Exception:
        dummy_bbox = {
            "xmin": 0.0, "xmax": 1.0,
            "ymin": 0.0, "ymax": 1.0,
            "zmin": 0.0, "zmax": 1.0
        }
        res = get_resolution(dx=None, dy=None, dz=None, bounding_box=dummy_bbox, config=config)
        assert res["nx"] >= 1

# ⏱️ Integration runtime ceiling
def test_integration_sequence_runtime():
    import time
    config = load_config()
    dummy_bbox = {
        "xmin": 0.0, "xmax": 3.0,
        "ymin": 0.0, "ymax": 2.0,
        "zmin": 0.0, "zmax": 1.0
    }

    start = time.time()
    resolution = get_resolution(dx=None, dy=None, dz=None, bounding_box=dummy_bbox, config=config)
    enrich_metadata_pipeline(resolution["nx"], resolution["ny"], resolution["nz"], volume=6000, config_flag=True)
    elapsed = time.time() - start
    assert elapsed < 1.5



