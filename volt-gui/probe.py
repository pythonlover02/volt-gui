import os

from pathlib import Path
from typing import Final

PROBE_FILE: Final[str] = "probe.toml"
PROBE_SEP: Final[str] = ";"
PROBE_ON: Final[str] = "on"

WHOLE_STEP: Final[int] = 2
FRACTION_STEP: Final[float] = 0.20
FRACTION_DIGITS: Final[int] = 2
COUNT_SPAN: Final[int] = 6
BIAS_CEILING: Final[float] = 4.0
SHADING_CEILING: Final[float] = 1.0
OFF_VALUE: Final[str] = "off"

PRESENT_FALLBACK: Final[tuple] = ("fifo", "fifo_relaxed", "mailbox", "immediate")
DEPTH_FALLBACK: Final[tuple] = ("8bit", "10bit")
DEVICE_FALLBACK: Final[tuple] = ("device 1", "device 2", "device 3", "device 4")
ANISO_FALLBACK: Final[float] = 16.0
BIAS_FALLBACK: Final[float] = 4.0
LEVEL_FALLBACK: Final[float] = 14.0
MIN_COUNT_FALLBACK: Final[float] = 2.0
MAX_COUNT_FALLBACK: Final[float] = 0.0


def build_probe_path() -> Path:
    return Path(os.path.expanduser("~/.config/volt-gui")) / PROBE_FILE


def _pair_of(line: str) -> tuple:
    return (line.split("=", 1)[0].strip(), line.split("=", 1)[1].strip().strip('"'))


def parse_probe_text(text: str) -> dict:
    return dict(_pair_of(line) for line in text.splitlines() if "=" in line)


def call_read_probe() -> dict:
    match build_probe_path().exists():
        case False:
            return {}
        case True:
            return parse_probe_text(build_probe_path().read_text(encoding="utf-8"))


def call_probe_stamp() -> float:
    match build_probe_path().exists():
        case False:
            return 0.0
        case True:
            return build_probe_path().stat().st_mtime


def probe_text(data: dict, key: str) -> str:
    return data.get(key, "")


def _is_number(text: str) -> bool:
    return text.replace("-", "", 1).replace(".", "", 1).isdigit()


def probe_number(data: dict, key: str, fallback: float) -> float:
    match _is_number(probe_text(data, key)):
        case True:
            return float(probe_text(data, key))
        case False:
            return fallback


def probe_flag(data: dict, key: str) -> bool:
    match probe_text(data, key):
        case "":
            return True
        case text:
            return text == PROBE_ON


def _filled(values: tuple, fallback: tuple) -> tuple:
    match len(values):
        case 0:
            return fallback
        case _:
            return values


def probe_list(data: dict, key: str, fallback: tuple) -> tuple:
    return _filled(
        tuple(v.lower() for v in probe_text(data, key).split(PROBE_SEP) if v != ""),
        fallback)


def plain_pairs(values: tuple) -> tuple:
    return tuple((v, v) for v in values)


def _whole_values(low: int, high: int) -> tuple:
    return tuple(str(v) for v in range(low, high + 1, WHOLE_STEP))


def _fraction_values(low: int, high: int) -> tuple:
    return tuple(
        str(round(v * FRACTION_STEP, FRACTION_DIGITS))
        for v in range(low, high + 1))


def _span_of(limit: float) -> int:
    return int(limit / FRACTION_STEP)


def present_options(data: dict) -> tuple:
    return plain_pairs(probe_list(data, "present_modes", PRESENT_FALLBACK))


def depth_options(data: dict) -> tuple:
    return plain_pairs(probe_list(data, "color_depths", DEPTH_FALLBACK))


def gpu_options(data: dict) -> tuple:
    return tuple(
        (str(at + 1), name)
        for at, name in enumerate(probe_list(data, "device_names", DEVICE_FALLBACK)))


def _aniso_ladder(data: dict) -> tuple:
    return plain_pairs(_whole_values(
        WHOLE_STEP,
        int(probe_number(data, "max_anisotropy", ANISO_FALLBACK))))


def aniso_options(data: dict) -> tuple:
    match probe_flag(data, "sampler_anisotropy"):
        case False:
            return ()
        case True:
            return ((OFF_VALUE, OFF_VALUE),) + _aniso_ladder(data)


def shading_options(data: dict) -> tuple:
    match probe_flag(data, "sample_rate_shading"):
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


def image_count_options(data: dict) -> tuple:
    low = int(probe_number(data, "min_image_count", MIN_COUNT_FALLBACK))
    high = int(probe_number(data, "max_image_count", MAX_COUNT_FALLBACK))
    return plain_pairs(_whole_values(low, _count_ceiling(low, high)))


def mip_options(data: dict) -> tuple:
    return plain_pairs(_whole_values(
        0,
        int(probe_number(data, "max_lod_level", LEVEL_FALLBACK))))


def lod_bias_options(data: dict) -> tuple:
    span = _span_of(min(probe_number(data, "max_lod_bias", BIAS_FALLBACK), BIAS_CEILING))
    return plain_pairs(_fraction_values(-span, span))
