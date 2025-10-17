#!/bin/bash

set -euo pipefail

RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m"
INSTALL_DIR="/usr/local/bin"
TARGETS=("volt" "volt-gui" "volt-helper")
DESKTOP_FILE="/usr/share/applications/volt-gui.desktop"
FILE=""

check_commands() {
    for cmd in rm dirname update-desktop-database; do
        if ! command -v "$cmd" &> /dev/null; then
            echo -e "${RED}Error: Required command "$cmd" not found${NC}" >&2
            exit 1
        fi
    done
}

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}Error: Please run this script as root (use sudo)${NC}" >&2
    exit 1
fi

check_commands

echo -e "${BLUE}Removing installed files...${NC}"

for target in "${TARGETS[@]}"; do
    FILE="$INSTALL_DIR/$target"
    if [[ -f "$FILE" ]]; then
        rm -v "$FILE"
    else
        echo "Warning: $FILE not found"
    fi
done

if [[ -f "$DESKTOP_FILE" ]]; then
    rm -v "$DESKTOP_FILE"
    echo -e "\n${BLUE}Updating desktop database...${NC}"
    update-desktop-database "$(dirname "$DESKTOP_FILE")"
else
    echo "Warning: Desktop entry $DESKTOP_FILE not found"
fi

echo -e "\nRemoval completed successfully!"
