from typing import Final

from database import DEFAULT_VALUE
from database import PROFILE_TABS
from database import find_settings_for_tab
from profiles import process_profile_widgets_block_signals
from profiles import process_profile_widgets_reset
from profiles import process_widget_value_update

PRESET_PLACEHOLDER: Final[str] = "Presets"

PRESET_OVERRIDES: Final[dict] = {
    "Default": {},
    "Quality": {
        "Display:present_mode": "fifo",
        "Display:image_count": "3",
        "Textures:filtering": "trilinear",
        "Textures:anisotropy": "16",
        "Textures:lod_bias": "-0.5",
        "Advanced:sample_shading": "1.0",
    },
    "Balanced": {
        "Display:present_mode": "mailbox",
        "Textures:filtering": "trilinear",
        "Textures:anisotropy": "8",
        "Advanced:sample_shading": "0.5",
    },
    "Performance FPS": {
        "Display:present_mode": "mailbox",
        "Display:image_count_max": "3",
        "Textures:anisotropy": "4",
        "Textures:lod_bias": "0.5",
        "Advanced:sample_shading": "off",
    },
    "Performance Low Latency": {
        "Display:present_mode": "immediate",
        "Display:image_count": "2",
        "Display:image_count_max": "2",
        "Textures:anisotropy": "4",
        "Textures:lod_bias": "0.5",
        "Advanced:sample_shading": "off",
    },
    "Potato FPS": {
        "Display:present_mode": "mailbox",
        "Display:image_count_max": "3",
        "Textures:filtering": "bilinear",
        "Textures:anisotropy": "off",
        "Textures:lod_bias": "1.0",
        "Advanced:sample_shading": "off",
    },
    "Potato Low Latency": {
        "Display:present_mode": "immediate",
        "Display:image_count": "2",
        "Display:image_count_max": "2",
        "Textures:filtering": "bilinear",
        "Textures:anisotropy": "off",
        "Textures:lod_bias": "1.0",
        "Advanced:sample_shading": "off",
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
        **{
            tab_name + ":" + setting_key: DEFAULT_VALUE
            for tab_name in PROFILE_TABS
            for setting_key in find_settings_for_tab(tab_name)},
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


def process_preset_apply(widget_collection: dict, preset_name: str) -> bool:
    match is_valid_preset_name(preset_name):
        case False:
            return False
        case True:
            process_profile_widgets_block_signals(widget_collection, True)
            process_profile_widgets_reset(widget_collection)
            for widget_key, setting_value in build_preset_values(preset_name).items():
                match widget_collection.get(widget_key):
                    case None:
                        continue
                    case widget:
                        process_widget_value_update(widget, setting_value)
            process_profile_widgets_block_signals(widget_collection, False)
            return True
