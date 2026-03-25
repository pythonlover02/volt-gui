import os, configparser

from pathlib import Path

from PySide6.QtWidgets import QComboBox

from database import *


def get_profile_name_from_path(file_path):
    return file_path.stem.replace("config-", "")


def is_default_profile_path(file_path):
    return get_profile_name_from_path(file_path).lower() == "default"


def find_all_profiles():
    if not Path(os.path.expanduser("~/.config/volt-gui")).exists(): return ("Default",)
    result = ["Default"]
    for profile_path in Path(os.path.expanduser("~/.config/volt-gui")).glob("config-*.ini"):
        if is_default_profile_path(profile_path): continue
        result.append(get_profile_name_from_path(profile_path))
    return tuple(result)


def build_configuration_path(profile_name):
    Path(os.path.expanduser("~/.config/volt-gui")).mkdir(parents=True, exist_ok=True)
    if profile_name == "Default": return Path(os.path.expanduser("~/.config/volt-gui")) / "config-Default.ini"
    return Path(os.path.expanduser("~/.config/volt-gui")) / ("config-" + profile_name + ".ini")


def build_options_path():
    Path(os.path.expanduser("~/.config/volt-gui")).mkdir(parents=True, exist_ok=True)
    return Path(os.path.expanduser("~/.config/volt-gui")) / "options.ini"


def process_widget_value_update(combo_widget, display_value):
    if not isinstance(combo_widget, QComboBox): return None
    if combo_widget.findText(display_value) >= 0:
        combo_widget.setCurrentIndex(combo_widget.findText(display_value))
        combo_widget.custom_value = None
        return None
    combo_widget.addItem(display_value)
    combo_widget.setCurrentIndex(combo_widget.count() - 1)
    combo_widget.custom_value = display_value
    return None


def process_widget_custom_value_cleanup(combo_widget):
    if getattr(combo_widget, "custom_value", None) is None: return None
    found_index = combo_widget.findText(combo_widget.custom_value)
    if found_index >= 0: combo_widget.removeItem(found_index)
    combo_widget.custom_value = None
    return None


def process_profile_widgets_block_signals(widget_collection, should_block):
    for tab_name in get_tabs_with_profile_support():
        for setting_key in find_settings_for_tab(tab_name):
            if widget_collection.get(tab_name + ":" + setting_key) is None: continue
            widget_collection[tab_name + ":" + setting_key].blockSignals(should_block)
    return None


def process_profile_widgets_reset(widget_collection):
    for tab_name in get_tabs_with_profile_support():
        for setting_key in find_settings_for_tab(tab_name):
            if widget_collection.get(tab_name + ":" + setting_key) is None: continue
            process_widget_custom_value_cleanup(widget_collection[tab_name + ":" + setting_key])
            widget_collection[tab_name + ":" + setting_key].setCurrentText("skip")
    return None


def process_profile_widget_load(widget_collection, profile_name):
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


def process_profile_save(widget_collection, profile_name):
    parser_instance = configparser.ConfigParser(interpolation=None)
    for tab_name in get_tabs_with_profile_support():
        if len(find_settings_for_tab(tab_name)) == 0: continue
        if tab_name not in parser_instance: parser_instance[tab_name] = {}
        for setting_key in find_settings_for_tab(tab_name):
            if widget_collection.get(tab_name + ":" + setting_key) is None: continue
            if not widget_collection[tab_name + ":" + setting_key].isEnabled(): continue
            if parse_widget_value(widget_collection[tab_name + ":" + setting_key]) is None: continue
            parser_instance[tab_name][setting_key] = parse_widget_value(widget_collection[tab_name + ":" + setting_key])
    with open(build_configuration_path(profile_name), "w") as file_handle:
        parser_instance.write(file_handle)
    return None


def process_profile_delete(profile_name):
    if profile_name == "Default": return False
    if not build_configuration_path(profile_name).exists(): return False
    build_configuration_path(profile_name).unlink()
    return True
