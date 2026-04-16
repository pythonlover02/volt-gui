# volt-gui

> **My AMD Adrenaline / NVIDIA Settings Linux Alternative**

A graphical interface for configuring GPU environment variables and performance settings for Linux gaming. Initially made for personal use, now open-sourced so others can benefit from it too.

![Badge Language](https://img.shields.io/github/languages/top/pythonlover02/volt-gui)
[![Stars](https://img.shields.io/github/stars/pythonlover02/volt-gui?style=social)](https://github.com/pythonlover02/volt-gui/stargazers)

![](/images/1.png)
![](/images/2.png)
![](/images/3.png)

## Table of Contents

- [What you can do?](#what-you-can-do)
- [Build/Test Requirements](#buildtest-requirements)
- [Installation](#installation)
- [Testing volt-gui](#testing-volt-gui)
- [How to use volt-gui](#how-to-use-volt-gui)
- [How to use the volt script](#how-to-use-the-volt-script)
- [Render Selector explained](#render-selector-explained)
- [Technical References](#technical-references)
- [Contributing](#contributing)

## What you can do?:

### GPU Configuration:
  - Mesa Drivers: Configure Mesa Drivers specific environment variables.
  - NVIDIA Drivers: Configure NVIDIA Proprietary Drivers specific environment variables.
  - Dynamic Render Selection: Select renderers for both OpenGL and Vulkan applications. The program dynamically sets the required environment variables depending on your GPU.
  - Configure various MangoHud options.
  - Configure Gamescope compositing window manager settings.
  - Configure LSFG frame generation settings.
  - Configure Proton and Wine environment variables for Steam gaming, including DXVK, synchronization, upscaling (FSR4, DLSS, XeSS), NVIDIA libraries, Wayland support, and audio configuration.
  - All GPU settings are automatically added to the `volt` script.
### Add custom launch options to the `volt` script:

These will be passed to the executed program. Example:
  ```
  gamemoderun
  ```
### Options:
  - Configure settings specific to the volt-gui program itself.
### Create or Delete Profiles:
  - Each profile has its own set of configurations, which can be applied through the program or system tray.

## Build/Test Requirements:
- Linux operating system
- Python 3.9 or higher
- Pip
- The `python3-venv` package is required on Debian/Debian based distros.
- bash
- make
- coreutils
- shasum (for dependency hash checking)

## Additional Requirements for Building with Nuitka:
- C/C++ Compiler
- patchelf
- ccache (optional, for optimizing compiling times)

## Additional Requirements for Creating AppImage:
- fuse or fuse3
- wget

## Additional Requirements:

- [mangohud](https://github.com/flightlessmango/MangoHud) is required to use the MangoHud tab. Both the native and Flatpak versions are supported.
- [gamescope](https://github.com/ValveSoftware/gamescope) is required to use the Gamescope tab. . Both the native and Flatpak versions are supported.
- [lsfg](https://github.com/PancakeTAS/lsfg-vk) is required to use the LSFG tab. Both the native and Flatpak versions are supported.
- `glxinfo` is required for OpenGL device detection in the Render Selector. Without it, no OpenGL devices will be detected and the selector will be empty, though manual values can still be typed.
- `vulkaninfo` and the `vulkan-mesa-layers` package are required for Vulkan device detection in the Render Selector. Without them, no Vulkan devices will be detected and the selector will be empty, though manual values can still be typed.

## Installation:

### Quick Install:

1. Build the application using one of the available targets:

   Using PyInstaller:

   ```bash
   make pyinstaller
   ```

   Using Nuitka:

   ```bash
   make nuitka
   ```

   _Note: Both use a Python virtual environment to avoid system wide package installation using pip._

2. Optionally create an AppImage:

   ```bash
   make appimage
   ```

3. Install the application system wide:

   ```bash
   make install
   ```

   This will:
   - Copy the executable to `/usr/local/bin/`
   - Create a desktop entry at `/usr/share/applications/volt-gui.desktop`

### Full Release Build:

To build all release artifacts (PyInstaller and Nuitka builds with their AppImages):

```bash
make release
```

Artifacts will be placed in the `releases/` directory.

### Removal:

To uninstall volt-gui:

```bash
make remove
```

This will:
- Remove `volt-gui`, `volt`, and `volt-helper` from `/usr/local/bin/`
- Remove the desktop entry `/usr/share/applications/volt-gui.desktop`

### Clean Build Artifacts:

```bash
make clean
```

## Testing volt-gui:

In the case you want to contribute to the project you can use the provided make target to test the changes you made. This will create a Python virtual environment if one does not already exist, install dependencies, and run the program:

```bash
make test
```

> [!NOTE]
> Use `make clean` to remove the virtual environment and all build artifacts. The `py_env` folder should be deleted if it becomes corrupted, or if it was created with your system python, and you want to use a python version that is inside a `distrobox` box, or vice versa.

## How to use `volt-gui`:

Simply launch volt-gui from your application menu or run `volt-gui` from the terminal.

## How to use the `volt` script:

The `GPU`, `Proton`, and `Launch Options` settings are saved on the `volt` script. Here are some examples of its usage:

### Native Programs:

When using the terminal or a custom desktop entry:

```
volt glxgears
```

When using a Launcher to play your game, you can just add it to the game launch options, like this:

Steam (Native):

```
volt %command%
```

Lutris (Native):

```
volt
```

### Flatpak:

When using the terminal or a custom desktop entry:

```
volt flatpak run net.pcsx2.PCSX2
```

## Render Selector explained:

- `Select OpenGL Renderer` Selects the GPU/Renderer that will be used to render OpenGL programs. Those GPUs/Renderers are obtained through `glxinfo`.
- `Select Vulkan Renderer` Selects the GPU/Renderer that will be used to render Vulkan programs. Those GPUs/Renderers are obtained through `vulkaninfo`, also for this to work on some distros you might need to install some additional dependencies like `vulkan-mesa-layers` on Arch Linux. More info is provided on the Welcome Window that opens once you open volt-gui.

## Technical References:

Based on documentation and references from:

- [MangoHud Github - Readme](https://github.com/flightlessmango/MangoHud/blob/master/README.md)
- [Gamescope Github](https://github.com/ValveSoftware/gamescope)
- [lsfg-vk Github - Readme](https://github.com/PancakeTAS/lsfg-vk)
- [lsfg-vk Github - Wiki](https://github.com/PancakeTAS/lsfg-vk/wiki)
- [Mesa Documentation - Environment Variables](https://docs.mesa3d.org/envvars.html#environment-variables)
- [FreeDesktop - Dri Configuration Options](https://dri.freedesktop.org/wiki/ConfigurationOptions/)
- [NVIDIA Drivers - Documentation](https://download.nvidia.com/XFree86/Linux-x86_64/)
- [Proton-CachyOS Github](https://github.com/CachyOS/proton-cachyos)
- Additionally, sometimes i had to read code from Open Source projects to check how some options work.

## Contributing:

Contributions are welcome. Please ensure compatibility with supported Python versions and follow the existing code structure.
Read: [Build/Test Requirements](#buildtest-requirements), [Installation](#installation), and [Testing volt-gui](#testing-volt-gui) before contributing.
