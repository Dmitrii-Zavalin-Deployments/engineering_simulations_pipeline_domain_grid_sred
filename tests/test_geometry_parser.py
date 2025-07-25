import pytest
from pathlib import Path

from src.geometry_parser import (
    extract_bounding_box_from_step,
    EmptyGeometryException
)

# 📦 STEP Assets
VALID_STEP = Path("test_models/test.step")
INVALID_STEP = Path("test_models/mock_invalid_geometry.step")
EMPTY_STEP = Path("test_models/empty.step")
MISSING_STEP = Path("test_models/file_does_not_exist.step")


# ✅ Valid STEP extraction test
def test_valid_step_extraction():
    bbox = extract_bounding_box_from_step(VALID_STEP)
    assert isinstance(bbox, dict)
    assert all(key in bbox for key in ["xmin", "xmax", "ymin", "ymax", "zmin", "zmax"])
    assert bbox["xmax"] > bbox["xmin"]
    assert bbox["ymax"] > bbox["ymin"]
    assert bbox["zmax"] > bbox["zmin"]


# 🚫 Empty STEP should explicitly raise EmptyGeometryException
def test_empty_step_file_rejection():
    with pytest.raises(EmptyGeometryException):
        extract_bounding_box_from_step(EMPTY_STEP)


# 🛡️ Malformed STEP file triggers general parse exception
def test_invalid_step_file_handling():
    with pytest.raises(Exception) as exc_info:
        extract_bounding_box_from_step(INVALID_STEP)
    assert "geometry" in str(exc_info.value).lower() or "parse" in str(exc_info.value).lower()


# ⚠️ Nonexistent file should raise file-level error
def test_missing_step_file():
    with pytest.raises(FileNotFoundError):
        extract_bounding_box_from_step(MISSING_STEP)


# 🎯 Performance bound: no long parse delays on small assets
def test_step_parsing_runtime_below_threshold():
    import time
    start = time.time()
    extract_bounding_box_from_step(VALID_STEP)
    duration = time.time() - start
    assert duration < 2.0  # seconds



