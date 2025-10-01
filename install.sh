#!/bin/bash

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo -e "\033[31mError: Please run this script as root (use sudo)\033[0m" >&2
  exit 1
fi

INSTALL_DIR="/usr/local/bin"
BIN_DIR="bin"
EXECUTABLE="$BIN_DIR/volt-gui"
HELPER_SCRIPT="scripts/volt-helper"
DESKTOP_FILE="/usr/share/applications/volt-gui.desktop"

if [[ ! -d "$BIN_DIR" ]]; then
  echo -e "\033[31mError: bin directory not found. Run make-pyinstaller.sh or make-nuitka.sh first.\033[0m" >&2
  exit 1
fi

if [[ ! -f "$EXECUTABLE" ]]; then
  echo -e "\033[31mError: Executable 'volt-gui' not found in bin directory. Run make-pyinstaller.sh or make-nuitka.sh first.\033[0m" >&2
  exit 1
fi

if [[ ! -f "$HELPER_SCRIPT" ]]; then
  echo -e "\033[31mError: Helper script $HELPER_SCRIPT not found.\033[0m" >&2
  exit 1
fi

echo -e "\033[34mInstalling main executable...\033[0m"
install -v -m 755 -T "$EXECUTABLE" "$INSTALL_DIR/volt-gui"

echo -e "\n\033[34mInstalling helper script...\033[0m"
install -v -m 755 -T "$HELPER_SCRIPT" "$INSTALL_DIR/volt-helper"

echo -e "\n\033[34mCreating desktop entry...\033[0m"
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

echo -e "\n\033[34mUpdating desktop database...\033[0m"
update-desktop-database "$(dirname "$DESKTOP_FILE")"

echo -e "\n\033[32mInstallation completed successfully!\033[0m"
echo "You can now run 'volt-gui' from the terminal or application menu."
