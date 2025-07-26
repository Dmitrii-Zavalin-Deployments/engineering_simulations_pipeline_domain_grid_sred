import os
import logging
from math import ceil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from OCC.Core.STEPControl import STEPControl_Reader
    from OCC.Core.Bnd import Bnd_Box
    import OCC.Core.BRepBndLib as brepbndlib

    # ✅ Check if required symbol exists
    if not hasattr(brepbndlib, "BRepBndLib"):
        raise ImportError(
            "Symbol 'BRepBndLib' not found in OCC.Core.BRepBndLib. "
            "You may be using an incompatible version of pythonocc-core."
        )

    BRepBndLib = brepbndlib.BRepBndLib

except ImportError as e:
    logger.error("Failed to import required OCC modules.")
    try:
        logger.debug(f"Available symbols in BRepBndLib: {dir(brepbndlib)}")
    except Exception:
        logger.debug("Unable to inspect BRepBndLib module symbols.")
    raise ImportError("Required libraries not found or incompatible. "
                      "Ensure pythonocc-core is correctly installed and version-aligned.") from e

DEFAULT_RESOLUTION = 0.01  # Approximate voxel size in meters

def compute_domain_from_step(step_path: str, resolution: float = DEFAULT_RESOLUTION):
    if not os.path.exists(step_path):
        raise FileNotFoundError(f"STEP file not found: {step_path}")

    logger.info(f"Reading STEP file: {step_path}")
    reader = STEPControl_Reader()
    status = reader.ReadFile(step_path)

    if status != 1:
        raise RuntimeError("Failed to read STEP file.")

    reader.TransferRoot()
    shape = reader.OneShape()

    bbox = Bnd_Box()
    BRepBndLib().Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

    logger.info(f"Geometry bounds: x=({xmin}, {xmax}), y=({ymin}, {ymax}), z=({zmin}, {zmax})")

    dx, dy, dz = xmax - xmin, ymax - ymin, zmax - zmin
    nx, ny, nz = ceil(dx / resolution), ceil(dy / resolution), ceil(dz / resolution)

    logger.info(f"Computed grid resolution: nx={nx}, ny={ny}, nz={nz}")

    return {
        "bounds": {
            "xmin": xmin, "xmax": xmax,
            "ymin": ymin, "ymax": ymax,
            "zmin": zmin, "zmax": zmax
        },
        "resolution": {
            "dx": dx, "dy": dy, "dz": dz
        },
        "grid": {
            "nx": nx, "ny": ny, "nz": nz
        }
    }



