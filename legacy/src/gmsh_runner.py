# src/gmsh_runner.py

import argparse
import json
import math
import gmsh
import os
from jsonschema import validate, ValidationError

# ✅ Schema path for audit-safe validation
SCHEMA_PATH = "schemas/domain_schema.json"

def compute_resolution(min_val, max_val, lc):
    return max(1, math.floor((max_val - min_val) / lc))

def round2(val):
    return float(f"{val:.2f}")

def extract_domain_definition(step_path, lc=None, nx=None, ny=None, nz=None, debug=False):
    if debug: print("[DEBUG] Initializing Gmsh...")
    gmsh.initialize()
    gmsh.open(step_path)
    gmsh.model.occ.synchronize()
    if debug: print("[DEBUG] STEP file loaded and synchronized.")

    min_x, min_y, min_z, max_x, max_y, max_z = gmsh.model.getBoundingBox(-1, -1)
    if debug:
        print(f"[DEBUG] Raw bounding box:")
        print(f"        min_x={min_x}, max_x={max_x}")
        print(f"        min_y={min_y}, max_y={max_y}")
        print(f"        min_z={min_z}, max_z={max_z}")

    if lc:
        nx = compute_resolution(min_x, max_x, lc)
        ny = compute_resolution(min_y, max_y, lc)
        nz = compute_resolution(min_z, max_z, lc)
        if debug:
            print(f"[DEBUG] Computed resolution from lc={lc}: nx={nx}, ny={ny}, nz={nz}")
    elif not (nx and ny and nz):
        raise ValueError("Either --lc or all of --nx, --ny, --nz must be provided.")

    gmsh.finalize()
    if debug: print("[DEBUG] Gmsh finalized.")

    domain = {
        "domain_definition": {
            "min_x": round2(min_x), "max_x": round2(max_x),
            "min_y": round2(min_y), "max_y": round2(max_y),
            "min_z": round2(min_z), "max_z": round2(max_z),
            "nx": nx, "ny": ny, "nz": nz
        }
    }

    if debug:
        print("[DEBUG] Final rounded domain definition:")
        print(json.dumps(domain, indent=2))

    return domain

def load_schema(schema_path):
    if not os.path.isfile(schema_path):
        raise FileNotFoundError(f"Missing schema file: {schema_path}")
    with open(schema_path, "r") as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Extract domain definition from STEP file using Gmsh")
    parser.add_argument("--step", type=str, required=True, help="Path to STEP file")
    parser.add_argument("--lc", type=float, help="Grid resolution (model units)")
    parser.add_argument("--nx", type=int, help="Grid resolution in x-direction")
    parser.add_argument("--ny", type=int, help="Grid resolution in y-direction")
    parser.add_argument("--nz", type=int, help="Grid resolution in z-direction")
    parser.add_argument("--schema", type=str, default=SCHEMA_PATH, help="Path to JSON schema")
    parser.add_argument("--output", type=str, help="Path to write domain JSON")
    parser.add_argument("--debug", action="store_true", help="Print debug information")

    args = parser.parse_args()

    print(f"[INFO] Extracting domain from: {args.step}")
    print(f"[INFO] Resolution: lc={args.lc}, nx={args.nx}, ny={args.ny}, nz={args.nz}")
    print(f"[INFO] Schema path: {args.schema}")

    try:
        domain_json = extract_domain_definition(
            step_path=args.step,
            lc=args.lc,
            nx=args.nx,
            ny=args.ny,
            nz=args.nz,
            debug=args.debug
        )

        schema = load_schema(args.schema)
        validate(instance=domain_json, schema=schema)
        print("[INFO] JSON schema validation passed.")

        if args.output:
            with open(args.output, "w") as f:
                json.dump(domain_json, f, indent=2)
            print(f"[INFO] Domain JSON written to: {args.output}")

    except ValidationError as e:
        print(f"[ERROR] Schema validation failed: {e.message}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected failure: {e}")
        raise
    finally:
        if gmsh.isInitialized():
            try:
                gmsh.finalize()
            except Exception as e:
                print(f"[WARN] Gmsh finalization error: {e}")

if __name__ == "__main__":
    main()



