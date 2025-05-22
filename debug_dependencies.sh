#!/bin/bash
set -e

echo "🔍 Checking installed Python packages..."
pip list

echo "📦 Installing pipdeptree if missing..."
pip install --quiet pipdeptree || echo "⚠️ Warning: pipdeptree installation failed!"

echo "📝 Checking dependency tree..."
pipdeptree > dependencies.txt || echo "⚠️ Warning: pipdeptree command failed!"

echo "✅ Debugging complete!"



