#!/bin/bash

# Collect all files recursively from src
src_files=$(find ./src -type f)
workflow_files=$(find ./.github/workflows -type f -name "*.yml")
unused_files=()

echo "🔍 Checking file references in src and .github/workflows..."

for file_path in $src_files; do
  file_name=$(basename "$file_path")

  # Skip __init__.py
  if [ "$file_name" = "__init__.py" ]; then
    continue
  fi

  referenced=false

  # Check other src files
  for other_path in $src_files; do
    if [ "$file_path" != "$other_path" ]; then
      if grep -q "$file_name" "$other_path"; then
        referenced=true
        break
      fi
    fi
  done

  # Check in workflow files
  if [ "$referenced" = false ]; then
    for wf_file in $workflow_files; do
      if grep -q "$file_name" "$wf_file"; then
        referenced=true
        break
      fi
    done
  fi

  if [ "$referenced" = false ]; then
    unused_files+=("$file_path")
  fi
done

# Show results
if [ ${#unused_files[@]} -eq 0 ]; then
  echo "✅ No unused files found."
  exit 0
fi

echo "🚫 Unused files found:"
for file in "${unused_files[@]}"; do
  echo "$file"
done

# Ask user for confirmation
read -p "Delete these files? (y/n): " confirm
if [ "$confirm" = "y" ]; then
  for file in "${unused_files[@]}"; do
    rm "$file"
  done
  echo "🗑️ Files deleted."

  # Git commit and push
  git add .
  git commit -m "🔧 Code cleanup: removed unused src files (excluding __init__.py)"
  git push
  echo "🚀 Changes committed and pushed."
else
  echo "❎ Skipping deletion."
fi



