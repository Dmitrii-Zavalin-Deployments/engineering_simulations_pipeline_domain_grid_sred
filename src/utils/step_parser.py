# src/utils/step_parser.py

"""
STEP Parser Utility (Gmsh-based)

This utility parses STEP files via Gmsh bindings to extract bounding box
metadata for preprocessing or quick diagnostics.
"""

from pathlib import Path
from typing import Dict
import gmsh


def get_step_bounds(step_path: Path) -> Dict:
    """
    Lightweight bounding box parser using Gmsh.

    Args:
        step_path (Path): Path to STEP file

    Returns:
        dict: { min_x, max_x, min_y, max_y, min_z, max_z }
    """
    if not step_path.exists():
        raise FileNotFoundError(f"STEP file not found: {step_path}")

    gmsh.initialize()
    gmsh.model.add("quick_model")

    try:
        gmsh.open(str(step_path))
        bounds = gmsh.model.getBoundingBox()
        return dict(zip(
            ["min_x", "min_y", "min_z", "max_x", "max_y", "max_z"],
            bounds
        ))

    finally:
        gmsh.finalize()


__all__ = ["get_step_bounds"]



