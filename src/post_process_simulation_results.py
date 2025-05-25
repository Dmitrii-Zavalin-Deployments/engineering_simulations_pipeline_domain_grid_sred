import os
import json
import numpy as np

def post_process_simulation_results(input_json_filename="navier_stokes_results.json", output_dir="processed_data"):
    """
    Extracts velocity fields, pressure, and (placeholder for) turbulence from simulation results
    and outputs structured binary (.npy) files.

    Args:
        input_json_filename (str): The name of the input JSON file containing simulation results.
        output_dir (str): The directory where the processed .npy files will be saved.
    """
    print("Preprocessing engineering_simulations_pipeline_preprocessing_sred")
    print("-" * 70)

    # Determine input and output paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming input JSON is in ../data/testing-input-output/ as per your previous code
    input_filepath = os.path.join(current_dir, "..", "data", "testing-input-output", input_json_filename)
    output_filepath = os.path.join(current_dir, output_dir)

    if not os.path.exists(input_filepath):
        print(f"❌ Error: Input JSON file not found at {input_filepath}")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_filepath, exist_ok=True)

    print(f"Loading results from: {input_filepath}")
    try:
        with open(input_filepath, "r") as f:
            results_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON from {input_filepath}: {e}")
        return
    except Exception as e:
        print(f"❌ An unexpected error occurred while loading {input_filepath}: {e}")
        return

    time_points = np.array(results_data["time_points"])
    velocity_history = np.array(results_data["velocity_history"])
    pressure_history = np.array(results_data["pressure_history"])
    mesh_info = results_data["mesh_info"]

    num_time_steps = len(time_points)
    num_nodes = mesh_info["nodes"]
    grid_shape = tuple(mesh_info["grid_shape"])

    print(f"Processing data for {num_time_steps} time steps and {num_nodes} nodes.")
    print(f"Grid shape: {grid_shape}")

    # Save time points
    time_points_output_path = os.path.join(output_filepath, "time_points.npy")
    np.save(time_points_output_path, time_points)
    print(f"✅ Saved time points to: {time_points_output_path}")

    # Save velocity history
    # Reshape velocity history to (num_time_steps, Nz, Ny, Nx, 3) if grid_shape is (Nx, Ny, Nz)
    # The original velocity_history is (num_time_steps, num_nodes, 3)
    # We need to map the 1D node index back to 3D (k, j, i) for proper reshaping.
    # This assumes a C-like (row-major) order where the last index changes fastest (i.e., x-direction).
    # If your original `idx_to_node` was (i, j, k) where i changes fastest, this is compatible.
    
    # Reverse grid_shape for reshaping if assuming (k, j, i) order for output for consistency
    # with typical 3D array indexing (depth, height, width)
    # Let's keep it consistent with the internal (Nx, Ny, Nz) but specify order 'C'
    
    # Note: velocity_history is (num_time_steps, num_nodes, 3)
    # Target shape for saving as a grid: (num_time_steps, Nz, Ny, Nx, 3)
    # This might require careful reordering of nodes if the 1D index mapping isn't sequential in Z, Y, X.
    # However, create_structured_grid_info maps (i, j, k) to 1D index: k*ny*nx + j*nx + i
    # This means the last dimension (x) varies fastest, then y, then z.
    # So, reshaping directly to (Nz, Ny, Nx, 3) for a single timestep should work if nodes_coords is in that order.

    # Option 1: Iterate and reshape each time step
    # This is safer as it respects the order from the original 'create_structured_grid_info'
    # which fills nodes_coords by iterating k, then j, then i.
    # This corresponds to a (z, y, x) block order.
    # So, we want to reshape to (num_time_steps, Nz, Ny, Nx, 3)
    
    # We need to map the 1D index to the 3D index for each node, and then place it correctly.
    # Since nodes_coords is already in (Nx*Ny*Nz, 3) order where the 1D index corresponds
    # to k*ny*nx + j*nx + i, we can directly reshape the 1D node arrays.
    
    # Reshape each timestep's velocity and pressure to the 3D grid shape
    # For velocity, it's (num_nodes, 3) -> (Nz, Ny, Nx, 3)
    # For pressure, it's (num_nodes,) -> (Nz, Ny, Nx)

    # Create arrays to hold reshaped data
    velocity_grid_history = np.zeros((num_time_steps, grid_shape[2], grid_shape[1], grid_shape[0], 3))
    pressure_grid_history = np.zeros((num_time_steps, grid_shape[2], grid_shape[1], grid_shape[0]))

    # For each time step, reshape the 1D arrays back into 3D grids
    for t in range(num_time_steps):
        # Reshape velocity (Nx, Ny, Nz) -> (Nz, Ny, Nx) for standard array access
        velocity_grid_history[t] = velocity_history[t].reshape(grid_shape[2], grid_shape[1], grid_shape[0], 3)
        pressure_grid_history[t] = pressure_history[t].reshape(grid_shape[2], grid_shape[1], grid_shape[0])

    velocity_output_path = os.path.join(output_filepath, "velocity_history.npy")
    np.save(velocity_output_path, velocity_grid_history)
    print(f"✅ Saved velocity history (shape: {velocity_grid_history.shape}) to: {velocity_output_path}")

    # Save pressure history
    pressure_output_path = os.path.join(output_filepath, "pressure_history.npy")
    np.save(pressure_output_path, pressure_grid_history)
    print(f"✅ Saved pressure history (shape: {pressure_grid_history.shape}) to: {pressure_output_path}")

    # Placeholder for turbulence data (e.g., Kinetic Energy)
    # You would replace this with actual turbulence model output if available.
    # For now, let's calculate kinetic energy (0.5 * rho * |v|^2)
    density = results_data["fluid_properties"]["density"]
    kinetic_energy_history = 0.5 * density * np.linalg.norm(velocity_history, axis=2)**2
    
    kinetic_energy_grid_history = np.zeros((num_time_steps, grid_shape[2], grid_shape[1], grid_shape[0]))
    for t in range(num_time_steps):
        kinetic_energy_grid_history[t] = kinetic_energy_history[t].reshape(grid_shape[2], grid_shape[1], grid_shape[0])

    turbulence_output_path = os.path.join(output_filepath, "turbulence_kinetic_energy_history.npy")
    np.save(turbulence_output_path, kinetic_energy_grid_history)
    print(f"✅ Saved turbulence (kinetic energy) history (shape: {kinetic_energy_grid_history.shape}) to: {turbulence_output_path}")

    # Save mesh coordinates separately if needed for visualization or other tools
    nodes_coords_output_path = os.path.join(output_filepath, "nodes_coords.npy")
    np.save(nodes_coords_output_path, np.array(mesh_info["nodes_coords"]))
    print(f"✅ Saved node coordinates to: {nodes_coords_output_path}")

    # Optionally, save grid metadata to a separate JSON for convenience
    grid_metadata_output_path = os.path.join(output_filepath, "grid_metadata.json")
    with open(grid_metadata_output_path, "w") as f:
        json.dump({
            "nodes": mesh_info["nodes"],
            "grid_shape": mesh_info["grid_shape"],
            "dx": mesh_info["dx"],
            "dy": mesh_info["dy"],
            "dz": mesh_info["dz"],
            "num_time_steps": num_time_steps,
            "total_time": results_data["simulation_parameters"]["total_time"],
            "time_step_size": results_data["simulation_parameters"]["time_step"]
        }, f, indent=4)
    print(f"✅ Saved grid metadata to: {grid_metadata_output_path}")

    print("-" * 70)
    print("Preprocessing completed.")

if __name__ == "__main__":
    # You can specify the input JSON filename here.
    # Make sure 'fluid_simulation_input.json' (or whatever your input is)
    # has been run by the previous script to generate 'navier_stokes_results.json'
    # in the correct relative path (../data/testing-input-output/).
    post_process_simulation_results("navier_stokes_results.json")
