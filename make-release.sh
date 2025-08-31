#!/bin/bash
# Exit immediately on errors, unset variables, and pipe failures
set -euo pipefail

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
RELEASE_DIR="releases"
PYINSTALLER_BUILD="volt-gui-pyinstaller"
NUITKA_BUILD="volt-gui-nuitka"
BUILD_SCRIPTS=("make-pyinstaller.sh" "make-nuitka.sh")

# Cleanup function
cleanup() {
    # Remove any temporary files if needed
    true
}

# Check for required commands
check_commands() {
    local commands=("tar" "cp" "mkdir")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            echo -e "${RED}Error: Required command '$cmd' not found${NC}" >&2
            exit 1
        fi
    done
}

# Execute build script and copy artifacts
build_and_copy() {
    local build_script=$1
    local target_dir=$2
    
    echo -e "${CYAN}Executing build script: $build_script${NC}"
    # Run build script from the project root directory
    if ! (cd .. && ./"$build_script"); then
        echo -e "${RED}Error: Build script $build_script failed${NC}" >&2
        exit 1
    fi
    
    echo -e "${CYAN}Copying artifacts to $target_dir${NC}"
    mkdir -p "$target_dir"
    
    # Copy required files and directories from project root
    for item in bin install.sh remove.sh scripts; do
        if [[ -e "../$item" ]]; then
            cp -r "../$item" "$target_dir/"
        else
            echo -e "${YELLOW}Warning: $item not found, skipping${NC}"
        fi
    done
}

# Compress directory
compress_release() {
    local dir_name=$1
    echo -e "${CYAN}Compressing $dir_name to ${dir_name}.tar.gz${NC}"
    tar -czf "${dir_name}.tar.gz" "$dir_name"
}

# Main execution
main() {
    trap cleanup EXIT
    check_commands
    
    # Store the original directory
    ORIGINAL_DIR=$(pwd)
    
    # Remove and recreate release directory
    echo -e "${CYAN}Preparing release directory...${NC}"
    rm -rf "$RELEASE_DIR"
    mkdir -p "$RELEASE_DIR"
    cd "$RELEASE_DIR"
    
    # Process PyInstaller build
    echo -e "\n${YELLOW}=== Processing PyInstaller Build ===${NC}"
    build_and_copy "${BUILD_SCRIPTS[0]}" "$PYINSTALLER_BUILD"
    compress_release "$PYINSTALLER_BUILD"
    
    # Process Nuitka build
    echo -e "\n${YELLOW}=== Processing Nuitka Build ===${NC}"
    build_and_copy "${BUILD_SCRIPTS[1]}" "$NUITKA_BUILD"
    compress_release "$NUITKA_BUILD"
    
    # Return to original directory
    cd "$ORIGINAL_DIR"
    
    echo -e "\n${GREEN}Release build completed successfully!${NC}"
    echo -e "Created archives in ${YELLOW}$RELEASE_DIR${NC}:"
    echo -e "  ${YELLOW}${PYINSTALLER_BUILD}.tar.gz${NC}"
    echo -e "  ${YELLOW}${NUITKA_BUILD}.tar.gz${NC}"
    
    # Show archive sizes
    if command -v du &> /dev/null; then
        echo -e "\nArchive sizes:"
        du -h "$RELEASE_DIR"/*.tar.gz | sed 's/^/  /'
    fi
}

# Run main function
main