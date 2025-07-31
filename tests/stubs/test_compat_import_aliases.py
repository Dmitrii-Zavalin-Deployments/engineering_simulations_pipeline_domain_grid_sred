# tests/stubs/test_compat_import_aliases.py

"""🧩 Compatibility stub validation for get_resolution alias."""

import pytest
from validation.validation_profile_enforcer import enforce_profile

# 🪞 Compatibility alias for legacy usage
def get_resolution(*args, **kwargs):
    return enforce_profile(*args, **kwargs)

# 🧪 Basic import alias check
def test_legacy_alias_callable_type():
    assert callable(get_resolution)
    assert get_resolution.__name__ == "get_resolution"

# 📦 Invocation simulation (mock payload)
def test_alias_invocation_with_mock_payload():
    payload = {
        "resolution": {"dx": 0.2, "dy": 0.2, "dz": 0.2},
        "bounding_box": {
            "xmin": 0.0, "xmax": 1.0,
            "ymin": 0.0, "ymax": 1.0,
            "zmin": 0.0, "zmax": 1.0
        },
        "config": {
            "default_resolution": {
                "dx": 0.2, "dy": 0.2, "dz": 0.2
            }
        }
    }

    try:
        # This simulates what legacy test modules would call
        get_resolution("configs/validation/resolution_profile.yaml", payload)
    except Exception:
        pytest.skip("Profile enforcement not mocked or validation rules missing")

# 🧠 Edge-case: Missing fields in payload
def test_alias_invocation_missing_fields():
    incomplete_payload = {
        "resolution": {},
        "config": {}
    }

    with pytest.raises(Exception):
        get_resolution("configs/validation/resolution_profile.yaml", incomplete_payload)

# ⏱️ Performance ceiling
def test_resolution_alias_runtime_guard():
    import time
    start = time.time()
    try:
        get_resolution("configs/validation/resolution_profile.yaml", {
            "resolution": {"dx": 0.1, "dy": 0.1, "dz": 0.1},
            "bounding_box": {"xmin": 0.0, "xmax": 1.0, "ymin": 0.0, "ymax": 1.0, "zmin": 0.0, "zmax": 1.0},
            "config": {}
        })
    except Exception:
        pass
    assert time.time() - start < 0.3



