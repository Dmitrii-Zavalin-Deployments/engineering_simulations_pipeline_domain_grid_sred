# src/rules/rule_engine_coercion.py

from src.rules.config import debug_log
from src.rules.rule_engine_utils import RuleEvaluationError
from src.validation.expression_utils import is_symbolic_reference
from src.rules.type_compatibility_utils import are_types_comparable  # ✅ Replaces validation_helpers

def _coerce_types_for_comparison(left, right, mode: str = "strict"):  # ✅ Added mode argument
    try:
        debug_log(f"Attempting type coercion: left={left} ({type(left)}), right={right} ({type(right)}), mode='{mode}'")

        if left is None or right is None:
            debug_log("Skipping coercion due to unresolved operand")
            return left, right

        if isinstance(left, str) and is_symbolic_reference(left):
            raise RuleEvaluationError(f"Cannot coerce unresolved reference: {left}")
        if isinstance(right, str) and is_symbolic_reference(right):
            raise RuleEvaluationError(f"Cannot coerce unresolved reference: {right}")

        # ✅ Validate semantic compatibility first
        if not are_types_comparable(left, right, mode):
            raise RuleEvaluationError(f"Incompatible types under '{mode}' mode: {type(left)} vs {type(right)}")

        # Boolean coercion
        if isinstance(left, bool) or isinstance(right, bool):
            coerced = bool(left), bool(right)
            debug_log(f"Coerced to boolean: {coerced}")
            return coerced

        # Numeric coercion: str ↔ int/float
        if isinstance(left, (int, float)) and isinstance(right, str):
            try:
                right_coerced = type(left)(right)
                debug_log(f"Coerced right str to numeric: {right_coerced}")
                return left, right_coerced
            except Exception as e:
                raise RuleEvaluationError(f"Failed coercion of right string: {e}")

        if isinstance(right, (int, float)) and isinstance(left, str):
            try:
                left_coerced = type(right)(left)
                debug_log(f"Coerced left str to numeric: {left_coerced}")
                return left_coerced, right
            except Exception as e:
                raise RuleEvaluationError(f"Failed coercion of left string: {e}")

        # Dual string numeric coercion (relaxed)
        if isinstance(left, str) and isinstance(right, str):
            for num_type in (int, float):
                try:
                    left_num = num_type(left)
                    right_num = num_type(right)
                    debug_log(f"Coerced both strings to {num_type}: {left_num}, {right_num}")
                    return left_num, right_num
                except ValueError:
                    continue

        debug_log("Coercion fallback: using original values")
        return left, right

    except Exception as e:
        raise RuleEvaluationError(f"Type coercion failed in relaxed mode: {e}")



