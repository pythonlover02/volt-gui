import os, configparser

from pathlib import Path

from PySide6.QtWidgets import QLineEdit, QComboBox

from database import *


def get_profile_name_from_path(file_path) -> str:
    return file_path.stem.replace("config-", "")


def is_default_profile_path(file_path) -> bool:
    return get_profile_name_from_path(file_path).lower() == "default"


def find_all_profiles() -> tuple:
    if not Path(os.path.expanduser("~/.config/volt-gui")).exists(): return ("Default",)
    return ("Default",) + tuple(get_profile_name_from_path(profile_path) for profile_path in Path(os.path.expanduser("~/.config/volt-gui")).glob("config-*.ini") if not is_default_profile_path(profile_path))


def build_configuration_path(profile_name: str):
    Path(os.path.expanduser("~/.config/volt-gui")).mkdir(parents=True, exist_ok=True)
    if profile_name == "Default":
        return Path(os.path.expanduser("~/.config/volt-gui")) / "config-Default.ini"
    return Path(os.path.expanduser("~/.config/volt-gui")) / ("config-" + profile_name + ".ini")


def build_options_path():
    Path(os.path.expanduser("~/.config/volt-gui")).mkdir(parents=True, exist_ok=True)
    return Path(os.path.expanduser("~/.config/volt-gui")) / "options.ini"


def process_widget_value_update(widget, display_value: str) -> None:
    if isinstance(widget, QLineEdit): widget.setText(display_value); return None
    if hasattr(widget, "setCurrentText"): widget.setCurrentText(display_value); return None
    return None


def process_profile_widgets_block_signals(widget_collection: dict, should_block: bool) -> None:
    for tab_name in get_tabs_with_profile_support():
        for setting_key in find_settings_for_tab(tab_name):
            if widget_collection.get(tab_name + ":" + setting_key) is None: continue
            widget_collection[tab_name + ":" + setting_key].blockSignals(should_block)
    return None


def process_profile_widgets_reset(widget_collection: dict) -> None:
    for tab_name in get_tabs_with_profile_support():
        for setting_key in find_settings_for_tab(tab_name):
            widget = widget_collection.get(tab_name + ":" + setting_key)
            if widget is None: continue
            if isinstance(widget, QLineEdit): widget.setText(""); continue
            if hasattr(widget, "setCurrentText"): widget.setCurrentText(""); continue
    return None


def process_profile_widget_load(widget_collection: dict, profile_name: str) -> bool:
    process_profile_widgets_block_signals(widget_collection, True)
    process_profile_widgets_reset(widget_collection)
    if build_configuration_path(profile_name).exists():
        parser_instance = configparser.ConfigParser(interpolation=None)
        parser_instance.read(build_configuration_path(profile_name))
        for section_name in parser_instance.sections():
            for setting_key, setting_value in parser_instance.items(section_name):
                if widget_collection.get(section_name + ":" + setting_key) is not None:
                    process_widget_value_update(widget_collection[section_name + ":" + setting_key], setting_value)
    process_profile_widgets_block_signals(widget_collection, False)
    return True


def process_profile_save(widget_collection: dict, profile_name: str) -> None:
    parser_instance = configparser.ConfigParser(interpolation=None)
    for tab_name in get_tabs_with_profile_support():
        if len(find_settings_for_tab(tab_name)) == 0: continue
        if tab_name not in parser_instance: parser_instance[tab_name] = {}
        for setting_key in find_settings_for_tab(tab_name):
            if widget_collection.get(tab_name + ":" + setting_key) is None: continue
            if not widget_collection[tab_name + ":" + setting_key].isEnabled(): continue
            value = parse_widget_value(widget_collection[tab_name + ":" + setting_key])
            if value is None: continue
            parser_instance[tab_name][setting_key] = value
    with open(build_configuration_path(profile_name), "w") as file_handle:
        parser_instance.write(file_handle)
    return None


def process_profile_delete(profile_name: str) -> bool:
    if profile_name == "Default": return False
    if not build_configuration_path(profile_name).exists(): return False
    build_configuration_path(profile_name).unlink()
    return True
