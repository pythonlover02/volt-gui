#!/bin/bash

set -euo pipefail

RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m"
RELEASE_DIR="releases"
PYINSTALLER_BUILD="volt-gui-pyinstaller"
NUITKA_BUILD="volt-gui-nuitka"
BUILD_SCRIPTS=("make-pyinstaller.sh" "make-nuitka.sh")
APPIMAGE_SCRIPT="make-appimage.sh"
ORIGINAL_DIR=$(pwd)

cleanup() {
    true
}

check_commands() {
    for cmd in tar cp mkdir mv pwd cd du sed rm; do
        if ! command -v "$cmd" &> /dev/null; then
            echo -e "${RED}Error: Required command "$cmd" not found${NC}" >&2
            exit 1
        fi
    done
}

build_and_copy() {
    local build_script="$1"
    local target_dir="$2"
    local build_type="$3"
    local appimage_file="volt-gui-x86_64.AppImage"
    local renamed_appimage="volt-gui-${build_type}-x86_64.AppImage"

    echo -e "${BLUE}Executing build script: $build_script${NC}"
    if ! (cd "$ORIGINAL_DIR" && ./"$build_script"); then
        echo -e "${RED}Error: Build script $build_script failed${NC}" >&2
        exit 1
    fi

    echo -e "${BLUE}Building AppImage for $build_type${NC}"
    if ! (cd "$ORIGINAL_DIR" && ./"$APPIMAGE_SCRIPT"); then
        echo -e "${RED}Error: AppImage build failed${NC}" >&2
        exit 1
    fi

    echo -e "${BLUE}Renaming AppImage to $renamed_appimage${NC}"
    if [[ -f "$ORIGINAL_DIR/$appimage_file" ]]; then
        mv "$ORIGINAL_DIR/$appimage_file" "$ORIGINAL_DIR/$renamed_appimage"
    else
        echo -e "${RED}Error: AppImage file not found${NC}" >&2
        exit 1
    fi

    echo -e "${BLUE}Copying artifacts to $target_dir${NC}"
    mkdir -p "$target_dir"
    for item in bin install.sh remove.sh; do
        if [[ -e "$ORIGINAL_DIR/$item" ]]; then
            cp -r "$ORIGINAL_DIR/$item" "$target_dir/"
        else
            echo "Warning: $item not found, skipping"
        fi
    done

    echo -e "${BLUE}Moving AppImage to release directory${NC}"
    mv "$ORIGINAL_DIR/$renamed_appimage" .
}

compress_release() {
    local dir_name="$1"

    echo -e "${BLUE}Compressing $dir_name to ${dir_name}.tar.gz${NC}"
    tar -czf "${dir_name}.tar.gz" "$dir_name"
}

main() {
    trap cleanup EXIT
    check_commands

    echo -e "${BLUE}Preparing release directory...${NC}"
    rm -rf "$RELEASE_DIR"
    mkdir -p "$RELEASE_DIR"
    cd "$RELEASE_DIR"

    echo -e "\n=== Processing PyInstaller Build ==="
    build_and_copy "${BUILD_SCRIPTS[0]}" "$PYINSTALLER_BUILD" "pyinstaller"
    compress_release "$PYINSTALLER_BUILD"

    echo -e "\n=== Processing Nuitka Build ==="
    build_and_copy "${BUILD_SCRIPTS[1]}" "$NUITKA_BUILD" "nuitka"
    compress_release "$NUITKA_BUILD"

    cd "$ORIGINAL_DIR"

    echo -e "\nRelease build completed successfully!"
    echo -e "Created archives in $RELEASE_DIR:"
    echo -e " ${PYINSTALLER_BUILD}.tar.gz"
    echo -e " ${NUITKA_BUILD}.tar.gz"
    echo -e "\nCreated AppImages in $RELEASE_DIR:"
    echo -e " volt-gui-pyinstaller-x86_64.AppImage"
    echo -e " volt-gui-nuitka-x86_64.AppImage"

    if command -v du &> /dev/null; then
        echo -e "\nArchive sizes:"
        du -h "$RELEASE_DIR"/*.tar.gz | sed "s/^/ /"
        echo -e "\nAppImage sizes:"
        du -h "$RELEASE_DIR"/*.AppImage | sed "s/^/ /"
    fi
}

main
