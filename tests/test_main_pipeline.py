# tests/test_main_pipeline.py

import unittest
import os
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from src.run_pipeline import main, DEFAULT_RESOLUTION


class TestMainPipeline(unittest.TestCase):
    @patch.dict(os.environ, {"PIPELINE_TEST_MODE": "true"})
    @patch("src.run_pipeline.sys.exit")
    @patch("src.run_pipeline.log_checkpoint")
    @patch("src.run_pipeline.validate_step_file", return_value=True)
    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("src.run_pipeline.extract_bounding_box_with_gmsh", return_value={"x": 0, "y": 0, "z": 0})
    @patch("src.run_pipeline.validate_domain_bounds")
    @patch("src.run_pipeline.enforce_profile")
    @patch("src.run_pipeline.open", new_callable=mock_open)
    def test_main_pipeline_success(*mocks):
        mock_glob = mocks[4]
        mock_step_file = MagicMock(spec=Path)
        mock_step_file.name = "model.STEP"
        mock_step_file.suffix = ".STEP"
        mock_glob.return_value = [mock_step_file]

        result = main(resolution=DEFAULT_RESOLUTION)
        assert result == 0

    @patch.dict(os.environ, {"PIPELINE_TEST_MODE": "true"})
    @patch("src.run_pipeline.sys.exit")
    @patch("pathlib.Path.exists", return_value=False)
    @patch("src.run_pipeline.log_error")
    def test_main_input_directory_missing(mock_log_error, *_):
        result = main(resolution=DEFAULT_RESOLUTION)
        assert result == 1
        mock_log_error.assert_called()
        args, kwargs = mock_log_error.call_args
        assert "Input directory not found" in args[0]
        assert kwargs.get("fatal")

    @patch.dict(os.environ, {"PIPELINE_TEST_MODE": "true"})
    @patch("builtins.print")
    @patch("src.run_pipeline.validate_step_file", return_value=True)
    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("src.run_pipeline.extract_bounding_box_with_gmsh", return_value={"x": 0, "y": 0, "z": 0})
    @patch("src.run_pipeline.validate_domain_bounds")
    @patch("src.run_pipeline.enforce_profile")
    def test_debug_json_enabled(mock_enforce, mock_validate_bounds, mock_gmsh,
                                mock_exists, mock_glob, mock_validate_step_file, mock_print):
        mock_step_file = MagicMock(spec=Path)
        mock_step_file.name = "debug.Step"
        mock_step_file.suffix = ".Step"
        mock_glob.return_value = [mock_step_file]

        result = main(resolution=DEFAULT_RESOLUTION, debug_json=True)
        assert result == 0
        mock_print.assert_called()
        printed = mock_print.call_args[0][0]
        assert '"domain_definition"' in printed

    @patch.dict(os.environ, {"PIPELINE_TEST_MODE": "true"})
    @patch("pathlib.Path.exists", side_effect=lambda: True)
    @patch("pathlib.Path.rename")
    @patch("src.run_pipeline.validate_step_file", return_value=True)
    @patch("pathlib.Path.glob")
    @patch("src.run_pipeline.extract_bounding_box_with_gmsh", return_value={"x": 0, "y": 0, "z": 0})
    @patch("src.run_pipeline.validate_domain_bounds")
    @patch("src.run_pipeline.enforce_profile")
    @patch("src.run_pipeline.open", new_callable=mock_open)
    def test_output_backup_triggered(mock_open_fn, mock_enforce, mock_validate_bounds,
                                     mock_gmsh, mock_glob, mock_validate_step_file,
                                     mock_rename, mock_exists):
        mock_step_file = MagicMock(spec=Path)
        mock_step_file.name = "domain.STEP"
        mock_step_file.suffix = ".STEP"
        mock_glob.return_value = [mock_step_file]

        result = main(resolution=DEFAULT_RESOLUTION)
        assert result == 0
        mock_rename.assert_called()



