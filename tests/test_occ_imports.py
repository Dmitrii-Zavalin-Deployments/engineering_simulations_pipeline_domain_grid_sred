import pytest

def test_module_exists():
    """
    Ensure OCC.Core.BRepBndLib module is present and importable.
    """
    try:
        import OCC.Core.BRepBndLib
    except ImportError:
        pytest.fail("OCC.Core.BRepBndLib module import failed.")

def test_brepbndlib_class_presence():
    """
    Check that 'BRepBndLib' symbol exists within the imported module.
    """
    import OCC.Core.BRepBndLib as brepbndlib
    assert hasattr(brepbndlib, 'BRepBndLib'), "'BRepBndLib' not found in OCC.Core.BRepBndLib"

def test_brepbndlib_callable():
    """
    Confirm that BRepBndLib is callable as a constructor.
    """
    import OCC.Core.BRepBndLib as brepbndlib
    lib = brepbndlib.BRepBndLib()
    assert lib is not None, "BRepBndLib constructor did not yield an instance"

def test_brepbndlib_methods():
    """
    Validate presence of expected public methods on BRepBndLib instance.
    """
    import OCC.Core.BRepBndLib as brepbndlib
    instance = brepbndlib.BRepBndLib()
    assert hasattr(instance, "Add"), "Missing method 'Add' on BRepBndLib instance"



