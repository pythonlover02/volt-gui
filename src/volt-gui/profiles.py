import os

from functools import partial
from functools import reduce
from pathlib import Path
from typing import Any
from typing import Final
from typing import Optional

from database import DEFAULT_PROFILE
from database import DEFAULT_VALUE
from database import call_option_sources
from database import find_profile_fields
from probe import PROBE_FILE

SECTION_ORDER: Final[tuple] = ("gpu", "display", "textures", "rendering", "framerate")
OPTIONS_FILE: Final[str] = "options.toml"
PROFILE_SUFFIX: Final[str] = ".toml"
PAIR_SEP: Final[str] = " = "
RESERVED_STEMS: Final[tuple] = (
    DEFAULT_PROFILE,
    OPTIONS_FILE.removesuffix(PROFILE_SUFFIX),
    PROBE_FILE.removesuffix(PROFILE_SUFFIX))


def build_config_dir() -> Path:
    return Path(os.path.expanduser("~/.config/volt-gui"))


def build_profile_path(profile_name: str) -> Path:
    return build_config_dir() / (profile_name + PROFILE_SUFFIX)


def build_options_path() -> Path:
    return build_config_dir() / OPTIONS_FILE


def is_reserved_profile_name(profile_name: str) -> bool:
    return profile_name.strip().lower() in RESERVED_STEMS


def is_profile_file(file_path: Path) -> bool:
    return not is_reserved_profile_name(file_path.stem)


def call_all_profiles() -> tuple:
    match build_config_dir().exists():
        case False:
            return (DEFAULT_PROFILE,)
        case True:
            found = filter(is_profile_file, build_config_dir().glob("*" + PROFILE_SUFFIX))
            return (DEFAULT_PROFILE,) + tuple(sorted(path.stem for path in found))


def _quoted(value: str) -> str:
    return '"' + value + '"'


def _section_lines(section: str, pairs: tuple) -> tuple:
    return ("[" + section + "]",) + tuple(
        key + PAIR_SEP + _quoted(value) for key, value in pairs) + ("",)


def _in_section(section: str, field: tuple) -> bool:
    return field[1] == section


def _pairs_for_section(values: dict, section: str) -> tuple:
    kept = filter(partial(_in_section, section), find_profile_fields())
    return tuple(
        (config_key, values.get(widget_key, DEFAULT_VALUE))
        for widget_key, _, config_key in kept)


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


def _named(section_key: str, field: tuple) -> bool:
    return field[1] + "." + field[2] == section_key


def _widget_key_for(section_key: str) -> Optional[str]:
    named = filter(partial(_named, section_key), find_profile_fields())
    return next((widget_key for widget_key, _, _ in named), None)


def widget_value(widget: Any) -> str:
    match widget.currentData():
        case None:
            return DEFAULT_VALUE
        case data:
            return data


def process_widget_value_update(widget: Any, display_value: str) -> bool:
    match widget.findData(display_value):
        case -1:
            widget.setCurrentIndex(0)
            return False
        case index:
            widget.setCurrentIndex(index)
            return True


def process_widget_options_rebuild(widget: Any, options: tuple) -> None:
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
    for widget_key, options in call_option_sources():
        match widget_collection.get(widget_key):
            case None:
                continue
            case widget:
                process_widget_options_rebuild(widget, options)
    return None


def _widget_held(widget_collection: dict, field: tuple) -> bool:
    return widget_collection.get(field[0]) is not None


def collect_widget_values(widget_collection: dict) -> dict:
    return {
        widget_key: widget_value(widget_collection[widget_key])
        for widget_key, _, _ in filter(
            partial(_widget_held, widget_collection), find_profile_fields())}


def call_read_profile(profile_name: str) -> dict:
    match build_profile_path(profile_name).exists():
        case False:
            return {}
        case True:
            return parse_profile_text(build_profile_path(profile_name).read_text(encoding="utf-8"))


def _process_widget_value(widget_collection: dict, widget_key: str, value: str) -> bool:
    match widget_collection.get(widget_key):
        case None:
            return True
        case widget:
            return process_widget_value_update(widget, value)


def _process_parsed_value(widget_collection: dict, section_key: str, value: str) -> bool:
    match _widget_key_for(section_key):
        case None:
            return True
        case widget_key:
            return _process_widget_value(widget_collection, widget_key, value)


def _kept(value: str) -> bool:
    return value == DEFAULT_VALUE


def _applied(widget_collection: dict, item: tuple) -> bool:
    section_key, value = item
    return not _kept(value) and not _process_parsed_value(widget_collection, section_key, value)


def _apply_parsed(widget_collection: dict, parsed: dict) -> tuple:
    return tuple(
        section_key
        for section_key, _ in filter(partial(_applied, widget_collection), parsed.items()))


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
