def get_options_settings():
    return {
        "_tab_metadata": (False,),
        "_executable_required": (),
        "application_theme": (
            "Application Theme",
            (
                ("skip", None),
                ("default", "cachyos"),
                ("amd", "amd"),
                ("intel", "intel"),
                ("nvidia", "nvidia"),
                ("cachyos", "cachyos"),
            ),
            (
                ("option", "", "", "", ""),
            ),
        ),
        "window_transparency": (
            "Window Transparency",
            (
                ("skip", None),
                ("default", "disable"),
                ("disable", ""),
                ("enable", "enable"),
            ),
            (
                ("option", "", "", "", ""),
            ),
        ),
        "interface_scale_factor": (
            "Interface Scale Factor",
            (
                ("skip", None),
                ("default", "1.0"),
                ("0.25", "0.25"),
                ("0.5", "0.5"),
                ("0.75", "0.75"),
                ("1.0", "1.0"),
                ("1.25", "1.25"),
                ("1.5", "1.5"),
                ("1.75", "1.75"),
                ("2.0", "2.0"),
            ),
            (
                ("option", "", "", "", ""),
            ),
        ),
        "start_window_maximized": (
            "Start Window Maximized",
            (
                ("skip", None),
                ("default", "disable"),
                ("disable", ""),
                ("enable", "enable"),
            ),
            (
                ("option", "", "", "", ""),
            ),
        ),
        "start_window_minimized": (
            "Start Window Minimized",
            (
                ("skip", None),
                ("default", "disable"),
                ("disable", ""),
                ("enable", "enable"),
            ),
            (
                ("option", "", "", "", ""),
            ),
        ),
        "system_tray_behavior": (
            "System Tray Behavior",
            (
                ("skip", None),
                ("default", "disable"),
                ("disable", ""),
                ("enable", "enable"),
            ),
            (
                ("option", "", "", "", ""),
            ),
        ),
        "volt_script_location": (
            "Script Location",
            (
                ("skip", None),
                ("default", "/usr/local/bin/volt"),
                ("system", "/usr/local/bin/volt"),
                ("temporary", "/tmp/volt"),
            ),
            (
                ("option", "", "", "", ""),
            ),
        ),
        "welcome_message_display": (
            "Welcome Message Display",
            (
                ("skip", None),
                ("default", "enable"),
                ("disable", ""),
                ("enable", "enable"),
            ),
            (
                ("option", "", "", "", ""),
            ),
        ),
        "automatic_update_check": (
            "Automatic Update Check",
            (
                ("skip", None),
                ("default", "disable"),
                ("disable", ""),
                ("enable", "enable"),
            ),
            (
                ("option", "", "", "", ""),
            ),
        ),
    }
