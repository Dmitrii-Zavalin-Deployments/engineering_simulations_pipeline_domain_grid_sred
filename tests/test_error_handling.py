import os
import json
import numpy as np
import pytest
from src.post_process_simulation_results import post_process_simulation_results

# Use this path for shared test outputs
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "testing-input-output"))

# ---------- Negative + Fault Injection Tests ----------

def test_load_invalid_json(monkeypatch):
    class DummyFile:
        def __init__(self): self.text = "{ invalid json "
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return self.text

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: DummyFile())
    with pytest.raises(json.JSONDecodeError):
        post_process_simulation_results("navier_stokes_results.json", "initial_data.json")


def test_missing_keys_raise_keyerror(tmp_path):
    bad_results = {
        "time_points": [0.0],
        "velocity_history": [[[0, 0, 0]]],
        "pressure_history": [[0]]
        # Missing "mesh_info"
    }
    initial = {
        "fluid_properties": {"density": 1000},
        "simulation_parameters": {"time_step": 0.1, "total_time": 0.1}
    }

    res_path = tmp_path / "navier_stokes_results.json"
    init_path = tmp_path / "initial_data.json"
    res_path.write_text(json.dumps(bad_results))
    init_path.write_text(json.dumps(initial))

    with pytest.raises(KeyError, match="mesh_info"):
        post_process_simulation_results(res_path.name, init_path.name, output_dir=str(tmp_path))


def test_shape_mismatch_on_reshape(tmp_path):
    bad_results = {
        "time_points": [0.0, 0.1],
        "velocity_history": [[[0, 0, 0]] * 20] * 2,  # 20 nodes
        "pressure_history": [[0.0] * 20] * 2,
        "mesh_info": {
            "nodes": 20,
            "grid_shape": [2, 2, 3],  # Expected 12 nodes, mismatch
            "nodes_coords": [[0.0, 0.0, 0.0]] * 20,
            "dx": 1.0, "dy": 1.0, "dz": 1.0
        }
    }
    initial_data = {
        "fluid_properties": {"density": 1.0},
        "simulation_parameters": {
            "time_step": 0.1,
            "total_time": 0.2
        }
    }

    res_path = tmp_path / "navier_stokes_results.json"
    init_path = tmp_path / "initial_data.json"
    res_path.write_text(json.dumps(bad_results))
    init_path.write_text(json.dumps(initial_data))

    with pytest.raises(ValueError, match="Mismatch between expected and actual node count"):
        post_process_simulation_results(res_path.name, init_path.name, output_dir=str(tmp_path))


def test_non_monotonic_time_points(tmp_path):
    bad_results = {
        "time_points": [0.0, 0.1, 0.08],  # Non-monotonic
        "velocity_history": [[[0, 0, 0]] * 3],
        "pressure_history": [[0.0] * 3],
        "mesh_info": {
            "nodes": 3,
            "grid_shape": [1, 1, 3],
            "nodes_coords": [[0.0, 0.0, 0.0]] * 3,
            "dx": 1.0, "dy": 1.0, "dz": 1.0
        }
    }
    initial_data = {
        "fluid_properties": {"density": 1.0},
        "simulation_parameters": {
            "time_step": 0.1,
            "total_time": 0.3
        }
    }

    res_path = tmp_path / "navier_stokes_results.json"
    init_path = tmp_path / "initial_data.json"
    res_path.write_text(json.dumps(bad_results))
    init_path.write_text(json.dumps(initial_data))

    # You can optionally enforce this behavior in your main script
    time_array = np.array(bad_results["time_points"])
    diffs = np.diff(time_array)
    assert not np.all(diffs > 0), "Time steps must be strictly increasing"


def test_tke_nan_input_propagates():
    velocity = np.array([[[np.nan, 0.0, 0.0]]])
    density = 1000
    norms = np.linalg.norm(velocity, axis=2)
    tke = 0.5 * density * norms**2
    assert np.isnan(tke).all(), "TKE should be NaN if velocity contains NaN"



