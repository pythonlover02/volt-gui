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
        "MangoHud": get_mangohud_settings(),
        "Gamescope": get_gamescope_settings(),
        "LSFG": get_lsfg_settings(),
        "Launch Options": get_launch_settings(),
        "Options": get_options_settings(), "About": get_about_settings()
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
    return get_settings_database()[category_name][setting_name][0]


def get_setting_items(category_name: str, setting_name: str) -> tuple:
    return get_settings_database()[category_name][setting_name][1]


def get_setting_output_definitions(category_name: str, setting_name: str) -> tuple:
    return get_settings_database()[category_name][setting_name][2]


def get_item_display(item_tuple: tuple) -> str:
    return item_tuple[0]


def get_item_value(item_tuple: tuple):
    return item_tuple[1]


def get_about_description() -> str:
    return get_settings_database()["About"]["description"]


def get_about_license() -> str:
    return get_settings_database()["About"]["license"]


def get_about_author() -> str:
    return get_settings_database()["About"]["author"]


def get_about_version() -> str:
    return get_settings_database()["About"]["version"]


def get_about_data() -> dict:
    return {"Description": get_about_description(), "License": get_about_license(), "Author": get_about_author(), "Version": get_about_version()}


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


def is_output_type_environment_variable(output_definition: tuple) -> bool:
    return output_definition[0] == "environment_variable"


def is_output_type_argument(output_definition: tuple) -> bool:
    return output_definition[0] == "argument"


def is_output_type_option(output_definition: tuple) -> bool:
    return output_definition[0] == "option"


def get_output_type(output_definition: tuple) -> str:
    return output_definition[0]


def get_output_target(output_definition: tuple) -> str:
    return output_definition[1]


def get_output_joiner(output_definition: tuple) -> str:
    return output_definition[2]


def get_output_prefix(output_definition: tuple) -> str:
    return output_definition[3]


def get_output_suffix(output_definition: tuple) -> str:
    return output_definition[4]


def get_value_at_index(setting_value, resource_index: int):
    if isinstance(setting_value, tuple): return setting_value[resource_index] if resource_index < len(setting_value) else ""
    if setting_value is None: return None
    return setting_value


def find_mapped_value_for_display(category_name: str, setting_name: str, display_text: str):
    for item_entry in get_setting_items(category_name, setting_name):
        if get_item_display(item_entry) == display_text: return get_item_value(item_entry)
    return None


def get_render_environment_keys(api_type: str) -> tuple:
    setting_name = "opengl_rendering_device" if api_type == "opengl" else "vulkan_rendering_device"
    result = []
    for output_definition in get_setting_output_definitions("Render Selector", setting_name):
        result.append(get_output_target(output_definition))
    return tuple(result)


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
    if executable_required is not None and isinstance(executable_required, tuple) and len(executable_required) > 0 and not is_any_executable_available(executable_required): return {"locked": True, "message": build_missing_executables_message(executable_required)}
    if not is_render_selector_setting(category_name, setting_name): return {"locked": False, "message": ""}
    if setting_name == "opengl_rendering_device" and not is_executable_available("glxinfo"): return {"locked": True, "message": "glxinfo not available"}
    if setting_name == "vulkan_rendering_device" and not is_executable_available("vulkaninfo"): return {"locked": True, "message": "vulkaninfo not available"}
    return {"locked": False, "message": ""}


def find_environment_variable_targets_for_setting(category_name: str, setting_name: str) -> tuple:
    seen = {}
    for output_definition in get_setting_output_definitions(category_name, setting_name):
        if not is_output_type_environment_variable(output_definition): continue
        if get_output_target(output_definition) == "": continue
        seen[get_output_target(output_definition)] = None
    return tuple(seen.keys())


def find_argument_targets_for_setting(category_name: str, setting_name: str) -> tuple:
    seen = {}
    for output_definition in get_setting_output_definitions(category_name, setting_name):
        if not is_output_type_argument(output_definition): continue
        if get_output_target(output_definition) == "": continue
        seen[get_output_target(output_definition)] = None
    return tuple(seen.keys())


def process_file_write(file_path: str, file_content: str) -> bool:
    if not os.access(os.path.dirname(file_path) or ".", os.W_OK): return False
    open(file_path, "w").write(file_content)
    return True


def process_setting_into_collections(tab_name: str, setting_key: str, selected_display: str, widget_collection: dict, environment_collection: dict, grouped_environment_collection: dict, argument_collection: dict) -> None:
    if is_render_selector_setting(tab_name, setting_key):
        process_render_selector_into_environment(tab_name, setting_key, selected_display, widget_collection, environment_collection)
        return None
    mapped_value = find_mapped_value_for_display(tab_name, setting_key, selected_display)
    is_custom = mapped_value is None
    if is_custom: mapped_value = selected_display
    if mapped_value is None: return None
    for definition_index in range(len(get_setting_output_definitions(tab_name, setting_key))):
        process_single_output_definition(get_setting_output_definitions(tab_name, setting_key)[definition_index], definition_index, mapped_value, is_custom, selected_display, environment_collection, grouped_environment_collection, argument_collection)
    return None


def process_single_output_definition(output_definition: tuple, definition_index: int, mapped_value, is_custom: bool, selected_display: str, environment_collection: dict, grouped_environment_collection: dict, argument_collection: dict) -> None:
    value = mapped_value if is_custom else get_value_at_index(mapped_value, definition_index)
    if value is None: return None
    if is_output_type_option(output_definition): return None
    if is_output_type_environment_variable(output_definition): process_environment_output_definition(output_definition, value, environment_collection, grouped_environment_collection)
    if is_output_type_argument(output_definition): process_argument_output_definition(output_definition, value, selected_display, argument_collection)
    return None


def process_environment_output_definition(output_definition: tuple, value: str, environment_collection: dict, grouped_environment_collection: dict) -> None:
    if get_output_joiner(output_definition) != "":
        if get_output_target(output_definition) not in grouped_environment_collection: grouped_environment_collection[get_output_target(output_definition)] = {"joiner": get_output_joiner(output_definition), "parts": []}
        if value != "": grouped_environment_collection[get_output_target(output_definition)]["parts"].append(get_output_prefix(output_definition) + value)
        return None
    environment_collection[get_output_target(output_definition)] = value
    return None


def process_argument_output_definition(output_definition: tuple, value: str, selected_display: str, argument_collection: dict) -> None:
    if get_output_target(output_definition) not in argument_collection: argument_collection[get_output_target(output_definition)] = {"command": "", "suffix": "", "flags": []}
    if get_output_prefix(output_definition) == "":
        argument_collection[get_output_target(output_definition)]["command"] = value
        if get_output_suffix(output_definition) != "": argument_collection[get_output_target(output_definition)]["suffix"] = get_output_suffix(output_definition).strip()
        return None
    if value != "": argument_collection[get_output_target(output_definition)]["flags"].append((get_output_prefix(output_definition).strip(), value))
    elif selected_display != "default": argument_collection[get_output_target(output_definition)]["flags"].append((get_output_prefix(output_definition).strip(), ""))
    return None


def process_render_selector_into_environment(tab_name: str, setting_key: str, selected_display: str, widget_collection: dict, environment_collection: dict) -> None:
    environment_keys = get_render_environment_keys("opengl" if setting_key == "opengl_rendering_device" else "vulkan")
    if selected_display == "default":
        for environment_key in environment_keys: environment_collection[environment_key] = ""
        return None
    if setting_key == "opengl_rendering_device":
        process_opengl_render_into_environment(widget_collection[tab_name + ":" + setting_key], selected_display, environment_keys, environment_collection)
        return None
    if setting_key == "vulkan_rendering_device":
        process_vulkan_render_into_environment(widget_collection[tab_name + ":" + setting_key], selected_display, environment_keys, environment_collection)
        return None
    return None


def process_opengl_render_into_environment(combo_widget, selected_display: str, environment_keys: tuple, environment_collection: dict) -> None:
    device_map = getattr(combo_widget, "device_map", {})
    if selected_display not in device_map:
        for environment_key in environment_keys: environment_collection[environment_key] = selected_display
        return None
    used_keys = set()
    for environment_key, environment_value in device_map[selected_display].items():
        environment_collection[environment_key] = environment_value
        used_keys.add(environment_key)
    for environment_key in environment_keys:
        if environment_key not in used_keys: environment_collection[environment_key] = ""
    return None


def process_vulkan_render_into_environment(combo_widget, selected_display: str, environment_keys: tuple, environment_collection: dict) -> None:
    device_map = getattr(combo_widget, "device_map", {})
    if selected_display in device_map and device_map[selected_display] != "":
        environment_collection["MESA_VK_DEVICE_SELECT"] = device_map[selected_display] + "!"
    else:
        environment_collection["MESA_VK_DEVICE_SELECT"] = selected_display
    for environment_key in environment_keys:
        if environment_key != "MESA_VK_DEVICE_SELECT": environment_collection[environment_key] = ""
    return None


def build_argument_parts_with_suffix(data: dict, parts: list) -> None:
    parts.append(data["command"])
    for flag_name, flag_value in data["flags"]:
        parts.append(flag_name)
        if flag_value != "": parts.append(flag_value)
    parts.append(data["suffix"])
    return None


def build_argument_parts_without_suffix(data: dict, parts: list) -> None:
    parts.append(data["command"])
    for flag_name, flag_value in data["flags"]:
        parts.append(flag_name)
        if flag_value != "": parts.append(flag_value)
    return None


def build_launch_command_string(argument_collection: dict) -> str:
    parts = []
    for target, data in argument_collection.items():
        if data["command"] == "": continue
        if data["suffix"] != "": build_argument_parts_with_suffix(data, parts)
        else: build_argument_parts_without_suffix(data, parts)
    return " ".join(parts)


def build_final_apply_arguments(environment_collection: dict, grouped_environment_collection: dict, argument_collection: dict) -> tuple:
    environment_arguments = []
    for environment_key, environment_value in environment_collection.items():
        environment_arguments.append(environment_key + "=" + environment_value)
    for target, group_data in grouped_environment_collection.items():
        if len(group_data["parts"]) > 0: environment_arguments.append(target + "=" + group_data["joiner"].join(group_data["parts"]))
        else: environment_arguments.append(target + "=")
    launch_command = build_launch_command_string(argument_collection)
    if launch_command != "": environment_arguments.append("launch:" + launch_command)
    return tuple(environment_arguments)


def build_apply_results_from_widgets(widget_collection: dict) -> tuple:
    environment_collection = {}
    grouped_environment_collection = {}
    argument_collection = {}
    for tab_name in get_tabs_with_profile_support():
        for setting_key in find_settings_for_tab(tab_name):
            if widget_collection.get(tab_name + ":" + setting_key) is None: continue
            if not widget_collection[tab_name + ":" + setting_key].isEnabled(): continue
            if parse_widget_value(widget_collection[tab_name + ":" + setting_key]) is None: continue
            process_setting_into_collections(tab_name, setting_key, parse_widget_value(widget_collection[tab_name + ":" + setting_key]), widget_collection, environment_collection, grouped_environment_collection, argument_collection)
    return build_final_apply_arguments(environment_collection, grouped_environment_collection, argument_collection)


def parse_widget_value(combo_widget) -> str:
    if combo_widget.currentText() is None: return None
    if combo_widget.currentText() == "": return None
    if combo_widget.currentText() == "skip": return None
    return combo_widget.currentText()


def get_option_default_value(option_key: str):
    for item_entry in get_setting_items("Options", option_key):
        if get_item_display(item_entry) == "default": return get_item_value(item_entry)
    return None


def get_accent_colors(theme_name: str) -> tuple:
    if theme_name == "amd": return ("#E31937", "#FF2D4A", "#B81430")
    if theme_name == "intel": return ("#0068B5", "#1A8CFF", "#004D87")
    if theme_name == "nvidia": return ("#76B900", "#8ED11A", "#5A8F00")
    return ("#80dbcb", "#9ae4d8", "#66b0a2")
