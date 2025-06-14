# volt-gui:

A graphical user interface for configuring GPU related environment variables and more for Linux gaming. Originally designed just for me and my friends, but seing that it could be useful for other Linux users i have decided to Open Source it.

![Badge Language](https://img.shields.io/github/languages/top/pythonlover02/volt-gui)
[![Stars](https://img.shields.io/github/stars/pythonlover02/volt-gui?style=social)](https://github.com/pythonlover02/volt-gui/stargazers)

![](/images/1.png)
![](/images/2.png)
![](/images/3.png)

## What you can do?:

- CPU Management
  - Governor Selection: Choose from available CPU governors
  - Scheduler Configuration: Select CPU pluggable schedulers (requires [scx](https://github.com/sched-ext/scx) and `Linux Kernel >= 6.12` or a `Custom Patched Kernel`)
- GPU Configuration
  - Mesa Drivers: Configure Mesa Drivers specific environment variables
  - NVIDIA Drivers: Configure NVIDIA Proprietary Drivers specific environment variables
  - Render Selection: Choose the renderers for both OpenGL and Vulkan applications
  - Set frame limit for both OpenGL and Vulkan applications (requires [mangohud](https://github.com/flightlessmango/MangoHud))
  - All those GPU settings will be added to the `volt` script
- Disk Configuration
  - Change Disks Schedulers
- Kernel Configuration
  - Chose compaction_proactiveness value
  - Chose watermark_boost_factor value
  - Chose min_free_kbytes value
  - Chose max_map_count value
  - Chose swappiness value
  - Chose zone_reclaim_mode value
  - Chose page_lock_unfairness value
  - Chose sched_cfs_bandwidth_slice_us value
  - Chose sched_autogroup_enabled value

- Launch Options: add custom Launch Options to the `volt` that will be passed to the program executed, ej:
  ```
  gamemoderun PROTON_USE_WINED3D=1
  ```
- Extras
  - Useful Links for the average Linux Gamer
  - Useful Programs for the average Linux Gamer
- Options
  - Options for the program itself

> [!NOTE]  
> CPU, Disk and Kernel settings will be reverted or not when volt-gui its closed, depending of the options selected by the user on the option tab. But those options will always be reverted on system reboot.

## Build Requirements:

- Python 3.9 or higher
- Pip
- Linux operating system

### Additional requirements in the case you build the program using Nuitka:

- C/C++ Compiler
- patchelf
- ccache (optional, for optimizing compiling times)

### Additional requirements for some Options:
If this software its not provied leave those settings on unset:

- [scx](https://github.com/sched-ext/scx) in the case you want to make use of the CPU Pluggable Schedulers
- [mangohud](https://github.com/flightlessmango/MangoHud) in the case you want to make use of the Frame Options

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
   - Copy the helper scripts to `/usr/local/bin/`
   - Create a desktop entry at `/usr/share/applications/volt-gui.desktop`

### Removal:
1. To uninstall volt-gui:
   ```bash
   sudo ./remove.sh
   ```
   This will:
   - Remove the `volt-gui` executable from `/usr/local/bin/`
   - Remove the helper scripts from `/usr/local/bin/`
   - Remove the `volt` bash script from `/usr/local/bin/`
   - Remove the desktop entry `/usr/share/applications/volt-gui.desktop`

## How to use `volt-gui`:

Simply launch volt-gui from your application menu or run `volt-gui` from the terminal.

## How to use the `volt` script:

The `GPU` and `Launch Options` settings are saved on the `volt` script, this script must be called on your launcher launch options or before the program, example for Steam:

```
volt %command%
```

## GPU Selector explained:

- `GLX Vendor Library` Select a GLX provider between the NVIDIA Proprietary Drivers and Mesa Drivers.
- `Mesa Select GPU` Select which to use GPU among those available on the system. (Only for GPUs using the Mesa Drivers)
- `OpenGL Software Rendering` Use Mesa OpenGL Software Rendering; this will ignore the `Mesa Select GPU` option.
- `Vulkan ICD` Selects the Vulkan Installable Client Driver, obtained from `/usr/share/vulkan/icd.d/`.

## Technical References:

Documentation used:

- [Improving performance - Arch Linux Wiki](https://wiki.archlinux.org/title/Improving_performance)
- [Gaming - Arch Linux Wiki](https://wiki.archlinux.org/title/Gaming#Improving_performance)
- [sched-ext tutorial - CachyOs Wiki](https://wiki.cachyos.org/configuration/sched-ext/)
- [Mesa Documentation - Environment Variables](https://docs.mesa3d.org/envvars.html#environment-variables)
- [NVIDIA 570 Drivers Documentation](https://download.nvidia.com/XFree86/Linux-x86_64/570.153.02/README/openglenvvariables.html)
- [NVIDIA 470 Drivers Documentation](https://download.nvidia.com/XFree86/Linux-x86_64/470.256.02/README/openglenvvariables.html)
- [NVIDIA 390 Drivers Documentation](https://download.nvidia.com/XFree86/Linux-x86_64/390.157/README/openglenvvariables.html)

## Contributing:

Contributions are welcome. Please ensure any changes maintain compatibility with the supported Python versions and follow the existing code structure.
