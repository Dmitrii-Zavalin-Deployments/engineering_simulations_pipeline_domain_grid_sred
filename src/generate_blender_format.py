import json
import sys

# Debug: Check Python paths to ensure correct package loading
print("DEBUG: Python sys.path", sys.path)

# Try importing numpy, catch errors if it’s missing
try:
    import numpy as np
except ModuleNotFoundError:
    print("❌ Error: NumPy module not found! Please ensure it is installed.")
    sys.exit(1)

# Try importing pyopenvdb, handle errors if it’s missing
try:
    import pyopenvdb  # External library required for VDB generation
except ModuleNotFoundError:
    print("❌ Error: PyOpenVDB module not found! Please ensure it is installed.")
    sys.exit(1)

# Convert simulation results to JSON Particle format for Blender
def convert_to_json_particles(simulation_results, num_particles=1000):
    """Generates JSON particle format from fluid velocity fields."""
    particle_positions = np.random.rand(num_particles, 3) * 10  # Seed particles randomly
    particle_velocities = simulation_results.get("velocity", [])  # Extract velocity field

    if not particle_velocities:
        print("⚠️ Warning: No velocity data found in simulation results.")

    particle_data = [
        {"position": pos.tolist(), "velocity": vel.tolist()} 
        for pos, vel in zip(particle_positions, particle_velocities)
    ]

    return {"particles": particle_data}

# Save JSON Particle data
def save_json_particles(particle_data, output_path="fluid_particles.json"):
    """Stores computed particle data in JSON format."""
    try:
        with open(output_path, "w") as file:
            json.dump(particle_data, file, indent=4)
        print(f"✅ JSON particles saved successfully to {output_path}")
    except IOError as e:
        print(f"❌ Error saving JSON particles: {e}")

# Convert simulation results to Alembic Mesh format for Blender
def convert_to_alembic_mesh(simulation_results):
    """Generates structured mesh representation for Alembic format."""
    mesh_vertices = np.array(simulation_results.get("velocity", []))  # Use velocity magnitude for mesh representation
    if mesh_vertices.size == 0:
        print("⚠️ Warning: No mesh vertices found. Mesh conversion might be incorrect.")

    return {"mesh_vertices": mesh_vertices.tolist(), "format": "Alembic"}

# Convert simulation results to VDB Volume format for Blender
def convert_to_vdb_volume(simulation_results):
    """Generates voxelized density field for Blender VDB rendering."""
    grid = pyopenvdb.FloatGrid()
    velocity_data = np.array(simulation_results.get("velocity", []))

    if velocity_data.size == 0:
        print("⚠️ Warning: No velocity data found for VDB conversion.")
        return None

    grid.copyFrom(velocity_data)  # Convert velocity field to density representation
    grid.name = "fluid_density"
    return grid

# Validate output data before conversion to Blender formats
def validate_output_data(results):
    """Ensures computed results satisfy physical consistency rules."""
    if "velocity" not in results or np.mean(results["velocity"]) < 0:
        print("❌ Error: Negative velocity values detected or missing data.")
        sys.exit(1)

    if "pressure" not in results or np.mean(results["pressure"]) <= 101325:
        print("❌ Error: Pressure drop too extreme or missing data.")
        sys.exit(1)

# Process simulation results and convert to Blender-compatible formats
def process_simulation_data(simulation_results):
    """Executes the fluid dynamics conversion pipeline."""
    # Validate simulation results
    validate_output_data(simulation_results)

    # Convert data to Blender formats
    json_particles = convert_to_json_particles(simulation_results)
    alembic_mesh = convert_to_alembic_mesh(simulation_results)
    vdb_volume = convert_to_vdb_volume(simulation_results)

    # Save JSON Particle format
    save_json_particles(json_particles)

    return {
        "json_particles": json_particles,
        "alembic_mesh": alembic_mesh,
        "vdb_volume": vdb_volume
    }

# Example usage with placeholder simulation data
if __name__ == "__main__":
    simulation_results = {
        "velocity": np.random.rand(1000, 3) * 5,  # Example velocity field
        "pressure": np.full(1000, 101325)  # Example pressure field
    }
    
    processed_data = process_simulation_data(simulation_results)
    print("✅ Fluid dynamics conversion completed for Blender formats.")



