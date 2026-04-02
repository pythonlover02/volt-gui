import sys, os, glob
from PySide6.QtCore import QProcess
from mesa import *
from nvidia import *
from mangohud import *
from gamescope import *
from lsfg import *
from launch import *
from render import *
from options import *
from about import *


def get_settings_database() -> dict:
    return {
        "Mesa": get_mesa_settings(),
        "NVIDIA Proprietary": get_nvidia_settings(),
        "Render Selector": get_render_settings(),
        "Gamescope": get_gamescope_settings(),
        "MangoHud": get_mangohud_settings(),
        "LSFG": get_lsfg_settings(),
        "Launch Options": get_launch_settings(),
        "Options": get_options_settings(),
        "About": get_about_settings(),
    }


def get_tab_metadata(tab_name: str):
    if get_settings_database().get(tab_name) is None: return None
    if not isinstance(get_settings_database()[tab_name], dict): return None
    if not isinstance(get_settings_database()[tab_name].get("_tab_metadata"), tuple): return None
    return get_settings_database()[tab_name]["_tab_metadata"]


def is_tab_with_profile_support(tab_name: str) -> bool:
    if get_tab_metadata(tab_name) is None: return False
    if len(get_tab_metadata(tab_name)) < 1: return False
    return get_tab_metadata(tab_name)[0] is True


def get_tabs_with_profile_support() -> tuple:
    return tuple(filter(is_tab_with_profile_support, get_settings_database()))


def is_valid_tab_name(tab_name: str) -> bool:
    if tab_name.startswith("_"): return False
    if tab_name == "About": return False
    return True


def get_all_tab_names() -> tuple:
    return tuple(filter(is_valid_tab_name, get_settings_database())) + ("About",)


def get_setting_label(category_name: str, setting_name: str) -> str:
    return get_settings_database()[category_name][setting_name]["label"]


def get_setting_description(category_name: str, setting_name: str) -> str:
    return get_settings_database()[category_name][setting_name]["description"]


def get_setting_inputs(category_name: str, setting_name: str) -> str:
    return get_settings_database()[category_name][setting_name]["inputs"]


def get_setting_output(category_name: str, setting_name: str) -> tuple:
    return get_settings_database()[category_name][setting_name]["output"]


def get_about_description() -> str:
    return get_settings_database()["About"]["description"]


def get_about_license() -> str:
    return get_settings_database()["About"]["license"]


def get_about_author() -> str:
    return get_settings_database()["About"]["author"]


def get_about_version() -> str:
    return get_settings_database()["About"]["version"]


def get_about_data() -> dict:
    return {
        "Description": get_about_description(),
        "License": get_about_license(),
        "Author": get_about_author(),
        "Version": get_about_version(),
    }


def is_non_metadata_setting(setting_pair: tuple) -> bool:
    return not setting_pair[0].startswith("_")


def find_settings_for_tab(tab_name: str) -> dict:
    if not isinstance(get_settings_database().get(tab_name, {}), dict): return {}
    return dict(filter(is_non_metadata_setting, get_settings_database().get(tab_name, {}).items()))


def has_settings(tab_name: str) -> bool:
    return len(find_settings_for_tab(tab_name)) > 0


def is_render_selector_setting(category_name: str, setting_name: str) -> bool:
    if category_name != "Render Selector": return False
    return setting_name in ("opengl_rendering_device", "vulkan_rendering_device")


def is_render_selector_output(output: tuple) -> bool:
    if len(output) == 0: return False
    return isinstance(output[0], tuple)


def is_output_type_environment_variable(output: tuple) -> bool:
    return output[0] == "environment_variable"


def is_output_type_argument(output: tuple) -> bool:
    return output[0] == "argument"


def is_output_type_option(output: tuple) -> bool:
    return output[0] == "option"


def get_output_target(output: tuple) -> str:
    return output[1]


def get_output_separator(output: tuple) -> str:
    return output[2]


def get_render_environment_keys(api_type: str) -> tuple:
    setting_name = "opengl_rendering_device" if api_type == "opengl" else "vulkan_rendering_device"
    result = []
    for output_definition in get_setting_output("Render Selector", setting_name):
        result.append(get_output_target(output_definition))
    return tuple(result)


def find_environment_variable_targets_for_setting(category_name: str, setting_name: str) -> tuple:
    output = get_setting_output(category_name, setting_name)
    if is_render_selector_output(output):
        seen = {}
        for output_definition in output:
            if not is_output_type_environment_variable(output_definition): continue
            seen[get_output_target(output_definition)] = None
        return tuple(seen.keys())
    if is_output_type_environment_variable(output):
        return (get_output_target(output),)
    return ()


def find_argument_targets_for_setting(category_name: str, setting_name: str) -> tuple:
    output = get_setting_output(category_name, setting_name)
    if is_output_type_argument(output): return ("argument",)
    return ()


def format_environment_pair(key_value_pair: tuple) -> str:
    return key_value_pair[0] + "=" + key_value_pair[1]


def build_environment_list_from_dict(environment_dict: dict) -> list:
    result = []
    for key_value in environment_dict.items():
        result.append(format_environment_pair(key_value))
    return result


def is_not_frozen_restricted_key(key_value_pair: tuple) -> bool:
    return key_value_pair[0] not in ("LD_LIBRARY_PATH", "LD_PRELOAD")


def filter_frozen_environment_variables(environment_variables: dict) -> dict:
    if not getattr(sys, "frozen", False): return environment_variables
    return dict(filter(is_not_frozen_restricted_key, environment_variables.items()))


def build_filtered_path_string(path_value: str) -> str:
    result = []
    for path_entry in path_value.split(os.pathsep):
        if getattr(sys, "_MEIPASS") not in path_entry: result.append(path_entry)
    return os.pathsep.join(result)


def filter_meipass_from_path(environment_variables: dict) -> dict:
    if getattr(sys, "_MEIPASS", None) is None: return environment_variables
    if "PATH" not in environment_variables: return environment_variables
    return {**environment_variables, "PATH": build_filtered_path_string(environment_variables["PATH"])}


def build_clean_process_environment() -> dict:
    return filter_meipass_from_path(filter_frozen_environment_variables(os.environ.copy()))


def is_executable_file(file_path: str) -> bool:
    return os.access(file_path, os.X_OK)


def has_executable_in_directory(search_directory: str, executable_name: str) -> bool:
    for match_path in glob.glob(os.path.join(search_directory, executable_name + "*")):
        if is_executable_file(match_path): return True
    return False


def has_executable_in_path(executable_name: str) -> bool:
    if has_executable_in_directory("/usr/bin/", executable_name): return True
    return has_executable_in_directory("/usr/local/bin/", executable_name)


def is_available_in_flatpak(program_name: str) -> bool:
    process_instance = QProcess()
    process_instance.setEnvironment(build_environment_list_from_dict(build_clean_process_environment()))
    process_instance.start("flatpak", ["list"])
    if not process_instance.waitForFinished(10000): return False
    return program_name.lower() in process_instance.readAllStandardOutput().data().decode().lower()


def is_executable_available(executable_name: str) -> bool:
    if has_executable_in_path(executable_name): return True
    return is_available_in_flatpak(executable_name)


def is_any_executable_available(executable_tuple: tuple) -> bool:
    for executable_name in executable_tuple:
        if is_executable_available(executable_name): return True
    return False


def build_missing_executables_message(executable_tuple: tuple) -> str:
    return " + ".join(executable_tuple) + " not found"


def validate_setting_availability(category_name: str, setting_name: str) -> dict:
    tab_data = get_settings_database().get(category_name)
    if not isinstance(tab_data, dict): return {"locked": False, "message": ""}
    executable_required = tab_data.get("_executable_required")
    if executable_required is not None and isinstance(executable_required, tuple) and len(executable_required) > 0 and not is_any_executable_available(executable_required):
        return {"locked": True, "message": build_missing_executables_message(executable_required)}
    if not is_render_selector_setting(category_name, setting_name): return {"locked": False, "message": ""}
    if setting_name == "opengl_rendering_device" and not is_executable_available("glxinfo"):
        return {"locked": True, "message": "glxinfo not available"}
    if setting_name == "vulkan_rendering_device" and not is_executable_available("vulkaninfo"):
        return {"locked": True, "message": "vulkaninfo not available"}
    return {"locked": False, "message": ""}


def process_file_write(file_path: str, file_content: str) -> bool:
    if not os.access(os.path.dirname(file_path) or ".", os.W_OK): return False
    open(file_path, "w").write(file_content)
    return True


def parse_widget_value(widget) -> str:
    text = widget.currentText() if hasattr(widget, "currentText") else widget.text()
    if text is None: return None
    if text.strip() == "": return None
    return text.strip()


def get_option_default_value(option_key: str) -> str:
    return {
        "application_theme": "cachyos",
        "window_transparency": "off",
        "interface_scale_factor": "1.0",
        "start_window_maximized": "off",
        "start_window_minimized": "off",
        "system_tray_behavior": "off",
        "volt_script_location": "/usr/local/bin/volt",
        "welcome_message_display": "on",
        "automatic_update_check": "off",
    }.get(option_key, "")


def get_accent_colors(theme_name: str) -> tuple:
    if theme_name == "amd": return ("#E31937", "#FF2D4A", "#B81430")
    if theme_name == "intel": return ("#0068B5", "#1A8CFF", "#004D87")
    if theme_name == "nvidia": return ("#76B900", "#8ED11A", "#5A8F00")
    return ("#80dbcb", "#9ae4d8", "#66b0a2")


def process_environment_variable_setting(output: tuple, value: str, environment_collection: dict, grouped_environment_collection: dict) -> None:
    target = get_output_target(output)
    separator = get_output_separator(output)
    if separator != "":
        if value == "unset":
            environment_collection[target] = ""
            return None
        if target not in grouped_environment_collection:
            grouped_environment_collection[target] = {"separator": separator, "parts": []}
        grouped_environment_collection[target]["parts"].append(value)
        return None
    environment_collection[target] = "" if value == "unset" else value
    return None


def process_argument_setting(tab_name: str, value: str, argument_collection: list) -> None:
    if value == "unset": return None
    argument_collection.append((tab_name, value))
    return None


def process_setting_into_collections(tab_name: str, setting_key: str, value: str, widget_collection: dict, environment_collection: dict, grouped_environment_collection: dict, argument_collection: list) -> None:
    output = get_setting_output(tab_name, setting_key)
    if is_render_selector_setting(tab_name, setting_key):
        process_render_selector_into_environment(tab_name, setting_key, value, widget_collection, environment_collection)
        return None
    if is_output_type_option(output): return None
    if is_output_type_environment_variable(output):
        process_environment_variable_setting(output, value, environment_collection, grouped_environment_collection)
        return None
    if is_output_type_argument(output):
        process_argument_setting(tab_name, value, argument_collection)
        return None
    return None


def process_render_selector_into_environment(tab_name: str, setting_key: str, selected_value: str, widget_collection: dict, environment_collection: dict) -> None:
    environment_keys = get_render_environment_keys("opengl" if setting_key == "opengl_rendering_device" else "vulkan")
    if selected_value == "unset":
        for environment_key in environment_keys: environment_collection[environment_key] = ""
        return None
    if setting_key == "opengl_rendering_device":
        process_opengl_render_into_environment(widget_collection["Render Selector:" + setting_key], selected_value, environment_keys, environment_collection)
        return None
    if setting_key == "vulkan_rendering_device":
        process_vulkan_render_into_environment(widget_collection["Render Selector:" + setting_key], selected_value, environment_keys, environment_collection)
        return None
    return None


def resolve_render_selector_value(combo_widget, selected_value: str) -> str:
    index_map = getattr(combo_widget, "index_map", {})
    if selected_value in index_map: return index_map[selected_value]
    if "=" in selected_value: return selected_value.split("=", 1)[1]
    return selected_value


def process_opengl_render_into_environment(combo_widget, selected_value: str, environment_keys: tuple, environment_collection: dict) -> None:
    resolved_value = resolve_render_selector_value(combo_widget, selected_value)
    device_map = getattr(combo_widget, "device_map", {})
    if resolved_value not in device_map:
        for environment_key in environment_keys: environment_collection[environment_key] = resolved_value
        return None
    used_keys = set()
    for environment_key, environment_value in device_map[resolved_value].items():
        environment_collection[environment_key] = environment_value
        used_keys.add(environment_key)
    for environment_key in environment_keys:
        if environment_key not in used_keys: environment_collection[environment_key] = ""
    return None


def process_vulkan_render_into_environment(combo_widget, selected_value: str, environment_keys: tuple, environment_collection: dict) -> None:
    resolved_value = resolve_render_selector_value(combo_widget, selected_value)
    device_map = getattr(combo_widget, "device_map", {})
    if resolved_value in device_map and device_map[resolved_value] != "":
        environment_collection["MESA_VK_DEVICE_SELECT"] = device_map[resolved_value] + "!"
    else:
        environment_collection["MESA_VK_DEVICE_SELECT"] = resolved_value
    for environment_key in environment_keys:
        if environment_key != "MESA_VK_DEVICE_SELECT": environment_collection[environment_key] = ""
    return None


def build_gamescope_command_string(argument_collection: list) -> str:
    gamescope_parts = [value for tab, value in argument_collection if tab == "Gamescope"]
    other_parts = [value for tab, value in argument_collection if tab != "Gamescope"]
    if len(other_parts) == 0: return " ".join(gamescope_parts)
    return " ".join(gamescope_parts) + " -- " + " ".join(other_parts)


def build_launch_command_string(argument_collection: list) -> str:
    if len(argument_collection) == 0: return ""
    if argument_collection[0][1] == "gamescope": return build_gamescope_command_string(argument_collection)
    return " ".join(value for tab, value in argument_collection)


def build_final_apply_arguments(environment_collection: dict, grouped_environment_collection: dict, argument_collection: list) -> tuple:
    environment_arguments = []
    for environment_key, environment_value in environment_collection.items():
        environment_arguments.append(environment_key + "=" + environment_value)
    for target, group_data in grouped_environment_collection.items():
        if len(group_data["parts"]) > 0:
            environment_arguments.append(target + "=" + group_data["separator"].join(group_data["parts"]))
        else:
            environment_arguments.append(target + "=")
    launch_command = build_launch_command_string(argument_collection)
    if launch_command != "": environment_arguments.append("launch:" + launch_command)
    return tuple(environment_arguments)


def build_apply_results_from_widgets(widget_collection: dict) -> tuple:
    environment_collection = {}
    grouped_environment_collection = {}
    argument_collection = []
    for tab_name in get_tabs_with_profile_support():
        for setting_key in find_settings_for_tab(tab_name):
            if widget_collection.get(tab_name + ":" + setting_key) is None: continue
            if not widget_collection[tab_name + ":" + setting_key].isEnabled(): continue
            value = parse_widget_value(widget_collection[tab_name + ":" + setting_key])
            if value is None: continue
            process_setting_into_collections(tab_name, setting_key, value, widget_collection, environment_collection, grouped_environment_collection, argument_collection)
    return build_final_apply_arguments(environment_collection, grouped_environment_collection, argument_collection)
