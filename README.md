> [!NOTE]
> Bug reports and pull requests are welcome, but please understand that development happens in my free time and progress may be slow at times. The project is still maintained even if the last commit was made a while ago.

# volt-gui

> **My AMD Adrenaline / NVIDIA Settings Linux Alternative**

volt-gui is a graphical control panel for Vulkan games on Linux. Settings are
applied by **volt**, a Vulkan implicit layer written in Rust, so they work on
every Vulkan driver: RADV, ANV, NVK, AMDVLK, the NVIDIA proprietary driver.

The floor is **Vulkan 1.0**, and so is the ceiling: the layer requests no
extension beyond `VK_KHR_swapchain`, so every setting behaves the same on
every conformant driver. `VOLT_LOG=info` shows what was applied.

![](/images/1.png)
![](/images/2.png)
![](/images/3.png)

### At a glance

- **21 settings across 5 tabs**: GPU selection, display and swapchain, texture
  sampling, rendering toggles, and volt's own frame limiter.
- **Core Vulkan 1.0 only.** The layer asks for nothing beyond `VK_KHR_swapchain`,
  so behaviour never splits between drivers.
- **One value per setting**: the value volt forces, or `default`, which keeps
  whatever the game asked for. No ranges, no ordering, nothing to get backwards.
- **Lists read from your hardware.** Present modes, colour depths, colour spaces,
  transfer functions, alpha modes, GPU names, mip levels and LOD bias all come
  from a probe of your own device, not from a table built into volt-gui.
- **Enables nothing.** volt reads what the game asked for at device creation and
  applies a feature gated setting only where the game enabled that feature.
- **Every setting forces**, bar one. volt writes the value into its own copy of
  the create info, so a setting lands whether or not the game consulted a query
  first. GPU selection is the exception: there is no field naming the device, so
  hiding the others from enumeration is the only lever Vulkan gives.
- **Every path hooked, not just the obvious one.** The `2`/`EXT` query variants,
  device groups, shared swapchains, inline sampler writes and dynamic alpha to
  coverage get the same treatment as the core calls.
- **Dual-arch in one build**: `make` produces an x86_64 and an i686 layer served
  by a single manifest, so 32-bit games under Steam, Wine and Proton are covered.
- **Rootless install**, first class: everything into `~/.local`, for SteamOS,
  Bazzite, Silverblue and anything else with a read only `/usr`.
- **Flatpak support**, optional, via a runtime extension for
  `org.freedesktop.Platform` 23.08, 24.08 and 25.08.
- **Profiles and presets**: one TOML per configuration, switchable from the GUI,
  the system tray, or the launch command.

## Quick Start

```
# 1. Build and install, no root needed
git clone https://github.com/pythonlover02/volt-gui.git
cd volt-gui
make
make install-user

# 2. Open the panel, set what you want, press Apply
volt-gui

# 3. Launch the game through the launcher
volt -- ./game
```

That is a complete install for native, Steam, Wine and Proton games. Prefer a
system wide one? `make` then `sudo make install`. Pick one of the two, never
both.

Flatpak games need one extra piece, built and installed separately see
[Flatpak](#flatpak).

**Steam**, set the game Launch Options to:

```
volt -- %command%
```

## Table of Contents

- [What you can do?](#what-you-can-do)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Install paths](#install-paths)
- [Uninstalling](#uninstalling)
- [Cleaning build artifacts](#cleaning-build-artifacts)
- [Immutable Systems](#immutable-systems)
- [FEX-Emu / Box64](#fex-emu--box64)
- [Building Releases](#building-releases)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Files](#files)
- [Flatpak](#flatpak)
- [Flatpak without the launcher](#flatpak-without-the-launcher)
- [Profiles, Presets & Options](#profiles-presets--options)
- [What volt will never do](#what-volt-will-never-do)
- [Contributing](#contributing)

## What you can do?

Every setting defaults to **default**, meaning the layer does not touch that
value and the game keeps its own choice. A profile with everything on default does nothing.

Every setting is one value: the value volt forces, or `default`. There is no
range, no ordering, and nothing to get backwards.

| Tab | Section | Count | What it covers |
|-----|---------|------:|----------------|
| GPU | `[gpu]` | 1 | which device the game is shown |
| Display | `[display]` | 4 | present mode, image count, compositing, clipping |
| Textures | `[textures]` | 7 | magnification, minification, mip behaviour, anisotropy, LOD bias and range |
| Rendering | `[rendering]` | 4 | sample shading, alpha to coverage, alpha to one, depth clamp |
| Framerate | `[framerate]` | 5 | frame limit, offset, cadence, method, pacing |

Many of the values a setting offers come from your own hardware, not from a
list built into volt-gui. Present modes, image counts and alpha modes come
from what the surface reports, the GPU list from what the driver enumerates,
and anisotropy, mip levels and LOD bias run up to the limits the device
gives. A setting whose feature the device lacks holds nothing but `default`,
and so does every device backed setting until the probe has run: volt-gui
offers no option it has not read.

The rest carry fixed lists, because there is nothing to read. `nearest` and
`linear` are core Vulkan with no feature, no extension and no query behind
them, so every driver has both and none of them reports it. The five
**Framerate** settings have nothing to read at all: a game never tells Vulkan
what frame rate it wants.

Settings are read once, when the game starts, and never change while it
runs. Press Apply, then start the game again.

volt-gui learns this by running `volt-probe` under the profile you are
editing. It opens a one pixel window that is never mapped, creates a surface,
a swapchain and a sampler so the layer sees every path it needs, records what
the device reported, and exits. Nothing appears on screen and nothing is
drawn.

```
volt --probe myprofile -- volt-probe
```

It opens an X11 surface, which every desktop has, since a Wayland session runs
XWayland. It is not the only surface a game opens, because Wine and Proton have
native Wayland drivers and gamescope is its own path again, and the profile is
written before volt knows which one the game will pick. Reporting two backends
would offer values belonging to the path the game did not take.

Present modes, image counts and alpha modes are answered against a surface
rather than against the card, so the presentation path bounds them as much as
the hardware does, and a short list there is the answer rather than a failure.
Those three are also the only settings this affects. The lists mostly agree
across backends, and where they do not, the layer already has the path: image
count is clamped against the surface the game actually opened, and a present
mode or alpha mode that surface turns down leaves the game's own value in place
with a warning logged. Reading a native Wayland surface directly is on the
list; until then the cost of the mismatch is a line in the log.

A value volt has no name for still appears in the list, still saves to a
profile, and still applies. Where the specification admits only what a query
returned, a value the device did not report is not forced: volt keeps the
game's own value and logs a warning.

Where the specification bounds a value LOD bias against the device limit,
image count against what the surface allows volt clamps what it passes
down. That clamp is correctness, not a setting.

### GPU
- **Physical Device**: pick which GPU the game sees, listed by name. The
  layer hides the rest during device enumeration, so it works on every Vulkan
  driver. If nothing matches, the full list comes back and a warning is
  logged.

  This is the one setting volt cannot force. Every other card is written into
  a structure volt hands down, but nothing names the device a swapchain runs
  on: the game already holds a physical device by the time volt sees anything
  it could patch. A game that ignores enumeration order keeps the device it
  picked.

### Display
- **VSync / Present Mode**: whatever the surface supports. `immediate` turns
  vsync off, `mailbox` is low latency vsync, `fifo` is classic vsync,
  `fifo_relaxed` tears only below refresh. Every other mode is hidden from
  the list the game is shown, so a game's own vsync menu cannot offer one you
  ruled out. That filtering is what makes the setting hold wherever the game
  asks Vulkan what it may use: a swapchain may only switch between modes the
  surface reported, and a present may only name one the swapchain was built
  with. A mode the surface does not support falls back to the game's own
  choice with a warning.

  A game that enables `VK_KHR_swapchain_maintenance1` can switch present mode
  without rebuilding the swapchain. It can only switch among the modes the
  surface offered it, which volt has already filtered, so the setting still
  holds.
- **Swapchain Images**: how many images the swapchain holds. This is the
  frames in flight control: more images let the game run further ahead of
  the GPU, which smooths frame delivery and costs input lag, and fewer hold
  it closer to the display. If you came looking for an anti-lag setting,
  this is it. The list is what the surface allows, and the choice is
  reported back to the game, so a game that derives its count from the
  surface honours it on its own.
- **Composite Alpha**: how the compositor treats the finished image's alpha.
  Forcing `opaque` skips compositor blending on Wayland. A value the surface
  does not report falls back to the game's own choice with a warning.
- **Clipped Presentation**: whether the driver may skip pixels another window
  covers. On or off.

### Textures
- **Magnification Filter**: how a texture is sampled where it is drawn larger
  than its own size, which is anything close to the camera. `nearest` is sharp
  unfiltered pixels, `linear` smooths between them. This is the one filter a
  still screenshot shows you.
- **Minification Filter**: the same question where the texture is drawn
  smaller, which is most of the screen. `nearest` takes one texel and shimmers
  as the camera moves; `linear` averages and settles. This is where mipmaps
  and anisotropic filtering do their work, so leave it on `linear` unless you
  want the crawl.
- **Mipmap Mode**: a hard cut between mip levels, or a blend across them.

  These are three sampler fields and so they are three settings, which means
  every combination is reachable and none of them overrides another. The
  classic three: retro is `nearest`/`nearest`/`nearest`, bilinear is
  `linear`/`linear`/`nearest`, trilinear is `linear`/`linear`/`linear`. And
  the one no single named mode ever offered: sharp pixel art without distant
  shimmer is `nearest`/`linear`/`linear`.
- **Anisotropic Filtering**: off up to whatever your GPU reports. The list is
  read from the device, so it holds nothing but `default` only where the device
  itself lacks `samplerAnisotropy`. volt never enables the feature: where the
  game left it off the setting is ignored and a line is logged. Nearly every
  game enables it.
- **LOD Bias**: shift mipmap selection, sharper or blurrier, across the range
  the device allows.
- **Mip Floor** and **Mip Ceiling**: the lowest and highest mip levels
  samplers may use, called minimum and maximum LOD in Vulkan. A ceiling that
  lands below the floor is swapped with it rather than dropped.

### Rendering
- **Sample Shading**: shade at sample rate inside MSAA targets to reduce
  shimmer. The list is read from the device, so it holds nothing but `default`
  only where the device itself lacks `sampleRateShading`. volt never enables the
  feature: most deferred renderers never ask for it, and where the game left it
  off the setting is ignored and a line is logged.
- **Alpha To Coverage**: turn fragment alpha into coverage. Softens cutout
  edges on foliage and fences, and only does anything where the game already
  renders to an MSAA target.
- **Alpha To One**: force fragment alpha to 1 after the shader runs. Read from
  the device like sample shading, and volt never enables the feature: where the
  game left it off the setting is ignored and a line is logged.
- **Depth Clamp**: keep fragments outside the near and far planes and pin their
  depth rather than discarding them. Stops weapon models being sliced open
  against a wall. The same toggle covers the far plane, where geometry stops
  disappearing and flattens onto the plane instead, so try it per game. Most
  games never enable `depthClamp`, and volt will not enable it for them, so
  this card does nothing in most of them and logs a line saying so. Where a
  game did enable it, it usually wanted it for one pass, and forcing the
  toggle applies it everywhere.

### Framerate
- **Frame Limit**: cap the frame rate at present time, from a fixed list of
  common caps. Deadlines follow a fixed target timeline rather than the
  last present, unless the method is reactive, so scheduler jitter does not
  build up into a drift below the rate you asked for. The timeline is kept per
  swapchain and dropped when that swapchain is destroyed.
- **Frame Limit Offset**: shift the cap a few frames up or down, -10 to 10
  in steps of two, no shift by default. VRR displays want the cap sitting
  just under refresh: pick 144, set the offset to -6, and you land on 138.
  volt does not read your refresh rate and never shifts a cap by itself,
  since most displays are not VRR. Only does something when Frame Limit is
  set.
- **Frame Limit Cadence**: which rate the limiter paces at. `fixed` is your
  cap and nothing else. `smooth` paces at the slowest of the last few frames
  instead, so the fast frames wait for the slow ones and the cadence comes
  out even at whatever the machine is holding. `dynamic` reads exactly what
  `smooth` reads and rounds it down to a quarter step of the cap. The steps
  are quarter steps of the cap's frame time, so they sit close together low
  down and far apart up top: a 60 cap steps 60, 48, 40,
  34, 30, while a 240 cap steps 240, 192, 160, 137, 120. Both take the idea
  from consoles, which pick a rate the machine can hold and stay on it. A
  console gets there by dropping resolution, which volt cannot touch, so
  frame handling is the one place the idea fits. A limiter can only make
  frames later, which is why neither reads the average: a frame slower than
  the average could never be paced up to it. Both climb back on their own,
  and neither goes faster than the cap you set. The trade is frames for
  evenness: `fixed` does nothing at all once the machine falls under the cap,
  so what you get is whatever the machine produced, one frame long and the
  next short. A rate sitting right on one of `dynamic`'s steps can bounce
  between two of them, which is what rounding costs: `smooth` is the same
  reading without it. Set `fixed` if the machine holds the cap, or if you
  want every frame you can get for the input latency. Only does something
  when Frame Limit is set.
- **Frame Limit Method**: early holds the frame back so presents leave on a
  fixed cadence; late lets the present through and waits afterwards, so the
  game starts its next frame later and samples input closer to display time;
  reactive waits where early does but measures from the frame just shown
  instead of a fixed timeline, so a slow frame is never chased with a fast
  one. late is the equivalent of Reflex and Anti-Lag here: holding the next
  frame back is the mechanism those use too. Going further needs feedback
  on when the GPU actually finished, which lives in `VK_KHR_present_wait`
  and `VK_EXT_present_timing`, so it stays out.
- **Frame Pacing**: how the limiter kills time, from cheapest to tightest.
  `sleep` hands the whole wait to the kernel. `sliced` sleeps in short steps
  and rechecks the clock, correcting for the kernel waking late. `precise`
  sleeps most of the interval then busy waits half a millisecond. `spin`
  busy waits the whole interval, the steadiest option and the only one that
  keeps a core awake.

## How It Works

volt registers as an implicit Vulkan layer (`VK_LAYER_VOLT_settings`) through
the manifest at `/usr/share/vulkan/implicit_layer.d/VkLayer_volt.json`. The
manifest declares `enable_environment = VOLT_ENABLE`, so the loader always
discovers the layer but only activates it when `VOLT_ENABLE=1` is set in the
target process, which the `volt` launcher does for that process only.

The layer reads the selected profile from `~/.config/volt-gui/<profile>.toml`
once at startup and rewrites the Vulkan calls the game makes. The tabs run in
the order the layer acts:

| Tab | Where the layer acts |
|-----|----------------------|
| GPU | `vkEnumeratePhysicalDevices`, `vkEnumeratePhysicalDeviceGroups`, `vkEnumeratePhysicalDeviceGroupsKHR` |
| Display | `vkGetPhysicalDeviceSurfacePresentModesKHR`, `vkGetPhysicalDeviceSurfacePresentModes2EXT`, `vkGetPhysicalDeviceSurfaceCapabilities(2)KHR`, `vkCreateSwapchainKHR`, `vkCreateSharedSwapchainsKHR` |
| Textures | `vkCreateSampler`, `vkWriteSamplerDescriptorsEXT` |
| Rendering | `vkCreateGraphicsPipelines`, `vkCmdSetAlphaToCoverageEnableEXT`, `vkCmdSetAlphaToOneEnableEXT`, `vkCmdSetDepthClampEnableEXT` |
| Framerate | `vkQueuePresentKHR` |

Device creation is read and never modified: volt learns which features the game
enabled so a setting that needs one applies only where the game asked for it,
and it enables nothing the game left off.

Every setting is hooked on each path that reaches it, not just the obvious
one. A game that queries present modes through
`vkGetPhysicalDeviceSurfacePresentModes2EXT`, enumerates through
`vkEnumeratePhysicalDeviceGroups`, creates samplers inline through
`vkWriteSamplerDescriptorsEXT` or sets alpha to coverage as dynamic state gets
the same treatment as one that takes the core path. Where a surface
capabilities query carries a present mode list in its `pNext` chain, that list
is filtered in place too, so a game reading the compatible modes from there
sees the same set as one that asks for them directly.

An entry point for an extension the game never enabled is unreachable, and the
layer never hands it out: the hook is only returned when the call actually
resolves further down the chain.

Settings are frozen for the life of the process. Press Apply, then start the
game again.

volt-gui is the PySide6 front end. It edits the same profile files the layer
reads Apply just saves the profile, no elevated permissions, no scripts.

## Requirements

| Component | Requirement |
|-----------|-------------|
| **Layer** | Vulkan 1.0+ with `VK_KHR_swapchain`, Linux x86_64 (and i686 for 32-bit games) |
| **Build** | Rust 1.85.1+ with rustup, GNU make 4.3+ |
| **32-bit layer** | `gcc-multilib`, `libc6-dev-i386`; the `i686-unknown-linux-gnu` target is added automatically |
| **GUI**   | Python 3.10+, PySide6 (a venv is created under `build/` by the make targets) |
| **Flatpak bundles** | `flatpak`, `ostree` |
| **Container release** | `podman` or `docker` |
| **Probe** | `volt-probe`, built and installed alongside the launcher: every device backed option list is read through it |
| **Probe build** | `libxcb` headers (`libxcb1-dev` or your distribution's equivalent) |

Native aarch64 builds are not provided. See
[FEX-Emu / Box64](#fex-emu--box64) if you are on an aarch64 host.

## Installation

### Arch Linux (AUR)

There is an unofficial package on the AUR,
[volt-gui](https://aur.archlinux.org/packages/volt-gui). I do not maintain it,
but the packager has been in touch and has been good to deal with, so I have no
reason to steer anyone away from it.

Read the `PKGBUILD` before you build it. Not because of the packager, but
because the AUR lets anyone submit anything, so the build script is whatever
the submitter wrote, every time.

Building from source, or using the release archives, is what this repository
supports directly.

### From source

Every build target is a file, so make only rebuilds what actually changed.
Everything lands under `build/`; `make clean` is a single `rm -rf`.

| Command | What it does |
|---------|--------------|
| `make` | builds both layers, the `volt` launcher, the GUI and the desktop entry |
| `make layer-64` | `build/target/x86_64-unknown-linux-gnu/release/{libvolt.so,volt,volt-probe}` |
| `make layer-32` | `build/target/i686-unknown-linux-gnu/release/libvolt.so` |
| `make gui` | `build/bin/volt-gui` |
| `make desktop` | `build/share/volt-gui.desktop` |
| `make flatpak` | `build/bundles/*.flatpak`, one per supported runtime |
| `make dist` | the sources with `build/` populated, in `build/dist/` |
| `make release` | the release archive in `releases/`, host toolchain |
| `make container-image` | the build image only, from `container/Containerfile` |
| `make release-container` | the release archive, built inside that image |
| `sudo make install` | launcher, GUI, both layers, the manifest, the desktop entry and the icon |
| `make install-user` | the same into `~/.local`, no root |
| `sudo make flatpak-install` | the extension bundles, for the invoking user. Needs `make flatpak` first. |
| `make flatpak-install-user` | the extension bundles, `flatpak install --user`, no root. Needs `make flatpak` first. |
| `make setup-user` | `install-user` and `flatpak-install-user` at once. Needs `make flatpak` first. |
| `sudo make uninstall` | everything, including the user Flatpak extension and `~/.config/volt-gui` |
| `make uninstall-user` | the rootless install, including `~/.config/volt-gui` |
| `make clean` | `rm -rf build releases` |
| `make help` | the same list, printed from the Makefile itself |

```
git clone https://github.com/pythonlover02/volt-gui.git
cd volt-gui
make
sudo make install
```

A bare `make` builds both architectures and nothing else. The 32-bit layer is
not an optional extra any Steam library has 32-bit titles so it is part of
the default build; `make layer-32` exists only for building that one piece
while you work on it, and adds the Rust target for you if it is missing. The
Flatpak bundles are the opposite: they are optional, they are built only by
`make flatpak`, and neither install target touches them. `make` followed by
`make install-user` or `sudo make install` is a complete install for native,
Steam, Wine and Proton games.

The artifacts on the Actions tab are `make dist` trees, so they are a clone of
this repository with `build/` already filled in. Unpack one and `sudo make install`
installs it without compiling anything, and `make` on top rebuilds only what you
changed.

`volt-probe` is built by `make` and installed by both install targets, so
there is nothing extra to fetch at runtime. It links `libxcb`, which every
desktop already carries.

The GUI is built with PyInstaller into a single `build/bin/volt-gui`.

Building with `sudo` is refused: the build targets stop with an error rather
than leaving a root-owned `build/`. The install targets are the mirror of
that they only copy what is already in `build/`, and stop with an error
naming what is missing if you have not built it yet. Build as your user,
install as root. volt-gui itself also refuses to start under `sudo`.

Packagers can skip root entirely with `DESTDIR` set, `make install` stages
into the given prefix without needing it:

```
make
make install DESTDIR="$PWD/pkg" PREFIX=/usr
```

With `DESTDIR` set the install also skips `ldconfig`, the desktop database and
the icon cache, since none of those apply to a staged tree, and skips the check
for a competing user install.

### Install paths

| File | System install | User install |
|------|----------------|--------------|
| Launcher | `/usr/bin/volt` | `~/.local/bin/volt` |
| Probe | `/usr/bin/volt-probe` | `~/.local/bin/volt-probe` |
| GUI | `/usr/bin/volt-gui` | `~/.local/bin/volt-gui` |
| Library (64-bit) | `/usr/lib/x86_64-linux-gnu/libvolt.so`, or `/usr/lib64`, or `/usr/lib` | `~/.local/lib/volt/x86_64-linux-gnu/libvolt.so` |
| Library (32-bit) | `/usr/lib/i386-linux-gnu/libvolt.so`, or `/usr/lib32`, or `/usr/lib` | `~/.local/lib/volt/i386-linux-gnu/libvolt.so` |
| Layer manifest | `/usr/share/vulkan/implicit_layer.d/VkLayer_volt.json` | `~/.local/share/vulkan/implicit_layer.d/VkLayer_volt.json` |
| Desktop entry | `/usr/share/applications/volt-gui.desktop` | `~/.local/share/applications/volt-gui.desktop` |
| Icon | `/usr/share/icons/hicolor/256x256/apps/volt-gui.png` | `~/.local/share/icons/hicolor/256x256/apps/volt-gui.png` |
| Flatpak install stamps | `/var/lib/volt` | `~/.local/share/volt` |

The library directory is picked from what your distribution already has:
`lib/x86_64-linux-gnu` and `lib/i386-linux-gnu` where those exist, otherwise
`lib` and `lib32`, otherwise `lib64` and `lib`. Because the manifest lands in
the system wide implicit layer directory and the libraries in the standard
paths, 32-bit games find the 32-bit layer and 64-bit games the 64-bit one with
no `VK_LAYER_PATH` mapping of any kind.

> [!WARNING]
> Avoid changing `PREFIX` away from `/usr` or `/usr/local`. The Vulkan loader
> only scans a fixed set of manifest directories
> (`/usr/share/vulkan/implicit_layer.d`,
> `/usr/local/share/vulkan/implicit_layer.d`,
> `$XDG_DATA_DIRS/vulkan/implicit_layer.d` and `$VK_LAYER_PATH`). Installing to
> e.g. `/opt/volt` puts the manifest where nothing reads it, the library where
> `ldconfig` does not see it, and the launcher off `$PATH`. `library_path` in
> the manifest is a bare filename, which is what lets one manifest serve both
> architectures, so the `.so` has to be reachable through `ldconfig` or
> `LD_LIBRARY_PATH` either way.

### Uninstalling

```
sudo make uninstall     # system install
make uninstall-user     # ~/.local install
```

`sudo make uninstall` removes the launcher, the GUI, both libraries, the
manifest, the desktop entry, the icon, the install stamps under `/var/lib/volt`,
the user scope Flatpak extension, and `~/.config/volt-gui` for the invoking
user. Run directly as root there is no `SUDO_USER` to work from, so the user
scope steps are skipped: remove `~/.config/volt-gui` and the Flatpak extension
as your own user if you want those gone too.

`make uninstall-user` does the same for `~/.local`, including the Flatpak
extension and `~/.config/volt-gui`.

Neither target touches a volt-gui 1.x install. 1.x lived in `/usr/local/bin`,
2.0 lives in `/usr/bin`, and the desktop entry is the only file they share.
Remove 1.x with `make remove` from a v1.4.1 checkout, or by hand:

```
sudo rm -f /usr/local/bin/volt /usr/local/bin/volt-gui /usr/local/bin/volt-helper
sudo rm -f /usr/share/applications/volt-gui.desktop
sudo update-desktop-database /usr/share/applications
```

Do it before installing 2.0, not after. `/usr/local/bin` comes before
`/usr/bin` on most distributions, so a leftover 1.x `volt` shadows the 2.0
launcher. It never sets `VOLT_ENABLE`, the layer stays inactive, and every
setting silently does nothing. If 2.0 looks like it has no effect, run
`which volt` first.

### Cleaning build artifacts

```
make clean
```

Removes `build/` and `releases/`, along with any stray `bin/`, `bundles/`,
`py_env/` and `volt/target/` left over from older layouts. The venv, the
container image stamp and the cargo target directory all live under `build/`,
so nothing survives it.

## Immutable Systems

On SteamOS, Bazzite, Silverblue and anything else with a read only `/usr`,
`sudo make install` means `steamos-readonly disable` or a layered package, redone
after every system update. Nothing here needs that:

```
make
make install-user
```

Add the Flatpak extension too, if you want it:

```
make flatpak
make flatpak-install-user
```

`make setup-user` runs both installs in one step once the bundles exist.

`install-user` puts the launcher and the GUI in `~/.local/bin`, both layers under
`~/.local/lib/volt` and the manifest in `~/.local/share/vulkan/implicit_layer.d`,
which the loader already searches, so no environment variable is needed to find
it. The `.so` still is: `library_path` in the manifest is a bare filename, which
is what lets one manifest serve both architectures, so the `volt` launcher adds
both layer directories to `LD_LIBRARY_PATH` and ld.so picks the one matching the
game. `flatpak-install-user` installs the extension bundles with
`flatpak install --user`, which never needed root anyway.

`~/.local/bin` has to be on your `PATH`, because volt-gui runs `volt` and
`volt-probe` to read your hardware.

Pick one of the two installs, not both. The loader scans the system and the user
directory alike, so two manifests naming `VK_LAYER_VOLT_settings` leave it
undefined which one is used, or whether the layer is inserted twice and every
setting applied twice over. Both install targets refuse to run while the other
one owns the layer, and name the uninstall that clears the way.

The GUI is also one self contained binary, so unpacking a release archive and
double clicking `build/bin/volt-gui` opens the editor with nothing
installed at all. That is enough to write and copy profiles and not enough to
use them: with no layer on disk there is nothing for the probe to load, so every
device backed card holds nothing but `default`.

The Flatpak extension never covers native Steam games: they run under the Steam
Linux Runtime, which is not Flatpak, so a `--user` extension is never mounted
for them. The native install does reach them. Steam expands `%command%` on the
host, so the launcher only has to be on your `PATH`, and the runtime container
bind mounts your home directory and imports the host's implicit layers, so the
manifest and both layer directories under `~/.local` stay visible inside it.

## FEX-Emu / Box64

On an aarch64 host, x86_64 Vulkan games run through FEX-Emu or Box64. There is
no native aarch64 build here, because every shipping Vulkan game on Linux has an
x86_64 build and the translated x86_64 path is what people actually use.

Translation layers run the game inside their own root directory: a tree of
x86_64 binaries and libraries separate from the aarch64 host `/usr`. The layer
has to be installed into that tree, not the host.

### Flatpak, if your host runs x86_64 binaries transparently

If the kernel routes x86_64 ELFs through FEX-Emu or Box64 via `binfmt_misc`, an
x86_64 Flatpak runtime behaves like any other runtime and the extension is
picked up by games running inside it. Flatpak itself does not translate between
architectures, so set that up first, then:

```
flatpak install org.freedesktop.Platform//24.08 --arch=x86_64
make flatpak
make flatpak-install-user
```

### Otherwise: install into the translation layer root

```
make
make install DESTDIR=/path/to/translation-root
```

The destination must be a tree where the translated process sees `/usr/` as the
standard layout. Afterwards the manifest lives at
`<root>/usr/share/vulkan/implicit_layer.d/VkLayer_volt.json` and the libraries
under `<root>/usr/lib/…`, and the x86_64 loader inside the translated process
finds them through the normal paths. With `DESTDIR` set the install needs no
root and touches nothing on the host, so the two are independent: run
`make DESTDIR=/path/to/translation-root uninstall` to clear the tree, and
`make uninstall-user` or `sudo make uninstall` for anything on the host itself.

## Building Releases

Both release targets produce the same file in `releases/`:

```
volt-gui-<version>.tar.gz
```

The archive is a ready-to-install tree: the compiled layers sit at the paths
the Makefile expects, so unpacking and running `sudo make install` installs
without compiling anything. The sources, the Flatpak bundles and the Makefile
ride along.

**`make release`** builds against your own toolchain and glibc. Fast, and
right for a local build, but the binaries inherit your system's glibc floor.

**`make release-container`** builds everything inside `rust:1.85.1-bookworm`
(Debian 12, glibc 2.36, Python 3.11) from `container/Containerfile`, so the
floor is fixed regardless of what you run. It builds into `build/container/`,
so it never collides with your host build and neither invalidates the other.
The container runs as your own uid, so nothing it writes is root-owned.

Override the base if you want a different floor:

```
make release-container CONTAINER_BASE=rust:1.85.1-bullseye
make release-container CONTAINER=docker
```

Bullseye drops the floor to glibc 2.31 but ships Python 3.9, which is below
what the GUI needs use it only for `make layer-64 layer-32` inside the
container, not for a full release.

## Usage

The launcher syntax is:

```
volt [--probe] [PROFILE] -- COMMAND [ARGS...]
volt -- COMMAND [ARGS...]      # the default profile, ~/.config/volt-gui/default.toml
volt --help                    # or -h
```

Everything before `--` is launcher options: an optional profile name and an
optional `--probe`. Everything after is the command to run. Prepend it to your
game command:

```
volt -- %command%                # Steam, default profile
volt myprofile -- %command%      # Steam, named profile
volt -- ./game                   # terminal
volt -- flatpak run com.example.Game
```

The launch command for the selected profile is always shown next to the Apply
button in volt-gui, ready to copy.

A profile name must be non-empty printable ASCII with no path separator and no
`..`. Anything else falls back to the default profile with a warning. The
launcher writes a fully commented profile on first use if the file does not
exist yet.

`--probe` additionally asks the layer to record what the device supports into
`probe.toml`, once, when the first swapchain is created. That is what fills the
option lists, and it is what volt-gui runs behind the scenes:

```
volt --probe myprofile -- vkgears
```

To see what actually applied, raise the log level:

```
VOLT_LOG=info volt -- ./game
```

Every line is prefixed `[volt]` and goes to stderr.

## Environment Variables

| Variable | Purpose | Values | Default |
|----------|---------|--------|---------|
| `VOLT_CONFIG_NAME` | which profile the layer loads. Set by the launcher from the profile argument, and settable by hand. | any profile name (sanitised) | `default` |
| `VOLT_LOG` | log verbosity, written to stderr | `off`, `error`, `warn`, `info` | `warn` |
| `VOLT_PROBE` | write `probe.toml` when the first swapchain is created. Set by the launcher from `--probe`. | any non-empty value | *(unset)* |
| `VOLT_ENABLE` | activates the implicit layer. Set by the launcher on the child process, or by the wrapper inside a Flatpak sandbox. | `1` | *(unset)* |
| `VOLT_DISABLE` | the loader's own off switch, declared by the manifest | `1` | *(unset)* |

Two more are read but not owned by volt: `HOME` decides where profiles live,
and falls back to `/tmp` with a warning if it is unset, and `LD_LIBRARY_PATH`
is extended by the launcher with both `~/.local/lib/volt` directories so a
rootless install can be found, preserving whatever was already there.

There is no environment override for the settings themselves. A profile file is
the only way to set them, which is what keeps the panel and the layer describing
the same thing.

## Files

Everything volt and volt-gui write lives in one directory.

| Path | What it is |
|------|------------|
| `~/.config/volt-gui/default.toml` | the default profile |
| `~/.config/volt-gui/<name>.toml` | named profiles, one per configuration |
| `~/.config/volt-gui/probe.toml` | what the last probe read from this device |
| `~/.config/volt-gui/options.toml` | volt-gui's own preferences and the last active profile |

Profiles are plain TOML with one section per tab and one string per setting,
so they can be written by hand, copied between machines, or kept in a dotfiles
repository. `probe.toml` is written by the layer and read by the GUI; volt-gui
watches it and rebuilds the option lists as soon as it changes, which is how a
freshly probed device fills the panel without a restart. Deleting it costs
nothing but a re-probe.

## Flatpak

Flatpak games run sandboxed and cannot see host environment paths, so the layer
ships as a **Flatpak runtime extension** for `org.freedesktop.Platform` 23.08,
24.08 and 25.08. The bundle mounts both libraries, the manifest and a small
wrapper script under `/usr/lib/extensions/vulkan/volt` inside the runtime.

This is a separate, optional install: neither `make` nor the install targets
produce or touch the bundles. Build them explicitly, then install them:

```
make flatpak
make flatpak-install-user     # or: sudo make flatpak-install
```

`make flatpak` lists both layers and the launcher as prerequisites, so it
builds whatever is missing on its own. `make setup-user` runs `install-user`
and `flatpak-install-user` together once the bundles exist.

One bundle is produced per supported runtime:

```
org.freedesktop.Platform.VulkanLayer.volt-23.08.flatpak
org.freedesktop.Platform.VulkanLayer.volt-24.08.flatpak
org.freedesktop.Platform.VulkanLayer.volt-25.08.flatpak
```

Install the one matching your runtime; run `flatpak list` and look for
`org.freedesktop.Platform` if you are unsure. Multiple versions can coexist.
The bundle always carries the 32-bit library too, for Flatpak games that run
32-bit Vulkan binaries.

```
flatpak install --user build/bundles/org.freedesktop.Platform.VulkanLayer.volt-24.08.flatpak
flatpak uninstall --user org.freedesktop.Platform.VulkanLayer.volt
```

The `volt` launcher detects `flatpak run` commands and routes activation
through the in-sandbox wrapper automatically:

```
volt -- flatpak run com.example.Game
volt -- flatpak run --branch=stable com.example.Game   # flags pass through
volt myprofile -- flatpak run com.example.Game         # named profile
```

It rewrites the command to run the wrapper through `--command=` and injects the
profile name and the probe flag as sandbox environment variables. The wrapper
sets `VOLT_ENABLE=1`, adds the extension's data, binary and library directories
so the loader finds the manifest and the matching `.so`, then execs the
application entry point, read from `/app/manifest.json` and falling back to the
`command` key in `/.flatpak-info`. Where neither names one the wrapper stops
with an error rather than exec'ing nothing.

There is no Flatpak build of volt-gui itself, only the layer extension.

### Flatpak without the launcher

Everything above prepends `volt` to a `flatpak run` command. You can skip the
launcher entirely and call the in sandbox wrapper yourself, useful where only
the extension is installed and there is no `volt` on `$PATH`:

```
flatpak run --command=/usr/lib/extensions/vulkan/volt/bin/volt-flatpak com.example.Game
```

Plain `VOLT_*` variables set on the host shell reach the sandbox, so a profile
or a log level can be prepended the usual way:

```
VOLT_CONFIG_NAME=myprofile flatpak run --command=/usr/lib/extensions/vulkan/volt/bin/volt-flatpak com.example.Game
```

The same line works as a Steam **Launch Options** entry for a Flatpak game:

```
/usr/lib/extensions/vulkan/volt/bin/volt-flatpak %command%
```

Your home directory is mounted into the sandbox, so `~/.config/volt-gui`
resolves exactly as it does natively and profiles written in the panel apply
unchanged.

## Profiles, Presets & Options

### Profiles

Profiles are TOML files in `~/.config/volt-gui/`, one per configuration.
Create and switch them from the GUI or the system tray; select one at launch
with `volt <name> -- ...`. Switching profiles saves the one you were on first,
so nothing is lost on the way out, and restarts the probe so the lists match
the profile you are now editing.

### Presets

Presets populate the active profile with curated values, from **Quality**
(trilinear, 16x anisotropy, blended mips, 10 bit colour, classic vsync) down
to **Potato Low Latency** (bilinear, anisotropy off, hard mip cuts, immediate
present, 2 image swapchain).
A preset writes every value in the profile, so anything it does not set goes
back to default. That includes the frame limit, composite alpha and clipped
presentation: those depend on your display and your compositor, so those
choices stay yours.

A preset can name something your hardware does not offer. That setting resets
to default and volt-gui says which ones, so the rest of the preset still
lands.

### Options

The **Options** tab holds volt-gui's own preferences rather than anything the
layer reads: theme, window transparency, interface scale, whether the window
starts maximised or minimised to tray, the system tray icon, and the welcome
window. They save themselves as you change them
and take effect when volt-gui is restarted. Only one instance runs at a time.

## What volt will never do

volt changes what the game asks Vulkan for; it never draws. Anything that
requires injecting shaders or processing the image is out of scope:

- Sharpening, FSR or any upscaling, frame generation, post processing.
- Forced MSAA or SSAA. Adding samples means recreating every render target,
  adding resolves and rewriting the pipelines and the shaders that read them,
  which is the game's frame graph rather than a value passing by.
- Colour depth, colour space or transfer function. Every ten bit surface
  format is UNORM, so forcing eight to ten drops hardware sRGB encoding and
  the picture comes out washed out, and a game that hardcoded its format is
  left with image views that no longer match the swapchain. None of the three
  makes a game render wider content either: a wider container is the whole of
  the win, and breakage is the price. A game that genuinely wants HDR asks for
  it itself, through DXVK_HDR, PROTON_ENABLE_HDR or gamescope.
- Cubic filtering. It needs `VK_EXT_filter_cubic`, and it is admitted per
  format while a sampler names no format at all, so there is no moment at
  which volt can tell whether the filter would be legal.
- Overlays and HUDs. Use MangoHud for that.
- Overclocking, fan curves, power limits. That is sysfs territory, not the
  Vulkan API. Use LACT for that, or CoreCtrl if you also want CPU controls.
- OpenGL. The per driver environment variable maze that OpenGL support
  requires is exactly what this rewrite retired.
- Enable a Vulkan device feature or extension the game did not request. Where
  a setting needs a feature, volt reads what the game enabled and applies the
  setting only where the game enabled it.
- Require a Vulkan extension. Core 1.0 and `VK_KHR_swapchain` are the whole
  surface volt asks for, so behaviour never splits between drivers. volt may
  intercept an extension command the game itself calls, so a setting keeps
  applying where the game moved that state elsewhere; a hook for an extension
  the game never enabled is unreachable and its entry point is never handed
  out.
- Resolution scaling. Presenting an image smaller than the surface needs
  `VK_KHR_surface_maintenance1` and `VK_KHR_swapchain_maintenance1`, and
  volt enables neither, so that path exists only where the game asked for
  both. Use gamescope for that.
- Frame pacing tighter than the limiter gives. Deadlines measured against
  the display rather than a clock need `VK_KHR_present_wait` or
  `VK_EXT_present_timing`. The late method is as close as core Vulkan
  reaches.
- Change a setting under a running game. The profile is read once at startup.
- Write into memory the game owns. volt patches the structures it passes on
  and fills the arrays a query asks it to fill; a `pNext` chain the game built
  is read and never written. A setting reaches the game through the lists volt
  hands it, not by reaching into what the game already built.

## Contributing

Contributions are welcome. The layer is plain Rust with no build scripts; the
GUI is PySide6 only. Please keep changes working on core Vulkan 1.0 with no
extensions that floor is the point of the project.
