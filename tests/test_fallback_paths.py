import pytest
from src.processing.resolution_calculator import get_resolution

# 💡 Helper stub
def stub_bbox(xmin=0.0, xmax=3.0, ymin=0.0, ymax=2.0, zmin=0.0, zmax=1.0):
    return {
        "xmin": xmin, "xmax": xmax,
        "ymin": ymin, "ymax": ymax,
        "zmin": zmin, "zmax": zmax
    }

# 🎯 Full fallback: no hints, partial config → heuristic
def test_heuristic_fallback_triggered():
    config = { "default_resolution": {} }  # intentionally empty
    bbox = stub_bbox()
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config)
    assert res["dx"] > 0
    assert res["dy"] > 0
    assert res["dz"] > 0

# ⚙️ Config fallback activated (no hints provided)
def test_config_fallback_only():
    config = {
        "default_resolution": {
            "dx": 0.4,
            "dy": 0.5,
            "dz": 0.25
        }
    }
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=stub_bbox(), config=config)
    assert res["dx"] == 0.4
    assert res["dy"] == 0.5
    assert res["dz"] == 0.25

# 🧪 Mixed fallback: hint present for dx, config fills dy, heuristic fills dz
def test_mixed_fallback_sequence():
    config = {
        "default_resolution": { "dy": 0.5 }  # dz is missing
    }
    res = get_resolution(dx=0.4, dy=None, dz=None, bounding_box=stub_bbox(), config=config)
    assert res["dx"] == 0.4         # input
    assert res["dy"] == 0.5         # config
    assert res["dz"] > 0.0          # heuristic

# 🚨 Partial config omission triggers fallback
def test_missing_config_key_triggers_fallback():
    config = {
        "default_resolution": {
            "dx": 0.4  # dy + dz missing
        }
    }
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=stub_bbox(), config=config)
    assert res["dx"] == 0.4         # config
    assert res["dy"] > 0.0          # heuristic
    assert res["dz"] > 0.0          # heuristic

# ⛔️ All paths missing raises no crash — fallback must succeed
def test_fallback_chain_completes_safely():
    config = {}  # no default_resolution key
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=stub_bbox(), config=config)
    assert all(res[axis] > 0.0 for axis in ["dx", "dy", "dz"])

# ⏱️ Runtime ceiling check — fallback flow should be performant
def test_fallback_resolution_runtime():
    import time
    config = {}  # pure heuristic
    bbox = stub_bbox()
    start = time.time()
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config)
    assert time.time() - start < 1.0



