# tests/integration/test_resolution_calculator_property.py

import pytest
import json
import math
from hypothesis import given, strategies as st
from src.processing.resolution_calculator import get_resolution

CONFIG_PATH = "configs/system_config.json"

# Utility
def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Safe fallback for test resilience
        return {
            "default_resolution": {
                "dx": 0.1,
                "dy": 0.1,
                "dz": 0.1
            }
        }

# Strategy: Generate bounding boxes with randomized ranges
@st.composite
def bounding_box_strategy(draw):
    xmin = draw(st.floats(min_value=-100, max_value=100))
    xmax = draw(st.floats(min_value=xmin, max_value=xmin + 100))  # Ensure proper range
    ymin = draw(st.floats(min_value=-100, max_value=100))
    ymax = draw(st.floats(min_value=ymin, max_value=ymin + 100))
    zmin = draw(st.floats(min_value=-100, max_value=100))
    zmax = draw(st.floats(min_value=zmin, max_value=zmin + 100))

    return {
        "xmin": xmin,
        "xmax": xmax,
        "ymin": ymin,
        "ymax": ymax,
        "zmin": zmin,
        "zmax": zmax
    }

# Strategy: Generate invalid bounding boxes (reversed bounds, zero ranges)
@st.composite
def malformed_bbox_strategy(draw):
    xmin = draw(st.floats(min_value=0, max_value=0.1))
    xmax = draw(st.floats(min_value=-0.1, max_value=0))  # Reversed
    ymin = draw(st.floats(min_value=0, max_value=0.01))
    ymax = draw(st.floats(min_value=0, max_value=0.01))  # Near zero
    zmin = draw(st.floats(min_value=0.99, max_value=1.01))
    zmax = draw(st.floats(min_value=0.99, max_value=1.01))  # Equal/flat

    return {
        "xmin": xmin,
        "xmax": xmax,
        "ymin": ymin,
        "ymax": ymax,
        "zmin": zmin,
        "zmax": zmax
    }

# 🎯 Main test: Fuzz resolution fallback with randomized bounding box
@given(bbox=bounding_box_strategy())
def test_resolution_with_randomized_bbox(bbox):
    config = load_config()
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config)

    # Validate resolution values are positive and finite
    for axis in ["dx", "dy", "dz"]:
        assert axis in res
        assert isinstance(res[axis], float)
        assert res[axis] > 0
        assert math.isfinite(res[axis])

# 🧪 Edge-case permutation: malformed bbox should trigger fallback or safe error
@given(bbox=malformed_bbox_strategy())
def test_resolution_with_malformed_bbox(bbox):
    config = load_config()
    try:
        res = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config)
        for axis in ["dx", "dy", "dz"]:
            assert res[axis] > 0
            assert math.isfinite(res[axis])
    except ValueError as e:
        # Expect fallback failure with informative error
        assert "bounding box" in str(e).lower()

# 🚨 Guard against extreme spacing hint corruption
@given(dx=st.floats(min_value=1e-8, max_value=1000),
       dy=st.floats(min_value=1e-8, max_value=1000),
       dz=st.floats(min_value=1e-8, max_value=1000))
def test_resolution_with_extreme_hints(dx, dy, dz):
    config = load_config()
    bbox = {
        "xmin": 0.0, "xmax": 10.0,
        "ymin": 0.0, "ymax": 20.0,
        "zmin": 0.0, "zmax": 30.0
    }
    res = get_resolution(dx=dx, dy=dy, dz=dz, bounding_box=bbox, config=config)

    # Ensure resolution fallback is bypassed and direct values retained
    assert math.isclose(res["dx"], dx, rel_tol=1e-6)
    assert math.isclose(res["dy"], dy, rel_tol=1e-6)
    assert math.isclose(res["dz"], dz, rel_tol=1e-6)



