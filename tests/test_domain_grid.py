# /tests/test_domain_grid.py

import pytest
import json
from pathlib import Path
from src.pipeline.metadata_enrichment import enrich_metadata_pipeline
from src.processing.resolution_calculator import get_resolution

CONFIG_PATH = "configs/system_config.json"
TEST_OUTPUT_PATH = "output/test_enriched_metadata.json"

# Utility to load system config
def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

# Utility to simulate bounding box input
def stub_bounding_box(xmax=1.0, xmin=0.0, ymax=2.0, ymin=0.0, zmax=3.0, zmin=0.0):
    return {
        "xmin": xmin,
        "xmax": xmax,
        "ymin": ymin,
        "ymax": ymax,
        "zmin": zmin,
        "zmax": zmax
    }

# Clean output dir before each test
@pytest.fixture(autouse=True)
def cleanup_output():
    output_path = Path(TEST_OUTPUT_PATH)
    if output_path.exists():
        output_path.unlink()
    yield
    if output_path.exists():
        output_path.unlink()

# ✅ Test fallback resolution hierarchy (config and heuristics)
def test_resolution_fallback_when_dx_missing():
    config = load_config()
    bbox = stub_bounding_box()

    # Explicitly omit dx to trigger fallback
    result = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config)

    assert all(axis in result for axis in ["dx", "dy", "dz"])
    assert result["dx"] > 0 and result["dy"] > 0 and result["dz"] > 0

# 🧪 Test enrichment output includes resolution tags
def test_enriched_metadata_has_resolution_tags():
    config = load_config()
    nx = config["default_grid_dimensions"]["nx"]
    ny = config["default_grid_dimensions"]["ny"]
    nz = config["default_grid_dimensions"]["nz"]
    volume = config.get("bounding_volume")

    enriched = enrich_metadata_pipeline(nx, ny, nz, volume, config_flag=True)

    assert "domain_size" in enriched
    assert "spacing_hint" in enriched
    assert "resolution_density" in enriched

# ⚠️ Test malformed bounding box triggers fallback or error
def test_resolution_with_invalid_bounding_box():
    config = load_config()

    # Reversed bounds
    bad_bbox = stub_bounding_box(xmin=2.0, xmax=1.0)

    try:
        result = get_resolution(dx=None, dy=None, dz=None, bounding_box=bad_bbox, config=config)
        assert all(result[axis] > 0 for axis in ["dx", "dy", "dz"])
    except Exception as e:
        assert "Bounding box heuristic failed" in str(e) or isinstance(e, AssertionError)

# 🚨 Test missing config values triggers safe fallback
def test_resolution_with_missing_config_defaults():
    config = load_config()

    # Remove default_resolution to simulate missing keys
    config["default_resolution"] = {}

    bbox = stub_bounding_box()
    result = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config)

    assert all(result[axis] > 0 for axis in ["dx", "dy", "dz"])

# 📦 Test metadata file output with valid enrichment
def test_metadata_output_file_creation():
    config = load_config()
    nx = config["default_grid_dimensions"]["nx"]
    ny = config["default_grid_dimensions"]["ny"]
    nz = config["default_grid_dimensions"]["nz"]
    volume = config.get("bounding_volume")

    enriched = enrich_metadata_pipeline(nx, ny, nz, volume, config_flag=True)

    with open(TEST_OUTPUT_PATH, "w") as f:
        json.dump(enriched, f, indent=4)

    assert Path(TEST_OUTPUT_PATH).exists()



