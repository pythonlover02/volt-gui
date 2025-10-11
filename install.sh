#!/bin/bash

set -euo pipefail

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="/usr/local/bin"
BIN_DIR="bin"
EXECUTABLE="$BIN_DIR/volt-gui"
HELPER_SCRIPT="scripts/volt-helper"
DESKTOP_FILE="/usr/share/applications/volt-gui.desktop"

if [[ $EUID -ne 0 ]]; then
  echo -e "${RED}Error: Please run this script as root (use sudo)${NC}" >&2
  exit 1
fi

if [[ ! -d "$BIN_DIR" ]]; then
  echo -e "${RED}Error: bin directory not found. Run make-pyinstaller.sh or make-nuitka.sh first.${NC}" >&2
  exit 1
fi

if [[ ! -f "$EXECUTABLE" ]]; then
  echo -e "${RED}Error: Executable 'volt-gui' not found in bin directory. Run make-pyinstaller.sh or make-nuitka.sh first.${NC}" >&2
  exit 1
fi

if [[ ! -f "$HELPER_SCRIPT" ]]; then
  echo -e "${RED}Error: Helper script $HELPER_SCRIPT not found.${NC}" >&2
  exit 1
fi

echo -e "${BLUE}Installing main executable...${NC}"
mkdir -p "$INSTALL_DIR"
install -v -m 755 -T "$EXECUTABLE" "$INSTALL_DIR/volt-gui"

echo -e "\n${BLUE}Installing helper script...${NC}"
install -v -m 755 -T "$HELPER_SCRIPT" "$INSTALL_DIR/volt-helper"

echo -e "\n${BLUE}Creating desktop entry...${NC}"
mkdir -p "$(dirname "$DESKTOP_FILE")"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=volt-gui
Comment=A simple GUI program to modify and create the "volt" script and more
Exec=volt-gui
Icon=preferences-system
Terminal=false
Type=Application
Categories=Utility;
EOF

echo "Desktop entry created at $DESKTOP_FILE"

echo -e "\n${BLUE}Updating desktop database...${NC}"
update-desktop-database "$(dirname "$DESKTOP_FILE")"

echo -e "\nInstallation completed successfully!"
echo "You can now run 'volt-gui' from the terminal or application menu."
