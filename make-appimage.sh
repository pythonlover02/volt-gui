#!/bin/bash

set -euo pipefail

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'
APP_NAME="volt-gui"
BIN_DIR="bin"
EXECUTABLE="$BIN_DIR/volt-gui"
APPDIR="AppDir"
DESKTOP_FILE="volt-gui.desktop"
ICON_FILE="preferences-system.png"
SOURCE_ICON="images/1.png"
APPIMAGETOOL="appimagetool-x86_64.AppImage"
OUTPUT_FILE="${APP_NAME}-x86_64.AppImage"

cleanup() {
    rm -rf "$APPDIR" 2>/dev/null || true
}

check_commands() {
    for cmd in wget chmod mkdir cp cat dirname readlink du cut; do
        if ! command -v "$cmd" &> /dev/null; then
            echo -e "${RED}Error: Required command '$cmd' not found${NC}" >&2
            exit 1
        fi
    done
}

verify_files() {
    if [[ ! -f "$EXECUTABLE" ]]; then
        echo -e "${RED}Error: Executable $EXECUTABLE not found${NC}" >&2
        echo "Please run the build script first to create the executable" >&2
        exit 1
    fi
    if [[ ! -f "$SOURCE_ICON" ]]; then
        echo -e "${RED}Error: Icon file $SOURCE_ICON not found${NC}" >&2
        exit 1
    fi
}

create_appdir_structure() {
    echo -e "${BLUE}Creating AppDir structure...${NC}"
    mkdir -p "$APPDIR"
}

copy_icon() {
    echo -e "${BLUE}Copying icon...${NC}"
    cp "$SOURCE_ICON" "$APPDIR/$ICON_FILE"
}

create_desktop_file() {
    echo -e "${BLUE}Creating desktop file...${NC}"
    cat > "$APPDIR/$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Name=volt-gui
Comment=My AMD Adrenaline / NVIDIA Settings Linux Alternative
Exec=volt-gui
Icon=preferences-system
Terminal=false
Type=Application
Categories=Utility;
EOF
}

create_apprun() {
    echo -e "${BLUE}Creating AppRun script...${NC}"
    cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export APPDIR="${HERE}"
cd "${HOME}" 2>/dev/null || cd /tmp
exec "${HERE}/volt-gui" "$@"
EOF
    chmod +x "$APPDIR/AppRun"
}

copy_executable() {
    echo -e "${BLUE}Copying executable...${NC}"
    cp "$EXECUTABLE" "$APPDIR/$APP_NAME"
    chmod +x "$APPDIR/$APP_NAME"
}

download_appimagetool() {
    if [[ ! -f "$APPIMAGETOOL" ]]; then
        echo -e "${BLUE}Downloading appimagetool...${NC}"
        wget -q --show-progress \
            "https://github.com/AppImage/AppImageKit/releases/download/continuous/$APPIMAGETOOL"
        chmod +x "$APPIMAGETOOL"
    else
        echo "appimagetool already downloaded"
    fi
}

build_appimage() {
    echo -e "${BLUE}Building AppImage...${NC}"
    if ! ./"$APPIMAGETOOL" "$APPDIR" "$OUTPUT_FILE"; then
        echo -e "${RED}Error: Failed to build AppImage${NC}" >&2
        exit 1
    fi
    chmod +x "$OUTPUT_FILE"
}

print_success() {
    echo -e "\nBuild successful!"
    echo -e "AppImage: $OUTPUT_FILE"
    if command -v du &> /dev/null; then
        size=$(du -h "$OUTPUT_FILE" 2>/dev/null | cut -f1 || echo "Unknown")
        echo -e "File size: $size"
    fi
}

main() {
    trap cleanup EXIT
    check_commands
    verify_files
    create_appdir_structure
    copy_icon
    create_desktop_file
    copy_executable
    create_apprun
    download_appimagetool
    build_appimage
    print_success
}

main "$@"
