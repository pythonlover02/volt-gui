from typing import Final

from database import DEFAULT_VALUE
from database import find_profile_fields
from profiles import process_profile_widgets_block_signals
from profiles import process_profile_widgets_reset
from profiles import process_widget_value_update

PRESET_PLACEHOLDER: Final[str] = "Presets"

PRESET_OVERRIDES: Final[dict] = {
    "Default": {},
    "Quality": {
        "Display:present_mode": "fifo",
        "Display:image_count": "4",
        "Display:color_depth_min": "10bit",
        "Framerate:frame_limit_method": "early",
        "Framerate:frame_pacing": "precise",
        "Textures:filtering": "trilinear",
        "Textures:anisotropy": "16",
        "Textures:lod_bias": "-0.6",
        "Textures:mipmap_mode": "linear",
        "Textures:mip_floor": "0",
        "Rendering:sample_shading": "1.0",
        "Rendering:alpha_to_coverage": "on",
    },
    "Balanced": {
        "Display:present_mode": "mailbox",
        "Framerate:frame_limit_method": "early",
        "Framerate:frame_pacing": "sliced",
        "Textures:filtering": "trilinear",
        "Textures:anisotropy": "8",
        "Textures:mipmap_mode": "linear",
        "Textures:mip_floor": "0",
        "Rendering:sample_shading": "0.6",
    },
    "Performance FPS": {
        "Display:present_mode": "mailbox",
        "Display:image_count_max": "4",
        "Display:color_depth_max": "8bit",
        "Framerate:frame_limit_method": "early",
        "Framerate:frame_pacing": "sleep",
        "Textures:filtering": "bilinear",
        "Textures:mipmap_mode": "linear",
        "Textures:anisotropy": "4",
        "Textures:lod_bias": "0.6",
        "Rendering:sample_shading": "off",
    },
    "Performance Low Latency": {
        "Display:present_mode": "immediate",
        "Display:image_count": "2",
        "Display:image_count_max": "2",
        "Display:color_depth_max": "8bit",
        "Framerate:frame_limit_method": "late",
        "Framerate:frame_pacing": "spin",
        "Textures:filtering": "bilinear",
        "Textures:mipmap_mode": "linear",
        "Textures:anisotropy": "4",
        "Textures:lod_bias": "0.6",
        "Rendering:sample_shading": "off",
    },
    "Potato FPS": {
        "Display:present_mode": "mailbox",
        "Display:image_count_max": "4",
        "Display:color_depth_max": "8bit",
        "Framerate:frame_limit_method": "early",
        "Framerate:frame_pacing": "sleep",
        "Textures:filtering": "bilinear",
        "Textures:mipmap_mode": "nearest",
        "Textures:anisotropy": "off",
        "Textures:lod_bias": "1.0",
        "Textures:mip_floor_min": "2",
        "Rendering:sample_shading": "off",
        "Rendering:alpha_to_coverage": "off",
    },
    "Potato Low Latency": {
        "Display:present_mode": "immediate",
        "Display:image_count": "2",
        "Display:image_count_max": "2",
        "Display:color_depth_max": "8bit",
        "Framerate:frame_limit_method": "late",
        "Framerate:frame_pacing": "sleep",
        "Textures:filtering": "bilinear",
        "Textures:mipmap_mode": "nearest",
        "Textures:anisotropy": "off",
        "Textures:lod_bias": "1.0",
        "Textures:mip_floor_min": "2",
        "Rendering:sample_shading": "off",
        "Rendering:alpha_to_coverage": "off",
    },
}


def get_preset_placeholder_label() -> str:
    return PRESET_PLACEHOLDER


def get_preset_names() -> tuple:
    return tuple(PRESET_OVERRIDES.keys())


def is_valid_preset_name(preset_name: str) -> bool:
    return preset_name in PRESET_OVERRIDES


def build_preset_values(preset_name: str) -> dict:
    return {
        **{widget_key: DEFAULT_VALUE for widget_key, _, _ in find_profile_fields()},
        **PRESET_OVERRIDES.get(preset_name, {})}


def build_preset_combo_items(combo_widget) -> None:
    combo_widget.blockSignals(True)
    combo_widget.clear()
    combo_widget.addItem(get_preset_placeholder_label())
    combo_widget.insertSeparator(combo_widget.count())
    for preset_name in get_preset_names():
        combo_widget.addItem(preset_name)
    combo_widget.blockSignals(False)
    return None


def _preset_dropped(widget_collection: dict, values: dict) -> tuple:
    return tuple(
        widget_key
        for widget_key, setting_value in values.items()
        if widget_collection.get(widget_key) is not None
        and not process_widget_value_update(widget_collection[widget_key], setting_value))


def process_preset_apply(widget_collection: dict, preset_name: str) -> tuple:
    match is_valid_preset_name(preset_name):
        case False:
            return ()
        case True:
            process_profile_widgets_block_signals(widget_collection, True)
            process_profile_widgets_reset(widget_collection)
            dropped = _preset_dropped(widget_collection, build_preset_values(preset_name))
            process_profile_widgets_block_signals(widget_collection, False)
            return dropped
