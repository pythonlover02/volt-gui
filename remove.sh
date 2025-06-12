#!/bin/bash

# Exit on errors
set -eu

# Check if running with sudo
if [[ $EUID -ne 0 ]]; then
  echo -e "\033[31mError: Please run this script as root (use sudo)\033[0m" >&2
  exit 1
fi

# Configuration
INSTALL_DIR="/usr/local/bin"
TARGETS=("volt" "volt-gui" "volt-helper")
DESKTOP_FILE="/usr/share/applications/volt-gui.desktop"

# Remove installed files
echo -e "\033[34mRemoving installed files...\033[0m"

# Remove main executable and helper
for target in "${TARGETS[@]}"; do
  file="$INSTALL_DIR/$target"
  if [[ -f "$file" ]]; then
    rm -v "$file"
  else
    echo -e "\033[33mWarning: $file not found\033[0m"
  fi
done

# Remove desktop entry
if [[ -f "$DESKTOP_FILE" ]]; then
  rm -v "$DESKTOP_FILE"
  # Update desktop database
  echo -e "\n\033[34mUpdating desktop database...\033[0m"
  update-desktop-database "$(dirname "$DESKTOP_FILE")"
else
  echo -e "\033[33mWarning: Desktop entry $DESKTOP_FILE not found\033[0m"
fi

echo -e "\n\033[32mRemoval completed successfully!\033[0m"