#!/bin/bash

# Exit on errors and unset variables
set -eu

# Check if running with sudo
if [[ $EUID -ne 0 ]]; then
  echo -e "\033[31mError: Please run this script as root (use sudo)\033[0m" >&2
  exit 1
fi

# Configuration
INSTALL_DIR="/usr/local/bin"
RELEASE_DIR="release"
EXECUTABLE="$RELEASE_DIR/volt-gui"
HELPER_SCRIPT="scripts/volt-helper"
DESKTOP_FILE="/usr/share/applications/volt-gui.desktop"

# Check release directory
if [[ ! -d "$RELEASE_DIR" ]]; then
  echo -e "\033[31mError: Release directory not found. Run build.sh first.\033[0m" >&2
  exit 1
fi

# Check main executable
if [[ ! -f "$EXECUTABLE" ]]; then
  echo -e "\033[31mError: Executable 'volt-gui' not found in release directory. Run build.sh first.\033[0m" >&2
  exit 1
fi

# Check helper script
if [[ ! -f "$HELPER_SCRIPT" ]]; then
  echo -e "\033[31mError: Helper script $HELPER_SCRIPT not found.\033[0m" >&2
  exit 1
fi

# Install main executable
echo -e "\033[34mInstalling main executable...\033[0m"
install -v -m 755 -T "$EXECUTABLE" "$INSTALL_DIR/volt-gui"

# Install helper script
echo -e "\n\033[34mInstalling helper script...\033[0m"
install -v -m 755 -T "$HELPER_SCRIPT" "$INSTALL_DIR/volt-helper"

# Create desktop entry
echo -e "\n\033[34mCreating desktop entry...\033[0m"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=0.1
Name=volt-gui
Comment=A simple GUI program to modify and create the "volt" script and more
Exec=volt-gui
Icon=preferences-system
Terminal=false
Type=Application
Categories=Utility;
EOF

echo "Desktop entry created at $DESKTOP_FILE"

# Update desktop database
echo -e "\n\033[34mUpdating desktop database...\033[0m"
update-desktop-database "$(dirname "$DESKTOP_FILE")"

echo -e "\n\033[32mInstallation completed successfully!\033[0m"
echo "You can now run 'volt-gui' from the terminal or application menu."
