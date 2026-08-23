import os

from pathlib import Path
from typing import Final
from typing import Optional

PROBE_FILE: Final[str] = "probe.toml"
PROBE_SEP: Final[str] = ";"
PROBE_ON: Final[str] = "on"

MS_PER_S: Final[float] = 1000.0
FRAMETIME_DIGITS: Final[int] = 1
WHOLE_STEP: Final[int] = 2
FRACTION_STEP: Final[float] = 0.20
FRACTION_DIGITS: Final[int] = 2
COUNT_SPAN: Final[int] = 6
BIAS_CEILING: Final[float] = 4.0
SHADING_CEILING: Final[float] = 1.0
OFF_VALUE: Final[str] = "off"


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


def probe_number(data: dict, key: str) -> Optional[float]:
    match _is_number(probe_text(data, key)):
        case True:
            return float(probe_text(data, key))
        case False:
            return None


def probe_flag(data: dict, key: str) -> bool:
    return probe_text(data, key) == PROBE_ON


def probe_list(data: dict, key: str) -> tuple:
    return tuple(v.lower() for v in probe_text(data, key).split(PROBE_SEP) if v != "")


def plain_pairs(values: tuple) -> tuple:
    return tuple((v, v) for v in values)


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


def present_options(data: dict) -> tuple:
    return plain_pairs(probe_list(data, "present_modes"))


def alpha_options(data: dict) -> tuple:
    return plain_pairs(probe_list(data, "composite_alphas"))


def gpu_options(data: dict) -> tuple:
    return tuple(
        (str(at + 1), name)
        for at, name in enumerate(probe_list(data, "device_names")))


def _aniso_ladder(limit: Optional[float]) -> tuple:
    match limit:
        case None:
            return ()
        case value:
            return ((OFF_VALUE, OFF_VALUE),) + plain_pairs(
                _whole_values(WHOLE_STEP, int(value)))


def aniso_options(data: dict) -> tuple:
    match probe_flag(data, "sampler_anisotropy"):
        case False:
            return ()
        case True:
            return _aniso_ladder(probe_number(data, "max_anisotropy"))


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


def _count_values(low: Optional[float], high: Optional[float]) -> tuple:
    match (low, high):
        case (None, _) | (_, None):
            return ()
        case (start, stop):
            return plain_pairs(
                _whole_values(int(start), _count_ceiling(int(start), int(stop))))


def image_count_options(data: dict) -> tuple:
    return _count_values(
        probe_number(data, "min_image_count"),
        probe_number(data, "max_image_count"))


def _mip_values(limit: Optional[float]) -> tuple:
    match limit:
        case None:
            return ()
        case value:
            return plain_pairs(_whole_values(0, int(value)))


def mip_options(data: dict) -> tuple:
    return _mip_values(probe_number(data, "max_lod_level"))


def _bias_ladder(span: int) -> tuple:
    return plain_pairs(_fraction_values(-span, span))


def _bias_values(limit: Optional[float]) -> tuple:
    match limit:
        case None:
            return ()
        case value:
            return _bias_ladder(_span_of(min(value, BIAS_CEILING)))


def lod_bias_options(data: dict) -> tuple:
    return _bias_values(probe_number(data, "max_lod_bias"))
