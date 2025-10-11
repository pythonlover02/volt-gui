#!/bin/bash

set -euo pipefail

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

VENV_DIR="py_env"
REQ_FILE="requirements.txt"
REQ_HASH_FILE="$VENV_DIR/requirements.sha256"
SRC_FILE="src/volt-gui.py"
BIN_DIR="bin"
BASE_FILENAME=$(basename "$SRC_FILE" .py)

NUITKA_OPTS=(
    "--onefile"
    "--output-filename=$BASE_FILENAME"
    "--assume-yes-for-downloads"
    "--enable-plugin=pyside6"
)

cleanup() {
    rm -rf "$BASE_FILENAME.build/" "$BASE_FILENAME.dist/" "$BASE_FILENAME.onefile-build/" 2>/dev/null || true
}

check_commands() {
    local commands=("python3" "pip")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            echo -e "${RED}Error: Required command '$cmd' not found${NC}" >&2
            exit 1
        fi
    done
}

create_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        echo -e "${BLUE}Creating python3 virtual environment...${NC}"
        python3 -m venv "$VENV_DIR"
    fi
}

verify_requirements() {
    if [[ ! -f "$REQ_FILE" ]]; then
        echo -e "${RED}Error: Requirements file $REQ_FILE not found${NC}" >&2
        exit 1
    fi
}

update_dependencies() {
    local current_hash stored_hash
    current_hash=$(shasum -a 256 "$REQ_FILE" | cut -d' ' -f1)
    stored_hash=$(cat "$REQ_HASH_FILE" 2>/dev/null || true)

    if [[ ! -f "$REQ_HASH_FILE" ]] || [[ "$current_hash" != "$stored_hash" ]]; then
        echo -e "${BLUE}Updating dependencies...${NC}"
        pip install --upgrade pip
        pip install --no-cache-dir -r "$REQ_FILE"
        echo "$current_hash" > "$REQ_HASH_FILE"
    fi
}

build_executable() {
    echo -e "${BLUE}Building executable with Nuitka...${NC}"
    echo -e "Nuitka options: ${NUITKA_OPTS[*]}"

    if ! nuitka "${NUITKA_OPTS[@]}" "$SRC_FILE"; then
        echo -e "${RED}Error: Nuitka failed to build executable${NC}" >&2
        exit 1
    fi
}

move_to_bin() {
    mkdir -p "$BIN_DIR"
    mv "$BASE_FILENAME" "$BIN_DIR/" 2>/dev/null || true
}

main() {
    trap cleanup EXIT
    check_commands
    verify_requirements
    create_venv

    echo -e "${BLUE}Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"

    update_dependencies
    build_executable
    move_to_bin

    echo -e "\nBuild successful!"
    echo -e "Executable: $BIN_DIR/$(basename "$BASE_FILENAME")"

    if command -v du &> /dev/null; then
        local size=$(du -h "$BIN_DIR"/* 2>/dev/null | cut -f1 || echo "Unknown")
        echo -e "File size: $size"
    fi
}

main
