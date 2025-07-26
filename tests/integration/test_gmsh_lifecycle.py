import pytest
import gmsh


def test_gmsh_initialize_and_finalize_safe():
    """Validate that Gmsh can be initialized and finalized cleanly."""
    assert not gmsh.isInitialized(), "Gmsh should not be initialized at start"

    gmsh.initialize()
    assert gmsh.isInitialized(), "Gmsh should be initialized after initialize()"

    gmsh.finalize()
    assert not gmsh.isInitialized(), "Gmsh should return to uninitialized state after finalize()"


def test_gmsh_double_initialize_is_tolerated():
    """Check that reinitializing Gmsh does not crash or corrupt state."""
    gmsh.initialize()
    try:
        gmsh.initialize()  # May log a warning but should not throw
        assert gmsh.isInitialized(), "Gmsh should still be considered initialized"
    finally:
        gmsh.finalize()
    assert not gmsh.isInitialized(), "Finalized state should be clean after nested initialize"


def test_finalize_before_initialize_is_safe():
    """Ensure finalize() can be called without prior initialization."""
    if gmsh.isInitialized():
        gmsh.finalize()
    assert not gmsh.isInitialized()

    try:
        gmsh.finalize()  # Should not raise — safe no-op if not initialized
    except Exception as e:
        pytest.fail(f"Unexpected exception on finalize(): {e}")
    assert not gmsh.isInitialized()


def test_gmsh_initialize_flag_during_session():
    """Confirm gmsh.isInitialized() reflects real-time state inside session."""
    gmsh.initialize()
    try:
        assert gmsh.isInitialized()
        gmsh.model.add("dummy")
        assert gmsh.isInitialized()
    finally:
        gmsh.finalize()
    assert not gmsh.isInitialized()



