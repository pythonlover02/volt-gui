#!/bin/bash

# configuration
VENV_DIR="py_env"
REQ_FILE="requirements.txt"
REQ_HASH_FILE="$VENV_DIR/requirements.hash"
SRC_FILE="src/volt-gui.py"
RELEASE_DIR="release"
BASE_FILENAME=$(basename "$SRC_FILE" .py)
SPEC_FILE="$BASE_FILENAME.spec"

# create fresh venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python -m venv "$VENV_DIR"
fi

# activate venv, update dependencies and build
source "$VENV_DIR/bin/activate"

current_hash=$(md5sum "$REQ_FILE" 2>/dev/null | cut -d' ' -f1)
stored_hash=$(cat "$REQ_HASH_FILE" 2>/dev/null)

if [ ! -f "$REQ_HASH_FILE" ] || [ "$current_hash" != "$stored_hash" ]; then
    echo "Updating dependencies..."
    pip install --upgrade pip
    pip install -r "$REQ_FILE"
    echo "$current_hash" > "$REQ_HASH_FILE"
fi

echo "Building executable..."
pyinstaller --onefile "$SRC_FILE"

# move to release folder
mkdir -p "$RELEASE_DIR"
cp "dist/$BASE_FILENAME" "$RELEASE_DIR/"

# cleanup
rm -rf dist build __pycache__ "$SPEC_FILE"

echo "Build successful! Executable: $RELEASE_DIR/$BASE_FILENAME"
deactivate

