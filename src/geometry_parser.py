# src/geometry_parser.py

from pathlib import Path
from typing import Dict
import logging
import os
import gmsh
import builtins
from logger_utils import log_checkpoint  # ✅ Standardized logging

log = logging.getLogger(__name__)


class EmptyGeometryException(Exception):
    """Raised when no geometry is found in the STEP file."""
    pass


def extract_bounding_box_with_gmsh(filepath: Path, resolution: float = 0.01) -> Dict:
    """
    Loads a STEP file using Gmsh and extracts bounding box, grid resolution,
    and optionally surface tags. Falls back to OCP if Gmsh fails.

    Args:
        filepath (Path): Path to the .step file.
        resolution (float): Voxel resolution in meters.

    Returns:
        dict: domain_definition metadata
    """
    log_checkpoint("🛠️ Starting Gmsh-based domain extraction...")

    if not filepath.exists():
        raise FileNotFoundError(f"STEP file not found: {filepath}")

    try:
        gmsh.initialize()
        gmsh.model.add("domain_model")
        gmsh.logger.start()
        gmsh.open(str(filepath))

        min_x, min_y, min_z, max_x, max_y, max_z = gmsh.model.getBoundingBox()

        # Validate geometry presence
        if max_x <= min_x or max_y <= min_y or max_z <= min_z:
            raise EmptyGeometryException("STEP file appears to contain no valid geometry.")

        nx = int((max_x - min_x) / resolution)
        ny = int((max_y - min_y) / resolution)
        nz = int((max_z - min_z) / resolution)

        # Optional: collect surface tags
        surface_tags = gmsh.model.getEntities(dim=2)
        surfaces = [tag[1] for tag in surface_tags] if surface_tags else []

        log_checkpoint("📦 Bounding box and surfaces extracted.")
        return {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "min_z": min_z,
            "max_z": max_z,
            "nx": nx,
            "ny": ny,
            "nz": nz,
            "surface_tags": surfaces
        }

    except Exception as gmsh_error:
        log.warning(f"Gmsh extraction failed: {gmsh_error}")
        log_checkpoint("🔁 Attempting fallback with OCP...")

        try:
            from ocp_vscode import show, show_topology
            from ocp_tessellate import load_step
            from ocp_tessellate.boundingbox import bounding_box

            shape = load_step(str(filepath))
            bounds = bounding_box(shape)

            min_x, min_y, min_z = bounds[0]
            max_x, max_y, max_z = bounds[1]

            nx = int((max_x - min_x) / resolution)
            ny = int((max_y - min_y) / resolution)
            nz = int((max_z - min_z) / resolution)

            log_checkpoint("📦 Fallback geometry extracted via OCP.")
            return {
                "min_x": min_x,
                "max_x": max_x,
                "min_y": min_y,
                "max_y": max_y,
                "min_z": min_z,
                "max_z": max_z,
                "nx": nx,
                "ny": ny,
                "nz": nz,
                "surface_tags": []  # No tagging from OCP fallback
            }

        except Exception as ocp_error:
            log.error(f"OCP fallback also failed: {ocp_error}")
            raise RuntimeError("Failed to extract bounding box with both Gmsh and OCP.")

    finally:
        builtins.try_finally(lambda: gmsh.finalize(), suppress_exceptions=True)



