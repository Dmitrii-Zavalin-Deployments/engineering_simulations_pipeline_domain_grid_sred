# tests/test_geometry_parser.py

import pytest
from pathlib import Path
from src.geometry_parser import (
    extract_bounding_box_with_freecad,
    EmptyGeometryException
)

# 📦 STEP Assets
VALID_STEP = Path("tests/assets/simple.step")
EMPTY_STEP = Path("tests/assets/empty.step")
MISSING_STEP = Path("tests/assets/file_does_not_exist.step")


# ✅ Valid STEP extraction using FreeCAD
def test_extract_bounding_box_with_freecad():
    bbox = extract_bounding_box_with_freecad(VALID_STEP)
    assert isinstance(bbox, dict)
    assert all(key in bbox for key in ["xmin", "xmax", "ymin", "ymax", "zmin", "zmax"])
    assert bbox["xmax"] > bbox["xmin"]
    assert bbox["ymax"] > bbox["ymin"]
    assert bbox["zmax"] > bbox["zmin"]


# 🚫 Empty STEP should raise EmptyGeometryException
def test_empty_geometry_raises_exception():
    with pytest.raises(EmptyGeometryException):
        extract_bounding_box_with_freecad(EMPTY_STEP)


# ⚠️ Nonexistent file should raise FileNotFoundError
def test_missing_step_file_raises_file_error():
    with pytest.raises(FileNotFoundError):
        extract_bounding_box_with_freecad(MISSING_STEP)


# 🎯 Parse performance remains within acceptable bounds
def test_freecad_parsing_runtime_below_threshold():
    import time
    start = time.time()
    extract_bounding_box_with_freecad(VALID_STEP)
    duration = time.time() - start
    assert duration < 2.5  # seconds



