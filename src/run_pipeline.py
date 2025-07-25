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

# 📁 Configurable I/O Directory — now supports ENV override
IO_DIRECTORY = Path(os.getenv("IO_DIRECTORY", "/data/testing-input-output"))
CONFIG_PATH = Path(os.getenv("CONFIG_PATH", IO_DIRECTORY / "system_config.json"))
OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", IO_DIRECTORY / "enriched_metadata.json"))

def load_config(path=CONFIG_PATH):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found at {path} — using defaults")
        return {
            "default_grid_dimensions": {"nx": 10, "ny": 10, "nz": 10},
            "bounding_volume": None,
            "tagging_enabled": False,
            "step_filename": "empty.step"
        }
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON structure in config file: {path}")
        raise

def save_metadata(metadata, path=OUTPUT_PATH):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"✅ Metadata saved to {path}")

# 🧪 Inline fallback validator for bounding box inputs
def validate_bounding_box_inputs(bbox):
    if not isinstance(bbox, (list, tuple)) or not all(isinstance(coord, (int, float)) for coord in bbox):
        raise ValueError("Invalid bounding box inputs detected.")

def main():
    print("🚀 Pipeline starting...")
    config = load_config()

    nx = config["default_grid_dimensions"]["nx"]
    ny = config["default_grid_dimensions"]["ny"]
    nz = config["default_grid_dimensions"]["nz"]
    bounding_volume = config.get("bounding_volume")

    # 📥 STEP input file must exist at specified path
    step_filename = config.get("step_filename", "empty.step")
    filepath = IO_DIRECTORY / step_filename

    print(f"📄 Reading STEP file from {filepath}")
    try:
        bounding_box = extract_bounding_box_from_step(filepath)
    except EmptyGeometryException:
        print("⚠️ Empty STEP geometry — activating fallback")
        bounding_box = None

    if bounding_box is not None:
        validate_bounding_box_inputs(bounding_box)

    resolution = get_resolution(
        dx=None, dy=None, dz=None,
        bounding_box=bounding_box,
        config=config
    )

    enriched = enrich_metadata_pipeline(
        nx, ny, nz, bounding_volume,
        config_flag=config.get("tagging_enabled", False)
    )

    enriched.update({
        "dx": resolution["dx"],
        "dy": resolution["dy"],
        "dz": resolution["dz"]
    })

    save_metadata(enriched)
    print("🏁 Pipeline completed.")

if __name__ == "__main__":
    main()
