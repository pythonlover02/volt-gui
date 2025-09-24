#!/bin/bash

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

RELEASE_DIR="releases"
PYINSTALLER_BUILD="volt-gui-pyinstaller"
NUITKA_BUILD="volt-gui-nuitka"
BUILD_SCRIPTS=("make-pyinstaller.sh" "make-nuitka.sh")

cleanup() {
    true
}

check_commands() {
    local commands=("tar" "cp" "mkdir")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            echo -e "${RED}Error: Required command '$cmd' not found${NC}" >&2
            exit 1
        fi
    done
}

build_and_copy() {
    local build_script=$1
    local target_dir=$2

    echo -e "${CYAN}Executing build script: $build_script${NC}"
    if ! (cd .. && ./"$build_script"); then
        echo -e "${RED}Error: Build script $build_script failed${NC}" >&2
        exit 1
    fi

    echo -e "${CYAN}Copying artifacts to $target_dir${NC}"
    mkdir -p "$target_dir"

    for item in bin install.sh remove.sh scripts; do
        if [[ -e "../$item" ]]; then
            cp -r "../$item" "$target_dir/"
        else
            echo -e "${YELLOW}Warning: $item not found, skipping${NC}"
        fi
    done
}

compress_release() {
    local dir_name=$1
    echo -e "${CYAN}Compressing $dir_name to ${dir_name}.tar.gz${NC}"
    tar -czf "${dir_name}.tar.gz" "$dir_name"
}

main() {
    trap cleanup EXIT
    check_commands

    ORIGINAL_DIR=$(pwd)

    echo -e "${CYAN}Preparing release directory...${NC}"
    rm -rf "$RELEASE_DIR"
    mkdir -p "$RELEASE_DIR"
    cd "$RELEASE_DIR"

    echo -e "\n${YELLOW}=== Processing PyInstaller Build ===${NC}"
    build_and_copy "${BUILD_SCRIPTS[0]}" "$PYINSTALLER_BUILD"
    compress_release "$PYINSTALLER_BUILD"

    echo -e "\n${YELLOW}=== Processing Nuitka Build ===${NC}"
    build_and_copy "${BUILD_SCRIPTS[1]}" "$NUITKA_BUILD"
    compress_release "$NUITKA_BUILD"

    cd "$ORIGINAL_DIR"

    echo -e "\n${GREEN}Release build completed successfully!${NC}"
    echo -e "Created archives in ${YELLOW}$RELEASE_DIR${NC}:"
    echo -e "  ${YELLOW}${PYINSTALLER_BUILD}.tar.gz${NC}"
    echo -e "  ${YELLOW}${NUITKA_BUILD}.tar.gz${NC}"

    if command -v du &> /dev/null; then
        echo -e "\nArchive sizes:"
        du -h "$RELEASE_DIR"/*.tar.gz | sed 's/^/  /'
    fi
}

main
