> [!NOTE]
> Bug reports and pull requests are welcome, but please understand that development happens in my free time and progress may be slow at times. The project is still maintained even if the last commit was made a while ago.

# volt-gui

> **My AMD Adrenaline / NVIDIA Settings Linux Alternative**

volt-gui is a graphical control panel for Vulkan games on Linux. Settings are
applied by **volt**, a Vulkan implicit layer written in Rust, so they work on
every Vulkan driver: RADV, ANV, NVK, AMDVLK, the NVIDIA proprietary driver.

The floor is **Vulkan 1.0**: every core setting works there. Some settings use
optional extensions on top of that floor. When the driver has the extension it
is used; when it does not, the setting is skipped and the rest keeps working.
`VOLT_LOG=info` shows what was enabled.

![](/images/1.png)
![](/images/2.png)
![](/images/3.png)

## Table of Contents

- [What you can do?](#what-you-can-do)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Flatpak](#flatpak)
- [Profiles & Presets](#profiles--presets)
- [What volt will never do](#what-volt-will-never-do)
- [Contributing](#contributing)

## What you can do?

Every setting defaults to **default**, meaning the layer does not touch that
value and the game keeps its own choice. A profile with everything on default does nothing.

### Display
- **VSync / Present Mode**: fifo, fifo_relaxed, mailbox, immediate. Unsupported
  modes fall back to the game's own choice.
- **Swapchain Images**: request a specific image count, or clamp the game's
  request with independent minimum and maximum bounds. Fewer images lower
  display latency.
- **Color Depth**: prefer 10-bit, HDR10 or scRGB surface formats. Games that
  pick the first supported format follow the preference; hardcoded choices
  are respected. HDR values need driver and compositor support
  (`VK_EXT_swapchain_colorspace`, `VK_EXT_hdr_metadata`).
- On drivers with `VK_EXT_swapchain_maintenance1`, changing the present mode
  in a saved profile takes effect in a running game without swapchain
  recreation.

### Framerate
- **Frame Limit**: cap the frame rate at present time, pick a common cap or
  type any value.
- **Frame Pacing**: sleep for CPU friendly limiting, or precise busy waiting
  for tighter frametimes.
- **AMD Anti-Lag**: driver side input latency reduction
  (`VK_AMD_anti_lag`).
- **NVIDIA Low Latency**: driver side input latency reduction with an
  optional boost mode (`VK_NV_low_latency2`).

### Textures
- **Texture Filtering**: retro (sharp pixels), bilinear, trilinear.
- **Anisotropic Filtering**: off to 16x, clamped to what your GPU reports.
- **LOD Bias** with independent minimum and maximum clamps: force a bias, or
  only bound what the game asks for.
- **Minimum / Maximum LOD**: bound the mip levels samplers may use. On
  drivers with `VK_EXT_image_view_min_lod` the minimum also applies at the
  image view level.

### Rendering
- **Wireframe**: render polygons as lines (needs the fillModeNonSolid device
  feature).
- **Sample Shading**: shade at sample rate inside MSAA targets to reduce
  shimmer (needs the sampleRateShading device feature).

### GPU
- **Physical Device**: pick which GPU the game sees, by index. The layer
  filters device enumeration itself, so it works on every Vulkan driver.

## How It Works

volt registers as an implicit Vulkan layer, gated by `VOLT_ENABLE=1` which the
`volt` launcher sets on the target process only. The layer reads the selected
profile from `~/.config/volt-gui/<profile>.toml` and rewrites the Vulkan calls
the game makes: `vkEnumeratePhysicalDevices` for GPU selection,
`vkCreateSampler` for texture settings, `vkCreateSwapchainKHR` for present
mode and image count, `vkGetPhysicalDeviceSurfaceFormatsKHR` for the 10-bit
preference, `vkQueuePresentKHR` for the frame limiter, and
`vkCreateGraphicsPipelines` for the advanced toggles. Optional device
features are enabled at device creation only when the hardware supports them.

The layer watches the config directory with inotify: press Apply in volt-gui
while a game is running and the new values take effect live.

volt-gui is the PySide6 front end. It edits the same profile files the layer
reads Apply just saves the profile, no elevated permissions, no scripts.

## Requirements

| Component | Requirement |
|-----------|-------------|
| **Layer** | Vulkan 1.0+ with `VK_KHR_swapchain`, Linux x86_64 (optionally i686 for 32-bit games) |
| **Build** | Rust 1.77+, GNU make 4.3+ |
| **GUI**   | Python 3.9+, PySide6 (a venv is created by the make targets) |

## Installation

| Command | What it does |
|---------|--------------|
| `make` | Build the 64-bit layer and the `volt` launcher |
| `make 32` | Build the 32-bit layer for 32-bit games |
| `make gui-pyinstaller` | Build the GUI binary with PyInstaller into `bin/` |
| `make gui-nuitka` | Build the GUI binary with Nuitka into `bin/` |
| `make flatpak` | Build the Flatpak runtime extension bundles (needs `make` + `make 32`) |
| `make release` | Portable container builds plus the full release matrix in `releases/` |
| `sudo make install` | Install launcher, GUI, layer libraries and manifest. Never builds. |
| `sudo make flatpak-install` | Install the built extension bundles for the invoking user |
| `sudo make uninstall` | Remove everything, including the user Flatpak extension and `~/.config/volt-gui` |
| `make clean` | Remove all build artifacts |

```
git clone https://github.com/pythonlover02/volt-gui.git
cd volt-gui
make
make 32                # optional, for 32-bit games
make gui-pyinstaller   # or make gui-nuitka
sudo make install
```

`make release` produces: `volt-gui-pyinstaller-x86_64.AppImage`,
`volt-gui-nuitka-x86_64.AppImage`, and matching `.tar.gz` archives that carry
the binaries, the Makefile, the layer sources, and the Flatpak extension
bundles.

## Usage

Prepend the launcher to your game command:

```
volt -- %command%                # Steam, default profile
volt myprofile -- %command%      # Steam, named profile
volt -- ./game                   # terminal
volt -- flatpak run com.example.Game
```

The launch command for the selected profile is always shown next to the Apply
button in volt-gui, ready to copy.

## Flatpak

Flatpak games run sandboxed, so the layer ships as a **Flatpak runtime
extension** for `org.freedesktop.Platform` 23.08, 24.08 and 25.08. Build with
`make flatpak`, install with `sudo make flatpak-install` (or grab the bundles
from the release archives). The `volt` launcher detects `flatpak run` commands
and routes activation through the in-sandbox wrapper automatically.

There is no Flatpak build of volt-gui itself, only the layer extension.

## Profiles & Presets

Profiles are TOML files in `~/.config/volt-gui/`, one per configuration.
Create and switch them from the GUI or the system tray; select one at launch
with `volt <name> -- ...`.

Presets populate the active profile with curated values, from **Quality**
(trilinear, 16x anisotropy, full sample shading) down to **Potato Low
Latency** (bilinear, anisotropy off, immediate present, 2 image swapchain).
Presets never touch the frame limit caps are display specific, so that
choice stays yours.

## What volt will never do

volt changes what the game asks Vulkan for; it never draws. Anything that
requires injecting shaders or processing the image is out of scope:

- Sharpening, FSR or any upscaling, frame generation, post processing.
- Forced MSAA or SSAA. Render passes belong to the game. Sample Shading is
  as far as this can go without breaking games.
- Overlays and HUDs. Use MangoHud for that.
- Overclocking, fan curves, power limits. That is sysfs territory, not the
  Vulkan API. Use CoreCtrl for that.
- OpenGL. The per driver environment variable maze that OpenGL support
  requires is exactly what this rewrite retired.

## Contributing

Contributions are welcome. The layer is plain Rust with no build scripts; the
GUI is PySide6 only. Please keep changes working on Vulkan 1.0 that floor is
the point of the project.
