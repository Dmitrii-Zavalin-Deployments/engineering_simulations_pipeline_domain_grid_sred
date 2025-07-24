# /src/processing/resolution_calculator.py

import json
import logging

logger = logging.getLogger(__name__)

def load_config(path="configs/system_config.json"):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Unable to load system config: %s", e)
        return {}

def get_resolution(dx=None, dy=None, dz=None, bounding_box=None, config=None):
    """
    Compute spatial resolution in x, y, z using fallback logic:
    1. Use provided dx/dy/dz
    2. Use config-defined defaults
    3. Derive heuristically from bounding box size
    """

    config = config or load_config()
    fallback_defaults = config.get("default_resolution", {})

    # Direct values (priority 1)
    resolution = {
        "dx": dx if dx is not None else None,
        "dy": dy if dy is not None else None,
        "dz": dz if dz is not None else None
    }

    # Config-defined defaults (priority 2)
    for axis in ["dx", "dy", "dz"]:
        if resolution[axis] is None and fallback_defaults.get(axis) is not None:
            resolution[axis] = fallback_defaults[axis]
            logger.info(f"Using config fallback for {axis}: {resolution[axis]}")

    # Heuristic derivation (priority 3)
    if bounding_box and any(resolution[axis] is None for axis in ["dx", "dy", "dz"]):
        try:
            x_range = bounding_box["xmax"] - bounding_box["xmin"]
            y_range = bounding_box["ymax"] - bounding_box["ymin"]
            z_range = bounding_box["zmax"] - bounding_box["zmin"]
            nx = config.get("default_grid_dimensions", {}).get("nx", 1)
            ny = config.get("default_grid_dimensions", {}).get("ny", 1)
            nz = config.get("default_grid_dimensions", {}).get("nz", 1)

            if resolution["dx"] is None:
                resolution["dx"] = x_range / nx
                logger.info(f"Derived dx from bounding box: {resolution['dx']}")
            if resolution["dy"] is None:
                resolution["dy"] = y_range / ny
                logger.info(f"Derived dy from bounding box: {resolution['dy']}")
            if resolution["dz"] is None:
                resolution["dz"] = z_range / nz
                logger.info(f"Derived dz from bounding box: {resolution['dz']}")
        except Exception as e:
            logger.warning("Bounding box heuristic failed: %s", e)

    return resolution



