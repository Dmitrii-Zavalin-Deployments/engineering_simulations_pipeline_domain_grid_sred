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


def extract_bounding_box_with_gmsh(step_path, resolution=0.01):
    """
    Parses STEP geometry with Gmsh and returns domain_definition
    including bounding box and grid resolution.

    Parameters:
        step_path (str): Path to STEP file
        resolution (float): Grid resolution in meters

    Returns:
        dict: domain_definition dictionary
    """
    if not os.path.isfile(step_path):
        raise FileNotFoundError(f"STEP file not found: {step_path}")

    gmsh.initialize()
    gmsh.model.add("domain_model")

    try:
        gmsh.logger.start()
        gmsh.open(step_path)

        # ✅ Fixed API call with explicit parameters
        min_x, min_y, min_z, max_x, max_y, max_z = gmsh.model.getBoundingBox(dim=3, tag=0)

        # ✅ Added guard against malformed geometries
        if (max_x - min_x) <= 0 or (max_y - min_y) <= 0 or (max_z - min_z) <= 0:
            raise ValueError("Invalid geometry: bounding box has zero size.")

        nx = int((max_x - min_x) / resolution)
        ny = int((max_y - min_y) / resolution)
        nz = int((max_z - min_z) / resolution)

        domain_definition = {
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

    finally:
        gmsh.finalize()

    return domain_definition


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gmsh STEP parser for domain metadata")
    parser.add_argument("--step", type=str, required=True, help="Path to STEP file")
    parser.add_argument("--resolution", type=float, default=0.01, help="Grid resolution in meters")
    parser.add_argument("--output", type=str, help="Path to write domain JSON")

    args = parser.parse_args()
    result = extract_bounding_box_with_gmsh(args.step, resolution=args.resolution)

    print(json.dumps({"domain_definition": result}, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"domain_definition": result}, f, indent=2)



