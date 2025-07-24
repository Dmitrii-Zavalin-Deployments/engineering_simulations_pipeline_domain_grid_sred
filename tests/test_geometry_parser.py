import pytest
from pathlib import Path
from src.geometry_parser import extract_bounding_box_from_step

# 📦 STEP Assets
VALID_STEP = Path("test_models/test.step")
INVALID_STEP = Path("test_models/mock_invalid_geometry.step")  # must exist
EMPTY_STEP = Path("test_models/empty.step")  # simulate an empty STEP if needed

# ✅ Valid STEP extraction test
def test_valid_step_extraction():
    bbox = extract_bounding_box_from_step(VALID_STEP)
    assert isinstance(bbox, dict)
    assert all(key in bbox for key in ["xmin", "xmax", "ymin", "ymax", "zmin", "zmax"])
    assert bbox["xmax"] > bbox["xmin"]
    assert bbox["ymax"] > bbox["ymin"]
    assert bbox["zmax"] > bbox["zmin"]

# 🛡️ Malformed STEP file triggers error or skip
def test_invalid_step_file_handling():
    with pytest.raises(Exception) as exc_info:
        extract_bounding_box_from_step(INVALID_STEP)
    assert "Unsupported geometry" in str(exc_info.value) or "no solids" in str(exc_info.value).lower()

# 🚫 Empty STEP should fail or produce no bounding box
def test_empty_step_file():
    try:
        result = extract_bounding_box_from_step(EMPTY_STEP)
        assert all(result[axis] == 0.0 for axis in result.values()) or result is None
    except Exception as e:
        assert "empty" in str(e).lower() or isinstance(e, ValueError)

# ⚠️ Nonexistent file should raise file-level error
def test_missing_step_file():
    nonexistent = Path("test_models/file_does_not_exist.step")
    with pytest.raises(FileNotFoundError):
        extract_bounding_box_from_step(nonexistent)

# 🎯 Performance bound: no long parse delays on small assets
def test_step_parsing_runtime_below_threshold():
    import time
    start = time.time()
    extract_bounding_box_from_step(VALID_STEP)
    duration = time.time() - start
    assert duration < 2.0  # seconds



