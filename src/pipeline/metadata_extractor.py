# /src/pipeline/metadata_extractor.py

import json
from metadata_enrichment import enrich_metadata_pipeline

def get_dimensions_from_source():
    # Replace this with actual data loading logic
    return 64, 64, 128  # Example values

def get_bounding_volume():
    # Replace this with real calculation or metadata
    return 512.0  # Example in m³

def load_runtime_config(path="configs/system_config.json"):
    with open(path, 'r') as f:
        return json.load(f)

def store_enriched_metadata(metadata, path="output/enriched_metadata.json"):
    with open(path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"Metadata saved to {path}")

def main():
    nx, ny, nz = get_dimensions_from_source()
    bounding_volume = get_bounding_volume()
    config = load_runtime_config()

    metadata = enrich_metadata_pipeline(
        nx, ny, nz, bounding_volume,
        config_flag=config.get("tagging_enabled", False)
    )

    store_enriched_metadata(metadata)

if __name__ == "__main__":
    main()



