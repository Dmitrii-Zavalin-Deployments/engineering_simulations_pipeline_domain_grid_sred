# src/run_pipeline.py

# ----------------------------------------------------------------------
# Lightweight entrypoint for STEP-driven domain generation pipeline
# Streamlined for deterministic geometry analysis and metadata export
# ----------------------------------------------------------------------

import sys
import json
from pathlib import Path
from gmsh_runner import extract_bounding_box_with_gmsh
from validation.validation_profile_enforcer import enforce_profile, ValidationProfileError
from domain_definition_writer import validate_domain_bounds, DomainValidationError
from logger_utils import log_checkpoint, log_error, log_success

# 🎛️ CLI resolution override
DEFAULT_RESOLUTION = 0.01  # meters
PROFILE_PATH = "schemas/validation_profile.yaml"
IO_DIRECTORY = Path(__file__).parent.resolve() / "data/testing-input-output"
OUTPUT_PATH = IO_DIRECTORY / "domain_metadata.json"

__all__ = ["sanitize_payload"]

def sanitize_payload(metadata: dict) -> dict:
    """
    Normalize and clean domain metadata dictionary to ensure schema compliance.
    This might include resolving nulls, coercing types, or removing extraneous fields.
    """
    domain = metadata.get("domain_definition", {})
    sanitized = {
        "domain_definition": {
            "x": float(domain.get("x", 0.0)),
            "y": float(domain.get("y", 0.0)),
            "z": float(domain.get("z", 0.0)),
            "width": float(domain.get("width", 0.0)),
            "height": float(domain.get("height", 0.0)),
            "depth": float(domain.get("depth", 0.0)),
        }
    }
    return sanitized

def main(resolution=DEFAULT_RESOLUTION):
    log_checkpoint("🔧 Pipeline script has entered main()")
    log_checkpoint("🚀 STEP-driven pipeline initialized (Gmsh backend)")

    # ✅ Defensive type guard to prevent monkeypatch conflicts
    global IO_DIRECTORY
    if not isinstance(IO_DIRECTORY, Path):
        IO_DIRECTORY = Path(IO_DIRECTORY)

    if not IO_DIRECTORY.exists():
        log_error(f"Input directory not found: {IO_DIRECTORY}", fatal=True)
        sys.exit(1)  # ✅ Enforce early exit for stability

    step_files = list(IO_DIRECTORY.glob("*.step"))
    if len(step_files) == 0:
        log_error("No STEP files found", fatal=True)
        sys.exit(1)  # ✅ Enforce early exit
    elif len(step_files) > 1:
        log_error("Multiple STEP files detected — provide exactly one", fatal=True)
        sys.exit(1)  # ✅ Enforce early exit

    step_path = step_files[0]
    log_checkpoint(f"📄 Using STEP file: {step_path.name}")

    # 🧠 Geometry extraction via Gmsh runner
    try:
        log_checkpoint("📂 Calling Gmsh geometry parser...")
        domain_definition = extract_bounding_box_with_gmsh(str(step_path), resolution)
        log_checkpoint(f"📐 Domain extracted: {domain_definition}")
    except Exception as e:
        log_error(f"Gmsh geometry extraction failed:\n{e}", fatal=True)
        sys.exit(1)  # ✅ Fail safely on error

    # 🔐 Cross-field bounds check
    try:
        validate_domain_bounds(domain_definition)
        log_success("Domain bounds validated successfully")
    except DomainValidationError as err:
        log_error(f"Domain bounds validation failed:\n{err}", fatal=True)
        sys.exit(1)  # ✅ Defensive exit

    metadata = {"domain_definition": domain_definition}

    try:
        log_checkpoint("🔎 Validating domain metadata against schema...")
        enforce_profile(PROFILE_PATH, metadata)
        log_success("Metadata schema validation passed")
    except ValidationProfileError as e:
        log_error(f"Validation failed:\n{e}", fatal=True)
        sys.exit(1)

    sanitized_metadata = sanitize_payload(metadata)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(sanitized_metadata, f, indent=2)
    log_success(f"Metadata written to {OUTPUT_PATH}")

    # 🧼 Explicit exit for CI flow
    log_checkpoint("🏁 Pipeline completed successfully")
    sys.exit(0)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="STEP-driven domain pipeline (Gmsh backend)")
    parser.add_argument("--resolution", type=float, default=DEFAULT_RESOLUTION,
                        help="Voxel resolution in meters (default: 0.01)")

    args = parser.parse_args()
    main(resolution=args.resolution)


