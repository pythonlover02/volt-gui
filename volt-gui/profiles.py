import os

from functools import reduce
from pathlib import Path
from typing import Final
from typing import Optional

from database import DEFAULT_PROFILE
from database import DEFAULT_VALUE
from database import find_option_sources
from database import find_profile_fields

SECTION_ORDER: Final[tuple] = ("display", "framerate", "textures", "rendering", "gpu")
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
        (config_key, values.get(widget_key, DEFAULT_VALUE))
        for widget_key, field_section, config_key in find_profile_fields()
        if field_section == section)


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
        (widget_key
         for widget_key, section, config_key in find_profile_fields()
         if section + "." + config_key == section_key),
        None)


def widget_value(widget) -> str:
    match widget.currentData():
        case None:
            return DEFAULT_VALUE
        case data:
            return data


def process_widget_value_update(widget, display_value: str) -> bool:
    match widget.findData(display_value):
        case -1:
            widget.setCurrentIndex(0)
            return False
        case index:
            widget.setCurrentIndex(index)
            return True


def process_widget_options_rebuild(widget, options: tuple) -> None:
    keep = widget_value(widget)
    widget.clear()
    for value, label in options:
        widget.addItem(label, value)
    process_widget_value_update(widget, keep)
    return None


def process_profile_widgets_block_signals(widget_collection: dict, should_block: bool) -> None:
    for widget_key, _, _ in find_profile_fields():
        match widget_collection.get(widget_key):
            case None:
                continue
            case widget:
                widget.blockSignals(should_block)
    return None


def process_profile_widgets_reset(widget_collection: dict) -> None:
    for widget_key, _, _ in find_profile_fields():
        match widget_collection.get(widget_key):
            case None:
                continue
            case widget:
                widget.setCurrentIndex(0)
    return None


def process_profile_options_rebuild(widget_collection: dict) -> None:
    for widget_key, options in find_option_sources():
        match widget_collection.get(widget_key):
            case None:
                continue
            case widget:
                process_widget_options_rebuild(widget, options)
    return None


def collect_widget_values(widget_collection: dict) -> dict:
    return {
        widget_key: widget_value(widget_collection[widget_key])
        for widget_key, _, _ in find_profile_fields()
        if widget_collection.get(widget_key) is not None}


def call_read_profile(profile_name: str) -> dict:
    match build_profile_path(profile_name).exists():
        case False:
            return {}
        case True:
            return parse_profile_text(build_profile_path(profile_name).read_text(encoding="utf-8"))


def _apply_to_widget(widget_collection: dict, widget_key: str, value: str) -> bool:
    match widget_collection.get(widget_key):
        case None:
            return True
        case widget:
            return process_widget_value_update(widget, value)


def _apply_one(widget_collection: dict, section_key: str, value: str) -> bool:
    match _widget_key_for(section_key):
        case None:
            return True
        case widget_key:
            return _apply_to_widget(widget_collection, widget_key, value)


def _kept(value: str) -> bool:
    return value == DEFAULT_VALUE


def _apply_parsed(widget_collection: dict, parsed: dict) -> tuple:
    return tuple(
        section_key
        for section_key, value in parsed.items()
        if not _kept(value) and not _apply_one(widget_collection, section_key, value))


def process_profile_widget_load(widget_collection: dict, profile_name: str) -> tuple:
    process_profile_widgets_block_signals(widget_collection, True)
    process_profile_widgets_reset(widget_collection)
    dropped = _apply_parsed(widget_collection, call_read_profile(profile_name))
    process_profile_widgets_block_signals(widget_collection, False)
    return dropped


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
