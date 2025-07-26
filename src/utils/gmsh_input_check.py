# src/utils/gmsh_input_check.py

"""
Utility: Validate imported STEP geometry integrity before domain extraction.

Checks that the STEP file contains at least one 3D volume entity
to safely proceed with bounding box extraction or meshing.
"""

try:
    import gmsh
except ImportError:
    raise RuntimeError("Gmsh module not found. Run: pip install gmsh==4.11.1")


def validate_step_has_volumes(step_path):
    """
    Validates that the specified STEP file contains at least one 3D volume entity.

    Parameters:
        step_path (str): Path to the STEP file.

    Raises:
        FileNotFoundError: If the file path is invalid.
        RuntimeError: If no 3D volume entities are found.
    """
    import os
    if not os.path.isfile(step_path):
        raise FileNotFoundError(f"STEP file not found: {step_path}")

    gmsh.initialize()
    try:
        gmsh.model.add("volume_check_model")
        gmsh.open(step_path)

        volumes = gmsh.model.getEntities(3)
        if not volumes:
            raise RuntimeError(f"STEP file contains no 3D volumes: {step_path}")
    finally:
        gmsh.finalize()



