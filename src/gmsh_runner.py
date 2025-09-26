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
from src.utils.gmsh_input_check import validate_step_has_volumes
# ✅ Import fallback resolution profile loader
from src.utils.input_validation import load_resolution_profile

FLOW_DATA_PATH = "data/testing-input-output/flow_data.json"

def extract_internal_bounding_box(surface_tags):
    """
    Computes bounding box across selected internal surfaces.

    Parameters:
        surface_tags (List[Tuple[int, int]]): List of (dim, tag) tuples for surfaces

    Returns:
        Tuple[float, float, float, float, float, float]: min_x, min_y, min_z, max_x, max_y, max_z
    """
    boxes = [gmsh.model.getBoundingBox(dim, tag) for dim, tag in surface_tags]
    min_x = min(box[0] for box in boxes)
    min_y = min(box[1] for box in boxes)
    min_z = min(box[2] for box in boxes)
    max_x = max(box[3] for box in boxes)
    max_y = max(box[4] for box in boxes)
    max_z = max(box[5] for box in boxes)
    return min_x, min_y, min_z, max_x, max_y, max_z

def extract_bounding_box_with_gmsh(step_path, resolution=None, flow_region=None):
    """
    Parses STEP geometry with Gmsh and returns domain_definition
    including bounding box and grid resolution.

    Parameters:
        step_path (str or Path): Path to STEP file
        resolution (float or None): Grid resolution in meters. If None, fallback profile will be used.
        flow_region (str or None): Optional override for flow region ("internal" or "external")

    Returns:
        dict: domain_definition dictionary
    """
    if not os.path.isfile(step_path):
        raise FileNotFoundError(f"STEP file not found: {step_path}")

    # 🧩 Load resolution fallback
    if resolution is None:
        try:
            profile = load_resolution_profile()
            resolution = profile.get("default_resolution", {}).get("dx", 0.01)
        except Exception:
            resolution = 0.01

    # 🧩 Load flow region from flow_data.json if not provided
    if flow_region is None:
        try:
            with open(FLOW_DATA_PATH) as f:
                flow_data = json.load(f)
                flow_region = flow_data.get("model_properties", {}).get("flow_region", "external")
        except Exception:
            flow_region = "external"

    gmsh.initialize()
    try:
        gmsh.model.add("domain_model")
        gmsh.logger.start()

        validate_step_has_volumes(step_path)
        gmsh.open(str(step_path))

        if flow_region == "internal":
            # 🧩 Filter internal surfaces by physical tags
            physical_groups = gmsh.model.getPhysicalGroups(dim=2)
            internal_tags = [
                (dim, tag) for dim, tag in physical_groups
                if gmsh.model.getPhysicalName(dim, tag).lower() in {"inlet", "outlet", "internal"}
            ]
            if not internal_tags:
                raise ValueError(
                    "Flow region set to 'internal', but no physical surfaces named 'inlet', 'outlet', or 'internal' were found.\n"
                    "This likely means the STEP file lacks tagged surface groups. Please ensure your geometry includes properly named physical surfaces."
                )
            min_x, min_y, min_z, max_x, max_y, max_z = extract_internal_bounding_box(internal_tags)
        else:
            # 🧩 Use full volume bounding box
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
    finally:
        gmsh.finalize()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gmsh STEP parser for domain metadata")
    parser.add_argument("--step", type=str, required=True, help="Path to STEP file")
    parser.add_argument("--resolution", type=float, help="Grid resolution in meters")
    parser.add_argument("--output", type=str, help="Path to write domain JSON")
    parser.add_argument("--flow_region", type=str, choices=["internal", "external"],
                        help="Override flow region strategy (internal or external)")

    args = parser.parse_args()

    result = extract_bounding_box_with_gmsh(
        step_path=args.step,
        resolution=args.resolution,
        flow_region=args.flow_region
    )

    print(json.dumps({"domain_definition": result}, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"domain_definition": result}, f, indent=2)



