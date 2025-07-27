# tests/bootstrap/test_conftest_sys_path.py

import sys
import pathlib
import importlib.util
import time

def test_src_path_exists_and_injected():
    """Verify src/ is injected and physically present"""
    expected = pathlib.Path(__file__).resolve().parents[2] / "src"
    assert expected.exists(), f"'src/' directory missing: {expected}"
    assert any(str(expected) == p for p in sys.path), "'src' not injected into sys.path"

def test_pipeline_module_importable():
    """Confirm 'pipeline' package is resolvable"""
    try:
        import pipeline
    except ModuleNotFoundError:
        assert False, "Unable to import 'pipeline' — sys.path injection failed"
    assert hasattr(pipeline, "__file__"), "Pipeline module appears empty or malformed"

def test_utils_module_importable():
    """Confirm nested utils module is resolvable"""
    try:
        from utils import gmsh_input_check
    except ModuleNotFoundError:
        assert False, "Unable to import 'utils.gmsh_input_check'"
    assert callable(getattr(gmsh_input_check, "run_gmsh_validation", None))  # Adjust as needed

def test_sys_path_injection_runtime_ceiling():
    """Ensure path injection and lookup are fast"""
    start = time.time()
    import pipeline
    elapsed = time.time() - start
    assert elapsed < 0.5, f"Import injection exceeded expected runtime: {elapsed:.2f}s"

def test_importlib_spec_detectable():
    """Use importlib to verify module spec resolution"""
    spec = importlib.util.find_spec("pipeline")
    assert spec is not None, "Pipeline module not detectable via importlib"
    assert spec.origin.endswith("__init__.py") or spec.origin.endswith(".py"), "Pipeline origin spec malformed"



