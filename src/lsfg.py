def get_lsfg_settings() -> dict:
    return {
        "_tab_metadata": (True,),
        "_executable_required": ("lsfg",),
        "lsfg": {
            "label": "LSFG",
            "description": "LSFG frame generation activation variable.",
            "inputs": "1=on, 0=off",
            "output": ("environment_variable", "LSFG_LEGACY", ""),
        },
        "vulkan_frames_per_second_multiplier": {
            "label": "FPS Multiplier",
            "description": "Frame generation multiplier.",
            "inputs": "2=2x, 3=3x, 4=4x",
            "output": ("environment_variable", "LSFG_MULTIPLIER", ""),
        },
        "vulkan_motion_estimation_quality": {
            "label": "Motion Estimation Quality",
            "description": "Optical flow quality scale.",
            "inputs": "0.25=low, 0.50=medium, 0.75=high, 1.0=maximum",
            "output": ("environment_variable", "LSFG_FLOW_SCALE", ""),
        },
        "vulkan_performance_mode": {
            "label": "Performance Mode",
            "description": "Reduced quality for better performance.",
            "inputs": "1=on, 0=off",
            "output": ("environment_variable", "LSFG_PERFORMANCE_MODE", ""),
        },
        "vulkan_high_dynamic_range_mode": {
            "label": "HDR Mode",
            "description": "HDR-aware frame generation mode.",
            "inputs": "1=on, 0=off",
            "output": ("environment_variable", "LSFG_HDR_MODE", ""),
        },
        "library_path_override": {
            "label": "Library Path Override",
            "description": "Override path for the LSFG shared library.",
            "inputs": "path=filesystem path",
            "output": ("environment_variable", "LSFG_DLL_PATH", ""),
        },
        "vulkan_experimental_present_mode_override": {
            "label": "Experimental VSync Mode Override",
            "description": "Override Vulkan present mode.",
            "inputs": "fifo=vsync-on, mailbox=triple-buffer, immediate=vsync-off",
            "output": ("environment_variable", "LSFG_EXPERIMENTAL_PRESENT_MODE", ""),
        },
    }
