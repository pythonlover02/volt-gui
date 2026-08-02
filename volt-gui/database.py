from typing import Final


APP_VERSION: Final[str] = "2.0.0"
APP_AUTHOR: Final[str] = "pythonlover02"
APP_LICENSE: Final[str] = "GPL 3.0 License"
APP_DESCRIPTION: Final[str] = "My AMD Adrenaline / NVIDIA Settings Linux Alternative"

DEFAULT_VALUE: Final[str] = "default"
DEFAULT_PROFILE: Final[str] = "default"

PROFILE_TABS: Final[tuple] = ("Display", "Framerate", "Textures", "Rendering", "GPU")
ALL_TABS: Final[tuple] = ("Display", "Framerate", "Textures", "Rendering", "GPU", "Options", "About")

LOD_STEPS: Final[tuple] = ("-3.0", "-2.5", "-2.0", "-1.5", "-1.0", "-0.5", "0.0", "0.5", "1.0", "1.5", "2.0", "2.5", "3.0")
LOD_LEVELS: Final[tuple] = ("0.0", "1.0", "2.0", "3.0", "4.0", "6.0", "8.0", "12.0")
COUNT_STEPS: Final[tuple] = ("2", "3", "4")

SETTINGS_DB: Final[dict] = {
    "GPU": {
        "device": {
            "section": "gpu",
            "label": "Physical Device",
            "description": "Which physical device the game is allowed to see, by index in the order the driver reports them. The layer filters device enumeration itself, so this works on every Vulkan driver. Out of range indices keep all devices and log a warning.",
            "options": (DEFAULT_VALUE, "1", "2", "3", "4"),
            "editable": True,
        },
    },
    "Display": {
        "present_mode": {
            "section": "display",
            "label": "VSync / Present Mode",
            "description": "How finished frames reach the screen. fifo is classic vsync, fifo_relaxed tears only below refresh, mailbox is low latency vsync, immediate disables vsync entirely. Unsupported modes on your surface fall back to the application's own choice.",
            "options": (DEFAULT_VALUE, "fifo", "fifo_relaxed", "mailbox", "immediate"),
            "editable": False,
        },
        "image_count": {
            "section": "display",
            "label": "Swapchain Images",
            "description": "Number of images requested for the swapchain. Fewer images lower display latency, more images smooth frame delivery. Clamped to what the surface supports.",
            "options": (DEFAULT_VALUE,) + COUNT_STEPS,
            "editable": True,
        },
        "image_count_min": {
            "section": "display",
            "label": "Swapchain Images Minimum",
            "description": "Lower clamp applied to the application's own swapchain image request when Swapchain Images is default.",
            "options": (DEFAULT_VALUE,) + COUNT_STEPS,
            "editable": True,
        },
        "image_count_max": {
            "section": "display",
            "label": "Swapchain Images Maximum",
            "description": "Upper clamp applied to the application's own swapchain image request when Swapchain Images is default. Lower values reduce latency.",
            "options": (DEFAULT_VALUE,) + COUNT_STEPS,
            "editable": True,
        },
        "color_depth": {
            "section": "display",
            "label": "Color Depth",
            "description": "Reorder the surface formats the game sees when it queries the surface. 10bit prefers 10-bit SDR formats. Games that pick the first supported format follow the preference; hardcoded choices are respected. The layer only reorders what the surface already reports, so the preference works wherever the driver offers the format.",
            "options": (DEFAULT_VALUE, "10bit"),
            "editable": False,
        },
    },
    "Framerate": {
        "frame_limit": {
            "section": "framerate",
            "label": "Frame Limit",
            "description": "Cap the frame rate at present time. Pick a common cap or type any FPS value. Lower caps reduce power draw and can stabilize frametimes.",
            "options": (DEFAULT_VALUE, "30", "40", "48", "60", "75", "90", "120", "144", "165", "240"),
            "editable": True,
        },
        "frame_pacing": {
            "section": "framerate",
            "label": "Frame Pacing",
            "description": "How the frame limiter waits. sleep is CPU friendly, precise sleeps most of the interval then busy waits the remainder for tighter frametimes at a small CPU cost. Only applies when Frame Limit is set.",
            "options": (DEFAULT_VALUE, "sleep", "precise"),
            "editable": False,
        },
    },
    "Textures": {
        "filtering": {
            "section": "textures",
            "label": "Texture Filtering",
            "description": "Force the sampler filter mode. retro gives sharp unfiltered pixels, bilinear smooths within a mip level, trilinear also blends between mip levels.",
            "options": (DEFAULT_VALUE, "retro", "bilinear", "trilinear"),
            "editable": False,
        },
        "anisotropy": {
            "section": "textures",
            "label": "Anisotropic Filtering",
            "description": "Sharpen textures viewed at steep angles. Higher values look better at a small cost. Clamped to the maximum your GPU reports; ignored when the device lacks the feature.",
            "options": (DEFAULT_VALUE, "off", "2", "4", "8", "16"),
            "editable": True,
        },
        "lod_bias": {
            "section": "textures",
            "label": "LOD Bias",
            "description": "Shift mipmap selection. Negative values sharpen at the cost of shimmer, positive values blur but render faster.",
            "options": (DEFAULT_VALUE,) + LOD_STEPS,
            "editable": True,
        },
        "lod_bias_min": {
            "section": "textures",
            "label": "LOD Bias Minimum",
            "description": "Lower clamp applied to the application's own LOD bias when LOD Bias is default.",
            "options": (DEFAULT_VALUE,) + LOD_STEPS,
            "editable": True,
        },
        "lod_bias_max": {
            "section": "textures",
            "label": "LOD Bias Maximum",
            "description": "Upper clamp applied to the application's own LOD bias when LOD Bias is default.",
            "options": (DEFAULT_VALUE,) + LOD_STEPS,
            "editable": True,
        },
        "lod_min": {
            "section": "textures",
            "label": "Minimum LOD",
            "description": "Lowest mip level samplers may use. Raising it forces smaller mips everywhere, trading detail for speed. Applied through the sampler path.",
            "options": (DEFAULT_VALUE,) + LOD_LEVELS,
            "editable": True,
        },
        "lod_max": {
            "section": "textures",
            "label": "Maximum LOD",
            "description": "Highest mip level samplers may use. Lowering it keeps distant textures sharper than the application intended.",
            "options": (DEFAULT_VALUE,) + LOD_LEVELS,
            "editable": True,
        },
    },
    "Rendering": {
        "sample_shading": {
            "section": "rendering",
            "label": "Sample Shading",
            "description": "Shade at sample rate inside MSAA render targets to reduce shimmer. The value is the minimum fraction of samples shaded. Requires the sampleRateShading device feature; only affects applications already using MSAA.",
            "options": (DEFAULT_VALUE, "off", "0.25", "0.5", "1.0"),
            "editable": True,
        },
    },
}

OPTIONS_DB: Final[dict] = {
    "application_theme": {
        "label": "Application Theme",
        "description": "Color theme for the application. Takes effect on program restart.",
        "options": ("cachyos", "amd", "intel", "nvidia"),
        "editable": False,
    },
    "window_transparency": {
        "label": "Window Transparency",
        "description": "Window background transparency. Takes effect on program restart.",
        "options": ("off", "on"),
        "editable": False,
    },
    "interface_scale_factor": {
        "label": "Interface Scale Factor",
        "description": "UI scaling multiplier. Takes effect on program restart.",
        "options": ("1.0", "0.25", "0.5", "0.75", "1.25", "1.5", "1.75", "2.0"),
        "editable": False,
    },
    "start_window_maximized": {
        "label": "Start Window Maximized",
        "description": "Start the window in maximized state. Takes effect on program restart.",
        "options": ("off", "on"),
        "editable": False,
    },
    "start_window_minimized": {
        "label": "Start Window Minimized",
        "description": "Start the window minimized to tray. Takes effect on program restart.",
        "options": ("off", "on"),
        "editable": False,
    },
    "system_tray_behavior": {
        "label": "System Tray",
        "description": "Show icon in the system tray. Takes effect on program restart.",
        "options": ("off", "on"),
        "editable": False,
    },
    "welcome_message_display": {
        "label": "Welcome Message",
        "description": "Show the welcome message on startup. Takes effect on program restart.",
        "options": ("on", "off"),
        "editable": False,
    },
    "automatic_update_check": {
        "label": "Automatic Update Check",
        "description": "Check for updates on startup. Takes effect on program restart.",
        "options": ("off", "on"),
        "editable": False,
    },
}


def find_settings_for_tab(tab_name: str) -> dict:
    return SETTINGS_DB.get(tab_name, {})


def get_setting_label(tab_name: str, setting_key: str) -> str:
    return SETTINGS_DB[tab_name][setting_key]["label"]


def get_setting_description(tab_name: str, setting_key: str) -> str:
    return SETTINGS_DB[tab_name][setting_key]["description"]


def get_setting_options(tab_name: str, setting_key: str) -> tuple:
    return SETTINGS_DB[tab_name][setting_key]["options"]


def is_setting_editable(tab_name: str, setting_key: str) -> bool:
    return SETTINGS_DB[tab_name][setting_key]["editable"]


def get_setting_section(tab_name: str, setting_key: str) -> str:
    return SETTINGS_DB[tab_name][setting_key]["section"]


def get_option_label(option_key: str) -> str:
    return OPTIONS_DB[option_key]["label"]


def get_option_description(option_key: str) -> str:
    return OPTIONS_DB[option_key]["description"]


def get_option_options(option_key: str) -> tuple:
    return OPTIONS_DB[option_key]["options"]


def get_option_default_value(option_key: str) -> str:
    return OPTIONS_DB[option_key]["options"][0]


def get_accent_colors(theme_name: str) -> tuple:
    match theme_name:
        case "amd":
            return ("#E31937", "#FF2D4A", "#B81430")
        case "intel":
            return ("#0068B5", "#1A8CFF", "#004D87")
        case "nvidia":
            return ("#76B900", "#8ED11A", "#5A8F00")
        case _:
            return ("#80dbcb", "#9ae4d8", "#66b0a2")


def get_about_data() -> dict:
    return {
        "Description": APP_DESCRIPTION,
        "License": APP_LICENSE,
        "Author": APP_AUTHOR,
        "Version": APP_VERSION,
    }
