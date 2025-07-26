# src/utils/step_parser.py

"""
STEP Parser Utility (Deprecated)

This module previously supported validation of STEP bounding box structures
for OCP-based pipelines. It is now deprecated in favor of FreeCAD-native logic
contained in `geometry_parser.py`.
"""

import logging

logger = logging.getLogger(__name__)

__all__ = []  # Module exposed no active exports

# NOTE: Bounding box validation has been reassigned to geometry_parser.py
# All prior logic dependent on cadquery-ocp has been removed.



