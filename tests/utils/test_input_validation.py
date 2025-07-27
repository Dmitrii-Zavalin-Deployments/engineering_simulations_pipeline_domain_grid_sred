import pytest
from utils.gmsh_input_check import validate_bounding_box_inputs  # ✅ updated import

# 🧩 Minimal valid bounding box
def valid_bbox():
    return {
        "xmin": 0.0, "xmax": 1.0,
        "ymin": 0.0, "ymax": 1.0,
        "zmin": 0.0, "zmax": 1.0
    }

# ✅ Valid input passes
def test_valid_bbox_passes_validation():
    validate_bounding_box_inputs(valid_bbox())

# 🚫 Missing keys trigger failure
@pytest.mark.parametrize("missing_key", ["xmin", "xmax", "ymin", "ymax", "zmin", "zmax"])
def test_missing_key_raises(missing_key):
    bbox = valid_bbox()
    del bbox[missing_key]
    with pytest.raises(KeyError):
        validate_bounding_box_inputs(bbox)

# ⚠️ Zero-width dimensions raise error
@pytest.mark.parametrize("axis_pair", [
    ("xmin", "xmax"), ("ymin", "ymax"), ("zmin", "zmax")
])
def test_zero_width_domain_fails(axis_pair):
    bbox = valid_bbox()
    bbox[axis_pair[0]] = 1.0
    bbox[axis_pair[1]] = 1.0
    with pytest.raises(ValueError):
        validate_bounding_box_inputs(bbox)

# 🛡 Reversed bounds are rejected
@pytest.mark.parametrize("axis_pair", [
    ("xmin", "xmax"), ("ymin", "ymax"), ("zmin", "zmax")
])
def test_reversed_bounds_fail(axis_pair):
    bbox = valid_bbox()
    bbox[axis_pair[0]] = 2.0
    bbox[axis_pair[1]] = 1.0
    with pytest.raises(ValueError):
        validate_bounding_box_inputs(bbox)

# 🧠 Type mismatches raise error
@pytest.mark.parametrize("key,val", [
    ("xmin", "zero"), ("xmax", None), ("ymin", "0"), ("zmax", [1.0])
])
def test_non_numeric_types_fail(key, val):
    bbox = valid_bbox()
    bbox[key] = val
    with pytest.raises(TypeError):
        validate_bounding_box_inputs(bbox)

# 🔍 All axis values must be finite
def test_infinite_values_fail():
    import math
    bbox = valid_bbox()
    bbox["xmax"] = math.inf
    with pytest.raises(ValueError):
        validate_bounding_box_inputs(bbox)

# ⏱️ Runtime performance guard for edge-case evaluation
def test_validator_runtime_under_threshold():
    import time
    start = time.time()
    validate_bounding_box_inputs(valid_bbox())
    assert time.time() - start < 0.2  # seconds



