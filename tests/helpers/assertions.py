# tests/helpers/assertions.py

def assert_error_contains(exc, expected_phrase):
    """
    Assert that the provided exception message contains the expected substring.

    Parameters:
        exc (ExceptionInfo): Exception object from pytest.raises context
        expected_phrase (str): Substring expected to be in the exception message

    Raises:
        AssertionError: If expected_phrase is not found in the exception message
    """
    actual_message = str(exc.value)
    normalized_message = actual_message.split(":")[-1]
    assert expected_phrase in actual_message or expected_phrase in normalized_message, (
        f"Expected phrase '{expected_phrase}' not found in error: {actual_message}"
    )



