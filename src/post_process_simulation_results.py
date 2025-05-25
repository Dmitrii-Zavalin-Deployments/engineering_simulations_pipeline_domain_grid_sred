import os
import json
import numpy as np

def post_process_simulation_results(input_json_filename="navier_stokes_results.json",
                                    initial_data_filename="initial_data.json", # Changed to initial_data.json
                                    output_dir="processed_data"):
    """
    Extracts velocity fields, pressure, and (placeholder for) turbulence from simulation results
    and outputs structured binary (.npy) files.

    Args:
        input_json_filename (str): The name of the input JSON file containing simulation results (navier_stokes_results.json).
        initial_data_filename (str): The name of the initial data JSON file (initial_data.json)
                                       to retrieve fluid properties and simulation parameters.
        output_dir (str): The directory where the processed .npy files will be saved.
    """
    print("Preprocessing engineering_simulations_pipeline_preprocessing_sred")
    print("-" * 70)

    # Determine input and output paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data", "testing-input-output") # Consistent data directory
    
    results_filepath = os.path.join(data_dir, input_json_filename)
    initial_data_filepath = os.path.join(data_dir, initial_data_filename) # Path to initial_data.json
    
    output_filepath = os.path.join(current_dir, output_dir) # Output is directly from src/ (or your project root)

    if not os.path.exists(results_filepath):
        print(f"❌ Error: Simulation results JSON file not found at {results_filepath}")
        return
    
    if not os.path.exists(initial_data_filepath):
        print(f"❌ Error: Initial data JSON file not found at {initial_data_filepath}. Cannot get fluid properties/simulation parameters.")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_filepath, exist_ok=True)

    print(f"Loading simulation results from: {results_filepath}")
    try:
        with open(results_filepath, "r") as f:
            results_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON from {results_filepath}: {e}")
        return
    except Exception as e:
        print(f"❌ An unexpected error occurred while loading {results_filepath}: {e}")
        return

    print(f"Loading initial data from: {initial_data_filepath}")
    try:
        with open(initial_data_filepath, "r") as f:
            initial_data = json.load(f)
        
        density = initial_data["fluid_properties"]["density"]
        simulation_parameters = initial_data["simulation_parameters"]
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON from {initial_data_filepath}: {e}")
        return
    except KeyError as e:
        print(f"❌ Error: Missing key '{e}' in {initial_data_filepath}. Check JSON structure for fluid_properties or simulation_parameters.")
        return
    except Exception as e:
        print(f"❌ An unexpected error occurred while loading {initial_data_filepath}: {e}")
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

    # Reshape velocity and pressure history to 3D grid shape
    # For velocity, it's (num_nodes, 3) -> (Nz, Ny, Nx, 3)
    # For pressure, it's (num_nodes,) -> (Nz, Ny, Nx)
    
    # The grid_shape from mesh_info is (Nx, Ny, Nz).
    # When reshaping from a 1D array filled by (k, j, i) loop (outer k, inner i),
    # the numpy reshape order should match (Nz, Ny, Nx) for consistent 3D indexing.
    # The original create_structured_grid_info fills nodes in k (outer), j, i (inner) order.
    # So, a simple reshape to (Nz, Ny, Nx, ...) should be correct.
    
    # Note: velocity_history is (num_time_steps, num_nodes, 3)
    velocity_grid_history = velocity_history.reshape(num_time_steps, grid_shape[2], grid_shape[1], grid_shape[0], 3)
    velocity_output_path = os.path.join(output_filepath, "velocity_history.npy")
    np.save(velocity_output_path, velocity_grid_history)
    print(f"✅ Saved velocity history (shape: {velocity_grid_history.shape}) to: {velocity_output_path}")

    # Note: pressure_history is (num_time_steps, num_nodes,)
    pressure_grid_history = pressure_history.reshape(num_time_steps, grid_shape[2], grid_shape[1], grid_shape[0])
    pressure_output_path = os.path.join(output_filepath, "pressure_history.npy")
    np.save(pressure_output_path, pressure_grid_history)
    print(f"✅ Saved pressure history (shape: {pressure_grid_history.shape}) to: {pressure_output_path}")

    # Placeholder for turbulence data (e.g., Kinetic Energy)
    # Using the 'density' loaded from initial_data.json
    kinetic_energy_history = 0.5 * density * np.linalg.norm(velocity_history, axis=2)**2
    kinetic_energy_grid_history = kinetic_energy_history.reshape(num_time_steps, grid_shape[2], grid_shape[1], grid_shape[0])

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
            "total_time": simulation_parameters["total_time"], # Using loaded simulation_parameters
            "time_step_size": simulation_parameters["time_step"] # Using loaded simulation_parameters
        }, f, indent=4)
    print(f"✅ Saved grid metadata to: {grid_metadata_output_path}")

    print("-" * 70)
    print("Preprocessing completed.")

if __name__ == "__main__":
    # Call the function with both the results JSON and the initial data JSON
    post_process_simulation_results(input_json_filename="navier_stokes_results.json",
                                    initial_data_filename="initial_data.json")
