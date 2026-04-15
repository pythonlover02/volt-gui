def get_options_settings() -> dict:
    return {
        "_tab_metadata": (False,),
        "_executable_required": (),
        "application_theme": {
            "label": "Application Theme",
            "description": "Color theme for the application. Takes effect on program restart.",
            "inputs": "amd=amd, intel=intel, nvidia=nvidia, cachyos=cachyos",
            "output": ("option", "", "", "", ""),
        },
        "window_transparency": {
            "label": "Window Transparency",
            "description": "Window background transparency. Takes effect on program restart.",
            "inputs": "on=on, off=off",
            "output": ("option", "", "", "", ""),
        },
        "interface_scale_factor": {
            "label": "Interface Scale Factor",
            "description": "UI scaling multiplier. Takes effect on program restart.",
            "inputs": "0.25=0.25, 0.5=0.5, 0.75=0.75, 1.0=1.0, 1.25=1.25, 1.5=1.5, 1.75=1.75, 2.0=2.0",
            "output": ("option", "", "", "", ""),
        },
        "start_window_maximized": {
            "label": "Start Window Maximized",
            "description": "Start the window in maximized state. Takes effect on program restart.",
            "inputs": "on=on, off=off",
            "output": ("option", "", "", "", ""),
        },
        "start_window_minimized": {
            "label": "Start Window Minimized",
            "description": "Start the window minimized to tray. Takes effect on program restart.",
            "inputs": "on=on, off=off",
            "output": ("option", "", "", "", ""),
        },
        "system_tray_behavior": {
            "label": "System Tray",
            "description": "Show icon in the system tray. Takes effect on program restart.",
            "inputs": "on=on, off=off",
            "output": ("option", "", "", "", ""),
        },
        "volt_script_location": {
            "label": "Script Location",
            "description": "Filesystem path for the volt launcher script. The default /usr/local/bin/volt lets you type just 'volt' because /usr/local/bin is in PATH. Paths like /tmp/volt or ~/volt avoid needing sudo but require the full path (e.g. /tmp/volt %command%). If the chosen directory is writable by your user, sudo will not be requested. Takes effect on program restart.",
            "inputs": "filesystem=filesystem path (e.g. /usr/local/bin/volt)",
            "output": ("option", "", "", "", ""),
        },
        "welcome_message_display": {
            "label": "Welcome Message",
            "description": "Show the welcome message on startup. Takes effect on program restart.",
            "inputs": "on=on, off=off",
            "output": ("option", "", "", "", ""),
        },
        "automatic_update_check": {
            "label": "Automatic Update Check",
            "description": "Check for updates on startup. Takes effect on program restart.",
            "inputs": "on=on, off=off",
            "output": ("option", "", "", "", ""),
        },
    }
