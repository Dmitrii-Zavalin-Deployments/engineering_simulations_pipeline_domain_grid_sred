# src/geometry_parser.py

from pathlib import Path
from typing import Dict
import logging

log = logging.getLogger(__name__)

class EmptyGeometryException(Exception):
    """Raised when no geometry is found in the STEP file."""
    pass

def extract_bounding_box_with_freecad(filepath: Path) -> Dict:
    """
    Loads a STEP file using FreeCAD and extracts its bounding box.

    Args:
        filepath (Path): Path to the .step file.
    Returns:
        dict: Bounding box data in format {'xmin': ..., 'xmax': ..., ...}

    Raises:
        FileNotFoundError: If the file does not exist.
        EmptyGeometryException: If no valid geometry objects are detected.
        Exception: For FreeCAD import failures or shape errors.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"STEP file not found: {filepath}")

    try:
        import FreeCAD
        import Import
    except ImportError as e:
        raise ImportError("FreeCAD module not available in runtime environment") from e

    try:
        doc = FreeCAD.newDocument()
        Import.insert(str(filepath), doc.Name)

        if not doc.Objects:
            raise EmptyGeometryException("STEP file loaded but contains no geometry.")

        shape = doc.Objects[0].Shape
        bounds = shape.BoundBox
        return {
            "xmin": bounds.XMin,
            "xmax": bounds.XMax,
            "ymin": bounds.YMin,
            "ymax": bounds.YMax,
            "zmin": bounds.ZMin,
            "zmax": bounds.ZMax
        }

    except Exception as e:
        log.error(f"Failed to parse STEP file with FreeCAD: {e}")
        raise



