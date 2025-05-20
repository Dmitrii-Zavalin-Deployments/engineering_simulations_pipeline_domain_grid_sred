import unittest
import os
import json
import numpy as np
from jsonschema import validate


class TestSimulationPreprocessing(unittest.TestCase):

    def setUp(self):
        """Load input JSON and define binary output file path"""
        self.input_json_path = "data/testing-input-output/fluid_simulation.json"
        self.binary_npy_path = "data/testing-input-output/fluid_simulation.npy"
        
        with open(self.input_json_path) as f:
            self.input_data = json.load(f)

    ### INPUT VALIDATION ###

    def test_json_schema(self):
        """Ensure input file follows defined JSON schema"""
        schema = {
            "type": "object",
            "properties": {
                "simulation_info": {"type": "object"},
                "global_parameters": {"type": "object"},
                "data_points": {"type": "array"}
            },
            "required": ["simulation_info", "global_parameters", "data_points"]
        }
        validate(instance=self.input_data, schema=schema)

    def test_physical_consistency(self):
        """Ensure extracted fluid properties remain realistic"""
        assert 101000 <= self.input_data["global_parameters"]["pressure"]["value"] <= 102000, "Pressure out of bounds!"
        assert 0.05 <= self.input_data["global_parameters"]["energy_dissipation_rate"]["value"] <= 0.5, "Energy dissipation unrealistic!"

    ### BINARY OUTPUT VALIDATION ###

    def test_binary_output_exists(self):
        """Ensure .npy binary format is correctly generated"""
        assert os.path.exists(self.binary_npy_path), f"Binary file missing at {self.binary_npy_path}!"

    def test_binary_data_integrity(self):
        """Ensure structured .npy file stores correct numerical fields"""
        assert os.path.exists(self.binary_npy_path), "Binary file missing, cannot test integrity."
        np_data = np.load(self.binary_npy_path)
        assert np_data.shape[0] > 0, "Binary data structure appears empty!"
        assert "velocity" in np_data.dtype.names, "Missing velocity field!"
        assert "pressure" in np_data.dtype.names, "Missing pressure field!"
        assert "turbulence_intensity" in np_data.dtype.names, "Missing turbulence field!"


if __name__ == "__main__":
    unittest.main()



