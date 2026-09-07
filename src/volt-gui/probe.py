import os

from functools import reduce
from pathlib import Path
from typing import Final
from typing import Optional

PROBE_FILE: Final[str] = "probe.toml"
PROBE_SEP: Final[str] = ";"
PROBE_ON: Final[str] = "on"
PAIR_SEP: Final[str] = "="
DEVICE_SECTION: Final[str] = "probe"
TAG_OPEN: Final[str] = " ("
TAG_SEP: Final[str] = ", "
TAG_CLOSE: Final[str] = ")"

MS_PER_S: Final[float] = 1000.0
FRAMETIME_DIGITS: Final[int] = 1
WHOLE_STEP: Final[int] = 2
FRACTION_STEP: Final[float] = 0.20
FRACTION_DIGITS: Final[int] = 2
COUNT_SPAN: Final[int] = 6
BIAS_CEILING: Final[float] = 4.0
SHADING_CEILING: Final[float] = 1.0
OFF_VALUE: Final[str] = "off"
TOGGLE_VALUES: Final[tuple] = ("off", "on")


def build_probe_path() -> Path:
    return Path(os.path.expanduser("~/.config/volt-gui")) / PROBE_FILE


def _classify_line(line: str) -> tuple:
    match (line.startswith("["), PAIR_SEP in line, line.startswith("#"), line):
        case (_, _, True, _) | (_, _, _, ""):
            return ("skip",)
        case (True, _, _, _):
            return ("section", line.strip("[]").strip())
        case (False, True, _, _):
            return ("pair",
                    line.split(PAIR_SEP, 1)[0].strip(),
                    line.split(PAIR_SEP, 1)[1].strip().strip('"'))
        case _:
            return ("skip",)


def _with_section(sections: tuple, name: str) -> tuple:
    return sections + ((name, {}),)


def _with_pair(sections: tuple, key: str, value: str) -> tuple:
    match sections:
        case ():
            return ()
        case _:
            return sections[:-1] + ((sections[-1][0], {**sections[-1][1], key: value}),)


def _fold_line(state: tuple, line: str) -> tuple:
    match _classify_line(line.strip()):
        case ("section", name):
            return _with_section(state, name)
        case ("pair", key, value):
            return _with_pair(state, key, value)
        case _:
            return state


def parse_probe_text(text: str) -> tuple:
    return reduce(_fold_line, text.splitlines(), ())


def call_read_probe() -> tuple:
    match build_probe_path().exists():
        case False:
            return ()
        case True:
            return parse_probe_text(build_probe_path().read_text(encoding="utf-8"))


def call_probe_stamp() -> float:
    match build_probe_path().exists():
        case False:
            return 0.0
        case True:
            return build_probe_path().stat().st_mtime


def probe_device(data: tuple) -> dict:
    return next((values for name, values in data if name == DEVICE_SECTION), {})


def probe_surfaces(data: tuple) -> tuple:
    return tuple((name, values) for name, values in data if name != DEVICE_SECTION)


def probe_text(values: dict, key: str) -> str:
    return values.get(key, "")


def _is_number(text: str) -> bool:
    return text.replace("-", "", 1).replace(".", "", 1).isdigit()


def probe_number(values: dict, key: str) -> Optional[float]:
    match _is_number(probe_text(values, key)):
        case True:
            return float(probe_text(values, key))
        case False:
            return None


def probe_flag(values: dict, key: str) -> bool:
    return probe_text(values, key) == PROBE_ON


def probe_list(values: dict, key: str) -> tuple:
    return tuple(v.lower() for v in probe_text(values, key).split(PROBE_SEP) if v != "")


def plain_pairs(values: tuple) -> tuple:
    return tuple((v, v) for v in values)


def _tag_label(value: str, tags: tuple) -> str:
    return value + TAG_OPEN + TAG_SEP.join(tags) + TAG_CLOSE


def _tags_for(value: str, sources: tuple) -> tuple:
    return tuple(name for name, values in sources if value in values)


def _ordered_values(sources: tuple) -> tuple:
    return tuple(dict.fromkeys(value for _, values in sources for value in values))


def _tagged(values: tuple, sources: tuple) -> tuple:
    return tuple(
        (value, _tag_label(value, _tags_for(value, sources)))
        for value in values)


def tagged_pairs(sources: tuple) -> tuple:
    return _tagged(_ordered_values(sources), sources)


def tagged_count_pairs(sources: tuple) -> tuple:
    return _tagged(tuple(sorted(_ordered_values(sources), key=int)), sources)


def _frametime_label(fps: str) -> str:
    return fps + " (" + str(round(MS_PER_S / float(fps), FRAMETIME_DIGITS)) + "ms)"


def frametime_pairs(values: tuple) -> tuple:
    return tuple((v, _frametime_label(v)) for v in values)


def _first_step(low: int) -> int:
    return low + (low % WHOLE_STEP)


def _whole_values(low: int, high: int) -> tuple:
    return tuple(str(v) for v in range(_first_step(low), high + 1, WHOLE_STEP))


def _fraction_values(low: int, high: int) -> tuple:
    return tuple(
        str(round(v * FRACTION_STEP, FRACTION_DIGITS))
        for v in range(low, high + 1))


def _span_of(limit: float) -> int:
    return int(limit / FRACTION_STEP)


def _surface_lists(data: tuple, key: str) -> tuple:
    return tuple(
        (name, values)
        for name, values in (
            (n, probe_list(v, key)) for n, v in probe_surfaces(data))
        if values != ())


def present_options(data: tuple) -> tuple:
    return tagged_pairs(_surface_lists(data, "present_modes"))


def alpha_options(data: tuple) -> tuple:
    return tagged_pairs(_surface_lists(data, "composite_alphas"))


def gpu_options(data: tuple) -> tuple:
    return tuple(
        (str(at + 1), name)
        for at, name in enumerate(probe_list(probe_device(data), "device_names")))


def _aniso_ladder(limit: Optional[float]) -> tuple:
    match limit:
        case None:
            return ()
        case value:
            return ((OFF_VALUE, OFF_VALUE),) + plain_pairs(
                _whole_values(WHOLE_STEP, int(value)))


def aniso_options(data: tuple) -> tuple:
    match probe_flag(probe_device(data), "sampler_anisotropy"):
        case False:
            return ()
        case True:
            return _aniso_ladder(probe_number(probe_device(data), "max_anisotropy"))


def _toggle_ladder(held: bool) -> tuple:
    match held:
        case False:
            return ()
        case True:
            return plain_pairs(TOGGLE_VALUES)


def alpha_one_options(data: tuple) -> tuple:
    return _toggle_ladder(probe_flag(probe_device(data), "alpha_to_one"))


def clamp_options(data: tuple) -> tuple:
    return _toggle_ladder(probe_flag(probe_device(data), "depth_clamp"))


def shading_options(data: tuple) -> tuple:
    match probe_flag(probe_device(data), "sample_rate_shading"):
        case False:
            return ()
        case True:
            return ((OFF_VALUE, OFF_VALUE),) + plain_pairs(
                _fraction_values(1, _span_of(SHADING_CEILING)))


def _count_ceiling(low: int, high: int) -> int:
    match high:
        case 0:
            return low + COUNT_SPAN
        case _:
            return high


def _count_values(low: Optional[float], high: Optional[float]) -> tuple:
    match (low, high):
        case (None, _) | (_, None):
            return ()
        case (start, stop):
            return _whole_values(int(start), _count_ceiling(int(start), int(stop)))


def _count_sources(data: tuple) -> tuple:
    return tuple(
        (name, values)
        for name, values in (
            (n, _count_values(
                probe_number(v, "min_image_count"),
                probe_number(v, "max_image_count")))
            for n, v in probe_surfaces(data))
        if values != ())


def image_count_options(data: tuple) -> tuple:
    return tagged_count_pairs(_count_sources(data))


def _mip_values(limit: Optional[float]) -> tuple:
    match limit:
        case None:
            return ()
        case value:
            return plain_pairs(_whole_values(0, int(value)))


def mip_options(data: tuple) -> tuple:
    return _mip_values(probe_number(probe_device(data), "max_lod_level"))


def _bias_ladder(span: int) -> tuple:
    return plain_pairs(_fraction_values(-span, span))


def _bias_values(limit: Optional[float]) -> tuple:
    match limit:
        case None:
            return ()
        case value:
            return _bias_ladder(_span_of(min(value, BIAS_CEILING)))


def lod_bias_options(data: tuple) -> tuple:
    return _bias_values(probe_number(probe_device(data), "max_lod_bias"))
