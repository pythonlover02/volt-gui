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

Every setting carries three values:

- **Force**: the layer replaces whatever the game asked for.
- **Minimum** and **Maximum**: the layer leaves the game's own value alone
  unless it falls outside the range, and pulls it back to the nearest bound
  when it does.

Force wins over the bounds when both are set. Bounds are how you rule out the
extremes you do not want while leaving the game room to make its own choice.
A minimum above its own maximum is a mistake: both are ignored and a warning
is logged.

A setting carries bounds when the game supplies a value to bound. That is
every setting but the three under **Framerate**: a game never asks Vulkan for
a frame rate, so there is nothing to bound. Those three configure the layer's
own wait instead, and volt-gui groups them into one **Frame Limiter** card.

### Display
- **VSync / Present Mode**: fifo, fifo_relaxed, mailbox, immediate. The bounds
  run along that same order, from most latency to least, so a maximum of
  mailbox never lets a game tear and a minimum of mailbox never lets it sit
  on classic vsync. Unsupported modes fall back to the game's own choice.
- **Swapchain Images**: how many images the swapchain holds. Fewer images
  lower display latency, more images smooth frame delivery.
- **Color Depth**: which surface formats the game is allowed to see, 8-bit or
  10-bit. The layer filters the format list, so games that pick the first
  supported format follow the choice. A selection that matches no format is
  ignored and logged, so the game always sees at least the full list.

### Framerate
- **Frame Limit**, **Frame Limit Method** and **Frame Pacing**: cap the frame
  rate at present time, and choose when and how the limiter waits. Deadlines
  follow a fixed target timeline rather than the last present, so scheduler
  jitter does not accumulate into a drift below the requested rate.
- **Frame Limit Method**: early holds the frame back so presents leave on a
  fixed cadence; late lets the present through and waits afterwards, so the
  game starts its next frame later and samples input closer to display time.
- **Frame Pacing**: sleep for CPU friendly limiting, or precise busy waiting
  for tighter frametimes.

### Textures
- **Texture Filtering**: retro (sharp pixels), bilinear, trilinear. Samplers
  that match none of the three exactly are ranked down to the closest one
  below them before the bounds apply.
- **Mipmap Mode**: a hard cut between mip levels, or a blend across them,
  independently of the filter choice.
- **Anisotropic Filtering**: off to 16x. off counts as the lowest value, so a
  minimum of 4x raises a game that asked for less and leaves a game that
  asked for more alone. Clamped to what your GPU reports.
- **LOD Bias**: shift mipmap selection, sharper or blurrier.
- **Mip Floor** and **Mip Ceiling**: bound the mip levels samplers may use,
  the minimum and maximum LOD in Vulkan terms.

### Rendering
- **Sample Shading**: shade at sample rate inside MSAA targets to reduce
  shimmer (needs the sampleRateShading device feature).
- **Alpha To Coverage**: turn fragment alpha into coverage. Softens cutout
  edges on foliage and fences, and only does anything where the game already
  renders to an MSAA target.

### GPU
- **Physical Device**: pick which GPU the game sees, by index in the order
  the driver reports them. The layer filters device enumeration itself, so it
  works on every Vulkan driver. The bounds keep a range of indices instead of
  a single one. A selection that matches no device is ignored and logged, so
  the game always sees at least the full list.

## How It Works

volt registers as an implicit Vulkan layer, gated by `VOLT_ENABLE=1` which the
`volt` launcher sets on the target process only. The layer reads the selected
profile from `~/.config/volt-gui/<profile>.toml` and rewrites the Vulkan calls
the game makes: `vkEnumeratePhysicalDevices` for GPU selection,
`vkCreateSampler` for texture settings, `vkCreateSwapchainKHR` for present
mode and image count, `vkGetPhysicalDeviceSurfaceFormatsKHR` for the 10-bit
filter, `vkQueuePresentKHR` for the frame limiter, and
`vkCreateGraphicsPipelines` for the rendering toggles. Core device features
are enabled at device creation only when the hardware reports them.

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
A preset writes every value in the profile, so anything a preset does not
name goes back to default.

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
- Any Vulkan extension. Core 1.0 is the whole surface the layer touches, so
  behaviour never splits between drivers.

## Contributing

Contributions are welcome. The layer is plain Rust with no build scripts; the
GUI is PySide6 only. Please keep changes working on core Vulkan 1.0 with no
extensions that floor is the point of the project.
