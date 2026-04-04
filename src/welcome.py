from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QStackedWidget
from PySide6.QtCore import Qt
from database import *
from ui import *


def get_welcome_settings() -> dict:
    return {
        "Welcome": {
            "Welcome to volt gui": (
                ("text", "volt gui its my AMD Adrenaline / NVIDIA Settings Linux Alternative.\n\nIt allows you to manage GPU drivers and environment variables through a single interface, with support for MangoHud, Gamescope, and LSFG-VK."),
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
        "Options": {
            "Options": (
                ("text", "Changes to Options are saved automatically but require a restart of volt-gui to take effect."),
            )
        },
        "Proton": {
            "Proton Tab": (
                ("text", "The Proton tab provides environment variables for configuring Proton and Wine behavior when running Windows games on Linux through Steam.\n\nThe settings are based on the Proton-CachyOS project and include options for DXVK, synchronization, upscaling (FSR4, DLSS, XeSS), NVIDIA libraries, Wayland support, audio configuration, and more."),
                ("text", "These environment variables are applied via the volt script, just like all other settings. Use them in Steam Launch Options or any other launcher."),
            )
        },
        "Usage": {
            "Using the volt Script": (
                ("text", "To apply Environment Settings, prepend the volt script to your command:"),
                ("code", "volt %command%", "Steam (Launch Options):"),
                ("code", "volt", "Lutris (Command prefix):"),
                ("code", "volt flatpak run net.pcsx2.PCSX2", "Flatpak:"),
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
    content_layout.addWidget(create_sidebar_widget(tuple(welcome_settings.keys()), stacked_widget))
    content_layout.addWidget(stacked_widget, 1)
    main_layout.addLayout(content_layout, 1)
    button_container = QWidget()
    button_container.setProperty("buttonContainer", True)
    button_layout = QHBoxLayout(button_container)
    button_layout.setContentsMargins(12, 8, 12, 8)
    close_button = QPushButton("Close")
    close_button.setMinimumSize(90, 40)
    close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    close_button.clicked.connect(window.close)
    button_layout.addStretch(1)
    button_layout.addWidget(close_button)
    button_layout.addStretch(1)
    main_layout.addWidget(button_container)
    window.setCentralWidget(central_widget)
    return window
