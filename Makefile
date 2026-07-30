PREFIX  ?= /usr
DESTDIR ?=
bindir  ?= $(PREFIX)/bin
datadir ?= $(PREFIX)/share

ifneq ($(wildcard /usr/lib/x86_64-linux-gnu/.),)
LIBDIR_64_REL := lib/x86_64-linux-gnu
LIBDIR_32_REL := lib/i386-linux-gnu
else ifneq ($(wildcard /usr/lib32/.),)
LIBDIR_64_REL := lib
LIBDIR_32_REL := lib32
else ifneq ($(wildcard /usr/lib64/.),)
LIBDIR_64_REL := lib64
LIBDIR_32_REL := lib
else
LIBDIR_64_REL := lib
LIBDIR_32_REL := lib32
endif

LIBDIR_64    ?= $(PREFIX)/$(LIBDIR_64_REL)
LIBDIR_32    ?= $(PREFIX)/$(LIBDIR_32_REL)
VK_LAYER_DIR := $(datadir)/vulkan/implicit_layer.d
STATE_DIR    := /var/lib/volt

TARGET_64 := volt/target/x86_64-unknown-linux-gnu/release/libvolt.so
TARGET_32 := volt/target/i686-unknown-linux-gnu/release/libvolt.so
BIN       := volt/target/x86_64-unknown-linux-gnu/release/volt
GUI_BIN   := bin/volt-gui

MANIFEST := VkLayer_volt.json

CARGO   ?= cargo
RUSTUP  ?= rustup
PYTHON3 ?= python3
OSTREE  ?= ostree
FLATPAK ?= flatpak

FORCE_INSTALL ?= 0

RUST_SOURCES := $(wildcard volt/Cargo.toml volt/Cargo.lock volt/*.rs)

ifeq ($(filter grouped-target,$(.FEATURES)),)
$(error GNU make 4.3+ required)
endif

.PHONY: all 32 release gui-nuitka gui-pyinstaller flatpak install flatpak-install \
        uninstall clean check-root check-sudo-user check-no-sudo


all: $(TARGET_64) $(BIN)

$(TARGET_64) $(BIN) &: $(RUST_SOURCES)
	cd volt && $(CARGO) build --release --target x86_64-unknown-linux-gnu

32: $(TARGET_32)

$(TARGET_32): $(RUST_SOURCES)
	@command -v $(RUSTUP) >/dev/null 2>&1 || { \
	  echo "error: rustup required for 32-bit builds"; exit 1; }
	@$(RUSTUP) target list --installed | grep -q '^i686-unknown-linux-gnu$$' \
	  || $(RUSTUP) target add i686-unknown-linux-gnu
	cd volt && \
	CARGO_TARGET_I686_UNKNOWN_LINUX_GNU_LINKER=gcc \
	$(CARGO) build --release --target i686-unknown-linux-gnu


CONTAINER          ?= $(shell command -v podman 2>/dev/null || command -v docker 2>/dev/null || echo podman)
CONTAINER_IMAGE    := rust:1.82-bookworm
CONTAINER_STAMP_64 := volt/target/.container-stamp-64
CONTAINER_STAMP_32 := volt/target/.container-stamp-32

$(CONTAINER_STAMP_64): $(RUST_SOURCES)
	@command -v $(CONTAINER) >/dev/null 2>&1 || { \
	  echo "error: podman or docker required"; exit 1; }
	$(CONTAINER) run --rm -v $$(pwd)/volt:/src:z -w /src $(CONTAINER_IMAGE) sh -c '\
	  cargo build --release --target x86_64-unknown-linux-gnu'
	@mkdir -p $(@D)
	@touch $@

$(CONTAINER_STAMP_32): $(RUST_SOURCES)
	@command -v $(CONTAINER) >/dev/null 2>&1 || { \
	  echo "error: podman or docker required"; exit 1; }
	$(CONTAINER) run --rm -v $$(pwd)/volt:/src:z -w /src $(CONTAINER_IMAGE) sh -c '\
	  rustup target add i686-unknown-linux-gnu && \
	  apt-get update -qq && apt-get install -y -qq gcc-multilib 2>/dev/null && \
	  CARGO_TARGET_I686_UNKNOWN_LINUX_GNU_LINKER=gcc \
	  cargo build --release --target i686-unknown-linux-gnu'
	@mkdir -p $(@D)
	@touch $@


define ensure_venv
	if [ ! -d py_env ]; then \
	  echo "setting up python virtual environment"; \
	  $(PYTHON3) -m venv py_env; \
	fi; \
	. py_env/bin/activate; \
	hash=$$(shasum -a 256 requirements.txt | cut -d" " -f1); \
	stored=$$(cat py_env/requirements.sha256 2>/dev/null || true); \
	if [ "$$hash" != "$$stored" ]; then \
	  echo "installing python dependencies"; \
	  pip install --upgrade pip -q; \
	  pip install --no-cache-dir -r requirements.txt -q; \
	  echo "$$hash" > py_env/requirements.sha256; \
	fi
endef

gui-pyinstaller: check-no-sudo
	@set -e; \
	$(ensure_venv); \
	pyinstaller --onefile --name=volt-gui volt-gui/volt-gui.py -y --log-level WARN; \
	mkdir -p bin; \
	mv dist/volt-gui bin/; \
	rm -rf dist/ build/ volt-gui.spec; \
	echo "output: bin/volt-gui"

gui-nuitka: check-no-sudo
	@set -e; \
	$(ensure_venv); \
	nuitka --onefile --output-filename=volt-gui --assume-yes-for-downloads \
	  --enable-plugin=pyside6 volt-gui/volt-gui.py; \
	mkdir -p bin; \
	mv volt-gui bin/; \
	rm -rf volt-gui.build/ volt-gui.dist/ volt-gui.onefile-build/; \
	echo "output: bin/volt-gui"


FLATPAK_RUNTIMES := 23.08 24.08 25.08
FLATPAK_OUTDIR   := bundles
FLATPAK_WORKDIR  := .flatpak-work
FLATPAK_EXT_ID   := org.freedesktop.Platform.VulkanLayer.volt
FLATPAK_ARCH     := x86_64

FLATPAK_BUNDLES := $(foreach rt,$(FLATPAK_RUNTIMES),\
  $(FLATPAK_OUTDIR)/$(FLATPAK_EXT_ID)-$(rt).flatpak)

ifeq ($(and $(wildcard $(TARGET_64)),$(wildcard $(TARGET_32))),)
flatpak:
	@echo "nothing to package build first with 'make' and 'make 32'"
	@exit 1
else
flatpak: $(FLATPAK_BUNDLES)
endif

$(FLATPAK_OUTDIR)/$(FLATPAK_EXT_ID)-%.flatpak: \
    $(TARGET_64) $(TARGET_32) $(MANIFEST) LICENSE \
    flatpak/volt-flatpak flatpak/commit.py
	@command -v $(FLATPAK) >/dev/null 2>&1 || { echo "error: $(FLATPAK) required"; exit 1; }
	@command -v $(OSTREE)  >/dev/null 2>&1 || { echo "error: $(OSTREE) required";  exit 1; }
	@command -v $(PYTHON3) >/dev/null 2>&1 || { echo "error: $(PYTHON3) required"; exit 1; }
	@mkdir -p $(@D)
	@set -e; \
	rt="$*"; work="$(FLATPAK_WORKDIR).$$rt"; \
	rm -rf $$work; \
	mkdir -p $$work/stage/files/lib/x86_64-linux-gnu \
	         $$work/stage/files/lib/i386-linux-gnu \
	         $$work/stage/files/share/vulkan/implicit_layer.d \
	         $$work/stage/files/share/doc/volt \
	         $$work/stage/files/bin \
	         $$work/repo; \
	$(OSTREE) init --repo=$$work/repo --mode=archive-z2; \
	cp $(TARGET_64) $$work/stage/files/lib/x86_64-linux-gnu/libvolt.so; \
	cp $(TARGET_32) $$work/stage/files/lib/i386-linux-gnu/libvolt.so; \
	cp $(MANIFEST)  $$work/stage/files/share/vulkan/implicit_layer.d/$(MANIFEST); \
	cp LICENSE      $$work/stage/files/share/doc/volt/LICENSE; \
	cp flatpak/volt-flatpak $$work/stage/files/bin/volt-flatpak; \
	chmod +x $$work/stage/files/bin/volt-flatpak; \
	$(PYTHON3) flatpak/commit.py "$$rt" "$$work/repo" "$$work/stage"; \
	$(FLATPAK) build-bundle --arch=$(FLATPAK_ARCH) $$work/repo $@ \
	  $(FLATPAK_EXT_ID) "$$rt" --runtime; \
	rm -rf $$work


APPIMAGE_TOOL := appimagetool-x86_64.AppImage

define build_appimage
	if [ ! -f $(APPIMAGE_TOOL) ]; then \
	  wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/$(APPIMAGE_TOOL)"; \
	  chmod +x $(APPIMAGE_TOOL); \
	fi; \
	rm -rf AppDir; \
	mkdir -p AppDir; \
	cp images/1.png AppDir/preferences-system.png; \
	cp $(GUI_BIN) AppDir/volt-gui; \
	chmod +x AppDir/volt-gui; \
	printf '[Desktop Entry]\nName=volt-gui\nComment=My AMD Adrenaline / NVIDIA Settings Linux Alternative\nExec=volt-gui\nIcon=preferences-system\nTerminal=false\nType=Application\nCategories=Utility;\n' > AppDir/volt-gui.desktop; \
	printf '#!/bin/bash\nHERE="$$(dirname "$$(readlink -f "$${0}")")"\nexport APPDIR="$${HERE}"\ncd "$${HOME}" 2>/dev/null || cd /tmp\nexec "$${HERE}/volt-gui" "$$@"\n' > AppDir/AppRun; \
	chmod +x AppDir/AppRun; \
	./$(APPIMAGE_TOOL) AppDir volt-gui-x86_64.AppImage 2>/dev/null; \
	chmod +x volt-gui-x86_64.AppImage; \
	rm -rf AppDir
endef

define pack_release
	mkdir -p releases/volt-gui-$(1); \
	cp -r bin Makefile $(MANIFEST) volt releases/volt-gui-$(1)/; \
	rm -rf releases/volt-gui-$(1)/volt/target; \
	mkdir -p releases/volt-gui-$(1)/bundles; \
	cp $(FLATPAK_OUTDIR)/*.flatpak releases/volt-gui-$(1)/bundles/; \
	tar -czf releases/volt-gui-$(1).tar.gz -C releases volt-gui-$(1); \
	rm -rf releases/volt-gui-$(1)
endef

release: check-no-sudo $(CONTAINER_STAMP_64) $(CONTAINER_STAMP_32)
	@set -e; \
	rm -rf releases bin; \
	mkdir -p releases; \
	$(MAKE) flatpak; \
	$(MAKE) gui-pyinstaller; \
	$(call build_appimage); \
	mv volt-gui-x86_64.AppImage releases/volt-gui-pyinstaller-x86_64.AppImage; \
	$(call pack_release,pyinstaller); \
	rm -rf bin; \
	$(MAKE) gui-nuitka; \
	$(call build_appimage); \
	mv volt-gui-x86_64.AppImage releases/volt-gui-nuitka-x86_64.AppImage; \
	$(call pack_release,nuitka); \
	echo "artifacts:"; \
	du -h releases/* 2>/dev/null || true


INSTALL_FILES :=
ifneq (,$(wildcard $(BIN)))
INSTALL_FILES += $(DESTDIR)$(bindir)/volt
endif
ifneq (,$(wildcard $(GUI_BIN)))
INSTALL_FILES += $(DESTDIR)$(bindir)/volt-gui
endif
ifneq (,$(wildcard $(TARGET_64)))
INSTALL_FILES += $(DESTDIR)$(LIBDIR_64)/libvolt.so
endif
ifneq (,$(wildcard $(TARGET_32)))
INSTALL_FILES += $(DESTDIR)$(LIBDIR_32)/libvolt.so
endif
ifneq (,$(wildcard $(TARGET_64))$(wildcard $(TARGET_32)))
INSTALL_FILES += $(DESTDIR)$(VK_LAYER_DIR)/$(MANIFEST)
endif

BUILT_FLATPAKS := $(wildcard $(FLATPAK_OUTDIR)/$(FLATPAK_EXT_ID)-*.flatpak)
INSTALLED_FLATPAK_STAMPS := \
  $(BUILT_FLATPAKS:$(FLATPAK_OUTDIR)/%.flatpak=$(STATE_DIR)/.installed-%)

EXISTING_INSTALL := $(strip \
  $(wildcard $(DESTDIR)$(bindir)/volt) \
  $(wildcard $(DESTDIR)$(LIBDIR_64)/libvolt.so) \
  $(wildcard $(DESTDIR)$(LIBDIR_32)/libvolt.so))

ifneq ($(DESTDIR),)
EXISTING_INSTALL :=
endif
ifneq ($(FORCE_INSTALL),0)
EXISTING_INSTALL :=
endif

ifneq (,$(EXISTING_INSTALL))
install: check-root
	@echo "error: volt or a program with the same name is installed:"
	@for f in $(EXISTING_INSTALL); do echo "  $$f"; done
	@echo "if it's a prior version, run 'make uninstall' first or use FORCE_INSTALL=1"
	@exit 1
else ifeq (,$(strip $(INSTALL_FILES)))
install: check-root
	@echo "nothing to install build first with 'make', 'make 32', or the gui targets"
	@exit 1
else
install: check-root $(INSTALL_FILES)
	@test -n "$(DESTDIR)" || ldconfig 2>/dev/null || true
	@echo "install complete."
	@echo "  bin:       $(bindir)"
	@echo "  lib (64):  $(LIBDIR_64)"
	@echo "  lib (32):  $(LIBDIR_32)"
	@echo "  manifest:  $(VK_LAYER_DIR)"
endif

ifneq ($(DESTDIR),)
flatpak-install: check-root
	@echo "error: flatpak-install does not support DESTDIR"
	@echo "  package the .flatpak files from $(FLATPAK_OUTDIR)/ directly instead"
	@exit 1
else ifeq (,$(strip $(INSTALLED_FLATPAK_STAMPS)))
flatpak-install: check-root
	@echo "nothing to install build first with 'make flatpak'"
	@exit 1
else
flatpak-install: check-root $(INSTALLED_FLATPAK_STAMPS)
	@echo "flatpak extensions installed."
endif

$(DESTDIR)$(bindir)/volt:              $(BIN)      ; install -Dm755 $< $@
$(DESTDIR)$(bindir)/volt-gui:          $(GUI_BIN)  ; install -Dm755 $< $@
$(DESTDIR)$(LIBDIR_64)/libvolt.so:     $(TARGET_64); install -Dm755 $< $@
$(DESTDIR)$(LIBDIR_32)/libvolt.so:     $(TARGET_32); install -Dm755 $< $@
$(DESTDIR)$(VK_LAYER_DIR)/$(MANIFEST): $(MANIFEST) ; install -Dm644 $< $@

$(STATE_DIR)/.installed-%: $(FLATPAK_OUTDIR)/%.flatpak | check-sudo-user
	@mkdir -p $(@D)
	@su - "$$SUDO_USER" -c "$(FLATPAK) install --user -y --reinstall '$(abspath $<)'"
	@touch $@

uninstall: check-root
	rm -f $(DESTDIR)$(bindir)/volt
	rm -f $(DESTDIR)$(bindir)/volt-gui
	rm -f $(DESTDIR)$(LIBDIR_64)/libvolt.so
	rm -f $(DESTDIR)$(LIBDIR_32)/libvolt.so
	rm -f $(DESTDIR)$(VK_LAYER_DIR)/$(MANIFEST)
	@if [ -z "$(DESTDIR)" ]; then \
	  rm -rf $(STATE_DIR); \
	  ldconfig 2>/dev/null || true; \
	  if [ -n "$$SUDO_USER" ]; then \
	    su - "$$SUDO_USER" -c \
	      "flatpak uninstall --user -y $(FLATPAK_EXT_ID) 2>/dev/null" || true; \
	    su - "$$SUDO_USER" -c "rm -rf \"\$$HOME/.config/volt-gui\"" || true; \
	  else \
	    echo "note: SUDO_USER not set run as your user: flatpak uninstall --user $(FLATPAK_EXT_ID)"; \
	  fi; \
	fi

check-root:
	@if [ "$$(id -u)" -ne 0 ]; then \
	  echo "error: needs root run: sudo make $(MAKECMDGOALS)"; \
	  exit 1; \
	fi

check-sudo-user:
	@if [ -z "$$SUDO_USER" ]; then \
	  echo "error: SUDO_USER not set run via 'sudo make ...' from your user shell"; \
	  exit 1; \
	fi

check-no-sudo:
	@if [ "$$(id -u)" -eq 0 ]; then \
	  echo "error: do not run this target with sudo"; \
	  exit 1; \
	fi

clean:
	cd volt && $(CARGO) clean
	rm -rf bin py_env dist build *.spec *.build *.dist *.onefile-build
	rm -rf $(FLATPAK_OUTDIR) $(FLATPAK_WORKDIR)* AppDir *.AppImage releases
