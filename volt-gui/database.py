from typing import Final


APP_VERSION: Final[str] = "2.0.0"
APP_AUTHOR: Final[str] = "pythonlover02"
APP_LICENSE: Final[str] = "GPL 3.0 License"
APP_DESCRIPTION: Final[str] = "My AMD Adrenaline / NVIDIA Settings Linux Alternative"

DEFAULT_VALUE: Final[str] = "default"
DEFAULT_PROFILE: Final[str] = "default"

PROFILE_TABS: Final[tuple] = ("Display", "Framerate", "Textures", "Rendering", "GPU")
ALL_TABS: Final[tuple] = ("Display", "Framerate", "Textures", "Rendering", "GPU", "Options", "About")

BOUND_SUFFIXES: Final[tuple] = ("", "_min", "_max")
BOUND_CAPTIONS: Final[tuple] = ("Force", "Minimum", "Maximum")
SINGLE_SUFFIXES: Final[tuple] = ("",)
SINGLE_CAPTIONS: Final[tuple] = ("",)

LOD_STEPS: Final[tuple] = ("-3.0", "-2.5", "-2.0", "-1.5", "-1.0", "-0.5", "0.0", "0.5", "1.0", "1.5", "2.0", "2.5", "3.0")
LOD_LEVELS: Final[tuple] = ("0.0", "1.0", "2.0", "3.0", "4.0", "6.0", "8.0", "12.0")
COUNT_STEPS: Final[tuple] = ("2", "3", "4")

SETTINGS_DB: Final[dict] = {
    "GPU": {
        "device": {
            "section": "gpu",
            "label": "Physical Device",
            "description": "Which physical device the game sees, by index in the order the driver reports them. Force hides every other device. The bounds keep a range of indices and hide the rest. A selection that matches no device is ignored and logged, so the game always sees at least the full list.",
            "options": (DEFAULT_VALUE, "1", "2", "3", "4"),
            "editable": True,
            "bounded": True,
        },
    },
    "Display": {
        "present_mode": {
            "section": "display",
            "label": "VSync / Present Mode",
            "description": "How finished frames reach the screen. fifo is classic vsync, fifo_relaxed tears only below refresh, mailbox is low latency vsync, immediate disables vsync entirely. The bounds run along that same order, from most latency to least, so Maximum mailbox never lets a game tear and Minimum mailbox never lets it sit on classic vsync. Modes the surface does not support fall back to the application's own choice.",
            "options": (DEFAULT_VALUE, "fifo", "fifo_relaxed", "mailbox", "immediate"),
            "editable": False,
            "bounded": True,
        },
        "image_count": {
            "section": "display",
            "label": "Swapchain Images",
            "description": "Number of images in the swapchain. Fewer images lower display latency, more images smooth frame delivery. Clamped to what the surface supports after your own values are applied.",
            "options": (DEFAULT_VALUE,) + COUNT_STEPS,
            "editable": True,
            "bounded": True,
        },
        "color_depth": {
            "section": "display",
            "label": "Color Depth",
            "description": "Which surface formats the game is allowed to see. Force keeps only formats of that depth, and the bounds keep the range. Games that pick the first supported format follow the choice. A selection that matches no format is ignored and logged, so the game always sees at least the full list.",
            "options": (DEFAULT_VALUE, "8bit", "10bit"),
            "editable": False,
            "bounded": True,
        },
    },
    "Framerate": {
        "frame_limit": {
            "section": "framerate",
            "label": "Frame Limit",
            "description": "Cap the frame rate at present time. Pick a common cap or type any FPS value.",
            "options": (DEFAULT_VALUE, "30", "40", "48", "60", "75", "90", "120", "144", "165", "240"),
            "editable": True,
            "bounded": False,
        },
        "frame_limit_method": {
            "section": "framerate",
            "label": "Frame Limit Method",
            "description": "Method sets when the limiter waits: early holds the frame back so presents leave on a fixed cadence, late lets the present through immediately and waits before returning to the application, which starts its next frame later and samples input closer to display time.",
            "options": (DEFAULT_VALUE, "early", "late"),
            "editable": False,
            "bounded": False,
        },
        "frame_pacing": {
            "section": "framerate",
            "label": "Frame Pacing",
            "description": "Pacing sets how the limiter waits: sleep is CPU friendly, precise sleeps most of the interval then busy waits the remainder for tighter frametimes at a small CPU cost. Method and Pacing only apply when Limit is set. These three carry no bounds: the application never asks Vulkan for a frame rate, so there is nothing to bound.",
            "options": (DEFAULT_VALUE, "sleep", "precise"),
            "editable": False,
            "bounded": False,
        },
    },
    "Textures": {
        "filtering": {
            "section": "textures",
            "label": "Texture Filtering",
            "description": "The sampler filter mode. retro gives sharp unfiltered pixels, bilinear smooths within a mip level, trilinear also blends between mip levels. Samplers that match none of the three exactly are ranked down to the closest one below them before the bounds apply.",
            "options": (DEFAULT_VALUE, "retro", "bilinear", "trilinear"),
            "editable": False,
            "bounded": True,
        },
        "mipmap_mode": {
            "section": "textures",
            "label": "Mipmap Mode",
            "description": "How samplers move between mip levels. nearest cuts hard from one mip to the next, linear blends across them. Minimum linear raises a sampler that cuts, Maximum nearest lowers one that blends. Applied after Texture Filtering, so it overrides the mip behaviour that choice implies. Only affects textures that carry mips.",
            "options": (DEFAULT_VALUE, "nearest", "linear"),
            "editable": False,
            "bounded": True,
        },
        "anisotropy": {
            "section": "textures",
            "label": "Anisotropic Filtering",
            "description": "Sharpen textures viewed at steep angles. Higher values look better at a small cost. off counts as the lowest value, so Minimum 4 raises a game that asked for less and leaves a game that asked for more alone. Clamped to the maximum your GPU reports; ignored when the device lacks the feature.",
            "options": (DEFAULT_VALUE, "off", "2", "4", "8", "16"),
            "editable": True,
            "bounded": True,
        },
        "lod_bias": {
            "section": "textures",
            "label": "LOD Bias",
            "description": "Shift mipmap selection. Negative values sharpen at the cost of shimmer, positive values blur but render faster. Clamped to the range your GPU reports.",
            "options": (DEFAULT_VALUE,) + LOD_STEPS,
            "editable": True,
            "bounded": True,
        },
        "mip_floor": {
            "section": "textures",
            "label": "Mip Floor",
            "description": "The lowest mip level samplers may use, the minimum LOD in Vulkan terms. Raising it forces smaller mips everywhere, trading detail for speed.",
            "options": (DEFAULT_VALUE,) + LOD_LEVELS,
            "editable": True,
            "bounded": True,
        },
        "mip_ceiling": {
            "section": "textures",
            "label": "Mip Ceiling",
            "description": "The highest mip level samplers may use, the maximum LOD in Vulkan terms. Lowering it keeps distant textures sharper than the application intended.",
            "options": (DEFAULT_VALUE,) + LOD_LEVELS,
            "editable": True,
            "bounded": True,
        },
    },
    "Rendering": {
        "sample_shading": {
            "section": "rendering",
            "label": "Sample Shading",
            "description": "Shade at sample rate inside MSAA render targets to reduce shimmer. The value is the minimum fraction of samples shaded, and off counts as zero. Requires the sampleRateShading device feature; only affects applications already using MSAA.",
            "options": (DEFAULT_VALUE, "off", "0.25", "0.5", "1.0"),
            "editable": True,
            "bounded": True,
        },
        "alpha_to_coverage": {
            "section": "rendering",
            "label": "Alpha To Coverage",
            "description": "Turn fragment alpha into coverage, which softens cutout edges on foliage and fences. Minimum on raises a pipeline that asked for off, Maximum off lowers one that asked for on. Only has an effect where the application already renders to an MSAA target.",
            "options": (DEFAULT_VALUE, "off", "on"),
            "editable": False,
            "bounded": True,
        },
    },
}

GROUPS_DB: Final[dict] = {
    "Framerate": {
        "label": "Frame Limiter",
        "keys": ("frame_limit", "frame_limit_method", "frame_pacing"),
        "captions": ("Limit", "Method", "Pacing"),
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
        "description": "UI scaling multiplier. Pick a step or type any value between 0.5 and 3.0. Anything outside that range falls back to 1.0. Takes effect on program restart.",
        "options": ("1.0", "0.25", "0.5", "0.75", "1.25", "1.5", "1.75", "2.0"),
        "editable": True,
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


def is_setting_bounded(tab_name: str, setting_key: str) -> bool:
    return SETTINGS_DB[tab_name][setting_key]["bounded"]


def get_setting_section(tab_name: str, setting_key: str) -> str:
    return SETTINGS_DB[tab_name][setting_key]["section"]


def get_setting_suffixes(tab_name: str, setting_key: str) -> tuple:
    match is_setting_bounded(tab_name, setting_key):
        case True:
            return BOUND_SUFFIXES
        case False:
            return SINGLE_SUFFIXES


def get_setting_captions(tab_name: str, setting_key: str) -> tuple:
    match is_setting_bounded(tab_name, setting_key):
        case True:
            return BOUND_CAPTIONS
        case False:
            return SINGLE_CAPTIONS


def find_setting_fields(tab_name: str, setting_key: str) -> tuple:
    return tuple(
        (tab_name + ":" + setting_key + suffix, setting_key + suffix)
        for suffix in get_setting_suffixes(tab_name, setting_key))


def find_setting_widget_keys(tab_name: str, setting_key: str) -> tuple:
    return tuple(
        widget_key for widget_key, _ in find_setting_fields(tab_name, setting_key))


def is_tab_grouped(tab_name: str) -> bool:
    return tab_name in GROUPS_DB


def get_group_label(tab_name: str) -> str:
    return GROUPS_DB[tab_name]["label"]


def get_group_description(tab_name: str) -> str:
    return " ".join(
        get_setting_description(tab_name, setting_key)
        for setting_key in GROUPS_DB[tab_name]["keys"])


def find_setting_columns(tab_name: str, setting_key: str) -> tuple:
    return tuple(
        (widget_key,
         caption,
         get_setting_options(tab_name, setting_key),
         is_setting_editable(tab_name, setting_key))
        for (widget_key, _), caption in zip(
            find_setting_fields(tab_name, setting_key),
            get_setting_captions(tab_name, setting_key)))


def find_group_columns(tab_name: str) -> tuple:
    return tuple(
        (tab_name + ":" + setting_key,
         caption,
         get_setting_options(tab_name, setting_key),
         is_setting_editable(tab_name, setting_key))
        for setting_key, caption in zip(
            GROUPS_DB[tab_name]["keys"], GROUPS_DB[tab_name]["captions"]))


def find_group_cards(tab_name: str) -> tuple:
    return ((tab_name,
             get_group_label(tab_name),
             get_group_description(tab_name),
             find_group_columns(tab_name)),)


def find_setting_cards(tab_name: str) -> tuple:
    return tuple(
        (tab_name + ":" + setting_key,
         get_setting_label(tab_name, setting_key),
         get_setting_description(tab_name, setting_key),
         find_setting_columns(tab_name, setting_key))
        for setting_key in find_settings_for_tab(tab_name))


def find_cards_for_tab(tab_name: str) -> tuple:
    match is_tab_grouped(tab_name):
        case True:
            return find_group_cards(tab_name)
        case False:
            return find_setting_cards(tab_name)


def find_profile_fields() -> tuple:
    return tuple(
        (widget_key, get_setting_section(tab_name, setting_key), config_key)
        for tab_name in PROFILE_TABS
        for setting_key in find_settings_for_tab(tab_name)
        for widget_key, config_key in find_setting_fields(tab_name, setting_key))


def get_option_label(option_key: str) -> str:
    return OPTIONS_DB[option_key]["label"]


def get_option_description(option_key: str) -> str:
    return OPTIONS_DB[option_key]["description"]


def get_option_options(option_key: str) -> tuple:
    return OPTIONS_DB[option_key]["options"]


def is_option_editable(option_key: str) -> bool:
    return OPTIONS_DB[option_key]["editable"]


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
