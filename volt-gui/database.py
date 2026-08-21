from typing import Final

from probe import alpha_options
from probe import aniso_options
from probe import call_read_probe
from probe import depth_options
from probe import frametime_pairs
from probe import gpu_options
from probe import image_count_options
from probe import lod_bias_options
from probe import mip_options
from probe import plain_pairs
from probe import present_options
from probe import shading_options
from probe import space_options
from probe import transfer_options


APP_VERSION: Final[str] = "2.0.1"
APP_AUTHOR: Final[str] = "pythonlover02"
APP_LICENSE: Final[str] = "GPL 3.0 License"
APP_DESCRIPTION: Final[str] = "My AMD Adrenaline / NVIDIA Settings Linux Alternative"

DEFAULT_VALUE: Final[str] = "default"
DEFAULT_PROFILE: Final[str] = "default"

PROFILE_TABS: Final[tuple] = ("GPU", "Display", "Textures", "Rendering", "Framerate")
ALL_TABS: Final[tuple] = ("GPU", "Display", "Textures", "Rendering", "Framerate", "Options", "About")


SETTINGS_DB: Final[dict] = {
    "GPU": {
        "device": {
            "section": "gpu",
            "label": "Physical Device",
            "description": "Which GPU the game sees, listed by name as this machine reports them. The layer hides every other device from enumeration, so a game that takes the first one it is offered gets yours. If your choice matches nothing, the full list comes back and a warning is logged.",
            "options": (DEFAULT_VALUE,),
        },
    },
    "Display": {
        "present_mode": {
            "section": "display",
            "label": "VSync / Present Mode",
            "description": "How finished frames reach the screen. immediate turns vsync off, mailbox is low latency vsync, fifo is classic vsync, fifo_relaxed tears only below refresh. The layer hides every other mode from the list the game is shown, so a game's own vsync menu cannot offer one you ruled out, whatever route it takes to ask. A mode the surface does not support falls back to the game's own choice with a warning.",
            "options": (DEFAULT_VALUE,),
        },
        "image_count": {
            "section": "display",
            "label": "Swapchain Images",
            "description": "How many images the swapchain holds. This is the frames in flight control, and the closest thing here to an anti-lag setting: more images let the game run further ahead of the GPU, which smooths frame delivery and costs input lag, while fewer hold it closer to the display. The list is what this surface allows, and the choice is reported back to the game as well, so a game that picks its count from what the surface offers honours it on its own.",
            "options": (DEFAULT_VALUE,),
        },
        "color_depth": {
            "section": "display",
            "label": "Color Depth",
            "description": "Bits per colour channel, grouped out of the surface formats this surface offers. The layer hides every other format, so a game that takes the first supported one ends up with yours. If nothing matches, the full list comes back and a warning is logged.",
            "options": (DEFAULT_VALUE,),
        },
        "color_space": {
            "section": "display",
            "label": "Color Space",
            "description": "Which color space the game is allowed to see, filtered out of the same surface format list as Color Depth. Everything past srgb_nonlinear comes from a swapchain colorspace extension and only appears when the stack around the game enabled it, through DXVK_HDR, PROTON_ENABLE_HDR or gamescope, so on most setups this card holds one entry. A space volt has no name for still appears and still applies.",
            "options": (DEFAULT_VALUE,),
        },
        "transfer_function": {
            "section": "display",
            "label": "Transfer Function",
            "description": "Whether the game is shown srgb surface formats, plain unorm ones, or float ones, filtered out of the same list again. srgb formats have the encoding curve applied by the display hardware, unorm formats leave it to whatever the game does in its own shaders. Getting this wrong looks washed out or crushed rather than broken, so set it back to default if the image looks wrong. No preset touches it.",
            "options": (DEFAULT_VALUE,),
        },
        "composite_alpha": {
            "section": "display",
            "label": "Composite Alpha",
            "description": "How the compositor treats the alpha channel of the finished image. opaque tells the compositor to skip blending the window altogether, which is the cheapest path on Wayland. The list is what this surface allows, and a value the surface turns down falls back to the game's own choice with a warning.",
            "options": (DEFAULT_VALUE,),
        },
        "clipped": {
            "section": "display",
            "label": "Clipped Presentation",
            "description": "Whether the driver may discard work on pixels another window covers. on is cheaper and is what almost every game asks for already. off keeps those pixels rendered, which only matters if something reads the presented image back. Core Vulkan, so the list never changes.",
            "options": (DEFAULT_VALUE, "off", "on"),
        },
    },
    "Framerate": {
        "frame_limit": {
            "section": "framerate",
            "label": "Frame Limit",
            "description": "Cap the frame rate at present time, shown with the frame budget each rate gives you. This one is volt's own, so the list is fixed rather than read from the device. Past about 500 the interval gets shorter than the kernel wakes reliably, so sleep pacing drifts above the cap and holding the rate needs sliced, precise or spin.",
            "options": (DEFAULT_VALUE, "20", "24", "30", "36", "40", "45", "48", "50", "60", "72", "75", "90", "100", "120", "144", "165", "180", "240", "300", "360", "540", "600", "720", "900", "1000"),
        },
        "frame_limit_method": {
            "section": "framerate",
            "label": "Frame Limit Method",
            "description": "When the limiter waits. early holds the frame back so presents leave on a fixed cadence. late lets the present through right away and waits before handing control back, so the game starts its next frame later and reads input closer to display time. reactive waits where early does, but measures each interval from the frame just shown rather than from a fixed timeline, so a slow frame is never chased with a fast one. late is the equivalent of Reflex and Anti-Lag here, since holding the next frame back is the mechanism those use too. Going further would need to know when the GPU actually finished a frame, which core Vulkan does not report, so there is nothing above late. Only does something when Frame Limit is set.",
            "options": (DEFAULT_VALUE, "early", "late", "reactive"),
        },
        "frame_pacing": {
            "section": "framerate",
            "label": "Frame Pacing",
            "description": "How the limiter waits, from cheapest to tightest. sleep hands the whole wait to the kernel and costs nothing. sliced sleeps in short steps and re-checks the clock, which corrects for the kernel waking late. precise sleeps most of the interval then busy waits half a millisecond. spin busy waits the whole thing, which is the steadiest and the only one that keeps a core awake. Only does something when Frame Limit is set.",
            "options": (DEFAULT_VALUE, "sleep", "sliced", "precise", "spin"),
        },
    },
    "Textures": {
        "filtering": {
            "section": "textures",
            "label": "Texture Filtering",
            "description": "The sampler filter mode. retro gives sharp unfiltered pixels, bilinear smooths within a mip level, trilinear also blends between mip levels. All three are core Vulkan, so the list never changes.",
            "options": (DEFAULT_VALUE, "retro", "bilinear", "trilinear"),
        },
        "mipmap_mode": {
            "section": "textures",
            "label": "Mipmap Mode",
            "description": "How samplers move between mip levels. nearest cuts hard from one mip to the next, linear blends across them. Both are core Vulkan, so the list never changes. Applied after Texture Filtering, so it overrides the mip behaviour that choice implies. Only affects textures that have mips.",
            "options": (DEFAULT_VALUE, "nearest", "linear"),
        },
        "anisotropy": {
            "section": "textures",
            "label": "Anisotropic Filtering",
            "description": "Sharpen textures viewed at steep angles. Higher values look better at a small cost. The list runs in steps of two up to what your GPU reports. This list is read from the device, so it holds nothing but default only where the device itself lacks samplerAnisotropy. volt never enables a feature the game left off: where the game did not ask for it the setting is ignored and the layer logs a line saying so. Nearly every game asks for it.",
            "options": (DEFAULT_VALUE,),
        },
        "lod_bias": {
            "section": "textures",
            "label": "LOD Bias",
            "description": "Shift mipmap selection. Negative values sharpen at the cost of shimmer, positive values blur but render faster. A negative bias is the nearest volt gets to sharpening textures seen at a steep angle. The list runs in steps of 0.2 across the range your GPU reports, and volt clamps what it passes down to that range.",
            "options": (DEFAULT_VALUE,),
        },
        "mip_floor": {
            "section": "textures",
            "label": "Mip Floor",
            "description": "The lowest mip level samplers may use, called minimum LOD in Vulkan. Raising it forces smaller mips everywhere, trading detail for speed. The list runs in steps of two up to the largest image your GPU can address, and a level past the last mip a texture has simply lands on that last mip.",
            "options": (DEFAULT_VALUE,),
        },
        "mip_ceiling": {
            "section": "textures",
            "label": "Mip Ceiling",
            "description": "The highest mip level samplers may use, called maximum LOD in Vulkan. Lowering it keeps distant textures sharper than the game intended. The list matches Mip Floor, and a ceiling that lands below the floor is swapped with it rather than dropped.",
            "options": (DEFAULT_VALUE,),
        },
    },
    "Rendering": {
        "sample_shading": {
            "section": "rendering",
            "label": "Sample Shading",
            "description": "Shade at sample rate inside MSAA render targets to reduce shimmer. The value is the smallest fraction of samples shaded, and off counts as zero. The list runs in steps of 0.2. This list is read from the device, so it holds nothing but default only where the device itself lacks sampleRateShading. volt never enables a feature the game left off: most modern renderers are deferred and never ask, and where the game did not ask the setting is ignored and the layer logs a line saying so. Only does something in a game already using MSAA.",
            "options": (DEFAULT_VALUE,),
        },
        "alpha_to_coverage": {
            "section": "rendering",
            "label": "Alpha To Coverage",
            "description": "Turn fragment alpha into coverage, which softens cutout edges on foliage and fences. Core Vulkan, so the list never changes. Only does something where the game already renders to an MSAA target.",
            "options": (DEFAULT_VALUE, "on", "off"),
        },
    },
}

OPTIONS_DB: Final[dict] = {
    "application_theme": {
        "label": "Application Theme",
        "description": "Color theme for the application. default is cachyos. Takes effect on program restart.",
        "options": (DEFAULT_VALUE, "cachyos", "amd", "intel", "nvidia"),
        "fallback": "cachyos",
    },
    "window_transparency": {
        "label": "Window Transparency",
        "description": "Window background transparency. default is off. Takes effect on program restart.",
        "options": (DEFAULT_VALUE, "on", "off"),
        "fallback": "off",
    },
    "interface_scale_factor": {
        "label": "Interface Scale Factor",
        "description": "UI scaling multiplier, in steps of 0.2. default is 1.0. Takes effect on program restart.",
        "options": (DEFAULT_VALUE, "0.6", "0.8", "1.0", "1.2", "1.4", "1.6", "1.8", "2.0", "2.2", "2.4", "2.6", "2.8", "3.0"),
        "fallback": "1.0",
    },
    "start_window_maximized": {
        "label": "Start Window Maximized",
        "description": "Start the window in maximized state. default is off. Takes effect on program restart.",
        "options": (DEFAULT_VALUE, "on", "off"),
        "fallback": "off",
    },
    "start_window_minimized": {
        "label": "Start Window Minimized",
        "description": "Start the window minimized to tray. default is off. Takes effect on program restart.",
        "options": (DEFAULT_VALUE, "on", "off"),
        "fallback": "off",
    },
    "system_tray_behavior": {
        "label": "System Tray",
        "description": "Show icon in the system tray. default is off. Takes effect on program restart.",
        "options": (DEFAULT_VALUE, "on", "off"),
        "fallback": "off",
    },
    "welcome_message_display": {
        "label": "Welcome Message",
        "description": "Show the welcome message on startup. default is on. Takes effect on program restart.",
        "options": (DEFAULT_VALUE, "on", "off"),
        "fallback": "on",
    },
    "automatic_update_check": {
        "label": "Automatic Update Check",
        "description": "Check for updates on startup. default is off. Takes effect on program restart.",
        "options": (DEFAULT_VALUE, "on", "off"),
        "fallback": "off",
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
    "color_space": space_options,
    "transfer_function": transfer_options,
    "composite_alpha": alpha_options,
    "anisotropy": aniso_options,
    "lod_bias": lod_bias_options,
    "mip_floor": mip_options,
    "mip_ceiling": mip_options,
    "sample_shading": shading_options,
    "frame_limit": lambda _: frametime_pairs(
        SETTINGS_DB["Framerate"]["frame_limit"]["options"][1:]),
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


def get_setting_section(tab_name: str, setting_key: str) -> str:
    return SETTINGS_DB[tab_name][setting_key]["section"]


def build_widget_key(tab_name: str, setting_key: str) -> str:
    return tab_name + ":" + setting_key


def find_cards_for_tab(tab_name: str) -> tuple:
    return tuple(
        (build_widget_key(tab_name, setting_key),
         get_setting_label(tab_name, setting_key),
         get_setting_description(tab_name, setting_key),
         get_setting_options(tab_name, setting_key))
        for setting_key in find_settings_for_tab(tab_name))


def _tab_option_sources(tab_name: str, data: dict) -> tuple:
    return tuple(
        (build_widget_key(tab_name, setting_key),
         find_setting_options(tab_name, setting_key, data))
        for setting_key in find_settings_for_tab(tab_name))


def find_option_sources() -> tuple:
    data = call_read_probe()
    return tuple(
        entry
        for tab_name in PROFILE_TABS
        for entry in _tab_option_sources(tab_name, data))


def find_profile_fields() -> tuple:
    return tuple(
        (build_widget_key(tab_name, setting_key),
         get_setting_section(tab_name, setting_key),
         setting_key)
        for tab_name in PROFILE_TABS
        for setting_key in find_settings_for_tab(tab_name))


def get_option_label(option_key: str) -> str:
    return OPTIONS_DB[option_key]["label"]


def get_option_description(option_key: str) -> str:
    return OPTIONS_DB[option_key]["description"]


def get_option_options(option_key: str) -> tuple:
    return plain_pairs(OPTIONS_DB[option_key]["options"])


def get_option_default_value(option_key: str) -> str:
    return OPTIONS_DB[option_key]["options"][0]


def get_option_fallback(option_key: str) -> str:
    return OPTIONS_DB[option_key]["fallback"]


def _option_is_unset(raw_value: str) -> bool:
    return raw_value in ("", DEFAULT_VALUE)


def resolve_option_value(option_key: str, raw_value: str) -> str:
    match _option_is_unset(raw_value):
        case True:
            return get_option_fallback(option_key)
        case False:
            return raw_value


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
