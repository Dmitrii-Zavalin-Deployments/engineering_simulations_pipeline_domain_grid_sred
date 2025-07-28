# tests/test_run_pipeline.py

import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from src.run_pipeline import sanitize_payload, main, DEFAULT_RESOLUTION

class TestSanitizePayload(unittest.TestCase):
    def test_complete_domain(self):
        raw = {"domain_definition": {"x": "1", "y": "2", "z": "3", "width": "4", "height": "5", "depth": "6"}}
        expected = {"domain_definition": {"x": 1.0, "y": 2.0, "z": 3.0, "width": 4.0, "height": 5.0, "depth": 6.0}}
        result = sanitize_payload(raw)
        self.assertEqual(result, expected)

    def test_missing_fields(self):
        raw = {"domain_definition": {"x": "1"}}
        expected = {"domain_definition": {"x": 1.0, "y": 0.0, "z": 0.0, "width": 0.0, "height": 0.0, "depth": 0.0}}
        result = sanitize_payload(raw)
        self.assertEqual(result, expected)

    def test_empty_metadata(self):
        result = sanitize_payload({})
        expected = {"domain_definition": {"x": 0.0, "y": 0.0, "z": 0.0, "width": 0.0, "height": 0.0, "depth": 0.0}}
        self.assertEqual(result, expected)

class TestPipelineMain(unittest.TestCase):
    @patch("pathlib.Path.glob", return_value=[MagicMock(name="mock.step", spec=Path)])
    @patch("pathlib.Path.exists", return_value=True)
    @patch("src.run_pipeline.extract_bounding_box_with_gmsh", return_value={"x": 1, "y": 2, "z": 3, "width": 4, "height": 5, "depth": 6})
    @patch("src.run_pipeline.validate_domain_bounds")
    @patch("src.run_pipeline.enforce_profile")
    @patch("src.run_pipeline.open", new_callable=mock_open)
    @patch("src.run_pipeline.sys.exit")
    def test_main_pipeline_success(
        self, mock_exit, mock_open_fn, mock_enforce, mock_validate, mock_gmsh,
        mock_exists, mock_glob
    ):
        main(resolution=DEFAULT_RESOLUTION)
        mock_gmsh.assert_called()
        mock_validate.assert_called()
        mock_enforce.assert_called()
        mock_open_fn.assert_called()
        mock_exit.assert_called_with(0)

    @patch("src.run_pipeline.sys.exit")  # ✅ Prevent actual exit
    @patch("pathlib.Path.glob", return_value=[])  # ✅ Prevent IndexError
    @patch("pathlib.Path.exists", return_value=False)  # ✅ Simulate missing dir
    @patch("src.run_pipeline.log_error")
    def test_main_input_directory_missing(self, mock_log_error, mock_exists, mock_glob, mock_exit):
        main(resolution=DEFAULT_RESOLUTION)
        mock_log_error.assert_called()
        mock_exit.assert_called_once_with(1)
        args, kwargs = mock_log_error.call_args
        assert "Input directory not found" in args[0]
        assert kwargs.get("fatal") is True


