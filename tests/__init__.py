# tests/__init__.py

import sys
from pathlib import Path

# Ensure the 'src' directory is in the module search path
SRC_ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_ROOT))



