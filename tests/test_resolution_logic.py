import pytest
import math
from src.processing.resolution_calculator import get_resolution

# 🧩 Helper bounding box stub
def stub_bbox(xmin=0.0, xmax=3.0, ymin=0.0, ymax=1.0, zmin=0.0, zmax=1.0):
    return {
        "xmin": xmin,
        "xmax": xmax,
        "ymin": ymin,
        "ymax": ymax,
        "zmin": zmin,
        "zmax": zmax
    }

# 📘 Config template
default_config = {
    "default_resolution": { "dx": 1.0, "dy": 0.5, "dz": 0.25 }
}

# ✅ Formula correctness with explicit spacing
def test_resolution_from_explicit_hints():
    bbox = stub_bbox()
    res = get_resolution(
        dx=1.0, dy=0.5, dz=0.25,
        bounding_box=bbox,
        config=default_config
    )
    assert res["dx"] == 1.0
    assert res["nx"] == math.ceil((3.0 - 0.0) / 1.0)
    assert res["dy"] == 0.5
    assert res["dz"] == 0.25

# ⚙️ Config fallback path (explicit hints missing)
def test_resolution_from_config_fallback():
    bbox = stub_bbox()
    config_only = {
        "default_resolution": { "dx": 0.6, "dy": 0.4, "dz": 0.2 }
    }
    res = get_resolution(
        dx=None, dy=None, dz=None,
        bounding_box=bbox,
        config=config_only
    )
    assert math.isclose(res["dx"], 0.6)
    assert math.isclose(res["dy"], 0.4)
    assert math.isclose(res["dz"], 0.2)
    assert res["nx"] == math.ceil((3.0 - 0.0) / 0.6)

# 🧠 Heuristic fallback when config is missing or incomplete
def test_resolution_from_heuristic_fallback():
    bbox = stub_bbox()
    config_empty = {
        "default_resolution": {}
    }
    res = get_resolution(
        dx=None, dy=None, dz=None,
        bounding_box=bbox,
        config=config_empty
    )
    assert res["dx"] > 0.0
    assert isinstance(res["nx"], int)
    assert res["nx"] >= 1

# 🚨 Partial config + missing hints → mixed fallback
def test_partial_config_with_missing_dx():
    bbox = stub_bbox()
    config_partial = {
        "default_resolution": { "dy": 0.4, "dz": 0.2 }
    }
    res = get_resolution(
        dx=None, dy=None, dz=None,
        bounding_box=bbox,
        config=config_partial
    )
    assert res["dy"] == 0.4
    assert res["dz"] == 0.2
    assert res["dx"] > 0.0  # heuristic applied

# 🧪 Resolution rounding confirmation
def test_resolution_rounding_is_correct():
    bbox = stub_bbox(xmax=2.9)
    res = get_resolution(
        dx=1.0, dy=0.5, dz=0.25,
        bounding_box=bbox,
        config=default_config
    )
    assert res["nx"] == 3  # ceil(2.9 / 1.0)

# ⚠️ Zero-width bounding box triggers failure
def test_zero_width_bbox_raises_error():
    bbox = stub_bbox(xmin=1.0, xmax=1.0)  # zero range
    with pytest.raises(Exception):
        get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config={})

# 🚫 Reversed bounding box axes raise errors
@pytest.mark.parametrize("xmin,xmax", [(2.0, 1.0), (5.0, -1.0)])
def test_reversed_bounds_raise_exception(xmin, xmax):
    bbox = stub_bbox(xmin=xmin, xmax=xmax)
    with pytest.raises(Exception):
        get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config={})

# ⏱️ Performance guard (fallback + heuristic computation time)
def test_resolution_fallback_runtime_below_threshold():
    import time
    bbox = stub_bbox()
    config_empty = { "default_resolution": {} }
    start = time.time()
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config_empty)
    elapsed = time.time() - start
    assert elapsed < 1.0  # seconds



