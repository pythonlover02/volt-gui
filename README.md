# volt-gui

> **My AMD Adrenaline / NVIDIA Settings Linux Alternative**

A graphical interface for configuring GPU, CPU, Disk, and Kernel performance settings for Linux gaming. Initially made for personal use, now open-sourced so others can benefit from it too.

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

### CPU Management:
  - Governor Selection: Choose from available CPU governors.
  - Adjust the maximum and minimum CPU frequencies within the permitted range.
  - Scheduler Configuration: Select, start and stop CPU pluggable schedulers (requires [scx](https://github.com/sched-ext/scx) and `Linux Kernel >= 6.12` or a `Custom Patched Kernel`).
### GPU Configuration:
  - Mesa Drivers: Configure Mesa Drivers specific environment variables.
  - NVIDIA Drivers: Configure NVIDIA Proprietary Drivers specific environment variables.
  - Dynamic Render Selection: Select renderers for both OpenGL and Vulkan applications. The program dynamically sets the required environment variables depending on your GPU.
  - Configure various MangoHud options.
  - Configure lsfg-vk settings
  - All GPU settings are automatically added to the `volt` script.
### Disk Configuration:
  - Change Disks Schedulers
### Configure Kernel Parameters related to:
  - CPU
  - Memory
  - Disk
  - System
  - Network
  - Security
### Add custom launch options to the `volt` script:

These will be passed to the executed program. Example:
  ```
  gamemoderun PROTON_USE_WINED3D=1
  ```
### Extras:
  - Useful Links and Programs for the average Linux Gamer.
### Options:
  - Configure settings specific to the volt-gui program itself.
### Create or Delete Profiles:
  - Each profile has its own set of configurations, which can be applied through the program or system tray.

## Build/Test Requirements:

- Python 3.9 or higher
- Pip
- The `python3-venv` package its required on Debian/Debian based distros.
- Linux operating system

## Additional requirements in the case you build the program using Nuitka:

- C/C++ Compiler
- patchelf
- ccache (optional, for optimizing compiling times)

## Additional requirements for some Options:

If this software is not provided, its options will be locked.

- [scx](https://github.com/sched-ext/scx) in the case you want to make use of the CPU Pluggable Schedulers
- [mangohud](https://github.com/flightlessmango/MangoHud) in the case you want to make use of the MangoHud Settings. Both the native or the Flatpak version satisfy the dependency.
- [lsfg-vk](https://github.com/PancakeTAS/lsfg-vk) in the case you want to make use of the LS Frame Gen Settings. Both the native or the Flatpak version satisfy the dependency, as long as its **not** the `noui` version.
- `glxinfo` its required to use the OpenGL Render Selector.
- `vulkaninfo` and the `vulkan mesa layer` are required to use the Vulkan Render Selector.

## Installation:

### Quick Install:

1. Run one of the builds scripts avaliable to create the application:

   Using Pyinstaller:

   ```bash
   ./make-pyinstaller.sh
   ```

   Using Nuitka:

   ```bash
   ./make-nuitka.sh
   ```

   _Note: Both use a Python virtual environment to avoid system wide package installation using pip_

2. Install the application system wide:
   ```bash
   sudo ./install.sh
   ```
   This will:
   - Copy the executable to `/usr/local/bin/`
   - Copy the `volt-helper` script to `/usr/local/bin/`
   - Create a desktop entry at `/usr/share/applications/volt-gui.desktop`

### Removal:

1. To uninstall volt-gui:
   ```bash
   sudo ./remove.sh
   ```
   This will:
   - Remove the `volt-gui` executable from `/usr/local/bin/`
   - Remove the `volt-helper` script from `/usr/local/bin/`
   - Remove the `volt` bash script from `/usr/local/bin/`
   - Remove the desktop entry `/usr/share/applications/volt-gui.desktop`

## Testing volt-gui:

In the case you want to contribute to the project you can use the provided `test.sh` script to test the changes you made. This script will create a Python virtual environment if one does not already exist. This way, you don't have to install the program dependencies systemwide.

The first time you run it, use the -c flag that will also copy the `volt-helper` to `/usr/local/bin/`, as the program requires it for appliying the settings:

```
./test.sh -c
```

After this unless you make changes to the `volt-helper`, or the script have been updated, just run it without the flag to avoid unnecessary overwrites of the script:

```
./test.sh
```

> [!NOTE]
> You can use the `remove.sh` script to remove the `volt-helper`. The `py_env` folder should be deleted in the case you created it with your system python, and you want to use a python version that its inside a `distrobox` box, or vice versa.

## How to use `volt-gui`:

Simply launch volt-gui from your application menu or run `volt-gui` from the terminal.

## How to use the `volt` script:

The `GPU` and `Launch Options` settings are saved on the `volt` script. Here are some examples of its usage:

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

- `Select OpenGL Renderer` Selects the GPU/Renderer that will be used to render OpenGL programs. Those GPUs/Renderers are obtained trough `glxinfo`.
- `Select Vulkan Renderer` Selects the GPU/Renderer that will be used to render Vulkan programs. Those GPUs/Renderers are obtained trough `vulkaninfo`, also for this to work on some distros you might need to install some additional dependencies like `vulkan-mesa-layers` on Arch Linux. More info its provided on the Welcome Window that opens once you open volt-gui.

## Technical References:

Based on documentation and references from:

- [Arch Linux Wiki - Improving performance](https://wiki.archlinux.org/title/Improving_performance)
- [Arch Linux Wiki - Gaming](https://wiki.archlinux.org/title/Gaming#Improving_performance)
- [sched-ext tutorial - CachyOs Wiki](https://wiki.cachyos.org/configuration/sched-ext/)
- [sched-ext scx Github - Readme](https://github.com/sched-ext/scx/blob/main/README.md)
- [MangoHud Github - Readme](https://github.com/flightlessmango/MangoHud/blob/master/README.md)
- [lsfg-vk Github - Readme](https://github.com/PancakeTAS/lsfg-vk)
- [lsfg-vk Github - Wiki](https://github.com/PancakeTAS/lsfg-vk/wiki)
- [Mesa Documentation - Environment Variables](https://docs.mesa3d.org/envvars.html#environment-variables)
- [FreeDesktop - Dri Configuration Options](https://dri.freedesktop.org/wiki/ConfigurationOptions/)
- [NVIDIA 580 Drivers - Documentation](https://download.nvidia.com/XFree86/Linux-x86_64/580.82.09/README/)
- [NVIDIA 570 Drivers - Documentation](https://download.nvidia.com/XFree86/Linux-x86_64/570.153.02/README/)
- [NVIDIA 470 Drivers - Documentation](https://download.nvidia.com/XFree86/Linux-x86_64/470.256.02/README/)
- [NVIDIA 390 Drivers - Documentation](https://download.nvidia.com/XFree86/Linux-x86_64/390.157/README/)
- [Linux Kernel - Subsystem Documentation](https://docs.kernel.org/subsystem-apis.html)
- Additionally, sometimes i had to read code from Open Source projects to check how some options work.

## Contributing:

Contributions are welcome. Please ensure compatibility with supported Python versions and follow the existing code structure.
Read: [Build/Test Requirements](#buildtest-requirements), [Installation](#installation), and [Testing volt-gui](#testing-volt-gui) before contributing.
