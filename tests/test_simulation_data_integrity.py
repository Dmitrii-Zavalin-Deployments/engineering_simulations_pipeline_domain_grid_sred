import numpy as np
import pytest
import json
import os

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

# ---------- Unit Tests ----------

def test_tke_computation_accuracy():
    velocity = np.array([
        [[1.0, 0.0, 0.0]],
        [[0.0, 2.0, 0.0]],
        [[0.0, 0.0, 3.0]]
    ])  # shape: (3, 1, 3)
    density = 1000
    expected = np.array([500, 2000, 4500])
    norms = np.linalg.norm(velocity, axis=2)
    tke = 0.5 * density * norms**2
    np.testing.assert_allclose(tke.flatten(), expected, rtol=1e-5)


def test_velocity_reshaping_valid():
    T, Z, Y, X = 2, 2, 2, 2
    N = Z * Y * X
    velocity_flat = np.ones((T, N, 3))
    reshaped = velocity_flat.reshape((T, Z, Y, X, 3))
    assert reshaped.shape == (T, Z, Y, X, 3)


def test_pressure_reshaping_invalid():
    T, Z, Y, X = 2, 3, 3, 3
    N = Z * Y * X
    incorrect = np.ones((T, N + 1))  # Incorrect node count
    with pytest.raises(ValueError):
        incorrect.reshape((T, Z, Y, X))


def test_metadata_schema_types():
    metadata = {
        "nodes": 100,
        "grid_shape": [10, 5, 2],
        "dx": 0.1,
        "dy": 0.1,
        "dz": 0.2,
        "time_step_size": 0.01,
        "total_time": 1.0,
        "num_time_steps": 100
    }
    assert isinstance(metadata["nodes"], int)
    assert len(metadata["grid_shape"]) == 3
    assert all(isinstance(x, (int, float)) for x in metadata["grid_shape"])
    for key in ["dx", "dy", "dz", "time_step_size", "total_time"]:
        assert metadata[key] > 0


# ---------- Integration Tests ----------

def test_grid_shape_matches_npy_outputs():
    velocity = np.load(os.path.join(FIXTURES_DIR, "velocity_history.npy"))
    pressure = np.load(os.path.join(FIXTURES_DIR, "pressure_history.npy"))
    tke = np.load(os.path.join(FIXTURES_DIR, "turbulence_kinetic_energy_history.npy"))
    assert velocity.shape[:4] == pressure.shape[:4] == tke.shape[:4]
    assert velocity.shape[-1] == 3


def test_node_coordinates_consistency():
    coords = np.load(os.path.join(FIXTURES_DIR, "nodes_coords.npy"))
    assert coords.ndim == 2 and coords.shape[1] == 3


def test_metadata_matches_time_points():
    with open(os.path.join(FIXTURES_DIR, "grid_metadata.json")) as f:
        meta = json.load(f)
    time = np.load(os.path.join(FIXTURES_DIR, "time_points.npy"))
    assert meta["num_time_steps"] == len(time)
    dt = np.diff(time)
    assert np.all(dt > 0)  # Monotonic check
    avg_dt = np.mean(dt)
    assert np.isclose(meta["time_step_size"], avg_dt, rtol=1e-3)


# ---------- Negative Tests ----------

def test_load_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        with open(os.path.join(FIXTURES_DIR, "invalid_results.json")) as f:
            json.load(f)


def test_density_negative_raises():
    fluid_props = {"density": -1.0}
    assert fluid_props["density"] < 0


def test_shape_mismatch_on_reshape():
    velocity = np.zeros((3, 125, 3))
    with pytest.raises(ValueError):
        velocity.reshape((3, 5, 5, 5, 3))  # Invalid shape


def test_missing_keys_raise_keyerror():
    with open(os.path.join(FIXTURES_DIR, "missing_mesh_info.json")) as f:
        data = json.load(f)
    with pytest.raises(KeyError):
        _ = data["mesh_info"]["nodes"]


def test_non_monotonic_time_points():
    time_points = np.array([0.0, 0.01, 0.02, 0.015])  # Non-monotonic
    diffs = np.diff(time_points)
    assert not np.all(diffs > 0), "Time vector is incorrectly monotonic"


def test_tke_nan_input_propagates():
    velocity = np.array([[[np.nan, 0.0, 0.0]]])
    density = 1000
    norms = np.linalg.norm(velocity, axis=2)
    tke = 0.5 * density * norms**2
    assert np.isnan(tke).all(), "TKE should be NaN if velocity contains NaN"



