# tests/conftest.py

import sys
import pathlib
import pytest
import gmsh
import yaml
from unittest.mock import patch, mock_open

# Adds src/ directory to sys.path for all tests
SRC_PATH = pathlib.Path(__file__).resolve().parents[1] / "src"
if SRC_PATH.exists():
    sys.path.insert(0, str(SRC_PATH))


@pytest.fixture(scope="function")
def gmsh_session():
    """
    Provides an initialized and finalized Gmsh session around each test.
    """
    gmsh.initialize()
    yield
    gmsh.finalize()


# 🧪 Fixture: Injects mocked STEP asset into temp test path
@pytest.fixture(scope="function")
def mock_step_file(tmp_path):
    """
    Loads mock_geometry.step into temporary path for geometry parsing tests.
    
    Usage:
        def test_geometry_parser(mock_step_file):
            domain = DomainLoader.from_step(mock_step_file)
            ...
    """
    fixture_path = pathlib.Path(__file__).parent / "fixtures" / "mock_geometry" / "mock_geometry.step"
    target_path = tmp_path / "mock_geometry.step"
    target_path.write_bytes(fixture_path.read_bytes())
    return str(target_path)


# 🧪 Fixture: Mocked STEP File Validator with file check override
@pytest.fixture(scope="function")
def mock_validate_step_file():
    """
    Centrally mocks the STEP file validation utility and its underlying filesystem check
    so tests can override its behavior without repeating patch logic across modules.

    Usage:
        def test_something(mock_validate_step_file):
            assert mock_validate_step_file.return_value is True
            mock_validate_step_file.assert_called_once()
    """
    with patch("os.path.isfile", return_value=True):
        with patch("src.utils.input_validation.validate_step_file", return_value=True) as mock_func:
            yield mock_func


# 🧪 Fixture: Mocked Gmsh I/O for Volume Validation
@pytest.fixture(scope="function")
def mock_gmsh_volume():
    """
    Simulates Gmsh loading and 3D volume entities for validation testing without file system access.

    Usage:
        def test_volume_something(mock_gmsh_volume):
            with mock_gmsh_volume:
                validate_step_has_volumes(...)
    """
    with patch("gmsh.open", return_value=None):
        with patch("gmsh.model.getEntities", return_value=[(3, 1)]):
            yield True  # Ensures fixture enters context correctly


# 🧪 Fixture: Mocked Empty Gmsh Entity Set — triggers volume absence errors
@pytest.fixture(scope="function")
def mock_gmsh_entities_empty():
    """
    Simulates an empty result from gmsh.model.getEntities to test missing volume detection logic.

    Usage:
        def test_volume_absence(mock_gmsh_entities_empty):
            with mock_gmsh_entities_empty:
                validate_step_has_volumes(...)
    """
    with patch("gmsh.open", return_value=None):
        with patch("gmsh.model.getEntities", return_value=[]):
            yield True  # ✅ Ensures compatibility with 'with' block context


# 🧪 Fixture: YAML Profile Loader Patch — for alias and rule validation
@pytest.fixture
def load_mock_profile():
    """
    Replaces `open()` with patched YAML string and returns parsed profile dictionary.

    Usage:
        def test_profile_safety(load_mock_profile):
            profile = load_mock_profile(VALID_ALIAS_PROFILE)
            assert "alias_map" in profile
    """
    def _loader(yaml_text):
        mocked_open = mock_open(read_data=yaml_text)
        with patch("builtins.open", mocked_open):
            with open("fake/path/profile.yaml") as f:
                return yaml.safe_load(f)
    return _loader


# 🧪 Utility: Expression Payload Factory
def get_payload_with_defaults(overrides=None):
    """
    Generates a baseline payload structure with common default keys and values,
    optionally overridden for edge-case expression tests.
    """
    base = {
        "hello": "world",
        "flag": True,
        "thresholds": {"warn_val": 150, "max_val": 150},
        "limits": {"upper": 10.0, "lower": 5.0},
        "metrics": {"score": 0.3},
        "values": {"x": 5},
        "system": {"subsystem": {"value": 42}},
        "expected": {"value": 42},
        "config": {"enabled": "true"},
        "domain_definition": {"max_z": 100.0, "min_z": 90.5},
        "a": {"b": 10},
        "x": {"y": 10},
        "rules": {"status_code": "not_a_number", "expected_code": 200},
    }

    if overrides:
        for key, value in overrides.items():
            if isinstance(base.get(key), dict) and not isinstance(value, dict):
                raise TypeError(f"Cannot override structured key '{key}' with scalar value: {value}")
            elif isinstance(base.get(key), dict) and isinstance(value, dict):
                base[key].update(value)
            else:
                base[key] = value
    return base



