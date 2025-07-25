# src/run_pipeline.py

# ----------------------------------------------------------------------
# Lightweight entrypoint for STEP-driven domain generation pipeline
# Streamlined for deterministic geometry analysis and metadata export
# ----------------------------------------------------------------------

import sys
from pathlib import Path
from pipeline.domain_generator import compute_domain_from_step
from utils.step_parser import validate_bounding_box
from validation.validation_profile_enforcer import enforce_profile, ValidationProfileError
import json

# ✅ Defensive runtime check for BRepBndLib_Add availability
try:
    from OCP.BRepBndLib import BRepBndLib_Add
except ImportError:
    raise ImportError("Missing BRepBndLib_Add — verify cadquery-ocp installation.")

# 🎛️ Accept optional CLI resolution override
DEFAULT_RESOLUTION = 0.01  # meters
PROFILE_PATH = "schemas/validation_profile.yaml"
IO_DIRECTORY = Path("./data/testing-input-output")
OUTPUT_PATH = IO_DIRECTORY / "domain_metadata.json"

def main(resolution=DEFAULT_RESOLUTION):
    print("🚀 STEP-driven pipeline initialized.")

    if not IO_DIRECTORY.exists():
        raise FileNotFoundError(f"Input directory not found: {IO_DIRECTORY}")

    step_files = list(IO_DIRECTORY.glob("*.step"))
    if len(step_files) == 0:
        raise FileNotFoundError("No STEP files found.")
    elif len(step_files) > 1:
        raise RuntimeError("Multiple STEP files detected — provide exactly one.")

    step_path = step_files[0]
    print(f"📄 Using STEP file: {step_path.name}")

    domain_info = compute_domain_from_step(str(step_path), resolution=resolution)
    validate_bounding_box(domain_info["bounds"])

    metadata = {
        "domain_definition": {
            "min_x": domain_info["bounds"]["xmin"],
            "max_x": domain_info["bounds"]["xmax"],
            "min_y": domain_info["bounds"]["ymin"],
            "max_y": domain_info["bounds"]["ymax"],
            "min_z": domain_info["bounds"]["zmin"],
            "max_z": domain_info["bounds"]["zmax"],
            "nx": domain_info["grid"]["nx"],
            "ny": domain_info["grid"]["ny"],
            "nz": domain_info["grid"]["nz"]
        }
    }

    try:
        enforce_profile(PROFILE_PATH, metadata)
    except ValidationProfileError as e:
        print(f"❌ Validation failed:\n{e}")
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Metadata written to {OUTPUT_PATH}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="STEP-driven domain pipeline")
    parser.add_argument("--resolution", type=float, default=DEFAULT_RESOLUTION,
                        help="Voxel resolution in meters (default: 0.01)")

    args = parser.parse_args()
    main(resolution=args.resolution)



