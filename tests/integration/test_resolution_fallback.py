# tests/integration/test_resolution_fallback.py

"""
Test suite for resolution fallback mechanisms and pipeline integration.
Covers config resolution logic, heuristic computation, and wrapper behavior.
"""

import pytest
import time
from pathlib import Path

from validation.validation_profile_enforcer import get_resolution  # ✅ corrected import
from run_pipeline import run_pipeline_with_geometry

# 💡 Helper stub
def stub_bbox(xmin=0.0, xmax=3.0, ymin=0.0, ymax=2.0, zmin=0.0, zmax=1.0):
    return {
        "xmin": xmin, "xmax": xmax,
        "ymin": ymin, "ymax": ymax,
        "zmin": zmin, "zmax": zmax
    }

# 🎯 Full fallback: no hints, partial config → heuristic
def test_heuristic_fallback_triggered():
    config = { "default_resolution": {} }
    bbox = stub_bbox()
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config)
    assert res["dx"] > 0
    assert res["dy"] > 0
    assert res["dz"] > 0

# ⚙️ Config fallback activated (no hints provided)
def test_config_fallback_only():
    config = {
        "default_resolution": {
            "dx": 0.4, "dy": 0.5, "dz": 0.25
        }
    }
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=stub_bbox(), config=config)
    assert res["dx"] == 0.4
    assert res["dy"] == 0.5
    assert res["dz"] == 0.25

# 🧪 Mixed fallback: hint → config → heuristic
def test_mixed_fallback_sequence():
    config = { "default_resolution": { "dy": 0.5 } }
    res = get_resolution(dx=0.4, dy=None, dz=None, bounding_box=stub_bbox(), config=config)
    assert res["dx"] == 0.4
    assert res["dy"] == 0.5
    assert res["dz"] > 0.0

# 🚨 Missing keys → heuristic fallback
def test_missing_config_key_triggers_fallback():
    config = { "default_resolution": { "dx": 0.4 } }
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=stub_bbox(), config=config)
    assert res["dx"] == 0.4
    assert res["dy"] > 0.0
    assert res["dz"] > 0.0

# ⛔️ No paths → fallback completion
def test_fallback_chain_completes_safely():
    config = {}  # no config
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=stub_bbox(), config=config)
    assert all(res[axis] > 0.0 for axis in ["dx", "dy", "dz"])

# ⏱️ Runtime ceiling check
def test_fallback_resolution_runtime():
    bbox = stub_bbox()
    config = {}
    start = time.time()
    res = get_resolution(dx=None, dy=None, dz=None, bounding_box=bbox, config=config)
    elapsed = time.time() - start
    assert elapsed < 1.5, f"Fallback runtime exceeded: {elapsed:.2f}s"

# 🔄 Structured fallback assertion — run_pipeline wrapper
def test_pipeline_triggers_config_fallback_on_geometry_failure():
    config = {
        "default_resolution": {
            "dx": 0.33, "dy": 0.44, "dz": 0.55
        },
        "default_grid_dimensions": { "nx": 10, "ny": 10, "nz": 10 },
        "bounding_volume": 0.0,
        "tagging_enabled": True
    }

    result = run_pipeline_with_geometry("empty.step", config)
    assert isinstance(result, dict)
    assert "resolution" in result
    assert result["resolution"]["dx"] == config["default_resolution"]["dx"]
    assert result["resolution"]["dy"] == config["default_resolution"]["dy"]
    assert result["resolution"]["dz"] == config["default_resolution"]["dz"]



