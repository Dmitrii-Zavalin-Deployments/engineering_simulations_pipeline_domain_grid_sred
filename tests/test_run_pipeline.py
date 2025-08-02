import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from src.run_pipeline import sanitize_payload, main, DEFAULT_RESOLUTION
from src.utils.coercion import coerce_numeric


class TestSanitizePayload(unittest.TestCase):
    def test_complete_domain(self):
        raw = {"domain_definition": {"x": "1", "y": "2", "z": "3", "width": "4", "height": "5", "depth": "6"}}
        expected = {
            "domain_definition": {
                "x": 1.0, "y": 2.0, "z": 3.0,
                "width": 4.0, "height": 5.0, "depth": 6.0
            }
        }
        result = sanitize_payload(raw)
        self.assertEqual(result, expected)

    def test_missing_fields(self):
        raw = {"domain_definition": {"x": "1"}}
        expected = {
            "domain_definition": {
                "x": 1.0, "y": 0.0, "z": 0.0,
                "width": 0.0, "height": 0.0, "depth": 0.0
            }
        }
        result = sanitize_payload(raw)
        self.assertEqual(result, expected)

    def test_empty_metadata(self):
        result = sanitize_payload({})
        expected = {
            "domain_definition": {
                "x": 0.0, "y": 0.0, "z": 0.0,
                "width": 0.0, "height": 0.0, "depth": 0.0
            }
        }
        self.assertEqual(result, expected)

    def test_width_clamping_on_misaligned_bounds(self):
        raw = {"domain_definition": {"min_x": "1.0", "max_x": "0.0"}}
        result = sanitize_payload(raw)
        domain = result["domain_definition"]
        self.assertIn("width", domain)
        self.assertIsInstance(coerce_numeric(domain["width"]), float)
        self.assertEqual(coerce_numeric(domain["width"]), 0.0)

    def test_fallback_on_invalid_width(self):
        raw = {"domain_definition": {"x": "1", "max_x": "5", "width": "invalid"}}
        result = sanitize_payload(raw)
        width = result["domain_definition"]["width"]
        self.assertEqual(width, 4.0)

    @patch("src.run_pipeline.coerce_numeric", side_effect=lambda val: None if val is None or val == "invalid" else float(val))
    def test_mocked_coercion_fallback(self, mock_coerce):
        raw = {
            "domain_definition": {
                "x": "1", "y": "0", "z": "0",
                "width": "invalid", "max_x": "5",
                "height": "0", "depth": "0"
            }
        }
        result = sanitize_payload(raw)
        self.assertEqual(result["domain_definition"]["width"], 4.0)
        mock_coerce.assert_any_call("invalid")


class TestPipelineMain(unittest.TestCase):
    @patch("src.run_pipeline.validate_step_file", return_value=True)
    @patch("os.path.isfile", return_value=True)
    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("src.run_pipeline.extract_bounding_box_with_gmsh", return_value={
        "min_x": 0, "max_x": 1,
        "min_y": 0, "max_y": 1,
        "min_z": 0, "max_z": 1,
        "nx": 10, "ny": 10, "nz": 10
    })
    @patch("src.run_pipeline.validate_domain_bounds")
    @patch("src.run_pipeline.enforce_profile")
    @patch("src.run_pipeline.open", new_callable=mock_open)
    @patch("src.run_pipeline.sys.exit")
    def test_main_pipeline_success(
        self, mock_exit, mock_open_fn, mock_enforce, mock_validate_bounds,
        mock_gmsh, mock_validate_step_file, mock_exists, mock_glob, mock_isfile
    ):
        mock_step_file = MagicMock(spec=Path)
        mock_step_file.name = "model.step"
        mock_glob.return_value = [mock_step_file]

        step_files = mock_glob.return_value
        # 🛡️ Revised guard to prevent IndexError from empty list
        assert step_files and isinstance(step_files[0], Path), "STEP file list is empty or invalid"

        main(resolution=DEFAULT_RESOLUTION)

        mock_gmsh.assert_called()
        mock_validate_bounds.assert_called()
        mock_enforce.assert_called()
        mock_open_fn.assert_called()
        mock_exit.assert_called_with(0)
        mock_validate_step_file.assert_called()

    @patch("src.run_pipeline.sys.exit", side_effect=SystemExit)
    @patch("pathlib.Path.exists", return_value=False)
    @patch("src.run_pipeline.log_error")
    def test_main_input_directory_missing(self, mock_log_error, mock_exists, mock_exit):
        with self.assertRaises(SystemExit):
            main(resolution=DEFAULT_RESOLUTION)
        mock_log_error.assert_called()
        mock_exit.assert_called_once_with(1)
        args, kwargs = mock_log_error.call_args
        self.assertIn("Input directory not found", args[0])
        self.assertTrue(kwargs.get("fatal"))

    def test_safe_list_indexing_guard(self):
        result_list = ["alpha", "beta", "gamma"]
        index = 1
        assert isinstance(result_list, list) and len(result_list) > index
        self.assertEqual(result_list[index], "beta")



