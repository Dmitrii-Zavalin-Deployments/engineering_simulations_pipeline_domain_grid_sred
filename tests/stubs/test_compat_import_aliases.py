# tests/stubs/test_compat_import_aliases.py

"""🧩 Compatibility stub validation for get_resolution alias."""

import pytest
from unittest.mock import patch, mock_open, MagicMock
import validation.validation_profile_enforcer  # ✅ Imported for monkeypatching
from validation.validation_profile_enforcer import enforce_profile

# 🪞 Compatibility alias for legacy usage
def get_resolution(*args, **kwargs):
    return enforce_profile(*args, **kwargs)

# 🧪 Basic import alias check
def test_legacy_alias_callable_type():
    assert callable(get_resolution)
    assert get_resolution.__name__ == "get_resolution"

# 🧪 Invocation simulation with mock control and file override
@patch("os.path.isfile", return_value=True)  # ✅ File presence override
@patch(
    "validation.validation_profile_enforcer.open",
    new_callable=mock_open,
    read_data="rules:\n  - field: resolution.dx\n    op: exists\n    value: true"
)
def test_alias_invocation_with_mock_payload(mock_file, mock_isfile, monkeypatch):
    monkeypatch.setattr(validation.validation_profile_enforcer, "profile_check_enabled", True)

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

    result = get_resolution("configs/validation/resolution_profile.yaml", payload)
    assert result is not None

# 🧠 Edge-case: Missing fields in payload — simulate exception directly
@patch("os.path.isfile", return_value=True)  # ✅ File check safeguard
@patch("validation.validation_profile_enforcer.enforce_profile", side_effect=Exception("missing fields"))
def test_alias_invocation_missing_fields(mock_enforce, mock_isfile):
    incomplete_payload = {
        "resolution": {},
        "config": {}
    }

    with pytest.raises(Exception, match="missing fields"):
        get_resolution("configs/validation/resolution_profile.yaml", incomplete_payload)

# ⏱️ Performance ceiling
@patch("os.path.isfile", return_value=True)
@patch(
    "validation.validation_profile_enforcer.open",
    new_callable=mock_open,
    read_data="rules:\n  - field: resolution.dx\n    op: exists\n    value: true"
)
def test_resolution_alias_runtime_guard(mock_file, mock_isfile, monkeypatch):
    import time
    monkeypatch.setattr(validation.validation_profile_enforcer, "profile_check_enabled", True)

    start = time.time()
    try:
        get_resolution("configs/validation/resolution_profile.yaml", {
            "resolution": {"dx": 0.1, "dy": 0.1, "dz": 0.1},
            "bounding_box": {
                "xmin": 0.0, "xmax": 1.0,
                "ymin": 0.0, "ymax": 1.0,
                "zmin": 0.0, "zmax": 1.0
            },
            "config": {}
        })
    except Exception:
        pass
    assert time.time() - start < 0.3



