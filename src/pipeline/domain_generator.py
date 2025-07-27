# src/pipeline/domain_generator.py

"""
Domain Generator using Gmsh-based STEP parser

Replaces legacy OCC or FreeCAD-based introspection logic.
Generates domain_definition metadata from STEP input.
"""

import logging
from pathlib import Path
from gmsh_runner import extract_bounding_box_with_gmsh

logger = logging.getLogger(__name__)

DEFAULT_RESOLUTION = 0.01  # Grid resolution in meters


def compute_domain_metadata(step_path: str, resolution: float = DEFAULT_RESOLUTION) -> dict:
    """
    Parses STEP geometry and returns domain_definition schema.

    Args:
        step_path (str): Path to STEP file (.step)
        resolution (float): Grid resolution in meters

    Returns:
        dict: domain_definition matching schema
    """
    step_file = Path(step_path)
    if not step_file.exists():
        raise FileNotFoundError(f"STEP file not found: {step_file}")

    logger.info(f"Extracting domain definition from: {step_file}")
    domain_definition = extract_bounding_box_with_gmsh(step_file, resolution=resolution)

    # Optionally verify required keys for downstream schema alignment
    required_keys = {"min_x", "max_x", "min_y", "max_y", "min_z", "max_z", "nx", "ny", "nz"}
    if not required_keys.issubset(domain_definition.keys()):
        raise ValueError(f"Incomplete domain metadata. Missing: {required_keys - domain_definition.keys()}")

    logger.info("✅ Domain definition successfully extracted via Gmsh.")
    return domain_definition



