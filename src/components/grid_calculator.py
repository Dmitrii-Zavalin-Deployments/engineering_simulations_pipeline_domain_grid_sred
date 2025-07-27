# src/components/grid_calculator.py

"""
Grid Calculator Utility

Computes 3D grid dimensions (nx, ny, nz) from bounding box extents
using a given spatial resolution. Supports validation and error handling
for malformed input and invalid resolution parameters.

Intended for reuse across domain definition, mesh inference, and metadata pipelines.
"""

from math import ceil
import logging
from typing import Dict, Union

__all__ = ["compute_grid_dimensions", "GridResolutionError"]

logger = logging.getLogger(__name__)

DEFAULT_RESOLUTION = 0.01  # meters

class GridResolutionError(Exception):
    """Raised when grid resolution cannot be computed due to invalid inputs."""
    pass

def compute_grid_dimensions(
    bounds: Dict[str, Union[int, float]],
    resolution: float = DEFAULT_RESOLUTION
) -> Dict[str, int]:
    """
    Computes grid dimensions (nx, ny, nz) from bounding box.

    Parameters:
    - bounds: dict with keys xmin, xmax, ymin, ymax, zmin, zmax
    - resolution: voxel size in meters

    Returns:
    - dict with keys 'nx', 'ny', 'nz'

    Raises:
    - GridResolutionError if bounding box is malformed or resolution is invalid
    """
    required_keys = {"xmin", "xmax", "ymin", "ymax", "zmin", "zmax"}
    missing = required_keys - bounds.keys()
    if missing:
        raise GridResolutionError(f"Missing bounding box keys: {', '.join(sorted(missing))}")

    try:
        dx = bounds["xmax"] - bounds["xmin"]
        dy = bounds["ymax"] - bounds["ymin"]
        dz = bounds["zmax"] - bounds["zmin"]
    except Exception as e:
        raise GridResolutionError(f"Failed to compute extents from bounds: {e}")

    if resolution <= 0:
        raise GridResolutionError(f"Resolution must be positive, got: {resolution}")

    nx, ny, nz = ceil(dx / resolution), ceil(dy / resolution), ceil(dz / resolution)
    logger.info(f"Grid dimensions computed: nx={nx}, ny={ny}, nz={nz}")

    return {"nx": nx, "ny": ny, "nz": nz}



