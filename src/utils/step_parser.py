# src/utils/step_parser.py

"""
STEP Geometry Validator

Provides validation for bounding box data extracted from STEP files.
Ensures required keys are present and values are numerically typed,
supporting fail-fast geometry ingestion across pipeline modules.
"""

import logging

logger = logging.getLogger(__name__)

__all__ = ["validate_bounding_box", "StepBoundingBoxError"]

REQUIRED_KEYS = {"xmin", "xmax", "ymin", "ymax", "zmin", "zmax"}

class StepBoundingBoxError(Exception):
    """Raised when bounding box data from STEP file is incomplete or invalid."""
    pass

def validate_bounding_box(bounds: dict) -> bool:
    """
    Validates presence and numeric type of bounding box keys.

    Parameters:
    - bounds (dict): Dictionary containing bounding box dimensions.

    Returns:
    - True if validation passes.

    Raises:
    - StepBoundingBoxError: If any required key is missing or has invalid value.
    """
    missing_keys = REQUIRED_KEYS - bounds.keys()
    if missing_keys:
        error_msg = f"Bounding box data incomplete. Missing keys: {', '.join(sorted(missing_keys))}"
        logger.error(error_msg)
        raise StepBoundingBoxError(error_msg)

    for key in REQUIRED_KEYS:
        value = bounds[key]
        if not isinstance(value, (int, float)):
            error_msg = f"Invalid value for key '{key}': {value} (type {type(value).__name__})"
            logger.error(error_msg)
            raise StepBoundingBoxError(error_msg)

    logger.info("✅ STEP bounding box data validated successfully.")
    return True



