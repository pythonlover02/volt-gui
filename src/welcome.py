from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QStackedWidget
from PySide6.QtCore import Qt
from database import *
from ui import *


def get_welcome_settings():
    return {
        "section_names": ("Welcome", "How it Works", "Render Selector", "Custom Values", "Profiles", "Usage"),
        "section_data": {
            "Welcome": {
                "Welcome to volt gui": (
                    ("text", "volt gui is a unified GPU configuration tool for Linux.\n\nIt allows you to manage GPU drivers and environment variables through a single interface, with support for MangoHud, Gamescope, and LSFG-VK."),
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
                    ("text", "If a setting's dropdown doesn't have the option you need, click the '+' button next to the setting and type your value."),
                )
            },
            "Profiles": {
                "Profiles": (
                    ("text", "Create profiles to quickly switch between configurations.\n\n1. Enter a name in New Profile and click New.\n2. Configure and Apply settings.\n3. Use the System Tray icon to switch profiles."),
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
    }


def create_welcome_window_widget():
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
    section_names = welcome_settings["section_names"]
    section_data = welcome_settings["section_data"]
    stacked_widget = QStackedWidget()
    for section_name in section_names:
        stacked_widget.addWidget(create_tab_content_widget(section_name, section_data[section_name], True)["tab"])
    content_layout.addWidget(create_sidebar_widget(section_names, stacked_widget))
    content_layout.addWidget(stacked_widget, 1)
    main_layout.addLayout(content_layout, 1)
    button_container = QWidget()
    button_container.setProperty("buttonContainer", True)
    button_layout = QHBoxLayout(button_container)
    button_layout.setContentsMargins(12, 8, 12, 8)
    close_button = QPushButton("Close")
    close_button.setMinimumSize(90, 30)
    close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    close_button.clicked.connect(window.close)
    button_layout.addStretch(1)
    button_layout.addWidget(close_button)
    button_layout.addStretch(1)
    main_layout.addWidget(button_container)
    window.setCentralWidget(central_widget)
    return window
