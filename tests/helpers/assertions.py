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
    assert expected_phrase in str(exc.value), (
        f"Expected phrase '{expected_phrase}' not found in error: {exc.value}"
    )



