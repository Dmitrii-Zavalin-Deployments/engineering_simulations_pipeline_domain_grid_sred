import os
import json
import numpy as np
import pytest

# Set correct path to simulation outputs
FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "testing-input-output"))

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
    incorrect = np.ones((T, 28))  # Should be 27 = 3×3×3
    with pytest.raises(ValueError):
        incorrect.reshape((T, Z, Y, X))


def test_metadata_schema_types():
    metadata_path = os.path.join(FIXTURES_DIR, "grid_metadata.json")
    with open(metadata_path) as f:
        metadata = json.load(f)
    assert isinstance(metadata["nodes"], int)
    assert len(metadata["grid_shape"]) == 3
    for key in ["dx", "dy", "dz", "time_step_size", "total_time"]:
        assert isinstance(metadata[key], (int, float)) and metadata[key] > 0


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
    deltas = np.diff(time)
    assert np.all(deltas > 0)
    assert np.isclose(np.mean(deltas), meta["time_step_size"], rtol=1e-3)


def test_all_npy_files_are_finite():
    files = [
        "velocity_history.npy",
        "pressure_history.npy",
        "turbulence_kinetic_energy_history.npy"
    ]
    for name in files:
        data = np.load(os.path.join(FIXTURES_DIR, name))
        assert np.all(np.isfinite(data)), f"{name} contains NaN or inf"


def test_grid_index_matches_node_coordinates():
    coords = np.load(os.path.join(FIXTURES_DIR, "nodes_coords.npy"))
    with open(os.path.join(FIXTURES_DIR, "grid_metadata.json")) as f:
        meta = json.load(f)
    X, Y, Z = meta["grid_shape"]
    dx, dy, dz = meta["dx"], meta["dy"], meta["dz"]

    expected = []
    for z in range(Z):
        for y in range(Y):
            for x in range(X):
                expected.append([x * dx, y * dy, z * dz])
    expected = np.array(expected)

    assert coords.shape == expected.shape, "Mismatch in expected vs actual node count"
    np.testing.assert_allclose(coords, expected, rtol=1e-6, err_msg="Node coordinate order does not match grid indexing")



