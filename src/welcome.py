from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QStackedWidget
from PySide6.QtCore import Qt
from database import *
from themes import *
from ui import *


def get_welcome_settings() -> dict:
    return {
        "Welcome": {
            "Welcome to volt gui": (
                ("text", "volt gui is my AMD Adrenaline / NVIDIA Settings Linux Alternative.\n\nIt allows you to manage GPU drivers and environment variables through a single interface, with support for MangoHud, Gamescope, Proton, and LSFG."),
            )
        },
        "How it Works": {
            "Setting Types": (
                ("text", "Settings in this application generate environment variables saved to the volt launcher script. You must launch your applications using this script for these settings to take effect."),
            )
        },
        "Render Selector": {
            "Render Device Selection": (
                ("text", "The Render Selector tab allows you to choose which GPU handles OpenGL or Vulkan processing in hybrid graphics setups."),
                ("text", "Requirements:\n- glxinfo is required for OpenGL detection.\n- vulkaninfo AND the Mesa Vulkan Layer are required for Vulkan selection."),
                ("code", "MESA_VK_DEVICE_SELECT=list vulkaninfo", "Verify Vulkan Layer installation:"),
            )
        },
        "Custom Values": {
            "Custom Values": (
                ("text", "Every setting accepts free-form text input. Type any value directly into the text field. Leave the field empty to skip the setting. Type \"unset\" to actively remove an environment variable."),
            )
        },
        "Profiles": {
            "Profiles": (
                ("text", "Create profiles to quickly switch between configurations.\n\n1. Enter a name in New Profile and click New.\n2. Configure and Apply settings.\n3. Use the System Tray icon to switch profiles."),
            )
        },
        "Presets": {
            "Presets": (
                ("text", "Presets are curated starting points that populate the currently active profile with recommended values. Seven presets are available, arranged as a ladder from maximum fidelity to maximum frames:\n\n- Reality: every visual knob maxed out regardless of cost. Forced 16x AF, 16x MSAA, sharpening + denoising, HDR with inverse tone mapping, FIFO vsync with 3-deep frame queue, LSFG 4x with maximum motion estimation quality. For users who want the game to look as good as possible and don't care about the frame rate or latency cost.\n- Quality: maximum visual fidelity without the latency compromises. 16x AF, 8x MSAA, HDR on, FIFO vsync with 2-deep queue, LSFG 2x at max quality. The 'I have a strong GPU and want it to look great' tier.\n- Balanced: a reasonable middle ground. 8x AF, 4x MSAA, light sharpening, mailbox present mode, 1-deep frame queue. Works well on most hardware for most games.\n- Performance FPS: framerate focus with safety guardrails. 4x AF, MSAA off, relaxed barriers, mailbox present, LSFG 3x. Aggressive but still visually correct.\n- Performance Low Latency: latency focus with safety guardrails. Same performance stance as Performance FPS but with immediate present mode, DXVK min-latency frame pacing, vsync off, Reflex, and present wait enabled.\n- Potato FPS: consequences be damned, frames above all. No AF, VRS 2x2, fp16 emulation off, lenient clears, draws out of order, all relaxed barriers, hardware planes off. Will glitch in some games. That's the contract.\n- Potato Low Latency: same aggressive stance as Potato FPS but biased for input latency instead of visual smoothness."),
                ("text", "Applying a preset wipes every value in the currently selected profile and replaces them with the preset values. A confirmation dialog is shown before this happens.\n\nPresets follow a strict design principle: we configure every tool settings but never activate the tool itself. That means presets tune MangoHud/Gamescope/LSFG/etc options, but they never enable MangoHud, launch Gamescope, turn on LSFG, or pick which DXVK fork (upstream, Sarek, low-latency) you run. The user decides what tools to run; presets just preconfigure them for when you do.\n\nPresets also never touch: resolution, refresh rate, fps caps, VRAM budgets, device filtering, filesystem paths, or debug flags. These are hardware and user specific, a wrong value there would cause stuttering or crashes on different systems. The Render Selector and Launch Options tabs stay empty for the same reason."),
                ("text", "After applying a preset, tweak anything you want and click Apply. The preset is a starting point, not a locked configuration."),
            )
        },
        "Options": {
            "Options": (
                ("text", "Changes to Options are saved automatically as you type but only take effect after restarting volt-gui. This includes the theme, scaling, tray behavior, script location, and all other preferences."),
            )
        },
        "Proton": {
            "Proton Tab": (
                ("text", "The Proton tab provides environment variables for configuring Proton and Wine behavior when running Windows games on Linux through Steam.\n\nThe settings are sourced from both Proton-CachyOS and Proton-GE, and cover DXVK fork selection, synchronization primitives (Esync, Fsync, NTSync), upscaling (FSR4, DLSS, XeSS), NVIDIA libraries, Wayland support, audio configuration, memory handling, and more."),
                ("text", "These environment variables are applied via the volt script, just like all other settings. Use them in Steam Launch Options or any other launcher."),
            )
        },
        "DXVK & VKD3D": {
            "DXVK Tab": (
                ("text", "The DXVK tab provides environment variables for configuring DXVK, the Vulkan-based translation layer for Direct3D 8, 9, 10, and 11.\n\nSettings are organized on this way:"),
                ("text", "DXVK, covers the upstream DXVK project. Includes the HUD, frame rate limiter, device filtering, HDR, inline config overrides, shader cache control, and debug options.\n\nDXVK Low-Latency, covers the dxvk-low-latency fork. Adds the frame pace mode setting (low-latency, max-frame-latency, min-latency, and VRR-aware modes) to reduce input lag and improve frame pacing.\n\nDXVK Sarek, covers the dxvk-sarek fork, intended for older GPUs that do not fully support Vulkan 1.3. Adds the legacy state cache controls, all-cores shader compilation, and the dyasync toggle."),
            ),
            "VKD3D Tab": (
                ("text", "The VKD3D tab provides environment variables for configuring vkd3d-proton, the Vulkan-based translation layer for Direct3D 12.\n\nIncludes the frame rate limiter, device selection, swapchain present mode, shader cache path, all VKD3D_CONFIG flags (ray tracing, queue control, NVIDIA static CBV hack, breadcrumbs debugging, and more), and advanced shader debugging tools such as dump paths, overrides, and RenderDoc auto-capture."),
                ("text", "The DXIL SPIRV RDNA3 Workaround setting is also found here, as it directly relates to vkd3d-proton's DXIL-to-SPIR-V compilation and is required for FSR4 on RDNA3 hardware."),
            ),
        },
        "Usage": {
            "Using the volt Script": (
                ("text", "To apply Environment Settings, prepend the volt script to your command:"),
                ("code", "volt %command%", "Steam (Launch Options):"),
                ("code", "volt", "Lutris (Command prefix):"),
                ("code", "volt flatpak run net.pcsx2.PCSX2", "Flatpak:"),
            ),
            "Script Location": (
                ("text", "The default location /usr/local/bin/volt lets you type just 'volt' because /usr/local/bin is part of the system PATH. Writing to this location requires sudo, which the application requests automatically."),
                ("text", "If your distro restricts writes to system directories, you can use a path like /tmp/volt or ~/volt instead. These do not require sudo but you must use the full path when launching:"),
                ("code", "/tmp/volt %command%", "Steam with /tmp/volt:"),
                ("code", "~/volt %command%", "Steam with ~/volt:"),
                ("text", "You can change the script location in the Options tab. The application will only request elevated permissions when the chosen path requires it."),
            )
        }
    }


def create_welcome_window_widget() -> QMainWindow:
    window = QMainWindow()
    window.setWindowTitle("volt-gui Welcome")
    window.setMinimumSize(540, 380)
    central_widget = QWidget()
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(8, 8, 8, 8)
    main_layout.setSpacing(8)
    content_layout = QHBoxLayout()
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(0)
    welcome_settings = get_welcome_settings()
    stacked_widget = QStackedWidget()
    for section_name, section_data in welcome_settings.items():
        stacked_widget.addWidget(create_tab_content_widget(section_name, section_data, True)["tab"])
    content_layout.addWidget(create_simple_sidebar_widget(tuple(welcome_settings.keys()), stacked_widget))
    content_layout.addWidget(stacked_widget, 1)
    main_layout.addLayout(content_layout, 1)
    button_container = QWidget()
    button_container.setProperty("buttonContainer", True)
    button_layout = QHBoxLayout(button_container)
    button_layout.setContentsMargins(8, 8, 8, 8)
    button_layout.setSpacing(8)
    button_layout.setAlignment(Qt.AlignVCenter)
    close_button = QPushButton("Close")
    close_button.setFixedSize(get_standard_button_width(), get_standard_button_height())
    close_button.clicked.connect(window.close)
    button_layout.addStretch(1)
    button_layout.addWidget(close_button, 0, Qt.AlignVCenter)
    button_layout.addStretch(1)
    main_layout.addWidget(button_container)
    window.setCentralWidget(central_widget)
    return window
