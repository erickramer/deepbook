#!/bin/sh
# Custom pre-commit hook that uses a local cache directory

# Set the PRE_COMMIT_HOME environment variable to use a local cache
export PRE_COMMIT_HOME="$(git rev-parse --show-toplevel)/.pre-commit-cache"

# Create the directory if it doesn't exist
mkdir -p "$PRE_COMMIT_HOME"

# Activate the virtual environment and run pre-commit
VENV="$(git rev-parse --show-toplevel)/test_venv"
if [ -d "$VENV" ]; then
  # If test_venv exists, use it
  "$VENV/bin/pre-commit" run --all-files
else
  # Check if pre-commit is installed globally
  if command -v pre-commit >/dev/null 2>&1; then
    pre-commit run --all-files
  else
    echo "Warning: pre-commit is not installed. Skipping checks."
    echo "Run 'make hooks' to set up pre-commit hooks."
    exit 0
  fi
fi
