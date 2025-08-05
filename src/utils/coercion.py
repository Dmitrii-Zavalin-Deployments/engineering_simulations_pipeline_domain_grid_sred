# src/utils/coercion.py

import math
from typing import Any, Union, Optional
from src.rules.config import debug_log
from src.logger_utils import log_warning  # ✅ Required for fallback injection
from src.utils.validation_helpers import is_valid_numeric_string

def coerce_numeric(value: Any) -> Optional[float]:
    if value is None:
        log_warning("🧯 Value for coercion is None → applying fallback: 0.0")
        return 0.0

    try:
        result = float(value)
        if math.isnan(result) or math.isinf(result):
            debug_log(f"[numeric] Rejected invalid float → result: {result} → returning None")
            return None
        debug_log(f"[numeric] Coerced native → {result}")
        return result
    except (ValueError, TypeError) as e:
        debug_log(f"[numeric] Native coercion failed for '{value}' → None | {e}")

    if is_valid_numeric_string(value):
        try:
            result = float(str(value).strip())
            if math.isnan(result) or math.isinf(result):
                debug_log(f"[numeric] Rejected string coercion → '{value}' → result: {result} → returning None")
                return None
            debug_log(f"[numeric] Coerced string '{value}' → {result}")
            return result
        except Exception as e:
            debug_log(f"[numeric] Coercion fallback failed for '{value}' → None | {e}")

    debug_log(f"[numeric] Rejected non-numeric value: '{value}'")
    return None



