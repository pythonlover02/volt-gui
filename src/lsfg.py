def get_lsfg_settings():
    return {
        "_tab_metadata": (True,),
        "_executable_required": ("lsfg",),
        "enable": (
            "Enable",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LSFG_LEGACY", "", "", ""),
            ),
        ),
        "vulkan_frames_per_second_multiplier": (
            "Frames Per Second Multiplier",
            (
                ("skip", None),
                ("default", ""),
                ("2x", "2"),
                ("3x", "3"),
                ("4x", "4"),
            ),
            (
                ("environment_variable", "LSFG_MULTIPLIER", "", "", ""),
            ),
        ),
        "vulkan_motion_estimation_quality": (
            "Motion Estimation Quality",
            (
                ("skip", None),
                ("default", ""),
                ("0.25", "0.25"),
                ("0.50", "0.50"),
                ("0.75", "0.75"),
                ("1.0", "1.0"),
            ),
            (
                ("environment_variable", "LSFG_FLOW_SCALE", "", "", ""),
            ),
        ),
        "vulkan_performance_mode": (
            "Performance Mode",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LSFG_PERFORMANCE_MODE", "", "", ""),
            ),
        ),
        "vulkan_high_dynamic_range_mode": (
            "High Dynamic Range Mode",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LSFG_HDR_MODE", "", "", ""),
            ),
        ),
        "library_path_override": (
            "Library Path Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "LSFG_DLL_PATH", "", "", ""),
            ),
        ),
        "vulkan_experimental_present_mode_override": (
            "Experimental Present Mode Override",
            (
                ("skip", None),
                ("default", ""),
                ("fifo", "fifo"),
                ("vsync", "vsync"),
                ("mailbox", "mailbox"),
                ("immediate", "immediate"),
            ),
            (
                ("environment_variable", "LSFG_EXPERIMENTAL_PRESENT_MODE", "", "", ""),
            ),
        ),
    }
