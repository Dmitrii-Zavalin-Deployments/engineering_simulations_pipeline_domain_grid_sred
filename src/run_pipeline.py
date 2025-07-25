# ----------------------------------------------------------------------
# Main entry-point for metadata enrichment and resolution tagging
# Designed for execution via GitHub Actions or local testing
# ----------------------------------------------------------------------

import json
import os
import logging
from pathlib import Path

from geometry_parser import extract_bounding_box_from_step, EmptyGeometryException
from pipeline.metadata_enrichment import enrich_metadata_pipeline
from processing.resolution_calculator import get_resolution

CONFIG_PATH = "configs/system_config.json"
OUTPUT_PATH = "output/enriched_metadata.json"

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def load_config(path=CONFIG_PATH):
    with open(path, 'r') as f:
        return json.load(f)


def save_metadata(metadata, path=OUTPUT_PATH):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"✅ Metadata saved to {path}")


def main():
    config = load_config()

    nx = config["default_grid_dimensions"]["nx"]
    ny = config["default_grid_dimensions"]["ny"]
    nz = config["default_grid_dimensions"]["nz"]
    bounding_volume = config.get("bounding_volume")

    filepath = Path(config.get("step_filepath", "test_models/empty.step"))

    # 🔁 Fallback trigger added here
    try:
        bounding_box = extract_bounding_box_from_step(filepath)
    except Exception as e:
        log.warning(f"Geometry parse failed — activating fallback. Reason: {e}")
        bounding_box = None

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


if __name__ == "__main__":
    main()



