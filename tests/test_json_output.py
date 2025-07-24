import pytest
import json
import jsonschema
from pathlib import Path

# 📘 Load the schema
SCHEMA_PATH = Path("schemas/domain_schema.json")
with open(SCHEMA_PATH, "r") as schema_file:
    SCHEMA = json.load(schema_file)

# 📂 Reference output sample
OUTPUT_FILE = Path("output/test_enriched_metadata.json")  # assumed to exist or produced via pipeline

# 🧪 Load function to prepare test payloads (stub for sample)
def load_payload():
    if not OUTPUT_FILE.exists():
        pytest.skip("Test output file not found. Run pipeline first.")
    with open(OUTPUT_FILE, "r") as f:
        return json.load(f)

# ✅ Validate output JSON against schema
def test_domain_definition_matches_schema():
    data = load_payload()
    jsonschema.validate(instance=data, schema=SCHEMA)

# 🛡 Verify presence of required fields
def test_required_keys_are_present():
    data = load_payload()
    dd = data.get("domain_definition")
    assert dd is not None
    required_keys = ["min_x", "max_x", "min_y", "max_y", "min_z", "max_z", "nx", "ny", "nz"]
    for key in required_keys:
        assert key in dd

# 🎯 Validate field types
def test_field_types_are_correct():
    data = load_payload()
    dd = data.get("domain_definition")
    assert isinstance(dd["nx"], int)
    assert isinstance(dd["ny"], int)
    assert isinstance(dd["nz"], int)
    for axis in ["min_x", "max_x", "min_y", "max_y", "min_z", "max_z"]:
        assert isinstance(dd[axis], float)

# ⚠️ Check metadata structure (if present)
def test_metadata_fields_are_correct():
    data = load_payload()
    md = data.get("metadata")
    if md:
        for key in ["domain_size", "spacing_hint", "resolution_density"]:
            assert key in md
            assert isinstance(md[key], float)

# 🚫 Ensure no extraneous keys
def test_schema_rejects_extra_fields():
    sample = load_payload()
    sample["domain_definition"]["unexpected_key"] = "should_not_be_here"
    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate(instance=sample, schema=SCHEMA)

# ⏱️ Performance guard for validation overhead
def test_schema_validation_runtime():
    import time
    data = load_payload()
    start = time.time()
    jsonschema.validate(instance=data, schema=SCHEMA)
    assert time.time() - start < 0.5  # seconds



