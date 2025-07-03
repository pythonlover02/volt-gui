> [!WARNING]  
> This program its WIP, bugs are expected.

# volt-gui:

A graphical user interface for configuring GPU related environment variables and more for Linux gaming. Originally designed just for me and my friends, but seing that it could be useful for other Linux users i have decided to Open Source it.

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

- CPU Management
  - Governor Selection: Choose from available CPU governors
  - Scheduler Configuration: Select CPU pluggable schedulers (requires [scx](https://github.com/sched-ext/scx) and `Linux Kernel >= 6.12` or a `Custom Patched Kernel`)
- GPU Configuration
  - Mesa Drivers: Configure Mesa Drivers specific environment variables
  - NVIDIA Drivers: Configure NVIDIA Proprietary Drivers specific environment variables
  - Render Selection: Choose the renderers for both OpenGL and Vulkan applications
  - Set a frame limit for both OpenGL and Vulkan applications, Texture Filters and MidMap LOD Bias for Vulkan only (requires [mangohud](https://github.com/flightlessmango/MangoHud))
  - All those GPU settings will be added to the `volt` script
- Disk Configuration
  - Change Disks Schedulers
- Kernel Configuration
  - Choose /proc/sys/vm/compaction_proactiveness value
  - Choose /proc/sys/vm/watermark_boost_factor value
  - Choose /proc/sys/vm/min_free_kbytes value
  - Choose /proc/sys/vm/max_map_count value
  - Choose /proc/sys/vm/swappiness value
  - Choose /proc/sys/vm/dirty_ratio value
  - Choose /proc/sys/vm/dirty_background_ratio value
  - Choose /proc/sys/vm/dirty_expire_centisecs value
  - Choose /proc/sys/vm/dirty_writeback_centisecs value
  - Choose /proc/sys/vm/vfs_cache_pressure value
  - Choose /sys/kernel/mm/transparent_hugepage/enabled value
  - Choose /sys/kernel/mm/transparent_hugepage/shmem_enabled value
  - Choose /sys/kernel/mm/transparent_hugepage/defrag value
  - Choose /proc/sys/vm/zone_reclaim_mode value
  - Choose /proc/sys/vm/page_lock_unfairness value
  - Choose /proc/sys/kernel/sched_cfs_bandwidth_slice_us value
  - Choose /proc/sys/kernel/sched_autogroup_enabled value
  - Choose /proc/sys/kernel/watchdog value
  - Choose /proc/sys/kernel/nmi_watchdog value
  - Choose /proc/sys/vm/laptop_mode value

- Launch Options: add custom Launch Options to the `volt` that will be passed to the program executed, ej:
  ```
  gamemoderun PROTON_USE_WINED3D=1
  ```
- Extras
  - Useful Links for the average Linux Gamer
  - Useful Programs for the average Linux Gamer
- Options
  - Options for the program itself
- Create or Delete Profiles, all of them with its own settings, witch you can apply trough the program or systray.

## Build/Test Requirements:

- Python 3.9 or higher
- Pip
- The `python3-venv` package its required on Debian/Debian based distros.
- Linux operating system

### Additional requirements in the case you build the program using Nuitka:

- C/C++ Compiler
- patchelf
- ccache (optional, for optimizing compiling times)

### Additional requirements for some Options:
If this software is not provided, its options will be locked.

- [scx](https://github.com/sched-ext/scx) in the case you want to make use of the CPU Pluggable Schedulers
- [mangohud](https://github.com/flightlessmango/MangoHud) in the case you want to make use of the Frame Options Settings. Both the native or the Flatpak version satisfy the dependency.

## Installation:

### Quick Install:
1. Run one of the builds scripts avaliable to create the application:
   
   Using Pyinstaller:
   ```bash
   ./build-pyinstaller.sh
   ```
   
   Using Nuitka:
   ```bash
   ./build-nuitka.sh
   ```

   *Note: Both use a Python virtual environment to avoid system wide package installation using pip*

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

- `OpenGL Provider` Select a OpenGL provider between the NVIDIA Proprietary Drivers and Mesa Drivers.
- `Mesa Select GPU` In this case “select” means the GPU will be first in the reported physical devices list, It applies to OpenGL and Vulkan and only GPUs using the Mesa Drivers. Something to add its that the `OpenGL Provider` and `Vulkan ICD` settings have priority over this.
- `Vulkan ICD` Selects the Vulkan Installable Client Driver, obtained from `/usr/share/vulkan/icd.d/`.

## Technical References:

Documentation used:

- [Arch Linux Wiki - Improving performance](https://wiki.archlinux.org/title/Improving_performance)
- [Arch Linux Wiki - Gaming](https://wiki.archlinux.org/title/Gaming#Improving_performance)
- [sched-ext tutorial - CachyOs Wiki](https://wiki.cachyos.org/configuration/sched-ext/)
- [sched-ext scx Github - Readme](https://github.com/sched-ext/scx/blob/main/README.md)
- [MangoHud Github - Readme](https://github.com/flightlessmango/MangoHud/blob/master/README.md)
- [Mesa Documentation - Environment Variables](https://docs.mesa3d.org/envvars.html#environment-variables)
- [FreeDesktop - Dri Configuration Options](https://dri.freedesktop.org/wiki/ConfigurationOptions/)
- [NVIDIA 570 Drivers - Documentation](https://download.nvidia.com/XFree86/Linux-x86_64/570.153.02/README/openglenvvariables.html)
- [NVIDIA 470 Drivers - Documentation](https://download.nvidia.com/XFree86/Linux-x86_64/470.256.02/README/openglenvvariables.html)
- [NVIDIA 390 Drivers - Documentation](https://download.nvidia.com/XFree86/Linux-x86_64/390.157/README/openglenvvariables.html)

## Contributing:

Contributions are welcome. Please ensure any changes maintain compatibility with the supported Python versions and follow the existing code structure. You might want to read: [Build/Test Requirements](#buildtest-requirements), [Installation](#installation) and [Testing volt-gui](#testing-volt-gui).
