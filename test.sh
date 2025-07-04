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
HELPER_SCRIPT="scripts/volt-helper"
INSTALL_DIR="/usr/local/bin"

# Default behavior
COPY_HELPER=false

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

# Create virtual environment
create_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        echo -e "${CYAN}Creating python3 virtual environment...${NC}"
        python3 -m venv "$VENV_DIR"
    fi
}

# Verify required files
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
    else
        echo -e "${GREEN}Dependencies are up to date${NC}"
    fi
}

# Install helper script
install_helper() {
    if [[ "$COPY_HELPER" == true ]]; then
        if [[ -f "$HELPER_SCRIPT" ]]; then
            echo -e "${CYAN}Installing helper script...${NC}"
            
            # Check if we need sudo
            if [[ ! -w "$INSTALL_DIR" ]]; then
                echo -e "${YELLOW}Installing to $INSTALL_DIR requires sudo privileges${NC}"
                sudo cp "$HELPER_SCRIPT" "$INSTALL_DIR/"
                sudo chmod +x "$INSTALL_DIR/$(basename "$HELPER_SCRIPT")"
            else
                cp "$HELPER_SCRIPT" "$INSTALL_DIR/"
                chmod +x "$INSTALL_DIR/$(basename "$HELPER_SCRIPT")"
            fi
            
            echo -e "${GREEN}Helper script installed to: ${YELLOW}$INSTALL_DIR/$(basename "$HELPER_SCRIPT")${NC}"
        else
            echo -e "${YELLOW}Warning: Helper script $HELPER_SCRIPT not found, skipping installation${NC}"
        fi
    fi
}

# Run the application
run_application() {
    echo -e "${CYAN}Running application in development mode...${NC}"
    echo -e "${YELLOW}Source file: $SRC_FILE${NC}"
    echo -e "${YELLOW}Virtual environment: $VENV_DIR${NC}"
    echo ""
    
    # Run the Python application
    if ! python3 "$SRC_FILE"; then
        echo -e "\n${RED}Application exited with error${NC}" >&2
        exit 1
    fi
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c)
                COPY_HELPER=true
                shift
                ;;
            *)
                echo -e "${RED}Error: Unknown option '$1'${NC}" >&2
                echo -e "${CYAN}Usage: $0 [-c]${NC}" >&2
                echo -e "  -c    Copy volt-helper script to $INSTALL_DIR" >&2
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    trap EXIT
    
    # Parse command line arguments
    parse_args "$@"
    
    check_commands
    verify_files
    create_venv
    
    # Activate virtual environment
    echo -e "${CYAN}Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"
    
    update_dependencies
    install_helper
    
    echo -e "\n${GREEN}Setup complete! Starting application...${NC}"
    echo -e "${CYAN}────────────────────────────────────────${NC}"
    
    run_application
}

# Run main function with all arguments
main "$@"