# tests/helpers/assertions.py

def assert_error_contains(exc, *expected_fragments):
    """
    Assert that the provided exception message contains the expected substring(s).

    Parameters:
        exc (ExceptionInfo): Exception object from pytest.raises context
        expected_fragments (str): One or more substrings expected to appear in the exception message

    Raises:
        AssertionError: If any expected fragment is not found in the exception message
    """
    actual_message = str(exc.value)
    simplified_message = actual_message.split(":", maxsplit=2)[-1] if ":" in actual_message else actual_message

    for fragment in expected_fragments:
        if fragment not in actual_message and fragment not in simplified_message:
            raise AssertionError(
                f"Expected fragment '{fragment}' not found in error: {actual_message}"
            )


def assert_expression(expr: str, payload: dict, flags: dict):
    """
    Assert that an expression evaluates to True against the payload and flags.

    Parameters:
        expr (str): Rule expression to evaluate
        payload (dict): Payload data to resolve keys from
        flags (dict): Evaluation flags (e.g., relaxed/strict type check)

    Raises:
        AssertionError: If the expression evaluates to False
    """
    from src.rules.rule_engine import _evaluate_expression  # Lazy import to avoid cycles
    result = _evaluate_expression(expr, payload, **flags)
    if not result:
        raise AssertionError(
            f"Expression failed: {expr}\nPayload: {payload}\nFlags: {flags}"
        )



