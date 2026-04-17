import threading

from PySide6.QtCore import QProcess, QTimer

from database import *


def build_empty_detection_state() -> dict:
    return {"devices": (), "device_map": {}, "loaded": False}


def get_opengl_detection_result(cache=[build_empty_detection_state()]):
    return cache[0]


def get_vulkan_detection_result(cache=[build_empty_detection_state()]):
    return cache[0]


def parse_device_name_from_raw(raw_text: str) -> str:
    if "/" in raw_text: return raw_text.split("/")[0].strip().lower()
    if "(" in raw_text: return raw_text.split("(")[0].strip().lower()
    return raw_text.lower()


def build_opengl_environment(extra_environment) -> list:
    clean_environment = build_clean_process_environment()
    remove_variables = get_render_environment_keys("opengl")
    merged = {}
    for environment_key, environment_value in clean_environment.items():
        if environment_key not in remove_variables: merged[environment_key] = environment_value
    if extra_environment is not None:
        for environment_key, environment_value in extra_environment.items():
            merged[environment_key] = environment_value
    return build_environment_list_from_dict(merged)


def process_opengl_info_command_sync(extra_environment):
    process_instance = QProcess()
    process_instance.setEnvironment(build_opengl_environment(extra_environment))
    process_instance.start("glxinfo")
    if not process_instance.waitForFinished(10000): return None
    return process_instance.readAllStandardOutput().data().decode()


def parse_opengl_device_from_output(command_output: str):
    for output_line in command_output.split("\n"):
        if "OpenGL renderer string:" not in output_line: continue
        return parse_device_name_from_raw(output_line.split(":", 1)[1].strip())
    return None


def find_opengl_device_from_environment(extra_environment):
    command_output = process_opengl_info_command_sync(extra_environment)
    if command_output is None: return None
    device_name = parse_opengl_device_from_output(command_output)
    if device_name is None: return None
    if "llvmpipe" in device_name: return None
    return (device_name, extra_environment if extra_environment is not None else {})


def find_opengl_mesa_device_at_index(device_index: int):
    return find_opengl_device_from_environment({"__GLX_VENDOR_LIBRARY_NAME": "mesa", "DRI_PRIME": str(device_index)})


def find_opengl_mesa_devices() -> tuple:
    return tuple(result for result in (find_opengl_mesa_device_at_index(device_index) for device_index in range(5)) if result is not None)


def find_opengl_nvidia_device():
    return find_opengl_device_from_environment({"__GLX_VENDOR_LIBRARY_NAME": "nvidia", "__NV_PRIME_RENDER_OFFLOAD": "1"})


def build_deduplicated_device_names(detected_devices: tuple) -> tuple:
    return tuple(dict.fromkeys(pair[0] for pair in detected_devices).keys())


def build_device_map_from_detected(detected_devices: tuple) -> dict:
    if len(detected_devices) == 0: return {}
    return {pair[0]: pair[1] for pair in reversed(detected_devices)}


def build_deduplicated_device_result(detected_devices: tuple) -> dict:
    return {
        "devices": build_deduplicated_device_names(detected_devices),
        "device_map": build_device_map_from_detected(detected_devices),
    }


def find_opengl_devices_sync() -> dict:
    return build_deduplicated_device_result(
        tuple(device for device in (find_opengl_device_from_environment(None), find_opengl_nvidia_device()) if device is not None)
        + find_opengl_mesa_devices()
        + (("llvmpipe (software rendering)", {"__GLX_VENDOR_LIBRARY_NAME": "mesa", "LIBGL_ALWAYS_SOFTWARE": "1"}), ("zink", {"__GLX_VENDOR_LIBRARY_NAME": "mesa", "MESA_LOADER_DRIVER_OVERRIDE": "zink", "LIBGL_KOPPER_DRI2": "1"}))
    )


def find_opengl_devices() -> dict:
    if not get_opengl_detection_result()["loaded"]: return {"devices": (), "device_map": {}}
    return {"devices": get_opengl_detection_result()["devices"], "device_map": get_opengl_detection_result()["device_map"]}


def process_opengl_detection_worker(completion_callback) -> None:
    result = find_opengl_devices_sync()
    get_opengl_detection_result()["devices"] = result["devices"]
    get_opengl_detection_result()["device_map"] = result["device_map"]
    get_opengl_detection_result()["loaded"] = True
    if completion_callback is not None: QTimer.singleShot(0, completion_callback)
    return None


def process_opengl_detection_async(completion_callback) -> None:
    threading.Thread(target=lambda: process_opengl_detection_worker(completion_callback), daemon=True).start()
    return None


def get_display_name_for_vulkan_device(raw_device_name: str) -> str:
    if "llvmpipe" in parse_device_name_from_raw(raw_device_name): return "llvmpipe (software rendering)"
    return parse_device_name_from_raw(raw_device_name)


def build_vulkan_device_identifier_string(accumulated_properties: dict) -> str:
    return accumulated_properties["vendorID"] + ":" + accumulated_properties["deviceID"]


def parse_vulkan_device_entries(command_output: str) -> tuple:
    accumulated_properties = {}
    result_entries = []
    for output_line in command_output.split("\n"):
        for property_name in ("vendorID", "deviceID", "deviceName"):
            if property_name not in output_line.strip(): continue
            if "=" not in output_line.strip(): continue
            accumulated_properties[property_name] = output_line.strip().split("=")[1].strip()
            if property_name != "deviceName": continue
            if "vendorID" not in accumulated_properties: continue
            if "deviceID" not in accumulated_properties: continue
            if "deviceName" not in accumulated_properties: continue
            result_entries.append((
                get_display_name_for_vulkan_device(accumulated_properties["deviceName"]),
                build_vulkan_device_identifier_string(accumulated_properties),
            ))
            accumulated_properties = {}
    return tuple(result_entries)


def find_vulkan_devices_sync() -> dict:
    process_instance = QProcess()
    process_instance.setEnvironment(build_environment_list_from_dict(build_clean_process_environment()))
    process_instance.start("vulkaninfo")
    if not process_instance.waitForFinished(10000): return {"devices": (), "device_map": {}}
    device_entries = parse_vulkan_device_entries(process_instance.readAllStandardOutput().data().decode())
    return {"devices": tuple(entry[0] for entry in device_entries), "device_map": {entry[0]: entry[1] for entry in device_entries}}


def find_vulkan_devices() -> dict:
    if not get_vulkan_detection_result()["loaded"]: return {"devices": (), "device_map": {}}
    return {"devices": get_vulkan_detection_result()["devices"], "device_map": get_vulkan_detection_result()["device_map"]}


def process_vulkan_detection_worker(completion_callback) -> None:
    result = find_vulkan_devices_sync()
    get_vulkan_detection_result()["devices"] = result["devices"]
    get_vulkan_detection_result()["device_map"] = result["device_map"]
    get_vulkan_detection_result()["loaded"] = True
    if completion_callback is not None: QTimer.singleShot(0, completion_callback)
    return None


def process_vulkan_detection_async(completion_callback) -> None:
    threading.Thread(target=lambda: process_vulkan_detection_worker(completion_callback), daemon=True).start()
    return None


def find_render_devices(api_type: str) -> dict:
    if api_type == "opengl": return find_opengl_devices()
    if api_type == "vulkan": return find_vulkan_devices()
    return {"devices": (), "device_map": {}}
