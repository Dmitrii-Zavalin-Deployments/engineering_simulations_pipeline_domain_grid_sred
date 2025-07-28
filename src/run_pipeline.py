# src/run_pipeline.py

# ----------------------------------------------------------------------
# Lightweight entrypoint for STEP-driven domain generation pipeline
# Streamlined for deterministic geometry analysis and metadata export
# ----------------------------------------------------------------------

import sys
import os
import json
from pathlib import Path
from gmsh_runner import extract_bounding_box_with_gmsh
from validation.validation_profile_enforcer import enforce_profile, ValidationProfileError
from domain_definition_writer import validate_domain_bounds, DomainValidationError
from logger_utils import log_checkpoint, log_error, log_success
from src.utils.coercion import safe_float  # ✅ Integrated from reusable coercion module

# 🎛️ CLI resolution override
DEFAULT_RESOLUTION = 0.01  # meters
PROFILE_PATH = "schemas/validation_profile.yaml"
IO_DIRECTORY = Path(__file__).parent.resolve() / "data/testing-input-output"
OUTPUT_PATH = IO_DIRECTORY / "domain_metadata.json"

__all__ = ["sanitize_payload"]

# 🧪 Optional test-mode guard
TEST_MODE_ENABLED = os.getenv("PIPELINE_TEST_MODE", "false").lower() == "true"

def conditional_exit(code=0):
    if TEST_MODE_ENABLED:
        log_checkpoint(f"🚦 TEST MODE ACTIVE: exit({code}) suppressed")
    else:
        sys.exit(code)

def default_domain():
    return {
        "x": 0.0, "y": 0.0, "z": 0.0,
        "width": 0.0, "height": 0.0, "depth": 0.0
    }

def sanitize_payload(metadata: dict) -> dict:
    """
    Normalize and clean domain metadata dictionary to ensure schema compliance.
    Includes default injection, type coercion, and legacy key fallback support.

    Legacy fallback:
    - If 'x', 'y', 'z' missing, fallback to 'min_x', etc.
    - If 'width' missing, derive as max_x - min_x (same for height, depth)
    """
    metadata.setdefault("domain_definition", default_domain())
    domain = metadata["domain_definition"]

    x = safe_float(domain.get("x") or domain.get("min_x"))
    y = safe_float(domain.get("y") or domain.get("min_y"))
    z = safe_float(domain.get("z") or domain.get("min_z"))

    width = safe_float(domain.get("width")) or (safe_float(domain.get("max_x")) - x)
    height = safe_float(domain.get("height")) or (safe_float(domain.get("max_y")) - y)
    depth = safe_float(domain.get("depth")) or (safe_float(domain.get("max_z")) - z)

    sanitized = {
        "domain_definition": {
            "x": x, "y": y, "z": z,
            "width": width, "height": height, "depth": depth,
        }
    }
    return sanitized

def main(resolution=DEFAULT_RESOLUTION):
    log_checkpoint("🔧 Pipeline script has entered main()")
    log_checkpoint("🚀 STEP-driven pipeline initialized (Gmsh backend)")

    global IO_DIRECTORY
    if not isinstance(IO_DIRECTORY, Path):
        IO_DIRECTORY = Path(IO_DIRECTORY)

    if not IO_DIRECTORY.exists():
        log_error(f"Input directory not found: {IO_DIRECTORY}", fatal=True)
        conditional_exit(1)

    step_files = list(IO_DIRECTORY.glob("*.step"))
    if len(step_files) == 0:
        log_error("No STEP files found", fatal=True)
        conditional_exit(1)
    elif len(step_files) > 1:
        log_error("Multiple STEP files detected — provide exactly one", fatal=True)
        conditional_exit(1)

    step_path = step_files[0]
    log_checkpoint(f"📄 Using STEP file: {step_path.name}")

    try:
        log_checkpoint("📂 Calling Gmsh geometry parser...")
        domain_definition = extract_bounding_box_with_gmsh(str(step_path), resolution)
        log_checkpoint(f"📐 Domain extracted: {domain_definition}")
    except Exception as e:
        log_error(f"Gmsh geometry extraction failed:\n{e}", fatal=True)
        conditional_exit(1)

    try:
        validate_domain_bounds(domain_definition)
        log_success("Domain bounds validated successfully")
    except DomainValidationError as err:
        log_error(f"Domain bounds validation failed:\n{err}", fatal=True)
        conditional_exit(1)

    metadata = {"domain_definition": domain_definition}

    try:
        log_checkpoint("🔎 Validating domain metadata against schema...")
        enforce_profile(PROFILE_PATH, metadata)
        log_success("Metadata schema validation passed")
    except ValidationProfileError as e:
        log_error(f"Validation failed:\n{e}", fatal=True)
        conditional_exit(1)

    sanitized_metadata = sanitize_payload(metadata)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(sanitized_metadata, f, indent=2)
    log_success(f"Metadata written to {OUTPUT_PATH}")

    log_checkpoint("🏁 Pipeline completed successfully")
    conditional_exit(0)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="STEP-driven domain pipeline (Gmsh backend)")
    parser.add_argument("--resolution", type=float, default=DEFAULT_RESOLUTION,
                        help="Voxel resolution in meters (default: 0.01)")

    args = parser.parse_args()
    main(resolution=args.resolution)



