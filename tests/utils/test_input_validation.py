# tests/utils/test_input_validation.py

import pytest
from utils.gmsh_input_check import validate_step_has_volumes  # ✅ corrected import

# 🧩 Dummy STEP structure with volumes
def step_with_volume():
    return { "solids": [ {"id": 101}, {"id": 202} ] }

# 🧩 Dummy STEP structure without volumes
def step_empty():
    return { "solids": [] }

# ✅ Valid STEP file passes volume check
def test_step_with_volume_passes():
    validate_step_has_volumes(step_with_volume())

# 🚫 Missing solids key triggers KeyError
def test_step_missing_solids_key_raises():
    invalid = { "shells": [] }
    with pytest.raises(KeyError):
        validate_step_has_volumes(invalid)

# ⛔️ Empty solids list fails volume validation
def test_step_with_no_volumes_raises():
    with pytest.raises(ValueError):
        validate_step_has_volumes(step_empty())

# 🧠 Invalid types raise TypeError
@pytest.mark.parametrize("bad_input", [None, "step", 42, ["solids"], {"solids": None}])
def test_invalid_step_types_raise(bad_input):
    with pytest.raises(TypeError):
        validate_step_has_volumes(bad_input)

# ⏱️ Runtime performance check
def test_volume_validator_runtime_safe():
    import time
    start = time.time()
    validate_step_has_volumes(step_with_volume())
    assert time.time() - start < 0.2



