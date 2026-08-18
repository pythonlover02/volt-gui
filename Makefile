PREFIX  ?= /usr
DESTDIR ?=
bindir  ?= $(PREFIX)/bin
datadir ?= $(PREFIX)/share

OUT      ?= build
RELEASES ?= releases
GUI      ?= pyinstaller

CARGO   ?= cargo
RUSTUP  ?= rustup
PYTHON3 ?= python3
OSTREE  ?= ostree
FLATPAK ?= flatpak
TAR     ?= tar
CC32    ?= gcc

ifeq ($(filter grouped-target,$(.FEATURES)),)
$(error GNU make 4.3+ required)
endif

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
DESKTOP_DIR  := $(datadir)/applications
ICON_DIR     := $(datadir)/icons/hicolor/256x256/apps
STATE_DIR    := /var/lib/volt
MANIFEST     := VkLayer_volt.json
DESKTOP_FILE := volt-gui.desktop
ICON_FILE    := volt-gui.png
ICON_SOURCE  := images/1.png

VERSION   := $(shell sed -n 's/^version = "\(.*\)"/\1/p' volt/Cargo.toml | head -n1)
TRIPLE_64 := x86_64-unknown-linux-gnu
TRIPLE_32 := i686-unknown-linux-gnu

TARGET_DIR := $(OUT)/target
BIN_DIR    := $(OUT)/bin
BUNDLE_DIR := $(OUT)/bundles
SHARE_DIR  := $(OUT)/share
VENV       := $(OUT)/py_env

DIST_DIR   := $(OUT)/dist
DIST_NAME   = volt-gui-$(VERSION)-$*
DIST        = $(DIST_DIR)/$(DIST_NAME)

CARGO_TARGET_DIR := $(abspath $(TARGET_DIR))
export CARGO_TARGET_DIR

LAYER_64 := $(TARGET_DIR)/$(TRIPLE_64)/release/libvolt.so
LAYER_32 := $(TARGET_DIR)/$(TRIPLE_32)/release/libvolt.so
LAUNCHER := $(TARGET_DIR)/$(TRIPLE_64)/release/volt
GUI_BIN  := $(BIN_DIR)/volt-gui-$(GUI)
DESKTOP  := $(SHARE_DIR)/$(DESKTOP_FILE)

RUST_SOURCES := volt/Cargo.toml volt/Cargo.lock $(wildcard volt/*.rs)
GUI_SOURCES  := $(wildcard volt-gui/*.py)
VENV_STAMP   := $(OUT)/.venv

DESKTOP_NAME     := volt-gui
DESKTOP_COMMENT  := My AMD Adrenaline / NVIDIA Settings Linux Alternative
DESKTOP_CATEGORY := Utility;
DESKTOP_KEYWORDS := vulkan;vsync;gpu;gaming;

FLATPAK_RUNTIMES := 23.08 24.08 25.08
FLATPAK_EXT_ID   := org.freedesktop.Platform.VulkanLayer.volt
FLATPAK_ARCH     := x86_64
LIBDIR_64_ARCH   := x86_64-linux-gnu
LIBDIR_32_ARCH   := i386-linux-gnu
FLATPAK_BUNDLES  := $(foreach rt,$(FLATPAK_RUNTIMES),\
  $(BUNDLE_DIR)/$(FLATPAK_EXT_ID)-$(rt).flatpak)

RELEASE_FILES := \
  $(RELEASES)/volt-gui-$(VERSION)-pyinstaller.tar.gz \
  $(RELEASES)/volt-gui-$(VERSION)-nuitka.tar.gz

CONTAINER       ?= $(shell command -v podman 2>/dev/null || command -v docker 2>/dev/null || echo podman)
CONTAINER_BASE  ?= rust:1.85.1-bookworm
CONTAINER_IMAGE ?= volt-gui-build
CONTAINER_OUT   ?= $(OUT)/container
CONTAINER_STAMP := $(OUT)/.container-image

NO_SUDO = @test -z "$$SUDO_USER" || { echo "error: do not build with sudo — run 'make' as your user, then 'sudo make install'"; exit 1; }

DIST_TREES := volt volt-gui images flatpak container .github

ifeq ($(DESTDIR),)
ROOT_GUARD := check-root
LAYER_GUARD := check-no-user-layer
LIVE_SYSTEM := 1
else
ROOT_GUARD :=
LAYER_GUARD :=
LIVE_SYSTEM :=
endif

USER_MANIFEST_HOME = $${SUDO_USER:+$$(getent passwd "$$SUDO_USER" | cut -d: -f6)}

INSTALL_FILES := \
  $(DESTDIR)$(bindir)/volt \
  $(DESTDIR)$(bindir)/volt-gui \
  $(DESTDIR)$(LIBDIR_64)/libvolt.so \
  $(DESTDIR)$(LIBDIR_32)/libvolt.so \
  $(DESTDIR)$(VK_LAYER_DIR)/$(MANIFEST) \
  $(DESTDIR)$(DESKTOP_DIR)/$(DESKTOP_FILE) \
  $(DESTDIR)$(ICON_DIR)/$(ICON_FILE)

USER_PREFIX    ?= $(HOME)/.local
USER_BIN       := $(USER_PREFIX)/bin
USER_LIB       := $(USER_PREFIX)/lib/volt
USER_DATA      := $(USER_PREFIX)/share
USER_LAYER_DIR := $(USER_DATA)/vulkan/implicit_layer.d
USER_DESK_DIR  := $(USER_DATA)/applications
USER_ICON_DIR  := $(USER_DATA)/icons/hicolor/256x256/apps
USER_STATE     := $(USER_DATA)/volt

USER_FILES := \
  $(USER_BIN)/volt \
  $(USER_BIN)/volt-gui \
  $(USER_LIB)/$(LIBDIR_64_ARCH)/libvolt.so \
  $(USER_LIB)/$(LIBDIR_32_ARCH)/libvolt.so \
  $(USER_LAYER_DIR)/$(MANIFEST) \
  $(USER_DESK_DIR)/$(DESKTOP_FILE) \
  $(USER_ICON_DIR)/$(ICON_FILE)

BUILT_ARTIFACTS := $(LAYER_64) $(LAYER_32) $(LAUNCHER) $(GUI_BIN) $(DESKTOP)

.DELETE_ON_ERROR:

.PHONY: all layer-64 layer-32 gui-pyinstaller gui-nuitka desktop flatpak dist \
        release release-container container-image install flatpak-install \
        install-user flatpak-install-user setup-user uninstall-user \
        uninstall clean help check-root check-sudo-user check-not-root \
        check-no-user-layer check-no-system-layer check-built check-bundles

all: $(LAYER_64) $(LAYER_32) $(LAUNCHER) $(GUI_BIN) $(DESKTOP)

layer-64:        $(LAYER_64) $(LAUNCHER)
layer-32:        $(LAYER_32)
gui-pyinstaller: $(BIN_DIR)/volt-gui-pyinstaller
gui-nuitka:      $(BIN_DIR)/volt-gui-nuitka
desktop:         $(DESKTOP)
flatpak:         $(FLATPAK_BUNDLES)
dist:            $(OUT)/.dist-$(GUI)
release:         $(RELEASE_FILES)
container-image: $(CONTAINER_STAMP)

$(OUT) $(BIN_DIR) $(BUNDLE_DIR) $(SHARE_DIR) $(RELEASES) $(OUT)/pyinstaller $(OUT)/nuitka:
	@mkdir -p $@

$(LAYER_64) $(LAUNCHER) &: $(RUST_SOURCES)
	$(NO_SUDO)
	cd volt && $(CARGO) build --release --target $(TRIPLE_64)

$(LAYER_32): $(RUST_SOURCES)
	$(NO_SUDO)
	-@$(RUSTUP) target add $(TRIPLE_32)
	cd volt && CARGO_TARGET_I686_UNKNOWN_LINUX_GNU_LINKER=$(CC32) \
	  $(CARGO) build --release --target $(TRIPLE_32)

$(VENV_STAMP): requirements.txt | $(OUT)
	$(NO_SUDO)
	$(PYTHON3) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip -q
	$(VENV)/bin/pip install --no-cache-dir -r requirements.txt -q
	@touch $@

$(BIN_DIR)/volt-gui-pyinstaller: $(GUI_SOURCES) $(VENV_STAMP) | $(BIN_DIR) $(OUT)/pyinstaller
	$(NO_SUDO)
	$(VENV)/bin/pyinstaller --onefile --name=$(@F) -y --log-level WARN \
	  --distpath $(BIN_DIR) --workpath $(OUT)/pyinstaller --specpath $(OUT)/pyinstaller \
	  volt-gui/volt-gui.py

$(BIN_DIR)/volt-gui-nuitka: $(GUI_SOURCES) $(VENV_STAMP) | $(BIN_DIR) $(OUT)/nuitka
	$(NO_SUDO)
	$(VENV)/bin/nuitka --onefile --assume-yes-for-downloads --enable-plugin=pyside6 \
	  --output-dir=$(OUT)/nuitka --output-filename=$(@F) volt-gui/volt-gui.py
	@cp $(OUT)/nuitka/$(@F) $@

$(DESKTOP): Makefile | $(SHARE_DIR)
	@printf '%s\n' \
	  '[Desktop Entry]' \
	  'Type=Application' \
	  'Version=1.0' \
	  'Name=$(DESKTOP_NAME)' \
	  'Comment=$(DESKTOP_COMMENT)' \
	  'Exec=volt-gui' \
	  'Icon=volt-gui' \
	  'Terminal=false' \
	  'Categories=$(DESKTOP_CATEGORY)' \
	  'Keywords=$(DESKTOP_KEYWORDS)' \
	  'StartupNotify=true' \
	  'StartupWMClass=volt-gui' > $@

$(BUNDLE_DIR)/$(FLATPAK_EXT_ID)-%.flatpak: $(LAYER_64) $(LAYER_32) $(LAUNCHER) \
    $(MANIFEST) LICENSE flatpak/volt-flatpak flatpak/commit.py | $(BUNDLE_DIR)
	rm -rf $(OUT)/flatpak.$*
	install -Dm755 $(LAYER_64) $(OUT)/flatpak.$*/stage/files/lib/x86_64-linux-gnu/libvolt.so
	install -Dm755 $(LAYER_32) $(OUT)/flatpak.$*/stage/files/lib/i386-linux-gnu/libvolt.so
	install -Dm644 $(MANIFEST) $(OUT)/flatpak.$*/stage/files/share/vulkan/implicit_layer.d/$(MANIFEST)
	install -Dm644 LICENSE $(OUT)/flatpak.$*/stage/files/share/doc/volt/LICENSE
	install -Dm755 flatpak/volt-flatpak $(OUT)/flatpak.$*/stage/files/bin/volt-flatpak
	install -Dm755 $(LAUNCHER) $(OUT)/flatpak.$*/stage/files/bin/volt
	$(OSTREE) init --repo=$(OUT)/flatpak.$*/repo --mode=archive-z2
	$(PYTHON3) flatpak/commit.py "$*" "$(OUT)/flatpak.$*/repo" "$(OUT)/flatpak.$*/stage"
	$(FLATPAK) build-bundle --arch=$(FLATPAK_ARCH) $(OUT)/flatpak.$*/repo $@ \
	  $(FLATPAK_EXT_ID) "$*" --runtime
	rm -rf $(OUT)/flatpak.$*

$(OUT)/.dist-%: $(BIN_DIR)/volt-gui-% \
    $(LAYER_64) $(LAYER_32) $(LAUNCHER) $(DESKTOP) $(FLATPAK_BUNDLES) \
    $(MANIFEST) Makefile LICENSE README.md requirements.txt | $(OUT)
	rm -rf $(DIST)
	install -Dm755 $< $(DIST)/build/bin/volt-gui-$*
	install -Dm755 $(LAYER_64) $(DIST)/build/target/$(TRIPLE_64)/release/libvolt.so
	install -Dm755 $(LAUNCHER) $(DIST)/build/target/$(TRIPLE_64)/release/volt
	install -Dm755 $(LAYER_32) $(DIST)/build/target/$(TRIPLE_32)/release/libvolt.so
	install -Dm644 $(DESKTOP) $(DIST)/build/share/$(DESKTOP_FILE)
	install -Dm644 $(MANIFEST) $(DIST)/$(MANIFEST)
	install -Dm644 Makefile $(DIST)/Makefile
	install -Dm644 LICENSE $(DIST)/LICENSE
	install -Dm644 README.md $(DIST)/README.md
	install -Dm644 requirements.txt $(DIST)/requirements.txt
	cp -r $(DIST_TREES) $(DIST)/
	rm -rf $(DIST)/volt/target
	mkdir -p $(DIST)/build/bundles
	cp $(FLATPAK_BUNDLES) $(DIST)/build/bundles/
	touch $(DIST)/build/.venv
	touch $(DIST)/build/bin/* $(DIST)/build/share/* \
	  $(DIST)/build/bundles/* $(DIST)/build/target/*/release/*
	@touch $@

$(RELEASES)/volt-gui-$(VERSION)-%.tar.gz: $(OUT)/.dist-% | $(RELEASES)
	$(TAR) -czf $@ -C $(DIST_DIR) $(DIST_NAME)

$(CONTAINER_STAMP): container/Containerfile | $(OUT)
	$(CONTAINER) build --build-arg BASE=$(CONTAINER_BASE) -t $(CONTAINER_IMAGE) -f $< container
	@touch $@

release-container: $(CONTAINER_STAMP)
	$(CONTAINER) run --rm -v "$(CURDIR):/src:z" -w /src \
	  --user "$$(id -u):$$(id -g)" \
	  -e HOME=/tmp \
	  -e CARGO_HOME=/src/$(CONTAINER_OUT)/cargo \
	  -e NUITKA_CACHE_DIR=/src/$(CONTAINER_OUT)/nuitka-cache \
	  $(CONTAINER_IMAGE) make release OUT=$(CONTAINER_OUT)

install: | $(ROOT_GUARD) check-built $(LAYER_GUARD)
	install -Dm755 $(LAUNCHER)    $(DESTDIR)$(bindir)/volt
	install -Dm755 $(GUI_BIN)     $(DESTDIR)$(bindir)/volt-gui
	install -Dm755 $(LAYER_64)    $(DESTDIR)$(LIBDIR_64)/libvolt.so
	install -Dm755 $(LAYER_32)    $(DESTDIR)$(LIBDIR_32)/libvolt.so
	install -Dm644 $(MANIFEST)    $(DESTDIR)$(VK_LAYER_DIR)/$(MANIFEST)
	install -Dm644 $(DESKTOP)     $(DESTDIR)$(DESKTOP_DIR)/$(DESKTOP_FILE)
	install -Dm644 $(ICON_SOURCE) $(DESTDIR)$(ICON_DIR)/$(ICON_FILE)
	@test -z "$(LIVE_SYSTEM)" || ldconfig 2>/dev/null || true
	@test -z "$(LIVE_SYSTEM)" || update-desktop-database $(DESKTOP_DIR) 2>/dev/null || true
	@test -z "$(LIVE_SYSTEM)" || gtk-update-icon-cache -qtf $(datadir)/icons/hicolor 2>/dev/null || true
	@echo "install complete."
	@echo "  bin:       $(bindir)"
	@echo "  lib (64):  $(LIBDIR_64)"
	@echo "  lib (32):  $(LIBDIR_32)"
	@echo "  manifest:  $(VK_LAYER_DIR)"
	@echo "  launcher:  $(DESKTOP_DIR)/$(DESKTOP_FILE)"
	@echo "  icon:      $(ICON_DIR)/$(ICON_FILE)"

flatpak-install: | check-root check-sudo-user check-bundles
	@for b in $(FLATPAK_BUNDLES); do \
	  case "$$b" in /*) p="$$b";; *) p="$(CURDIR)/$$b";; esac; \
	  s="$(STATE_DIR)/.installed-$$(basename "$$b" .flatpak)"; \
	  if [ ! -e "$$s" ] || [ "$$b" -nt "$$s" ]; then \
	    su - "$$SUDO_USER" -c "$(FLATPAK) install --user -y --reinstall '$$p'" || exit 1; \
	    mkdir -p "$(STATE_DIR)" && touch "$$s"; \
	  fi; done
	@echo "flatpak extensions installed."

install-user: | check-not-root check-built check-no-system-layer
	install -Dm755 $(LAUNCHER)    $(USER_BIN)/volt
	install -Dm755 $(GUI_BIN)     $(USER_BIN)/volt-gui
	install -Dm755 $(LAYER_64)    $(USER_LIB)/$(LIBDIR_64_ARCH)/libvolt.so
	install -Dm755 $(LAYER_32)    $(USER_LIB)/$(LIBDIR_32_ARCH)/libvolt.so
	install -Dm644 $(MANIFEST)    $(USER_LAYER_DIR)/$(MANIFEST)
	install -Dm644 $(DESKTOP)     $(USER_DESK_DIR)/$(DESKTOP_FILE)
	install -Dm644 $(ICON_SOURCE) $(USER_ICON_DIR)/$(ICON_FILE)
	@echo "user install complete, no root used."
	@echo "  bin:       $(USER_BIN)"
	@echo "  lib:       $(USER_LIB)"
	@echo "  manifest:  $(USER_LAYER_DIR)"
	@echo "$(USER_BIN) must be on PATH: volt-gui runs volt to read your hardware."

flatpak-install-user: | check-not-root check-bundles
	@for b in $(FLATPAK_BUNDLES); do \
	  case "$$b" in /*) p="$$b";; *) p="$(CURDIR)/$$b";; esac; \
	  s="$(USER_STATE)/.installed-$$(basename "$$b" .flatpak)"; \
	  if [ ! -e "$$s" ] || [ "$$b" -nt "$$s" ]; then \
	    $(FLATPAK) install --user -y --reinstall "$$p" || exit 1; \
	    mkdir -p "$(USER_STATE)" && touch "$$s"; \
	  fi; done
	@echo "flatpak extensions installed for this user."

setup-user: install-user flatpak-install-user
	@echo "ready: launch volt-gui from your menu, or run $(USER_BIN)/volt-gui."

uninstall-user: | check-not-root
	rm -f $(USER_FILES)
	rm -rf $(USER_STATE)
	$(FLATPAK) uninstall --user -y $(FLATPAK_EXT_ID) 2>/dev/null || true
	rm -rf "$(HOME)/.config/volt-gui"
	@echo "user uninstall complete."

uninstall: | $(ROOT_GUARD)
	rm -f $(INSTALL_FILES)
	@test -z "$(LIVE_SYSTEM)" || rm -rf $(STATE_DIR)
	@test -z "$(LIVE_SYSTEM)" || ldconfig 2>/dev/null || true
	@test -z "$(LIVE_SYSTEM)" || update-desktop-database $(DESKTOP_DIR) 2>/dev/null || true
	@test -z "$(LIVE_SYSTEM)" || gtk-update-icon-cache -qtf $(datadir)/icons/hicolor 2>/dev/null || true
	@test -z "$(LIVE_SYSTEM)" -o -z "$$SUDO_USER" || \
	  su - "$$SUDO_USER" -c "$(FLATPAK) uninstall --user -y $(FLATPAK_EXT_ID) 2>/dev/null" || true
	@test -z "$(LIVE_SYSTEM)" -o -z "$$SUDO_USER" || \
	  su - "$$SUDO_USER" -c "rm -rf \"\$$HOME/.config/volt-gui\"" || true
	@echo "uninstall complete."

clean:
	rm -rf $(OUT) $(RELEASES) bin bundles py_env volt/target

check-root:
	@test "$$(id -u)" -eq 0 || { echo "error: needs root — run: sudo make $(MAKECMDGOALS)"; exit 1; }

check-sudo-user:
	@test -n "$$SUDO_USER" || { echo "error: SUDO_USER not set — run via 'sudo make ...' from your user shell"; exit 1; }

check-not-root:
	@test "$$(id -u)" -ne 0 || { echo "error: this installs into \$$HOME — run as your user, no sudo"; exit 1; }

check-built:
	@missing=; for f in $(BUILT_ARTIFACTS); do \
	  test -e "$$f" || missing="$$missing $$f"; done; \
	test -z "$$missing" || { \
	  echo "error: build artifacts missing:"; \
	  for f in $$missing; do echo "  $$f"; done; \
	  echo "run 'make' as your user first (GUI=$(GUI)), then re-run this target"; \
	  exit 1; }

check-bundles:
	@missing=; for b in $(FLATPAK_BUNDLES); do \
	  test -e "$$b" || missing="$$missing $$b"; done; \
	test -z "$$missing" || { \
	  echo "error: flatpak bundles missing:"; \
	  for b in $$missing; do echo "  $$b"; done; \
	  echo "run 'make flatpak' as your user first"; \
	  exit 1; }

check-no-user-layer:
	@home="$(USER_MANIFEST_HOME)"; \
	  test -z "$$home" -o ! -e "$$home/.local/share/vulkan/implicit_layer.d/$(MANIFEST)" || { \
	  echo "error: a user install already owns the layer at"; \
	  echo "  $$home/.local/share/vulkan/implicit_layer.d/$(MANIFEST)"; \
	  echo "two manifests naming the same layer is undefined: run 'make uninstall-user' first"; \
	  exit 1; }

check-no-system-layer:
	@test ! -e "$(VK_LAYER_DIR)/$(MANIFEST)" || { \
	  echo "error: a system install already owns the layer at"; \
	  echo "  $(VK_LAYER_DIR)/$(MANIFEST)"; \
	  echo "two manifests naming the same layer is undefined: run 'sudo make uninstall' first"; \
	  exit 1; }

help:
	@echo "make                    layer (64 + 32), launcher, gui ($(GUI)), desktop entry"
	@echo "make layer-64           64-bit layer and the volt launcher"
	@echo "make layer-32           32-bit layer"
	@echo "make gui-pyinstaller    gui binary via PyInstaller"
	@echo "make gui-nuitka         gui binary via Nuitka"
	@echo "make desktop            desktop entry only"
	@echo "make flatpak            flatpak runtime extension bundles"
	@echo "make dist               source + build tree in $(DIST_DIR)/ (GUI=$(GUI))"
	@echo "make release            full release into $(RELEASES)/ (host toolchain)"
	@echo "make release-container  the same, built inside $(CONTAINER_BASE)"
	@echo "install targets never build: run 'make' (and 'make flatpak') as your user first"
	@echo "sudo make install       install (GUI=$(GUI))"
	@echo "sudo make flatpak-install"
	@echo "sudo make uninstall"
	@echo "make setup-user         install-user + flatpak-install-user, no root"
	@echo "make install-user       layer, launcher and gui into ~/.local"
	@echo "make flatpak-install-user  the extensions, flatpak --user"
	@echo "make uninstall-user"
	@echo "make clean"
