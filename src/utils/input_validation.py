# src/utils/input_validation.py

import os
from typing import Union

__all__ = ["validate_step_file"]

def validate_step_file(path: Union[str, bytes, os.PathLike]) -> bool:
    """
    Validates the existence and type of a STEP file path input.

    Args:
        path (Union[str, bytes, os.PathLike]): The file path to validate.

    Returns:
        bool: True if the STEP file exists and path is valid.

    Raises:
        TypeError: If the input is not a valid path-like type.
        FileNotFoundError: If the path does not exist or is not a file.

    Example:
        >>> validate_step_file("geometry/part.step")
        True
    """
    # 🛡️ Type validation
    if not isinstance(path, (str, bytes, os.PathLike)) or not path:
        raise TypeError(
            f"Expected STEP file path as str, bytes, or os.PathLike; got {type(path).__name__}"
        )

    # 📁 File existence check
    if not os.path.isfile(path):
        raise FileNotFoundError(f"STEP file not found: {path}")

    return True



