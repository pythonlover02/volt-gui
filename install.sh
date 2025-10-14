#!/bin/bash

set -euo pipefail

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'
BIN_DIR="bin"
EXECUTABLE="$BIN_DIR/volt-gui"
DESKTOP_FILE="/usr/share/applications/volt-gui.desktop"

check_commands() {
    for cmd in install mkdir cat update-desktop-database dirname; do
        if ! command -v "$cmd" &> /dev/null; then
            echo -e "${RED}Error: Required command '$cmd' not found${NC}" >&2
            exit 1
        fi
    done
}

if [[ $EUID -ne 0 ]]; then
  echo -e "${RED}Error: Please run this script as root (use sudo)${NC}" >&2
  exit 1
fi

check_commands

if [[ ! -d "$BIN_DIR" ]]; then
  echo -e "${RED}Error: bin directory not found. Run make-pyinstaller.sh or make-nuitka.sh first.${NC}" >&2
  exit 1
fi

if [[ ! -f "$EXECUTABLE" ]]; then
  echo -e "${RED}Error: Executable 'volt-gui' not found in bin directory. Run make-pyinstaller.sh or make-nuitka.sh first.${NC}" >&2
  exit 1
fi

echo -e "${BLUE}Installing main executable...${NC}"
install -v -m 755 -T "$EXECUTABLE" "$INSTALL_DIR/volt-gui"

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
