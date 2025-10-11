#!/bin/bash

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

VENV_DIR="py_env"
REQ_FILE="requirements.txt"
REQ_HASH_FILE="$VENV_DIR/requirements.sha256"
SRC_FILE="src/volt-gui.py"
HELPER_SCRIPT="scripts/volt-helper"
INSTALL_DIR="/usr/local/bin"

cleanup() {
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        deactivate 2>/dev/null || true
    fi
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
        echo -e "${CYAN}Creating python3 virtual environment...${NC}"
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
    local current_hash stored_hash
    current_hash=$(shasum -a 256 "$REQ_FILE" | cut -d' ' -f1)
    stored_hash=$(cat "$REQ_HASH_FILE" 2>/dev/null || true)

    if [[ ! -f "$REQ_HASH_FILE" ]] || [[ "$current_hash" != "$stored_hash" ]]; then
        echo -e "${CYAN}Updating dependencies...${NC}"
        pip install --upgrade pip
        pip install --no-cache-dir -r "$REQ_FILE"
        echo "$current_hash" > "$REQ_HASH_FILE"
    else
        echo -e "${GREEN}Dependencies are up to date${NC}"
    fi
}

install_helper() {
    if [[ ! -f "$HELPER_SCRIPT" ]]; then
        echo -e "${RED}Error: Helper script $HELPER_SCRIPT not found${NC}" >&2
        exit 1
    fi

    echo -e "${CYAN}Installing helper script...${NC}"
    cp "$HELPER_SCRIPT" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/$(basename "$HELPER_SCRIPT")"
    echo -e "${GREEN}Helper script installed to: ${YELLOW}$INSTALL_DIR/$(basename "$HELPER_SCRIPT")${NC}"
}

run_application() {
    echo -e "${CYAN}Running application in development mode...${NC}"
    echo -e "${YELLOW}Source file: $SRC_FILE${NC}"
    echo -e "${YELLOW}Virtual environment: $VENV_DIR${NC}"
    echo ""

    if ! python3 "$SRC_FILE"; then
        echo -e "\n${RED}Application exited with error${NC}" >&2
        exit 1
    fi
}

remove_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        echo -e "${CYAN}Removing virtual environment: $VENV_DIR${NC}"
        rm -rf "$VENV_DIR"
        echo -e "${GREEN}Virtual environment removed successfully${NC}"
    else
        echo -e "${YELLOW}No virtual environment found at: $VENV_DIR${NC}"
    fi
}

main() {
    trap cleanup EXIT

    if [[ "${1:-}" == "-r" ]]; then
        remove_venv
        exit 0
    fi

    if [[ "${1:-}" == "-c" ]]; then
        if [[ $EUID -ne 0 ]]; then
            echo -e "${RED}Error: Installing helper script requires sudo privileges${NC}" >&2
            echo -e "${YELLOW}Please run: sudo $0 -c${NC}" >&2
            exit 1
        fi
        install_helper
        exit 0
    fi

    if [[ $EUID -eq 0 ]]; then
        echo -e "${RED}Error: Do not run the application with sudo${NC}" >&2
        echo -e "${YELLOW}Please run without sudo: $0${NC}" >&2
        exit 1
    fi

    check_commands
    verify_files
    create_venv

    echo -e "${CYAN}Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"

    update_dependencies

    echo -e "\n${GREEN}Setup complete! Starting application...${NC}"
    echo -e "${CYAN}────────────────────────────────────────${NC}"

    run_application
}

main "$@"
