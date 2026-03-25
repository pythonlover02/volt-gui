SHELL := /bin/bash
MAKEFLAGS += --no-print-directory
.ONESHELL:
.PHONY: test pyinstaller nuitka appimage install remove release clean

define check_no_sudo
	[[ $$EUID -ne 0 ]] || { echo "Error: do not run this target with sudo"; exit 1; }
endef

define ensure_venv
	if [[ ! -d py_env ]]; then
		echo "  Setting up   : python virtual environment"
		python3 -m venv py_env
	fi
	source py_env/bin/activate
	hash=$$(shasum -a 256 requirements.txt | cut -d" " -f1)
	stored=$$(cat py_env/requirements.sha256 2>/dev/null || true)
	if [[ "$$hash" != "$$stored" ]]; then
		echo "  Installing   : python dependencies (requirements.txt changed)"
		pip install --upgrade pip -q
		pip install --no-cache-dir -r requirements.txt -q
		echo "$$hash" > py_env/requirements.sha256
	else
		echo "  Skipping     : dependencies up to date"
	fi
endef

test:
	set -euo pipefail
	$(check_no_sudo)
	echo ""
	echo "  Checking     : build environment"
	$(ensure_venv)
	echo "  Running      : volt-gui (dev mode)"
	echo ""
	python3 src/volt-gui.py

pyinstaller:
	set -euo pipefail
	$(check_no_sudo)
	echo ""
	echo "  Checking     : build environment"
	$(ensure_venv)
	echo "  Checking     : pyinstaller"
	command -v pyinstaller &>/dev/null && echo "  Available    : pyinstaller" || { echo "  Missing      : pyinstaller (install it inside the venv)"; exit 1; }
	echo "  Building     : volt-gui with pyinstaller"
	pyinstaller --onefile --name=volt-gui src/volt-gui.py -y --log-level WARN
	mkdir -p bin
	mv dist/volt-gui bin/
	rm -rf dist/ build/ volt-gui.spec
	echo "  Output       : bin/volt-gui"
	echo ""

nuitka:
	set -euo pipefail
	$(check_no_sudo)
	echo ""
	echo "  Checking     : build environment"
	$(ensure_venv)
	echo "  Checking     : nuitka"
	command -v nuitka &>/dev/null && echo "  Available    : nuitka" || { echo "  Missing      : nuitka (install it inside the venv)"; exit 1; }
	echo "  Building     : volt-gui with nuitka"
	nuitka --onefile --output-filename=volt-gui --assume-yes-for-downloads --enable-plugin=pyside6 src/volt-gui.py
	mkdir -p bin
	mv volt-gui bin/
	rm -rf volt-gui.build/ volt-gui.dist/ volt-gui.onefile-build/
	echo "  Output       : bin/volt-gui"
	echo ""

appimage:
	set -euo pipefail
	$(check_no_sudo)
	echo ""
	echo "  Checking     : bin/volt-gui"
	[[ -f bin/volt-gui ]] || { echo "  Missing      : bin/volt-gui -- run make pyinstaller or make nuitka first"; exit 1; }
	echo "  Available    : bin/volt-gui"
	echo "  Checking     : images/1.png"
	[[ -f images/1.png ]] || { echo "  Missing      : images/1.png"; exit 1; }
	echo "  Available    : images/1.png"
	echo "  Checking     : appimagetool"
	if [[ ! -f appimagetool-x86_64.AppImage ]]; then
		echo "  Downloading  : appimagetool"
		wget -q --show-progress "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
		chmod +x appimagetool-x86_64.AppImage
	else
		echo "  Available    : appimagetool-x86_64.AppImage"
	fi
	echo "  Building     : AppImage"
	rm -rf AppDir
	mkdir -p AppDir
	cp images/1.png AppDir/preferences-system.png
	cp bin/volt-gui AppDir/volt-gui
	chmod +x AppDir/volt-gui
	printf '[Desktop Entry]\nName=volt-gui\nComment=My AMD Adrenaline / NVIDIA Settings Linux Alternative\nExec=volt-gui\nIcon=preferences-system\nTerminal=false\nType=Application\nCategories=Utility;\n' > AppDir/volt-gui.desktop
	printf '#!/bin/bash\nHERE="$$(dirname "$$(readlink -f "$${0}")")"\nexport APPDIR="$${HERE}"\ncd "$${HOME}" 2>/dev/null || cd /tmp\nexec "$${HERE}/volt-gui" "$$@"\n' > AppDir/AppRun
	chmod +x AppDir/AppRun
	./appimagetool-x86_64.AppImage AppDir volt-gui-x86_64.AppImage 2>/dev/null
	chmod +x volt-gui-x86_64.AppImage
	rm -rf AppDir
	echo "  Output       : volt-gui-x86_64.AppImage"
	echo ""

install:
	set -euo pipefail
	$(check_no_sudo)
	echo ""
	echo "  Checking     : bin/volt-gui"
	[[ -f bin/volt-gui ]] || { echo "  Missing      : bin/volt-gui -- run make pyinstaller or make nuitka first"; exit 1; }
	echo "  Available    : bin/volt-gui"
	echo "  Installing   : sudo required for system install"
	sudo install -v -m 755 -T bin/volt-gui /usr/local/bin/volt-gui
	sudo mkdir -p /usr/share/applications
	printf '[Desktop Entry]\nName=volt-gui\nComment=My AMD Adrenaline / NVIDIA Settings Linux Alternative\nExec=volt-gui\nIcon=preferences-system\nTerminal=false\nType=Application\nCategories=Utility;\n' | sudo tee /usr/share/applications/volt-gui.desktop > /dev/null
	sudo update-desktop-database /usr/share/applications
	echo "  Installed    : /usr/local/bin/volt-gui"
	echo "  Installed    : /usr/share/applications/volt-gui.desktop"
	echo ""

remove:
	set -euo pipefail
	$(check_no_sudo)
	echo ""
	echo "  Removing     : sudo required"
	sudo rm -fv /usr/local/bin/volt /usr/local/bin/volt-gui /usr/local/bin/volt-helper
	sudo rm -fv /usr/share/applications/volt-gui.desktop
	sudo update-desktop-database /usr/share/applications
	echo "  Done         : volt-gui removed"
	echo ""

release:
	set -euo pipefail
	$(check_no_sudo)
	echo ""
	echo "  Building     : full release"
	rm -rf releases
	mkdir -p releases
	$(MAKE) pyinstaller
	$(MAKE) appimage
	mv volt-gui-x86_64.AppImage releases/volt-gui-pyinstaller-x86_64.AppImage
	mkdir -p releases/volt-gui-pyinstaller
	cp -r bin Makefile releases/volt-gui-pyinstaller/
	tar -czf releases/volt-gui-pyinstaller.tar.gz -C releases volt-gui-pyinstaller
	rm -rf bin
	$(MAKE) nuitka
	$(MAKE) appimage
	mv volt-gui-x86_64.AppImage releases/volt-gui-nuitka-x86_64.AppImage
	mkdir -p releases/volt-gui-nuitka
	cp -r bin Makefile releases/volt-gui-nuitka/
	tar -czf releases/volt-gui-nuitka.tar.gz -C releases volt-gui-nuitka
	rm -rf releases/volt-gui-pyinstaller releases/volt-gui-nuitka
	echo "  Artifacts    :"
	du -h releases/* 2>/dev/null || true
	echo ""

clean:
	set -euo pipefail
	$(check_no_sudo)
	echo ""
	echo "  Cleaning     : build artifacts"
	rm -rf bin/ py_env/ dist/ build/ *.spec *.build/ *.dist/ *.onefile-build/ AppDir/ *.AppImage releases/
	echo "  Done         : workspace clean"
	echo ""
