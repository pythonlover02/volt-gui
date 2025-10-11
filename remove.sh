#!/bin/bash

set -euo pipefail

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="/usr/local/bin"
TARGETS=("volt" "volt-gui" "volt-helper")
DESKTOP_FILE="/usr/share/applications/volt-gui.desktop"

if [[ $EUID -ne 0 ]]; then
  echo -e "${RED}Error: Please run this script as root (use sudo)${NC}" >&2
  exit 1
fi

echo -e "${BLUE}Removing installed files...${NC}"

for target in "${TARGETS[@]}"; do
  file="$INSTALL_DIR/$target"
  if [[ -f "$file" ]]; then
    rm -v "$file"
  else
    echo "Warning: $file not found"
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
