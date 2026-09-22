import os

from functools import partial
from functools import reduce
from math import ceil
from math import floor
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
ANISO_FIRST: Final[int] = 2
UNIT_EPSILON: Final[float] = 1e-9
STEP_DIGITS: Final[int] = 6
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


def _carries(value: str, source: tuple) -> bool:
    return value in source[1]


def _tags_for(value: str, sources: tuple) -> tuple:
    return tuple(name for name, _ in filter(partial(_carries, value), sources))


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


def _low_units(low: float, step: float) -> int:
    return ceil(low / step - UNIT_EPSILON)


def _high_units(high: float, step: float) -> int:
    return floor(high / step + UNIT_EPSILON)


def _step_text(units: int, step: float) -> str:
    match step:
        case int():
            return str(units * step)
        case _:
            return str(round(units * step, STEP_DIGITS))


def stepped_values(low: float, high: float, step: float) -> tuple:
    return tuple(
        _step_text(units, step)
        for units in range(_low_units(low, step), _high_units(high, step) + 1))


def _non_empty(entry: tuple) -> bool:
    return entry[1] != ()


def _surface_lists(data: tuple, key: str) -> tuple:
    return tuple(filter(_non_empty, (
        (n, probe_list(v, key)) for n, v in probe_surfaces(data))))


def present_options(data: tuple) -> tuple:
    return tagged_pairs(_surface_lists(data, "present_modes"))


def alpha_options(data: tuple) -> tuple:
    return tagged_pairs(_surface_lists(data, "composite_alphas"))


def gpu_options(data: tuple) -> tuple:
    return tuple(
        (str(at + 1), name)
        for at, name in enumerate(probe_list(probe_device(data), "device_names")))


def _aniso_ladder(limit: Optional[float], step: float) -> tuple:
    match limit:
        case None:
            return ()
        case value:
            return ((OFF_VALUE, OFF_VALUE),) + plain_pairs(
                stepped_values(ANISO_FIRST, value, step))


def aniso_options(data: tuple, step: float) -> tuple:
    match probe_flag(probe_device(data), "sampler_anisotropy"):
        case False:
            return ()
        case True:
            return _aniso_ladder(probe_number(probe_device(data), "max_anisotropy"), step)


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


def shading_options(data: tuple, step: float) -> tuple:
    match probe_flag(probe_device(data), "sample_rate_shading"):
        case False:
            return ()
        case True:
            return ((OFF_VALUE, OFF_VALUE),) + plain_pairs(
                stepped_values(step, SHADING_CEILING, step))


def _count_ceiling(low: int, high: int) -> int:
    match high:
        case 0:
            return low + COUNT_SPAN
        case _:
            return high


def _count_values(low: Optional[float], high: Optional[float], step: float) -> tuple:
    match (low, high):
        case (None, _) | (_, None):
            return ()
        case (start, stop):
            return stepped_values(int(start), _count_ceiling(int(start), int(stop)), step)


def _count_sources(data: tuple, step: float) -> tuple:
    return tuple(filter(_non_empty, (
        (n, _count_values(
            probe_number(v, "min_image_count"),
            probe_number(v, "max_image_count"),
            step))
        for n, v in probe_surfaces(data))))


def image_count_options(data: tuple, step: float) -> tuple:
    return tagged_count_pairs(_count_sources(data, step))


def _mip_values(limit: Optional[float], step: float) -> tuple:
    match limit:
        case None:
            return ()
        case value:
            return plain_pairs(stepped_values(0, value, step))


def mip_options(data: tuple, step: float) -> tuple:
    return _mip_values(probe_number(probe_device(data), "max_lod_level"), step)


def _bias_ladder(span: float, step: float) -> tuple:
    return plain_pairs(stepped_values(-span, span, step))


def _bias_values(limit: Optional[float], step: float) -> tuple:
    match limit:
        case None:
            return ()
        case value:
            return _bias_ladder(min(value, BIAS_CEILING), step)


def lod_bias_options(data: tuple, step: float) -> tuple:
    return _bias_values(probe_number(probe_device(data), "max_lod_bias"), step)
