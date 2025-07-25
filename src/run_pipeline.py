# src/run_pipeline.py

# ----------------------------------------------------------------------
# Main entry-point for metadata enrichment and resolution tagging
# Designed for execution via GitHub Actions or local testing
# ----------------------------------------------------------------------

import json
import os
from pathlib import Path

from geometry_parser import extract_bounding_box_from_step
from errors.exceptions import EmptyGeometryException
from pipeline.metadata_enrichment import enrich_metadata_pipeline
from processing.resolution_calculator import get_resolution

# 🧩 NEW: Import profile enforcement logic
from validation.validation_profile_enforcer import enforce_profile, ValidationProfileError

# 📁 Configurable I/O Directory — supports ENV override
IO_DIRECTORY = Path(os.getenv("IO_DIRECTORY", "./data/testing-input-output"))
CONFIG_PATH = Path(os.getenv("CONFIG_PATH", IO_DIRECTORY / "system_config.json"))
OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", IO_DIRECTORY / "enriched_metadata.json"))
PROFILE_PATH = "schemas/validation_profile.yaml"  # 🧩 NEW: Declarative logic profile

def load_config(path=CONFIG_PATH):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found at {path} — using defaults")
        return {
            "default_grid_dimensions": {"nx": 3, "ny": 2, "nz": 1},
            "bounding_volume": None,
            "tagging_enabled": False,
            "enable_payload_sanitization": True,
            "domain_definition": {
                "min_z": 90.5  # ✅ Float literal added to avoid str cast issues
            }
        }
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON structure in config file: {path}")
        raise

def save_metadata(metadata, path=OUTPUT_PATH):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"✅ Metadata saved to {path}")

def validate_bounding_box_inputs(bbox):
    if not isinstance(bbox, dict):
        raise ValueError("Bounding box should be a dictionary.")
    required_keys = {"xmin", "xmax", "ymin", "ymax", "zmin", "zmax"}
    if not required_keys.issubset(bbox.keys()):
        raise ValueError(f"Bounding box missing required keys: {required_keys}")
    for val in bbox.values():
        if not isinstance(val, (int, float)):
            raise ValueError("Bounding box values must be numeric.")

# 🧼 NEW: Pre-validation payload sanitization hook
def sanitize_payload(payload: dict):
    def try_cast_float(value):
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return value
        return value

    def recurse(obj):
        if isinstance(obj, dict):
            return {k: recurse(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [recurse(item) for item in obj]
        else:
            return try_cast_float(obj)

    return recurse(payload)

def main():
    print("🚀 Pipeline starting...")
    config = load_config()

    # 🛡️ Guard against missing directory
    if not IO_DIRECTORY.exists():
        raise FileNotFoundError(f"Directory does not exist: {IO_DIRECTORY}")

    # 🔍 Add diagnostics for STEP file discovery
    print(f"📁 Searching for .step files in: {IO_DIRECTORY}")
    step_files = list(IO_DIRECTORY.glob("*.step"))
    print(f"🔎 Detected STEP files: {[f.name for f in step_files]}")

    if len(step_files) == 0:
        raise FileNotFoundError(f"No .step files found in {IO_DIRECTORY}")
    elif len(step_files) > 1:
        raise RuntimeError(f"Multiple STEP files found in {IO_DIRECTORY}. Expected exactly one.")

    filepath = step_files[0]
    print(f"📄 Reading STEP file: {filepath.name}")

    try:
        bounding_box = extract_bounding_box_from_step(filepath)
    except EmptyGeometryException:
        raise RuntimeError(f"STEP file '{filepath.name}' contains no geometry.")

    validate_bounding_box_inputs(bounding_box)

    resolution = get_resolution(
        dx=None, dy=None, dz=None,
        bounding_box=bounding_box,
        config=config
    )

    domain_definition = {
        "min_x": bounding_box["xmin"],
        "max_x": bounding_box["xmax"],
        "min_y": bounding_box["ymin"],
        "max_y": bounding_box["ymax"],
        "min_z": bounding_box["zmin"],
        "max_z": bounding_box["zmax"],
        "nx": config["default_grid_dimensions"]["nx"],
        "ny": config["default_grid_dimensions"]["ny"],
        "nz": config["default_grid_dimensions"]["nz"]
    }

    metadata = {"domain_definition": domain_definition}

    # ✅ Always sanitize payload before validation
    metadata = sanitize_payload(metadata)

    # 🧩 NEW: Enforce declarative validation profile
    try:
        enforce_profile(PROFILE_PATH, metadata)
    except ValidationProfileError as vpe:
        print(f"❌ Profile rule triggered:\n{vpe}")
        raise

    save_metadata(metadata)
    print("🏁 Pipeline completed.")

if __name__ == "__main__":
    main()



