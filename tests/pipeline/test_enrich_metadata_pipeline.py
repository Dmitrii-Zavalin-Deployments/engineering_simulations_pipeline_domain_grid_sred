# tests/pipeline/test_enrich_metadata_pipeline.py

import pytest
import time
from pipeline.metadata_enrichment import enrich_metadata_pipeline

# 📘 Domain values
GRID_DIMENSIONS = {
    "nx": 10,
    "ny": 20,
    "nz": 30
}
VOLUME = 6000.0  # deliberately matches nx*ny*nz

# 🎯 Expected enrichment outputs (rounded to ±0.01)
EXPECTED = {
    "domain_size": 6000,
    "spacing_hint": 1.0,  # avg dx from known values
    "resolution_density": 1.0  # size / volume
}

# ✅ Derived metadata is numerically correct
def test_metadata_tag_values_match_expected():
    enriched = enrich_metadata_pipeline(
        nx=GRID_DIMENSIONS["nx"],
        ny=GRID_DIMENSIONS["ny"],
        nz=GRID_DIMENSIONS["nz"],
        volume=VOLUME,
        config_flag=True
    )

    for key, expected in EXPECTED.items():
        assert key in enriched
        assert round(enriched[key], 2) == round(expected, 2)

# 🔍 Tags match types and are consistently float-valued
def test_metadata_values_are_floats():
    enriched = enrich_metadata_pipeline(
        nx=GRID_DIMENSIONS["nx"],
        ny=GRID_DIMENSIONS["ny"],
        nz=GRID_DIMENSIONS["nz"],
        volume=VOLUME,
        config_flag=True
    )

    for key in ["domain_size", "spacing_hint", "resolution_density"]:
        assert isinstance(enriched[key], float)

# 🚫 Disabled tagging should skip enrichment
def test_tagging_disabled_returns_empty_or_none():
    result = enrich_metadata_pipeline(
        nx=GRID_DIMENSIONS["nx"],
        ny=GRID_DIMENSIONS["ny"],
        nz=GRID_DIMENSIONS["nz"],
        volume=VOLUME,
        config_flag=False  # disabled
    )
    assert result == {} or result is None

# ⚠️ Invalid volume input should yield safe output
def test_zero_or_none_volume_is_handled_safely():
    enriched_zero = enrich_metadata_pipeline(10, 10, 10, volume=0.0, config_flag=True)
    enriched_none = enrich_metadata_pipeline(10, 10, 10, volume=None, config_flag=True)
    for enriched in [enriched_zero, enriched_none]:
        assert "resolution_density" in enriched
        assert enriched["resolution_density"] == 0.0

# ⏱️ Runtime ceiling guard
def test_enrichment_runtime_is_fast():
    start = time.time()
    enrich_metadata_pipeline(10, 10, 10, volume=6000.0, config_flag=True)
    assert time.time() - start < 0.2  # seconds



