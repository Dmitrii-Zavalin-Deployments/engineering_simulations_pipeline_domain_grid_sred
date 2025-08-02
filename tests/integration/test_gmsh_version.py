# tests/integration/test_gmsh_version.py

import re
import pytest
import gmsh

EXPECTED_VERSION = "4.11.1"


def get_installed_gmsh_version():
    """Extracts the installed gmsh version string."""
    try:
        version_str = gmsh.__version__ if hasattr(gmsh, "__version__") else gmsh.__file__
        match = re.search(r"\d+\.\d+\.\d+", version_str)
        if match:
            return match.group(0)
    except Exception:
        pass
    return None


def test_gmsh_version_exact_match():
    """Test that the installed gmsh version matches the expected pinned version."""
    version = get_installed_gmsh_version()
    assert version is not None, "Unable to determine Gmsh version"
    assert version == EXPECTED_VERSION, f"Gmsh version mismatch: found {version}, expected {EXPECTED_VERSION}"


def test_gmsh_api_stability():
    """Smoke test to confirm stable Gmsh API presence."""
    gmsh.initialize()
    try:
        gmsh.model.add("version_check")

        # 🔧 Fallback Geometry Setup to Guarantee Volume 1 Exists
        volumes = gmsh.model.getEntities(3)
        if not volumes:
            gmsh.model.occ.addBox(0, 0, 0, 1, 1, 1)
            gmsh.model.occ.synchronize()
            gmsh.model.mesh.generate(3)

        # Now query bounding box
        bbox = gmsh.model.getBoundingBox(3, 1)
        assert isinstance(bbox, tuple)
        assert len(bbox) == 6
    finally:
        gmsh.finalize()



