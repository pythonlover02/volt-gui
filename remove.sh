#!/bin/bash
# check if running with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# remove the executable from /usr/local/bin/
if [ -f "/usr/local/bin/volt-gui" ]; then
  rm /usr/local/bin/volt-gui
  echo "Removed executable from /usr/local/bin/"
else
  echo "Executable not found in /usr/local/bin/"
fi

# remove desktop entry
DESKTOP_FILE="/usr/share/applications/volt-gui.desktop"
if [ -f "$DESKTOP_FILE" ]; then
  rm "$DESKTOP_FILE"
  echo "Removed desktop entry from $DESKTOP_FILE"
else
  echo "Desktop entry not found at $DESKTOP_FILE"
fi

echo "Removal completed successfully."
