# tests/conftest.py

import sys
import pathlib
import pytest
import gmsh

# Adds src/ directory to sys.path for all tests
SRC_PATH = pathlib.Path(__file__).resolve().parents[1] / "src"
if SRC_PATH.exists():
    sys.path.insert(0, str(SRC_PATH))


@pytest.fixture(scope="function")
def gmsh_session():
    """
    Provides an initialized and finalized Gmsh session around each test.

    Usage:
        def test_something(gmsh_session):
            # Gmsh is initialized here
            ...
            # Gmsh will finalize automatically after test
    """
    if not gmsh.isInitialized():
        gmsh.initialize()
    yield
    try:
        gmsh.finalize()
    except Exception:
        pass  # suppress teardown error to prevent test failure



