#!/bin/bash
set -e

echo "🔍 Checking installed Python packages..."
pip list

echo "📝 Checking dependency tree..."
pipdeptree > dependencies.txt

echo "📦 Checking PyOpenVDB availability..."
pip search pyopenvdb || echo "⚠️ PyOpenVDB not found"

echo "✅ Debugging complete!"



