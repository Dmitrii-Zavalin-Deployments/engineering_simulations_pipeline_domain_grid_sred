#!/usr/bin/env bash
# ------------------------------------------------------------------
# 🚀 Pipeline Launcher — FreeCAD Domain Generation (STEP-based)
# Automates headless geometry parsing and metadata export
# ------------------------------------------------------------------

set -e  # Exit immediately on error

echo "🟢 Environment bootstrap: preparing FreeCAD run..."

# Optional: detect and validate FreeCAD executable
FREECAD_BINARY="./FreeCAD.AppImage"
if [[ ! -f "$FREECAD_BINARY" ]]; then
  echo "❌ FreeCAD binary not found at $FREECAD_BINARY"
  exit 1
fi

echo "🚀 Launching FreeCAD pipeline..."
QT_QPA_PLATFORM=offscreen "$FREECAD_BINARY" --console --py src/run_pipeline.py --resolution 0.01

echo "✅ FreeCAD pipeline execution completed."



