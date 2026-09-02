> [!NOTE]
> Bug reports and pull requests are welcome, but please understand that development happens in my free time and progress may be slow at times. The project is still maintained even if the last commit was made a while ago.

# volt-gui

Control panel for Vulkan games on Linux. Settings are applied by **volt**, an implicit Vulkan layer written in Rust, so they work on every driver: RADV, ANV, NVK, AMDVLK, NVIDIA proprietary.

Vulkan 1.0 only. The layer requests nothing beyond `VK_KHR_swapchain`, so behaviour never splits between drivers.

![](/images/1.png)
![](/images/2.png)
![](/images/3.png)

## Quick Start

```
git clone https://github.com/pythonlover02/volt-gui.git
cd volt-gui
make
make install-user

volt-gui          # set what you want, press Apply
volt -- ./game
```

That covers native, Steam, Wine and Proton. For a system-wide install use `sudo make install` instead. Pick one, never both.

Steam launch options:

```
volt -- %command%
```

Flatpak games need some extra work, see [Flatpak](#flatpak).

## Table of Contents

- [Settings](#settings)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Install paths](#install-paths)
- [Uninstalling](#uninstalling)
- [Immutable Systems](#immutable-systems)
- [FEX-Emu / Box64](#fex-emu--box64)
- [Building Releases](#building-releases)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Files](#files)
- [Flatpak](#flatpak)
- [Profiles, Presets & Options](#profiles-presets--options)
- [What volt will never do](#what-volt-will-never-do)
- [Contributing](#contributing)

## Settings

21 settings across 5 tabs. Every one defaults to `default`, which leaves the game's own choice alone. A profile with everything on default does nothing.

Each setting is a single value. No ranges, no ordering, nothing to get backwards.

| Tab | Section | Count | Covers |
|-----|---------|------:|--------|
| GPU | `[gpu]` | 1 | which device the game sees |
| Display | `[display]` | 4 | present mode, image count, compositing, clipping |
| Textures | `[textures]` | 7 | filtering, mips, anisotropy, LOD |
| Rendering | `[rendering]` | 4 | sample shading, alpha to coverage, alpha to one, depth clamp |
| Framerate | `[framerate]` | 5 | limit, offset, cadence, method, pacing |

Most option lists are read from your hardware, not from a table in volt-gui. Present modes, image counts, alpha modes, GPU names, anisotropy, mip levels and LOD bias all come from a probe of your own device. A setting your hardware lacks holds only `default`.

Fixed lists exist where there is nothing to read. `nearest` and `linear` are core Vulkan with no query behind them. The Framerate settings have nothing to read either, since a game never tells Vulkan what frame rate it wants.

Settings are read once at game start. Press Apply, then restart the game.

### The probe

volt-gui runs `volt-probe` under the profile you are editing. It opens a 1px window that is never mapped, creates a surface, swapchain and sampler, records what the device reported, and exits. Nothing appears on screen.

```
volt --probe myprofile -- volt-probe
```

It uses X11, which every desktop has through XWayland. Games may open Wayland or gamescope surfaces instead, and the profile is written before volt knows which. This only affects present modes, image counts and alpha modes, and the lists mostly agree. Where they don't, the layer handles it at runtime: image count is clamped against the real surface, and a rejected present or alpha mode leaves the game's value with a warning.

### GPU

**Physical Device** pick which GPU the game sees. volt hides the rest during enumeration. If nothing matches, the full list comes back with a warning.

This is the only setting volt cannot force. Nothing in Vulkan names the device a swapchain runs on, so a game that ignores enumeration order keeps what it picked.

### Display

**VSync / Present Mode** `immediate` off, `mailbox` low-latency vsync, `fifo` classic vsync, `fifo_relaxed` tears below refresh. Modes you ruled out are hidden from the game, so its own vsync menu can't offer them.

**Swapchain Images** frames in flight. More lets the game run ahead of the GPU, smoothing delivery at the cost of input lag. Fewer holds it closer to the display. This is the anti-lag setting.

**Composite Alpha** how the compositor treats the finished image's alpha. `opaque` skips compositor blending on Wayland.

**Clipped Presentation** whether the driver may skip pixels another window covers.

### Textures

**Magnification Filter** sampling where a texture is drawn larger than its own size, so anything close to the camera. `nearest` is sharp pixels, `linear` smooths. The one filter a screenshot shows you.

**Minification Filter** the same where it's drawn smaller, which is most of the screen. `nearest` shimmers as the camera moves, `linear` settles. Leave on `linear` unless you want the crawl.

**Mipmap Mode** hard cut between mip levels, or a blend.

Three sampler fields, three settings, so every combination is reachable. Retro is `nearest`/`nearest`/`nearest`. Bilinear is `linear`/`linear`/`nearest`. Trilinear is `linear`/`linear`/`linear`. Sharp pixel art without distant shimmer is `nearest`/`linear`/`linear`, which no named mode ever offered.

**Anisotropic Filtering** off up to whatever your GPU reports. volt never enables `samplerAnisotropy`; where the game left it off the setting is ignored and logged. Nearly every game enables it.

**LOD Bias** shift mipmap selection sharper or blurrier.

**Mip Floor / Mip Ceiling** lowest and highest mip levels samplers may use. A ceiling below the floor is swapped rather than dropped.

### Rendering

**Sample Shading** shade at sample rate inside MSAA targets to cut shimmer. volt never enables `sampleRateShading`; most deferred renderers never ask for it.

**Alpha To Coverage** turns fragment alpha into coverage. Softens cutout edges on foliage and fences. Only does something where the game already renders to MSAA.

**Alpha To One** force fragment alpha to 1 after the shader. volt never enables the feature.

**Depth Clamp** keep fragments outside the near and far planes and pin their depth instead of discarding them. Stops weapon models being sliced open against walls. Same toggle covers the far plane, where geometry flattens onto it instead of vanishing, so test per game. Most games never enable `depthClamp` and volt won't enable it for them, so this usually does nothing and says so in the log.

### Framerate

Most limiters give you a cap and a method. volt gives you five settings. Nothing else on Linux covers all five.

**Frame Limit** cap at present time. Deadlines follow a fixed timeline rather than the last present, so scheduler jitter doesn't drift you below the rate you asked for. A frame that misses its deadline by more than one interval is released at once and the timeline reanchors from there, instead of waiting out the rest of the interval it already missed. Kept per swapchain.

**Frame Limit Offset** shift the cap by -10 to 10 in steps of two. VRR displays want the cap just under refresh: pick 144, set -6, land on 138. volt never shifts a cap on its own since most displays aren't VRR.

**Frame Limit Cadence** which rate the limiter paces at.

- `fixed` is your cap and nothing else.
- `smooth` paces at the slowest of the last few frames, so fast frames wait for slow ones and the cadence comes out even at whatever the machine holds.
- `dynamic` reads the same and rounds down to a quarter step of the cap. A 60 cap steps 60, 48, 40, 34, 30. A 240 cap steps 240, 192, 160, 137, 120.

Both take the idea from consoles: pick a rate the machine can hold and stay on it. Neither reads the average, because a limiter can only make frames later and a frame slower than the average could never be paced up to it. Both climb back on their own and neither exceeds your cap.

You're trading frames for evenness. `fixed` does nothing once the machine falls under the cap, so you get whatever it produced, one frame long and the next short. A rate sitting on one of `dynamic`'s steps can bounce between two, which is what rounding costs; `smooth` is the same reading without it. Use `fixed` if the machine holds the cap, or if you want every frame you can get.

**Frame Limit Method** `early` holds the frame back so presents leave on a fixed cadence. `late` lets the present through and waits after, so the game samples input closer to display time. This is the equivalent of Reflex and Anti-Lag. `reactive` waits where early does but measures from the frame just shown, so a slow frame is never chased with a fast one.

**Frame Pacing** how the limiter kills time. `sleep` hands the wait to the kernel. `sliced` sleeps in short steps and rechecks. `precise` sleeps most of it then busy waits half a millisecond. `spin` busy waits throughout, steadiest and the only one that keeps a core awake.

## How It Works

volt registers as an implicit layer (`VK_LAYER_VOLT_settings`). The manifest declares `enable_environment = VOLT_ENABLE`, so the loader always finds it but only activates it when the `volt` launcher sets that variable on the child process.

The layer reads `~/.config/volt-gui/<profile>.toml` once at startup and rewrites the calls the game makes:

| Tab | Where the layer acts |
|-----|----------------------|
| GPU | `vkEnumeratePhysicalDevices`, `vkEnumeratePhysicalDeviceGroups(KHR)` |
| Display | `vkGetPhysicalDeviceSurfacePresentModesKHR`, `...PresentModes2EXT`, `...SurfaceCapabilities(2)KHR`, `vkCreateSwapchainKHR`, `vkCreateSharedSwapchainsKHR` |
| Textures | `vkCreateSampler`, `vkWriteSamplerDescriptorsEXT` |
| Rendering | `vkCreateGraphicsPipelines`, `vkCmdSetAlphaToCoverageEnableEXT`, `vkCmdSetAlphaToOneEnableEXT`, `vkCmdSetDepthClampEnableEXT` |
| Framerate | `vkQueuePresentKHR` |

Device creation is read, never modified. volt learns which features the game enabled so feature-gated settings apply only where the game asked, and enables nothing itself.

Every setting is hooked on each path that reaches it. `2`/`EXT` query variants, device groups, shared swapchains, inline sampler writes and dynamic alpha-to-coverage get the same treatment as the core calls. Present mode lists carried in a `pNext` chain are filtered in place too.

An entry point for an extension the game never enabled is unreachable, and the layer only returns a hook when the call resolves further down the chain.

volt-gui is the PySide6 front end. Apply just saves the profile. No elevated permissions, no scripts.

## Requirements

| Component | Requirement |
|-----------|-------------|
| Layer | Vulkan 1.0+ with `VK_KHR_swapchain`, Linux x86_64 (plus i686 for 32-bit games) |
| Build | Rust 1.85.1+ with rustup, GNU make 4.3+ |
| 32-bit layer | `gcc-multilib`, `libc6-dev-i386` |
| GUI | Python 3.10+, PySide6 |
| Flatpak bundles | `flatpak`, `ostree` |
| Container release | `podman` or `docker` |
| Probe build | `libxcb` headers |

No native aarch64 build. See [FEX-Emu / Box64](#fex-emu--box64).

## Installation

### Arch Linux (AUR)

There's an unofficial [volt-gui](https://aur.archlinux.org/packages/volt-gui) package. I don't maintain it, but the packager has been good to deal with, so I won't steer you away.

Read the `PKGBUILD` first. Not because of the packager, but because the AUR lets anyone submit anything.

### From source

Every build target is a file, so make only rebuilds what changed. Everything lands under `build/`.

| Command | What it does |
|---------|--------------|
| `make` | both layers, launcher, GUI, desktop entry |
| `make layer-64` | 64-bit layer, launcher, probe |
| `make layer-32` | 32-bit layer |
| `make gui` | `build/bin/volt-gui` |
| `make flatpak` | `build/bundles/*.flatpak` |
| `make dist` | sources with `build/` populated |
| `make release` | archive in `releases/`, host toolchain |
| `make release-container` | same, inside the build image |
| `sudo make install` | system-wide |
| `make install-user` | into `~/.local`, no root |
| `sudo make flatpak-install` | extension bundles |
| `make flatpak-install-user` | same, `--user` |
| `make setup-user` | `install-user` + `flatpak-install-user` |
| `sudo make uninstall` | everything |
| `make uninstall-user` | the rootless install |
| `make clean` | `rm -rf build releases` |
| `make help` | this list |

A bare `make` builds both architectures. The 32-bit layer isn't optional, any Steam library has 32-bit titles. `make layer-32` exists for working on that one piece and adds the Rust target if missing.

Flatpak bundles are the opposite: optional, built only by `make flatpak`, and neither install target touches them.

Actions artifacts are `make dist` trees. Unpack one and `sudo make install` installs without compiling.

Building with `sudo` is refused, so you never end up with a root-owned `build/`. Install targets only copy what's already built and name what's missing if you skipped a step. volt-gui also refuses to start under `sudo`.

Packagers can stage without root:

```
make
make install DESTDIR="$PWD/pkg" PREFIX=/usr
```

With `DESTDIR` set the install skips `ldconfig`, the desktop database, the icon cache, and the competing-install check.

## Install paths

| File | System | User |
|------|--------|------|
| Launcher | `/usr/bin/volt` | `~/.local/bin/volt` |
| Probe | `/usr/bin/volt-probe` | `~/.local/bin/volt-probe` |
| GUI | `/usr/bin/volt-gui` | `~/.local/bin/volt-gui` |
| Library 64 | `/usr/lib/x86_64-linux-gnu/libvolt.so` | `~/.local/lib/volt/x86_64-linux-gnu/libvolt.so` |
| Library 32 | `/usr/lib/i386-linux-gnu/libvolt.so` | `~/.local/lib/volt/i386-linux-gnu/libvolt.so` |
| Manifest | `/usr/share/vulkan/implicit_layer.d/VkLayer_volt.json` | `~/.local/share/vulkan/implicit_layer.d/VkLayer_volt.json` |
| Desktop entry | `/usr/share/applications/volt-gui.desktop` | `~/.local/share/applications/volt-gui.desktop` |
| Icon | `/usr/share/icons/hicolor/256x256/apps/volt-gui.png` | `~/.local/share/icons/hicolor/256x256/apps/volt-gui.png` |
| Install stamps | `/var/lib/volt` | `~/.local/share/volt` |

The library directory follows what your distribution uses. Because the manifest lands in the implicit layer directory and the libraries in standard paths, 32-bit games find the 32-bit layer and 64-bit games the 64-bit one with no `VK_LAYER_PATH` mapping.

> [!WARNING]
> Don't change `PREFIX` away from `/usr` or `/usr/local`. The loader only scans a fixed set of manifest directories. Installing to `/opt/volt` puts the manifest where nothing reads it and the launcher off `$PATH`.

## Uninstalling

```
sudo make uninstall     # system
make uninstall-user     # ~/.local
```

Both remove the binaries, libraries, manifest, desktop entry, icon, install stamps, the user-scope Flatpak extension and `~/.config/volt-gui`. Run directly as root there's no `SUDO_USER` to work from, so the user-scope steps are skipped.

Neither touches a 1.x install. 1.x lived in `/usr/local/bin`, 2.0 lives in `/usr/bin`. Remove 1.x first:

```
sudo rm -f /usr/local/bin/volt /usr/local/bin/volt-gui /usr/local/bin/volt-helper
sudo rm -f /usr/share/applications/volt-gui.desktop
sudo update-desktop-database /usr/share/applications
```

Do it before installing 2.0. `/usr/local/bin` comes first on most distributions, so a leftover 1.x `volt` shadows the new launcher, never sets `VOLT_ENABLE`, and every setting silently does nothing. If 2.0 looks dead, run `which volt`.

`make clean` removes `build/` and `releases/` plus stray directories from older layouts.

## Immutable Systems

On SteamOS, Bazzite, Silverblue and anything with a read-only `/usr`, skip the system install:

```
make
make install-user
```

Plus the Flatpak extension if you want it:

```
make flatpak
make flatpak-install-user
```

`~/.local/bin` has to be on your `PATH`, because volt-gui runs `volt` and `volt-probe` to read your hardware.

Pick one install, not both. The loader scans system and user directories alike, so two manifests naming the same layer leave it undefined which is used, or whether the layer is inserted twice. Both install targets refuse to run while the other owns the layer.

The GUI is one self-contained binary, so unpacking a release and double-clicking `build/bin/volt-gui` opens the editor with nothing installed. Enough to write and copy profiles, not enough to use them: with no layer on disk the probe can't run, so every device-backed card holds only `default`.

The Flatpak extension never covers native Steam games, which run under the Steam Linux Runtime. The native install does reach them: Steam expands `%command%` on the host, and the runtime container bind-mounts your home directory and imports host implicit layers.

## FEX-Emu / Box64

On aarch64, x86_64 games run through FEX-Emu or Box64. There's no native aarch64 build because every shipping Vulkan game on Linux has an x86_64 build.

Translation layers run the game inside their own root: a tree of x86_64 binaries separate from the host `/usr`. The layer goes into that tree.

**If your kernel routes x86_64 ELFs through `binfmt_misc`,** an x86_64 Flatpak runtime behaves normally:

```
flatpak install org.freedesktop.Platform//24.08 --arch=x86_64
make flatpak
make flatpak-install-user
```

**Otherwise, install into the translation root:**

```
make
make install DESTDIR=/path/to/translation-root
```

Needs no root and touches nothing on the host. Clear it with `make DESTDIR=/path/to/translation-root uninstall`.

## Building Releases

Both targets produce `releases/volt-gui-<version>.tar.gz`, a ready-to-install tree. Unpack and `sudo make install` without compiling.

`make release` uses your toolchain and inherits your glibc floor.

`make release-container` builds inside `rust:1.85.1-bookworm` (glibc 2.36, Python 3.11), so the floor is fixed. Builds into `build/container/` and runs as your uid.

```
make release-container CONTAINER_BASE=rust:1.85.1-bullseye
make release-container CONTAINER=docker
```

Bullseye drops the floor to glibc 2.31 but ships Python 3.9, below what the GUI needs. Use it for `make layer-64 layer-32` only.

## Usage

```
volt [--probe] [PROFILE] -- COMMAND [ARGS...]
volt -- COMMAND [ARGS...]      # default profile
volt --help
```

Everything before `--` is launcher options, everything after is the command:

```
volt -- %command%                # Steam
volt myprofile -- %command%      # named profile
volt -- ./game
volt -- flatpak run com.example.Game
```

The launch command for the selected profile is shown next to the Apply button, ready to copy.

Profile names must be non-empty printable ASCII with no path separator and no `..`. Anything else falls back to default with a warning. The launcher writes a commented profile on first use.

To see what applied:

```
VOLT_LOG=info volt -- ./game
```

Every line is prefixed `[volt]` and goes to stderr.

At `info` every setting gets a line, naming what the game asked for and what
volt wrote in its place.

```
[volt] gpu device: asked 2
[volt] present_mode: asked fifo, forced mailbox
[volt] image_count: asked 3
[volt] mag_filter: asked linear, forced nearest
[volt] anisotropy: asked off, forced 16
[volt] depth_clamp: asked off; the application did not enable depthClamp
[volt] frame_limit: forced 60
[volt] frame_pacing: the profile did not set it
```

No forced value means volt left that setting alone, either because it is
`default` or because the game already asked for what you picked. The forced
value is the one volt wrote, so a setting the device clamped shows what
landed rather than what the profile says.

The five Framerate settings have no asked value, since a game never tells
Vulkan what frame rate it wants. They report what volt forced, or say the
profile did not set them.

The GPU line reports the device id as `forced N` when the profile sets a gpu, and `asked N` when it does not.

Each setting prints once per device, so 21 lines at most however many
samplers, pipelines or swapchains the game creates.

## Environment Variables

| Variable | Purpose | Values | Default |
|----------|---------|--------|---------|
| `VOLT_CONFIG_NAME` | which profile to load | any profile name | `default` |
| `VOLT_LOG` | log verbosity, to stderr | `off`, `error`, `warn`, `info` | `warn` |
| `VOLT_PROBE` | write `probe.toml` on first swapchain | any non-empty value | unset |
| `VOLT_ENABLE` | activates the layer | `1` | unset |
| `VOLT_DISABLE` | the loader's off switch | `1` | unset |

`HOME` decides where profiles live and falls back to `/tmp` with a warning. `LD_LIBRARY_PATH` is extended by the launcher with both layer directories, preserving what was there.

There's no environment override for the settings themselves. A profile file is the only way to set them, which keeps the panel and the layer describing the same thing.

## Files

| Path | What it is |
|------|------------|
| `~/.config/volt-gui/default.toml` | default profile |
| `~/.config/volt-gui/<name>.toml` | named profiles |
| `~/.config/volt-gui/probe.toml` | what the last probe read |
| `~/.config/volt-gui/options.toml` | volt-gui preferences and last active profile |

Profiles are plain TOML, one section per tab and one string per setting, so you can edit them by hand or keep them in a dotfiles repo. `probe.toml` is written by the layer and watched by the GUI, so a freshly probed device fills the panel without a restart. Deleting it costs a re-probe.

## Flatpak

Flatpak games can't see host paths, so the layer ships as a runtime extension for `org.freedesktop.Platform` 23.08, 24.08 and 25.08.

Separate and optional. Neither `make` nor the install targets produce or touch the bundles:

```
make flatpak
make flatpak-install-user     # or: sudo make flatpak-install
```

One bundle per runtime. Install the one matching yours, run `flatpak list` if unsure. Multiple versions can coexist. Every bundle carries the 32-bit library too.

```
flatpak install --user build/bundles/org.freedesktop.Platform.VulkanLayer.volt-24.08.flatpak
flatpak uninstall --user org.freedesktop.Platform.VulkanLayer.volt
```

The launcher detects `flatpak run` and routes through the in-sandbox wrapper:

```
volt -- flatpak run com.example.Game
volt -- flatpak run --branch=stable com.example.Game
volt myprofile -- flatpak run com.example.Game
```

There's no Flatpak build of volt-gui itself, only the layer.

### Without the launcher

Call the wrapper yourself, useful where only the extension is installed:

```
flatpak run --command=/usr/lib/extensions/vulkan/volt/bin/volt-flatpak com.example.Game
VOLT_CONFIG_NAME=myprofile flatpak run --command=/usr/lib/extensions/vulkan/volt/bin/volt-flatpak com.example.Game
```

Same line works as a Steam launch option for a Flatpak game:

```
/usr/lib/extensions/vulkan/volt/bin/volt-flatpak %command%
```

Your home directory is mounted into the sandbox, so profiles apply unchanged.

## Profiles, Presets & Options

**Profiles** are TOML files in `~/.config/volt-gui/`, one per configuration. Create and switch from the GUI, the tray, or `volt <name> -- ...`. Switching saves the one you were on and restarts the probe.

**Presets** fill the active profile with curated values, from Quality (trilinear, 16x anisotropy, blended mips, classic vsync) down to Potato Low Latency (bilinear, anisotropy off, hard mip cuts, immediate present, 2 images). A preset writes every value, so anything it doesn't set goes back to default. Frame limit, composite alpha and clipped presentation are left alone since those depend on your display. A preset naming something your hardware lacks resets that one to default and says which.

**Options** holds volt-gui's own preferences, not anything the layer reads: theme, transparency, scale, start maximised or in tray, tray icon, welcome window. They save as you change them and take effect on restart. One instance at a time.

## What volt will never do

volt changes what the game asks Vulkan for. It never draws. Anything needing shader injection or image processing is out of scope.

- **Sharpening, FSR, upscaling, frame generation, post processing.**
- **Forced MSAA or SSAA.** Adding samples means recreating every render target, adding resolves and rewriting pipelines and shaders. That's the game's frame graph, not a value passing by.
- **Colour depth, colour space, transfer function.** Every 10-bit surface format is UNORM, so forcing 8 to 10 drops hardware sRGB encoding and washes the picture out, and a game that hardcoded its format ends up with image views that don't match. None of it makes a game render wider content anyway. A game that wants HDR asks for it through DXVK_HDR, PROTON_ENABLE_HDR or gamescope.
- **Cubic filtering.** Needs `VK_EXT_filter_cubic`, admitted per format, while a sampler names no format at all. There's no moment where volt can tell whether it'd be legal.
- **Overlays and HUDs.** Use MangoHud.
- **Overclocking, fan curves, power limits.** That's sysfs, not Vulkan. Use LACT, or CoreCtrl if you want CPU controls too.
- **OpenGL.** The per-driver environment variable maze is exactly what this rewrite retired.
- **Enable a feature or extension the game didn't request.**
- **Require a Vulkan extension.** Core 1.0 and `VK_KHR_swapchain` is the whole surface.
- **Resolution scaling.** Needs `VK_KHR_surface_maintenance1` and `VK_KHR_swapchain_maintenance1`, and volt enables neither. Use gamescope.
- **Frame pacing tighter than the limiter gives.** Deadlines measured against the display need `VK_KHR_present_wait` or `VK_EXT_present_timing`. `late` is as close as core Vulkan reaches.
- **Change a setting under a running game.**
- **Write into memory the game owns.** volt patches the structures it passes on and fills the arrays a query asks it to fill. A `pNext` chain the game built is read, never written.

## Contributing

Contributions welcome. The layer is plain Rust with no build scripts, the GUI is PySide6 only. Keep changes working on core Vulkan 1.0 with no extensions that floor is the point of the project.
