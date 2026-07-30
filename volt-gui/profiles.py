import os

from functools import reduce
from pathlib import Path
from typing import Final
from typing import Optional

from database import DEFAULT_PROFILE
from database import DEFAULT_VALUE
from database import PROFILE_TABS
from database import find_settings_for_tab
from database import get_setting_section

SECTION_ORDER: Final[tuple] = ("display", "textures", "advanced")
OPTIONS_FILE: Final[str] = "options.toml"
PROFILE_SUFFIX: Final[str] = ".toml"
PAIR_SEP: Final[str] = " = "


def build_config_dir() -> Path:
    return Path(os.path.expanduser("~/.config/volt-gui"))


def build_profile_path(profile_name: str) -> Path:
    return build_config_dir() / (profile_name + PROFILE_SUFFIX)


def build_options_path() -> Path:
    return build_config_dir() / OPTIONS_FILE


def is_profile_file(file_path: Path) -> bool:
    match file_path.name == OPTIONS_FILE:
        case True:
            return False
        case False:
            return file_path.stem.lower() != DEFAULT_PROFILE


def find_all_profiles() -> tuple:
    match build_config_dir().exists():
        case False:
            return (DEFAULT_PROFILE,)
        case True:
            return (DEFAULT_PROFILE,) + tuple(sorted(
                path.stem for path in build_config_dir().glob("*" + PROFILE_SUFFIX)
                if is_profile_file(path)))


def _quoted(value: str) -> str:
    return '"' + value + '"'


def _section_lines(section: str, pairs: tuple) -> tuple:
    return ("[" + section + "]",) + tuple(
        key + PAIR_SEP + _quoted(value) for key, value in pairs) + ("",)


def _pairs_for_section(values: dict, section: str) -> tuple:
    return tuple(
        (setting_key, values.get(tab_name + ":" + setting_key, DEFAULT_VALUE))
        for tab_name in PROFILE_TABS
        for setting_key in find_settings_for_tab(tab_name)
        if get_setting_section(tab_name, setting_key) == section)


def serialize_profile(values: dict) -> str:
    return "\n".join(
        line
        for section in SECTION_ORDER
        for line in _section_lines(section, _pairs_for_section(values, section)))


def _classify_line(line: str) -> tuple:
    match (line.startswith("["), PAIR_SEP.strip() in line, line.startswith("#"), line):
        case (_, _, True, _) | (_, _, _, ""):
            return ("skip",)
        case (True, _, _, _):
            return ("section", line.strip("[]").strip())
        case (False, True, _, _):
            return ("pair", line.split("=", 1)[0].strip(), line.split("=", 1)[1].strip().strip('"'))
        case _:
            return ("skip",)


def _fold_line(state: tuple, line: str) -> tuple:
    match _classify_line(line.strip()):
        case ("section", name):
            return (name, state[1])
        case ("pair", key, value):
            return (state[0], state[1] + ((state[0] + "." + key, value),))
        case _:
            return state


def parse_profile_text(text: str) -> dict:
    return dict(reduce(_fold_line, text.splitlines(), ("", ()))[1])


def _widget_key_for(section_key: str) -> Optional[str]:
    return next(
        (tab_name + ":" + setting_key
         for tab_name in PROFILE_TABS
         for setting_key in find_settings_for_tab(tab_name)
         if get_setting_section(tab_name, setting_key) + "." + setting_key == section_key),
        None)


def process_widget_value_update(widget, display_value: str) -> None:
    widget.setCurrentText(display_value)
    return None


def process_profile_widgets_block_signals(widget_collection: dict, should_block: bool) -> None:
    for tab_name in PROFILE_TABS:
        for setting_key in find_settings_for_tab(tab_name):
            match widget_collection.get(tab_name + ":" + setting_key):
                case None:
                    continue
                case widget:
                    widget.blockSignals(should_block)
    return None


def process_profile_widgets_reset(widget_collection: dict) -> None:
    for tab_name in PROFILE_TABS:
        for setting_key in find_settings_for_tab(tab_name):
            match widget_collection.get(tab_name + ":" + setting_key):
                case None:
                    continue
                case widget:
                    widget.setCurrentText(DEFAULT_VALUE)
    return None


def collect_widget_values(widget_collection: dict) -> dict:
    return {
        tab_name + ":" + setting_key: widget_collection[tab_name + ":" + setting_key].currentText().strip()
        for tab_name in PROFILE_TABS
        for setting_key in find_settings_for_tab(tab_name)
        if widget_collection.get(tab_name + ":" + setting_key) is not None}


def call_read_profile(profile_name: str) -> dict:
    match build_profile_path(profile_name).exists():
        case False:
            return {}
        case True:
            return parse_profile_text(build_profile_path(profile_name).read_text(encoding="utf-8"))


def _apply_parsed(widget_collection: dict, parsed: dict) -> None:
    for section_key, value in parsed.items():
        match _widget_key_for(section_key):
            case None:
                continue
            case widget_key:
                match widget_collection.get(widget_key):
                    case None:
                        continue
                    case widget:
                        process_widget_value_update(widget, value)
    return None


def process_profile_widget_load(widget_collection: dict, profile_name: str) -> bool:
    process_profile_widgets_block_signals(widget_collection, True)
    process_profile_widgets_reset(widget_collection)
    _apply_parsed(widget_collection, call_read_profile(profile_name))
    process_profile_widgets_block_signals(widget_collection, False)
    return True


def call_write_profile(values: dict, profile_name: str) -> None:
    build_config_dir().mkdir(parents=True, exist_ok=True)
    build_profile_path(profile_name).write_text(serialize_profile(values), encoding="utf-8")
    return None


def process_profile_save(widget_collection: dict, profile_name: str) -> None:
    call_write_profile(collect_widget_values(widget_collection), profile_name)
    return None


def process_profile_delete(profile_name: str) -> bool:
    match (profile_name == DEFAULT_PROFILE, build_profile_path(profile_name).exists()):
        case (True, _) | (_, False):
            return False
        case (False, True):
            build_profile_path(profile_name).unlink()
            return True
