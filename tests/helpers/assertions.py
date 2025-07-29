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
    segments = actual_message.split(":", maxsplit=2)
    simplified_message = segments[-1] if len(segments) >= 2 else actual_message
    assert expected_phrase in actual_message or expected_phrase in simplified_message, (
        f"Expected phrase '{expected_phrase}' not found in error: {actual_message}"
    )



