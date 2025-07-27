import pytest
import json
from pathlib import Path
from pipeline.metadata_enrichment import enrich_metadata_pipeline
from validation.validation_profile_enforcer import get_resolution  # ✅ updated import

CONFIG_PATH = "configs/system_config.json"
TEST_OUTPUT_PATH = "output/test_enriched_metadata.json"

# Load system config safely
def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

# Simulate bounding box input
def stub_bounding_box(xmax=1.0, xmin=0.0, ymax=2.0, ymin=0.0, zmax=3.0, zmin=0.0):
    return {
        "xmin": xmin, "xmax": xmax,
        "ymin": ymin, "ymax": ymax,
        "zmin": zmin, "zmax": zmax
    }

# Auto cleanup for test output file
@pytest.fixture(autouse=True)
def cleanup_output():
    output_path = Path(TEST_OUTPUT_PATH)
    if output_path.exists():
        output_path.unlink()
    yield
    if output_path.exists():
        output_path.unlink()

# ✅ Fallback resolution when dx/dy/dz missing
def test_resolution_fallback_when_dx_missing():
    config = load_config()
    bbox = stub_bounding_box()
    result = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config)

    assert all(axis in result for axis in ["dx", "dy", "dz"])
    assert result["dx"] > 0 and result["dy"] > 0 and result["dz"] > 0

# 🧪 Metadata enrichment includes resolution fields
def test_enriched_metadata_has_resolution_tags():
    config = load_config()
    dimensions = config.get("default_grid_dimensions", {})
    nx = dimensions.get("nx", 10)
    ny = dimensions.get("ny", 10)
    nz = dimensions.get("nz", 10)
    volume = config.get("bounding_volume", 1000.0)

    enriched = enrich_metadata_pipeline(nx, ny, nz, volume, config_flag=True)

    assert "domain_size" in enriched
    assert "spacing_hint" in enriched
    assert "resolution_density" in enriched

# ⚠️ Malformed bounding box triggers failure
def test_resolution_with_invalid_bounding_box():
    config = load_config()
    bad_bbox = stub_bounding_box(xmin=2.0, xmax=1.0)  # Reversed bounds

    with pytest.raises(Exception):  # Or specify expected error type
        get_resolution(dx=None, dy=None, dz=None, bounding_box=bad_bbox, config=config)

# 🚨 Missing config keys fallback safely
def test_resolution_with_missing_config_defaults():
    config = load_config()
    config["default_resolution"] = {}  # Simulate missing keys

    bbox = stub_bounding_box()
    result = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config)

    assert all(result[axis] > 0 for axis in ["dx", "dy", "dz"])

# 📦 Metadata file creation after enrichment
def test_metadata_output_file_creation():
    config = load_config()
    dimensions = config.get("default_grid_dimensions", {})
    nx = dimensions.get("nx", 10)
    ny = dimensions.get("ny", 10)
    nz = dimensions.get("nz", 10)
    volume = config.get("bounding_volume", 1000.0)

    enriched = enrich_metadata_pipeline(nx, ny, nz, volume, config_flag=True)

    with open(TEST_OUTPUT_PATH, "w") as f:
        json.dump(enriched, f, indent=4)

    assert Path(TEST_OUTPUT_PATH).exists()



