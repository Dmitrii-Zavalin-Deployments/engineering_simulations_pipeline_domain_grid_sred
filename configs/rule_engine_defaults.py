# configs/rule_engine_defaults.py

"""
Default configuration options for the rule engine component.
Used to enforce consistent validation behavior across systems.
"""

# 🔧 Type check enforcement mode: "strict" or "relaxed"
DEFAULT_TYPE_CHECK_MODE = "strict"

# 🚦 Logging preferences (optional extensions)
LOG_LEVEL = "WARNING"

# 💡 Behavior flags (for future extension)
ENABLE_OPERATOR_WHITELIST = True
COERCION_FAILURE_MODE = "raise"  # Options: "raise", "warn", "silent"

# 🧪 Supported type modes
SUPPORTED_TYPE_MODES = {"strict", "relaxed"}

# ⚙️ Rule Engine Mode Settings — exposed flags for flexible configuration
RULE_ENGINE_SETTINGS = {
    "strict_type_check": False,
    "relaxed_type_check": True
}

def get_type_check_mode(profile_override: str | None = None) -> str:
    """
    Returns the configured type check mode, allowing optional profile override.

    Parameters:
        profile_override (str): Optional string to override default config

    Returns:
        str: "strict" or "relaxed"
    """
    mode = profile_override or DEFAULT_TYPE_CHECK_MODE
    if mode not in SUPPORTED_TYPE_MODES:
        raise ValueError(f"Invalid type check mode: {mode}")
    return mode



