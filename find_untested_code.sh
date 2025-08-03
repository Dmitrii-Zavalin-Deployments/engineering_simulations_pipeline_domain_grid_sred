#!/bin/bash

src_dir="./src"
test_dir="./tests"

echo "📂 Confirm that this script is in the same directory as the 'src' and 'tests' folders."
echo "👉 Press Enter (or any key) to continue..."
read -n 1 -s

echo "🔍 Scanning for missing unit tests..."

# Loop through all Python files in src directory
find "$src_dir" -type f -name "*.py" | while read -r src_file; do
    # Get relative path and filename
    rel_path="${src_file#$src_dir/}"
    filename="$(basename "$src_file")"
    test_filename="test_${filename}"

    # Construct expected test path
    test_path="${test_dir}/${rel_path%/*}/${test_filename}"

    if [ ! -f "$test_path" ]; then
        echo "🚫 Missing test for core file: $filename"
        echo "   ➤ Core file path: $src_file"
        echo "   ➤ Expected test path: $test_path"
        echo
    fi
done



