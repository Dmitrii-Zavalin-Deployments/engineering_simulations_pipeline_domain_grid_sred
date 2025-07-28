# src/gmsh_runner.py

# -------------------------------------------------------------------
# Gmsh-based geometry processor for STEP domain extraction pipeline
# -------------------------------------------------------------------

try:
    import gmsh
except ImportError:
    raise RuntimeError("Gmsh module not found. Run: pip install gmsh==4.11.1")

import json
import os

# ✅ Import volume integrity checker
from utils.gmsh_input_check import validate_step_has_volumes


def extract_bounding_box_with_gmsh(step_path, resolution=0.01):
    """
    Parses STEP geometry with Gmsh and returns domain_definition
    including bounding box and grid resolution.

    Assumes Gmsh session is already active — do NOT initialize/finalize here.

    Parameters:
        step_path (str or Path): Path to STEP file
        resolution (float): Grid resolution in meters

    Returns:
        dict: domain_definition dictionary
    """
    if not os.path.isfile(step_path):
        raise FileNotFoundError(f"STEP file not found: {step_path}")

    gmsh.model.add("domain_model")

    if not gmsh.logger.isStarted():
        gmsh.logger.start()

    validate_step_has_volumes(step_path)

    gmsh.open(str(step_path))

    volumes = gmsh.model.getEntities(3)
    entity_tag = volumes[0][1]

    min_x, min_y, min_z, max_x, max_y, max_z = gmsh.model.getBoundingBox(3, entity_tag)

    if (max_x - min_x) <= 0 or (max_y - min_y) <= 0 or (max_z - min_z) <= 0:
        raise ValueError("Invalid geometry: bounding box has zero size.")

    nx = int((max_x - min_x) / resolution)
    ny = int((max_y - min_y) / resolution)
    nz = int((max_z - min_z) / resolution)

    return {
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "min_z": min_z,
        "max_z": max_z,
        "nx": nx,
        "ny": ny,
        "nz": nz
    }



