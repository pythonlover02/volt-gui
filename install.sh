#!/bin/bash
# check if running with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi
# check if the release directory exists
if [ ! -d "release" ]; then
  echo "Release directory not found. Run build.sh first."
  exit 1
fi
# check if the executable exists
if [ ! -f "release/volt-gui" ]; then
  echo "Executable not found in release directory. Run build.sh first."
  exit 1
fi
# copy the executable to /usr/local/bin/
cp release/volt-gui /usr/local/bin/
# make it executable
chmod +x /usr/local/bin/volt-gui

# create desktop entry for all users
DESKTOP_FILE="/usr/share/applications/volt-gui.desktop"
cat > "$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Exec=volt-gui
Name=volt-gui
NoDisplay=false
StartupNotify=true
Terminal=false
Type=Application
EOF

# make desktop file executable
chmod 644 "$DESKTOP_FILE"

echo "Installation completed successfully. You can now run 'volt-gui' from anywhere."
echo "Desktop entry created at $DESKTOP_FILE"
