from typing import Final

from probe import aniso_options
from probe import call_read_probe
from probe import depth_options
from probe import gpu_options
from probe import image_count_options
from probe import lod_bias_options
from probe import mip_options
from probe import plain_pairs
from probe import present_options
from probe import shading_options


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


SETTINGS_DB: Final[dict] = {
    "GPU": {
        "device": {
            "section": "gpu",
            "label": "Physical Device",
            "description": "Which GPU the game sees. The list is what this machine reports, in the order the driver gives them. Force hides every other device, and the bounds keep a range. If nothing matches, the full list comes back and a warning is logged.",
            "options": (DEFAULT_VALUE,),
            "editable": False,
            "bounded": True,
        },
    },
    "Display": {
        "present_mode": {
            "section": "display",
            "label": "VSync / Present Mode",
            "description": "How finished frames reach the screen. The list is what this surface supports, ordered from most latency to least, so a Maximum of mailbox keeps a game from tearing and a Minimum of mailbox keeps it off classic vsync. fifo is classic vsync, fifo_relaxed tears only below refresh, mailbox is low latency vsync, immediate turns vsync off. A mode the surface turns down falls back to the game's own choice with a warning.",
            "options": (DEFAULT_VALUE,),
            "editable": False,
            "bounded": True,
        },
        "image_count": {
            "section": "display",
            "label": "Swapchain Images",
            "description": "How many images the swapchain holds. Fewer images lower display latency, more images smooth frame delivery. The list runs across what this surface allows, in steps of two.",
            "options": (DEFAULT_VALUE,),
            "editable": False,
            "bounded": True,
        },
        "color_depth": {
            "section": "display",
            "label": "Color Depth",
            "description": "Which surface formats the game is allowed to see, grouped by bits per colour channel. The list is the depths this surface actually offers. The layer hides the ones you did not pick, so a game that takes the first supported format ends up with yours. If nothing matches, the full list comes back and a warning is logged.",
            "options": (DEFAULT_VALUE,),
            "editable": False,
            "bounded": True,
        },
    },
    "Framerate": {
        "frame_limit": {
            "section": "framerate",
            "label": "Frame Limit",
            "description": "Cap the frame rate at present time. This one is volt's own, so the list is fixed rather than read from the device.",
            "options": (DEFAULT_VALUE, "20", "24", "30", "36", "40", "45", "48", "50", "60", "72", "75", "90", "100", "120", "144", "165", "180", "240", "300", "360", "540"),
            "editable": False,
            "bounded": False,
        },
        "frame_limit_method": {
            "section": "framerate",
            "label": "Frame Limit Method",
            "description": "Method sets when the limiter waits. early holds the frame back so presents leave on a fixed cadence. late lets the present through right away and waits before handing control back, so the game starts its next frame later and reads input closer to display time.",
            "options": (DEFAULT_VALUE, "early", "late"),
            "editable": False,
            "bounded": False,
        },
        "frame_pacing": {
            "section": "framerate",
            "label": "Frame Pacing",
            "description": "Pacing sets how the limiter waits. sleep is easier on the CPU. precise sleeps most of the interval then busy waits the rest, for tighter frametimes at a small CPU cost. Method and Pacing only do something when Limit is set. These three have no bounds, because a game never tells Vulkan what frame rate it wants.",
            "options": (DEFAULT_VALUE, "sleep", "precise"),
            "editable": False,
            "bounded": False,
        },
    },
    "Textures": {
        "filtering": {
            "section": "textures",
            "label": "Texture Filtering",
            "description": "The sampler filter mode. retro gives sharp unfiltered pixels, bilinear smooths within a mip level, trilinear also blends between mip levels. A sampler that matches none of the three exactly counts as the closest one below it.",
            "options": (DEFAULT_VALUE, "retro", "bilinear", "trilinear"),
            "editable": False,
            "bounded": True,
        },
        "mipmap_mode": {
            "section": "textures",
            "label": "Mipmap Mode",
            "description": "How samplers move between mip levels. nearest cuts hard from one mip to the next, linear blends across them. With only two values there is nothing in between, so a Minimum of linear or a Maximum of nearest does the same job as Force. Applied after Texture Filtering, so it overrides the mip behaviour that choice implies. Only affects textures that have mips.",
            "options": (DEFAULT_VALUE, "nearest", "linear"),
            "editable": False,
            "bounded": True,
        },
        "anisotropy": {
            "section": "textures",
            "label": "Anisotropic Filtering",
            "description": "Sharpen textures viewed at steep angles. Higher values look better at a small cost. off counts as the lowest setting, so a Minimum of 4 raises a game that asked for less and leaves a game that asked for more alone. The list runs in steps of two up to what your GPU reports, and holds only default on a device without the feature.",
            "options": (DEFAULT_VALUE,),
            "editable": False,
            "bounded": True,
        },
        "lod_bias": {
            "section": "textures",
            "label": "LOD Bias",
            "description": "Shift mipmap selection. Negative values sharpen at the cost of shimmer, positive values blur but render faster. The list runs in steps of 0.2 across the range your GPU reports.",
            "options": (DEFAULT_VALUE,),
            "editable": False,
            "bounded": True,
        },
        "mip_floor": {
            "section": "textures",
            "label": "Mip Floor",
            "description": "The lowest mip level samplers may use, called minimum LOD in Vulkan. Raising it forces smaller mips everywhere, trading detail for speed. The list runs in steps of two up to the largest image your GPU can address, and a level past the last mip a texture has simply lands on that last mip.",
            "options": (DEFAULT_VALUE,),
            "editable": False,
            "bounded": True,
        },
        "mip_ceiling": {
            "section": "textures",
            "label": "Mip Ceiling",
            "description": "The highest mip level samplers may use, called maximum LOD in Vulkan. Lowering it keeps distant textures sharper than the game intended. The list matches Mip Floor, and a ceiling that lands below the floor is swapped with it rather than dropped.",
            "options": (DEFAULT_VALUE,),
            "editable": False,
            "bounded": True,
        },
    },
    "Rendering": {
        "sample_shading": {
            "section": "rendering",
            "label": "Sample Shading",
            "description": "Shade at sample rate inside MSAA render targets to reduce shimmer. The value is the smallest fraction of samples shaded, and off counts as zero. The list runs in steps of 0.2, and holds only default on a device without the sampleRateShading feature. Only does something in a game already using MSAA.",
            "options": (DEFAULT_VALUE,),
            "editable": False,
            "bounded": True,
        },
        "alpha_to_coverage": {
            "section": "rendering",
            "label": "Alpha To Coverage",
            "description": "Turn fragment alpha into coverage, which softens cutout edges on foliage and fences. With only two values there is nothing in between, so a Minimum of on or a Maximum of off does the same job as Force. Only does something where the game already renders to an MSAA target.",
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
        "description": "UI scaling multiplier. A hand written value outside 0.5 to 3.0 falls back to 1.0. Takes effect on program restart.",
        "options": ("1.0", "0.5", "0.75", "1.25", "1.5", "1.75", "2.0", "2.5", "3.0"),
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


OPTION_BUILDERS: Final[dict] = {
    "device": gpu_options,
    "present_mode": present_options,
    "image_count": image_count_options,
    "color_depth": depth_options,
    "anisotropy": aniso_options,
    "lod_bias": lod_bias_options,
    "mip_floor": mip_options,
    "mip_ceiling": mip_options,
    "sample_shading": shading_options,
}


def _static_options(tab_name: str, setting_key: str) -> tuple:
    return plain_pairs(SETTINGS_DB[tab_name][setting_key]["options"])


def find_setting_options(tab_name: str, setting_key: str, data: dict) -> tuple:
    match OPTION_BUILDERS.get(setting_key):
        case None:
            return _static_options(tab_name, setting_key)
        case builder:
            return ((DEFAULT_VALUE, DEFAULT_VALUE),) + builder(data)


def get_setting_options(tab_name: str, setting_key: str) -> tuple:
    return find_setting_options(tab_name, setting_key, call_read_probe())


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


def _tab_option_sources(tab_name: str, data: dict) -> tuple:
    return tuple(
        (widget_key, find_setting_options(tab_name, setting_key, data))
        for setting_key in find_settings_for_tab(tab_name)
        for widget_key in find_setting_widget_keys(tab_name, setting_key))


def find_option_sources() -> tuple:
    data = call_read_probe()
    return tuple(
        entry
        for tab_name in PROFILE_TABS
        for entry in _tab_option_sources(tab_name, data))


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
    return plain_pairs(OPTIONS_DB[option_key]["options"])


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
