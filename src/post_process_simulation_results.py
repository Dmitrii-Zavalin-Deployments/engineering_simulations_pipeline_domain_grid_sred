import os
import json
import numpy as np

def post_process_simulation_results(input_json_filename="navier_stokes_results.json",
                                    initial_data_filename="initial_data.json",  # Using initial_data.json for fluid properties
                                    output_dir="data/testing-input-output"):  # Updated output directory
    """
    Extracts velocity fields, pressure, and turbulence data from simulation results
    and outputs structured binary (.npy) files in `data/testing-input-output/`.

    Args:
        input_json_filename (str): Simulation results JSON file (navier_stokes_results.json).
        initial_data_filename (str): Initial fluid properties JSON file (initial_data.json).
        output_dir (str): Directory for storing processed .npy files.
    """
    print("Preprocessing engineering_simulations_pipeline_preprocessing_sred")
    print("-" * 70)

    # Determine paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data", "testing-input-output")  # Standardized data directory
    
    results_filepath = os.path.join(data_dir, input_json_filename)
    initial_data_filepath = os.path.join(data_dir, initial_data_filename)  # Path to initial_data.json
    
    output_filepath = os.path.join(data_dir)  # Store processed data directly in `data/testing-input-output/`

    # Validate input files
    if not os.path.exists(results_filepath):
        print(f"❌ Error: Simulation results file not found at {results_filepath}")
        return
    if not os.path.exists(initial_data_filepath):
        print(f"❌ Error: Initial data file not found at {initial_data_filepath}. Cannot retrieve fluid properties.")
        return

    # Ensure output directory exists
    os.makedirs(output_filepath, exist_ok=True)

    print(f"Loading simulation results from: {results_filepath}")
    try:
        with open(results_filepath, "r") as f:
            results_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON decoding error: {e}")
        return

    print(f"Loading initial data from: {initial_data_filepath}")
    try:
        with open(initial_data_filepath, "r") as f:
            initial_data = json.load(f)
        density = initial_data["fluid_properties"]["density"]
        simulation_parameters = initial_data["simulation_parameters"]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Error loading initial data: {e}")
        return

    # Extract simulation results
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
    np.save(os.path.join(output_filepath, "time_points.npy"), time_points)
    print(f"✅ Saved time points to: {output_filepath}/time_points.npy")

    # Reshape velocity and pressure history
    velocity_grid_history = velocity_history.reshape(num_time_steps, grid_shape[2], grid_shape[1], grid_shape[0], 3)
    np.save(os.path.join(output_filepath, "velocity_history.npy"), velocity_grid_history)
    print(f"✅ Saved velocity history to: {output_filepath}/velocity_history.npy")

    pressure_grid_history = pressure_history.reshape(num_time_steps, grid_shape[2], grid_shape[1], grid_shape[0])
    np.save(os.path.join(output_filepath, "pressure_history.npy"), pressure_grid_history)
    print(f"✅ Saved pressure history to: {output_filepath}/pressure_history.npy")

    # Compute turbulence kinetic energy
    kinetic_energy_history = 0.5 * density * np.linalg.norm(velocity_history, axis=2) ** 2
    kinetic_energy_grid_history = kinetic_energy_history.reshape(num_time_steps, grid_shape[2], grid_shape[1], grid_shape[0])
    np.save(os.path.join(output_filepath, "turbulence_kinetic_energy_history.npy"), kinetic_energy_grid_history)
    print(f"✅ Saved turbulence kinetic energy history to: {output_filepath}/turbulence_kinetic_energy_history.npy")

    # Save node coordinates
    np.save(os.path.join(output_filepath, "nodes_coords.npy"), np.array(mesh_info["nodes_coords"]))
    print(f"✅ Saved node coordinates to: {output_filepath}/nodes_coords.npy")

    # Save metadata
    grid_metadata = {
        "nodes": mesh_info["nodes"],
        "grid_shape": mesh_info["grid_shape"],
        "dx": mesh_info["dx"],
        "dy": mesh_info["dy"],
        "dz": mesh_info["dz"],
        "num_time_steps": num_time_steps,
        "total_time": simulation_parameters["total_time"],
        "time_step_size": simulation_parameters["time_step"]
    }
    with open(os.path.join(output_filepath, "grid_metadata.json"), "w") as f:
        json.dump(grid_metadata, f, indent=4)
    print(f"✅ Saved grid metadata to: {output_filepath}/grid_metadata.json")

    print("-" * 70)
    print("Preprocessing completed.")

if __name__ == "__main__":
    post_process_simulation_results()
