# src/run_pipeline.py

# ----------------------------------------------------------------------
# Lightweight entrypoint for STEP-driven domain generation pipeline
# Streamlined for deterministic geometry analysis and metadata export
# ----------------------------------------------------------------------

import sys
import json
from pathlib import Path
from geometry_parser import extract_bounding_box_with_freecad
from validation.validation_profile_enforcer import enforce_profile, ValidationProfileError
from logger_utils import log_checkpoint, log_error, log_success

# 🎛️ CLI resolution override
DEFAULT_RESOLUTION = 0.01  # meters
PROFILE_PATH = "schemas/validation_profile.yaml"
IO_DIRECTORY = Path(__file__).parent.resolve() / "data/testing-input-output"
OUTPUT_PATH = IO_DIRECTORY / "domain_metadata.json"

def main(resolution=DEFAULT_RESOLUTION):
    log_checkpoint("🔧 Pipeline script has entered main()")
    log_checkpoint("🚀 STEP-driven pipeline initialized (FreeCAD backend)")

    if not IO_DIRECTORY.exists():
        log_error(f"Input directory not found: {IO_DIRECTORY}", fatal=True)

    step_files = list(IO_DIRECTORY.glob("*.step"))
    if len(step_files) == 0:
        log_error("No STEP files found", fatal=True)
    elif len(step_files) > 1:
        log_error("Multiple STEP files detected — provide exactly one", fatal=True)

    step_path = step_files[0]
    log_checkpoint(f"📄 Using STEP file: {step_path.name}")

    # 🧠 Geometry extraction with FreeCAD (wrapped for error visibility)
    try:
        log_checkpoint("📂 Calling FreeCAD geometry parser...")
        bounds = extract_bounding_box_with_freecad(str(step_path))
        log_checkpoint(f"📐 Bounding box extracted: {bounds}")
    except Exception as e:
        log_error(f"Geometry extraction failed:\n{e}", fatal=True)

    domain_info = {
        "bounds": bounds,
        "grid": {
            "nx": int((bounds["xmax"] - bounds["xmin"]) / resolution),
            "ny": int((bounds["ymax"] - bounds["ymin"]) / resolution),
            "nz": int((bounds["zmax"] - bounds["zmin"]) / resolution)
        }
    }

    metadata = {
        "domain_definition": {
            "min_x": bounds["xmin"],
            "max_x": bounds["xmax"],
            "min_y": bounds["ymin"],
            "max_y": bounds["ymax"],
            "min_z": bounds["zmin"],
            "max_z": bounds["zmax"],
            "nx": domain_info["grid"]["nx"],
            "ny": domain_info["grid"]["ny"],
            "nz": domain_info["grid"]["nz"]
        }
    }

    try:
        log_checkpoint("🔎 Validating domain metadata against schema...")
        enforce_profile(PROFILE_PATH, metadata)
        log_success("Metadata schema validation passed")
    except ValidationProfileError as e:
        log_error(f"Validation failed:\n{e}", fatal=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    log_success(f"Metadata written to {OUTPUT_PATH}")

    # 🧼 Explicit exit for CI flow
    log_checkpoint("🏁 Pipeline completed successfully")
    sys.exit(0)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="STEP-driven domain pipeline (FreeCAD only)")
    parser.add_argument("--resolution", type=float, default=DEFAULT_RESOLUTION,
                        help="Voxel resolution in meters (default: 0.01)")

    args = parser.parse_args()
    main(resolution=args.resolution)



