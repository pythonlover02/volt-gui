#!/bin/bash

# Exit immediately on errors, unset variables, and pipe failures
set -euo pipefail

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VENV_DIR="py_env"
REQ_FILE="requirements.txt"
REQ_HASH_FILE="$VENV_DIR/requirements.sha256"
SRC_FILE="src/volt-gui.py"
RELEASE_DIR="release"
BASE_FILENAME=$(basename "$SRC_FILE" .py)

# Nuitka options for the application
NUITKA_OPTS=(
    "--onefile"
    "--output-filename=$BASE_FILENAME"
    "--assume-yes-for-downloads"
    "--enable-plugin=pyside6"
)

# Cleanup function
cleanup() {
    rm -rf "$BASE_FILENAME.build/" "$BASE_FILENAME.dist/" "$BASE_FILENAME.onefile-build/" 2>/dev/null || true
}

# Check for required commands
check_commands() {
    local commands=("python3" "pip")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            echo -e "${RED}Error: Required command '$cmd' not found${NC}" >&2
            exit 1
        fi
    done
}

# Create virtual environments
create_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        echo -e "${CYAN}Creating python3 virtual environment...${NC}"
        python3 -m venv "$VENV_DIR"
    fi
}

# Verify requirements file
verify_requirements() {
    if [[ ! -f "$REQ_FILE" ]]; then
        echo -e "${RED}Error: Requirements file $REQ_FILE not found${NC}" >&2
        exit 1
    fi
}

# Update dependencies if needed
update_dependencies() {
    local current_hash stored_hash
    current_hash=$(shasum -a 256 "$REQ_FILE" | cut -d' ' -f1)
    stored_hash=$(cat "$REQ_HASH_FILE" 2>/dev/null || true)

    if [[ ! -f "$REQ_HASH_FILE" ]] || [[ "$current_hash" != "$stored_hash" ]]; then
        echo -e "${CYAN}Updating dependencies...${NC}"
        pip install --upgrade pip
        pip install --no-cache-dir -r "$REQ_FILE"
        echo "$current_hash" > "$REQ_HASH_FILE"
    fi
}

# Main build process
build_executable() {
    echo -e "${CYAN}Building executable with Nuitka...${NC}"
    echo -e "${YELLOW}Nuitka options: ${NUITKA_OPTS[*]}${NC}"
    
    if ! nuitka "${NUITKA_OPTS[@]}" "$SRC_FILE"; then
        echo -e "${RED}Error: Nuitka failed to build executable${NC}" >&2
        exit 1
    fi
}

# Move to release directory
move_to_release() {
    mkdir -p "$RELEASE_DIR"
    mv "$BASE_FILENAME" "$RELEASE_DIR/" 2>/dev/null || true
}

# Main execution
main() {
    trap cleanup EXIT
    check_commands
    verify_requirements
    create_venv
    
    # Activate virtual environment
    echo -e "${CYAN}Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"
    
    update_dependencies
    build_executable
    move_to_release

    echo -e "\n${GREEN}Build successful!${NC}"
    echo -e "Executable: ${YELLOW}$RELEASE_DIR/$(basename "$BASE_FILENAME")${NC}"
    
    # Show file size
    if command -v du &> /dev/null; then
        local size=$(du -h "$RELEASE_DIR"/* 2>/dev/null | cut -f1 || echo "Unknown")
        echo -e "File size: ${YELLOW}$size${NC}"
    fi
}

# Run main function
main