#!/bin/bash

set -euo pipefail

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'
VENV_DIR="py_env"
REQ_FILE="requirements.txt"
REQ_HASH_FILE="$VENV_DIR/requirements.sha256"
SRC_FILE="src/volt-gui.py"
CURRENT_HASH=""
STORED_HASH=""

cleanup() {
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        deactivate 2>/dev/null || true
    fi
}

check_commands() {
    for cmd in python3 pip; do
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

verify_files() {
    if [[ ! -f "$REQ_FILE" ]]; then
        echo -e "${RED}Error: Requirements file $REQ_FILE not found${NC}" >&2
        exit 1
    fi
    if [[ ! -f "$SRC_FILE" ]]; then
        echo -e "${RED}Error: Source file $SRC_FILE not found${NC}" >&2
        exit 1
    fi
}

update_dependencies() {
    CURRENT_HASH=$(shasum -a 256 "$REQ_FILE" | cut -d' ' -f1)
    STORED_HASH=$(cat "$REQ_HASH_FILE" 2>/dev/null || true)

    if [[ ! -f "$REQ_HASH_FILE" ]] || [[ "$CURRENT_HASH" != "$STORED_HASH" ]]; then
        echo -e "${BLUE}Updating dependencies...${NC}"
        pip install --upgrade pip
        pip install --no-cache-dir -r "$REQ_FILE"
        echo "$CURRENT_HASH" > "$REQ_HASH_FILE"
    else
        echo "Dependencies are up to date"
    fi
}

run_application() {
    echo -e "${BLUE}Running application in development mode...${NC}"
    echo "Source file: $SRC_FILE"
    echo "Virtual environment: $VENV_DIR"
    echo ""
    if ! python3 "$SRC_FILE"; then
        echo -e "\n${RED}Application exited with error${NC}" >&2
        exit 1
    fi
}

remove_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        echo -e "${BLUE}Removing virtual environment: $VENV_DIR${NC}"
        rm -rf "$VENV_DIR"
        echo "Virtual environment removed successfully"
    else
        echo "No virtual environment found at: $VENV_DIR"
    fi
}

main() {
    trap cleanup EXIT

    if [[ "${1:-}" == "-r" ]]; then
        remove_venv
        exit 0
    fi

    if [[ $EUID -eq 0 ]]; then
        echo -e "${RED}Error: Do not run the application with sudo${NC}" >&2
        echo "Please run without sudo: $0" >&2
        exit 1
    fi

    check_commands
    verify_files
    create_venv
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"
    update_dependencies
    echo -e "\nSetup complete! Starting application..."
    echo -e "${BLUE}────────────────────────────────────────${NC}"
    run_application
}

main "$@"
