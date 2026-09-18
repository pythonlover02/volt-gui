from functools import partial
from typing import Any
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
        "Framerate:frame_limit_method": "early",
        "Framerate:frame_pacing": "precise",
        "Textures:mag_filter": "linear",
        "Textures:min_filter": "linear",
        "Textures:mipmap_mode": "linear",
        "Textures:anisotropy": "16",
        "Textures:lod_bias": "-0.6",
        "Textures:mip_floor": "0",
    },
    "Balanced": {
        "Display:present_mode": "mailbox",
        "Framerate:frame_limit_method": "early",
        "Framerate:frame_pacing": "sliced",
        "Textures:mag_filter": "linear",
        "Textures:min_filter": "linear",
        "Textures:mipmap_mode": "linear",
        "Textures:anisotropy": "8",
        "Textures:mip_floor": "0",
    },
    "Performance FPS": {
        "Display:present_mode": "mailbox",
        "Display:image_count": "4",
        "Framerate:frame_limit_method": "early",
        "Framerate:frame_pacing": "sleep",
        "Textures:mag_filter": "linear",
        "Textures:min_filter": "linear",
        "Textures:mipmap_mode": "nearest",
        "Textures:anisotropy": "4",
        "Textures:lod_bias": "0.6",
    },
    "Performance Low Latency": {
        "Display:present_mode": "immediate",
        "Display:image_count": "2",
        "Framerate:frame_limit_method": "late",
        "Framerate:frame_pacing": "spin",
        "Textures:mag_filter": "linear",
        "Textures:min_filter": "linear",
        "Textures:mipmap_mode": "nearest",
        "Textures:anisotropy": "4",
        "Textures:lod_bias": "0.6",
    },
    "Potato FPS": {
        "Display:present_mode": "mailbox",
        "Display:image_count": "4",
        "Framerate:frame_limit_method": "early",
        "Framerate:frame_pacing": "sleep",
        "Textures:mag_filter": "linear",
        "Textures:min_filter": "linear",
        "Textures:mipmap_mode": "nearest",
        "Textures:anisotropy": "off",
        "Textures:lod_bias": "1.0",
        "Textures:mip_floor": "2",
        "Rendering:alpha_to_coverage": "off",
    },
    "Potato Low Latency": {
        "Display:present_mode": "immediate",
        "Display:image_count": "2",
        "Framerate:frame_limit_method": "late",
        "Framerate:frame_pacing": "sleep",
        "Textures:mag_filter": "linear",
        "Textures:min_filter": "linear",
        "Textures:mipmap_mode": "nearest",
        "Textures:anisotropy": "off",
        "Textures:lod_bias": "1.0",
        "Textures:mip_floor": "2",
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


def build_preset_combo_items(combo_widget: Any) -> None:
    combo_widget.blockSignals(True)
    combo_widget.clear()
    combo_widget.addItem(get_preset_placeholder_label())
    combo_widget.insertSeparator(combo_widget.count())
    for preset_name in get_preset_names():
        combo_widget.addItem(preset_name)
    combo_widget.blockSignals(False)
    return None


def _widget_dropped(widget_collection: dict, item: tuple) -> bool:
    widget_key, setting_value = item
    match widget_collection.get(widget_key):
        case None:
            return False
        case widget:
            return not process_widget_value_update(widget, setting_value)


def _preset_dropped(widget_collection: dict, values: dict) -> tuple:
    dropped = filter(partial(_widget_dropped, widget_collection), values.items())
    return tuple(widget_key for widget_key, _ in dropped)


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
