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

Every setting is one value: the value volt forces, or `default`. There is no
range, no ordering, and nothing to get backwards.

The values each setting offers come from your own hardware, not from a list
built into volt-gui. Present modes, colour depths, colour spaces, transfer
functions and alpha modes come from what the surface reports, the GPU list
from what the driver enumerates, and mip levels and LOD bias run up to the
limits the device gives. A setting whose feature the device lacks holds
nothing but `default`. Only the three **Framerate** settings have a fixed
list, since they are volt's own.

Settings are read once, when the game starts, and never change while it
runs. Press Apply, then start the game again.

volt-gui learns this by keeping a small `vkgears` window running under the
profile you are editing, which also serves as a live preview. Close it and
volt-gui carries on with what it learned last time.

```
volt --probe myprofile -- vkgears
```

A value volt has no name for still appears in the list, still saves to a
profile, and still applies. Where the specification admits only what a query
returned, a value the device did not report is not forced: volt keeps the
game's own value and logs a warning.

Where the specification bounds a value — LOD bias against the device limit,
image count against what the surface allows — volt clamps what it passes
down. That clamp is correctness, not a setting.

### GPU
- **Physical Device**: pick which GPU the game sees, listed by name. The
  layer hides the rest during device enumeration, so it works on every Vulkan
  driver. If nothing matches, the full list comes back and a warning is
  logged.

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
- **Swapchain Images**: how many images the swapchain holds. Fewer images
  lower display latency, more images smooth frame delivery. The list is what
  the surface allows, and the choice is reported back to the game, so a game
  that derives its count from the surface honours it on its own.
- **Color Depth**: the bits per colour channel this surface offers, usually
  8-bit and 10-bit. The layer hides the formats you did not pick, so a game
  that takes the first supported format ends up with yours. If nothing
  matches, the full list comes back and a warning is logged.
- **Color Space**: filtered out of the same list. Everything past
  `srgb_nonlinear` needs the stack around the game to have enabled it, through
  DXVK_HDR, PROTON_ENABLE_HDR or gamescope, so on most setups this card holds
  one entry.
- **Transfer Function**: whether the game is shown `srgb` formats, plain
  `unorm` ones, or float ones, filtered out of the same list again. Getting it
  wrong looks washed out or crushed rather than broken, so set it back to
  default if the image looks off. No preset touches it.
- **Composite Alpha**: how the compositor treats the finished image's alpha.
  Forcing `opaque` skips compositor blending on Wayland. A value the surface
  does not report falls back to the game's own choice with a warning.
- **Clipped Presentation**: whether the driver may skip pixels another window
  covers. On or off.

### Textures
- **Texture Filtering**: retro (sharp pixels), bilinear, trilinear. A sampler
  that matches none of the three exactly counts as the closest one below it.
- **Mipmap Mode**: a hard cut between mip levels, or a blend across them,
  independently of the filter choice.
- **LOD Bias**: shift mipmap selection, sharper or blurrier, across the range
  the device allows.
- **Mip Floor** and **Mip Ceiling**: the lowest and highest mip levels
  samplers may use, called minimum and maximum LOD in Vulkan.

### Rendering
- **Alpha To Coverage**: turn fragment alpha into coverage. Softens cutout
  edges on foliage and fences, and only does anything where the game already
  renders to an MSAA target.

### Framerate
- **Frame Limit**: cap the frame rate at present time, pick a common cap or
  type any value. Deadlines follow a fixed target timeline rather than the
  last present, unless the method is reactive, so scheduler jitter does not
  build up into a drift below the rate you asked for.
- **Frame Limit Method**: early holds the frame back so presents leave on a
  fixed cadence; late lets the present through and waits afterwards, so the
  game starts its next frame later and samples input closer to display time;
  reactive waits where early does but measures from the frame just shown
  instead of a fixed timeline, so a slow frame is never chased with a fast
  one.
- **Frame Pacing**: how the limiter kills time, from cheapest to tightest.
  `sleep` hands the whole wait to the kernel. `sliced` sleeps in short steps
  and rechecks the clock, correcting for the kernel waking late. `precise`
  sleeps most of the interval then busy waits half a millisecond. `spin`
  busy waits the whole interval, the steadiest option and the only one that
  keeps a core awake.

## How It Works

volt registers as an implicit Vulkan layer, gated by `VOLT_ENABLE=1` which the
`volt` launcher sets on the target process only. The layer reads the selected
profile from `~/.config/volt-gui/<profile>.toml` once at startup and rewrites
the Vulkan calls the game makes, and the tabs run in the order the layer acts:
device enumeration for GPU selection, the surface queries and swapchain
creation for the display settings, `vkCreateSampler` for texture settings,
`vkCreateGraphicsPipelines` for the rendering toggles, and `vkQueuePresentKHR`
for the frame limiter. Device creation passes straight through: volt enables
no feature the game left off.

Every setting is hooked on each path that reaches it, not just the obvious
one. A game that queries formats through
`vkGetPhysicalDeviceSurfaceFormats2KHR`, enumerates through
`vkEnumeratePhysicalDeviceGroups`, creates samplers inline through
`vkWriteSamplerDescriptorsEXT` or sets alpha to coverage as dynamic state gets
the same treatment as one that takes the core path.

Settings are frozen for the life of the process. Press Apply, then start the
game again.

volt-gui is the PySide6 front end. It edits the same profile files the layer
reads Apply just saves the profile, no elevated permissions, no scripts.

## Requirements

| Component | Requirement |
|-----------|-------------|
| **Layer** | Vulkan 1.0+ with `VK_KHR_swapchain`, Linux x86_64 (optionally i686 for 32-bit games) |
| **Build** | Rust 1.77+, GNU make 4.3+ |
| **GUI**   | Python 3.10+, PySide6 (a venv is created by the make targets) |
| **Preview** | `vkgears` from mesa-demos, optional: without it the option lists fall back to defaults |

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
(trilinear, blended mips, 10 bit colour, classic vsync) down to **Potato Low
Latency** (bilinear, hard mip cuts, immediate present, 2 image swapchain).
A preset writes every value in the profile, so anything it does not set goes
back to default. That includes the frame limit and the colour space, transfer
function, composite alpha and clipped settings: those depend on your display
and your compositor, so those choices stay yours.

A preset can name something your hardware does not offer. That setting resets
to default and volt-gui says which ones, so the rest of the preset still
lands.

## What volt will never do

volt changes what the game asks Vulkan for; it never draws. Anything that
requires injecting shaders or processing the image is out of scope:

- Sharpening, FSR or any upscaling, frame generation, post processing.
- Forced MSAA or SSAA. Render passes and sample counts belong to the game.
- Overlays and HUDs. Use MangoHud for that.
- Overclocking, fan curves, power limits. That is sysfs territory, not the
  Vulkan API. Use CoreCtrl for that.
- OpenGL. The per driver environment variable maze that OpenGL support
  requires is exactly what this rewrite retired.
- Enable a Vulkan device feature or extension the game did not request. A
  setting whose value is illegal without one is out of scope, whatever it
  would be worth.
- Require a Vulkan extension. Core 1.0 and `VK_KHR_swapchain` are the whole
  surface volt asks for, so behaviour never splits between drivers. volt may
  intercept an extension command the game itself calls, so a setting keeps
  applying where the game moved that state elsewhere; a hook for an extension
  the game never enabled is unreachable and its entry point is never handed
  out.
- Change a setting under a running game. The profile is read once at startup.
- Write into memory the game owns. volt patches the structures it passes on
  and fills the arrays a query asks it to fill; a `pNext` chain the game built
  is read and never written. A setting reaches the game through the lists volt
  hands it, not by reaching into what the game already built.

## Contributing

Contributions are welcome. The layer is plain Rust with no build scripts; the
GUI is PySide6 only. Please keep changes working on core Vulkan 1.0 with no
extensions that floor is the point of the project.
