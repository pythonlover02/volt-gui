import sys, os
from mesa import *
from nvidia import *
from render import *
from proton import *
from dxvk import *
from vkd3d import *
from gamescope import *
from mangohud import *
from lsfg import *
from launch import *
from options import *
from about import *


def build_settings_database() -> dict:
    return {
        "Mesa": get_mesa_settings(),
        "NVIDIA Proprietary": get_nvidia_settings(),
        "Render Selector": get_render_settings(),
        "Proton": get_proton_settings(),
        "DXVK": get_dxvk_settings(),
        "VKD3D": get_vkd3d_settings(),
        "Gamescope": get_gamescope_settings(),
        "MangoHud": get_mangohud_settings(),
        "LSFG": get_lsfg_settings(),
        "Launch Options": get_launch_settings(),
        "Options": get_options_settings(),
        "About": get_about_settings(),
    }


def get_settings_database(cache=[None]) -> dict:
    if cache[0] is None: cache[0] = build_settings_database()
    return cache[0]


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
    return output[4]


def get_output_sub_environment_variable(output: tuple) -> str:
    return output[2]


def get_output_sub_argument(output: tuple) -> str:
    return output[3]


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
    return [format_environment_pair(key_value) for key_value in environment_dict.items()]


def is_not_frozen_restricted_key(key_value_pair: tuple) -> bool:
    return key_value_pair[0] not in ("LD_LIBRARY_PATH", "LD_PRELOAD")


def filter_frozen_environment_variables(environment_variables: dict) -> dict:
    if getattr(sys, "frozen", False) is False: return environment_variables
    return dict(filter(is_not_frozen_restricted_key, environment_variables.items()))


def build_filtered_path_string(path_value: str) -> str:
    return os.pathsep.join(path_entry for path_entry in path_value.split(os.pathsep) if getattr(sys, "_MEIPASS", "") not in path_entry)


def filter_meipass_from_path(environment_variables: dict) -> dict:
    if getattr(sys, "_MEIPASS", None) is None: return environment_variables
    if "PATH" not in environment_variables: return environment_variables
    return {**environment_variables, "PATH": build_filtered_path_string(environment_variables["PATH"])}


def build_clean_process_environment() -> dict:
    return filter_meipass_from_path(filter_frozen_environment_variables(os.environ.copy()))


def is_path_writable_without_elevation(file_path: str) -> bool:
    if os.path.exists(file_path): return os.access(file_path, os.W_OK)
    return os.access(os.path.dirname(file_path) or ".", os.W_OK)


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
        if get_output_sub_argument(output) != "":
            grouped_environment_collection[target]["parts"].append(get_output_sub_argument(output))
        elif get_output_sub_environment_variable(output) != "":
            grouped_environment_collection[target]["parts"].append(get_output_sub_environment_variable(output) + value)
        else:
            grouped_environment_collection[target]["parts"].append(value)
        return None
    environment_collection[target] = "" if value == "unset" else value
    return None


def build_argument_value_from_output(output: tuple, value: str) -> str:
    target = get_output_target(output)
    if target == "": return value
    if target.endswith("=") or target.endswith(" "): return target + value
    return target


def process_argument_setting(output: tuple, tab_name: str, value: str, argument_collection: list) -> None:
    if value == "unset": return None
    argument_collection.append((tab_name, build_argument_value_from_output(output, value)))
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
        process_argument_setting(output, tab_name, value, argument_collection)
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
    gamescope_parts = tuple(value for tab, value in argument_collection if tab == "Gamescope")
    other_parts = tuple(value for tab, value in argument_collection if tab != "Gamescope")
    if len(other_parts) == 0: return " ".join(gamescope_parts)
    return " ".join(gamescope_parts) + " -- " + " ".join(other_parts)


def build_launch_command_string(argument_collection: tuple) -> str:
    if len(argument_collection) == 0: return ""
    if argument_collection[0][1] == "gamescope": return build_gamescope_command_string(argument_collection)
    return " ".join(value for tab, value in argument_collection)


def is_grouped_target_overridden(environment_key: str, grouped_environment_collection: dict) -> bool:
    if environment_key not in grouped_environment_collection: return False
    return len(grouped_environment_collection[environment_key]["parts"]) > 0


def build_final_apply_arguments(environment_collection: dict, grouped_environment_collection: dict, argument_collection: list) -> tuple:
    environment_arguments = [environment_key + "=" + environment_value for environment_key, environment_value in environment_collection.items() if not is_grouped_target_overridden(environment_key, grouped_environment_collection)]
    for target, group_data in grouped_environment_collection.items():
        if len(group_data["parts"]) > 0:
            environment_arguments.append(target + "=" + group_data["separator"].join(group_data["parts"]))
        else:
            environment_arguments.append(target + "=")
    launch_command = build_launch_command_string(argument_collection)
    if launch_command != "": environment_arguments.append("launch:" + launch_command)
    return tuple(environment_arguments)


def build_argument_mapping_display(output: tuple) -> str:
    if get_output_target(output) == "": return "argument: [value] \u2192 [value]"
    if get_output_target(output).endswith("=") or get_output_target(output).endswith(" "): return "argument: [value] \u2192 " + get_output_target(output) + "[value]"
    return "argument: [value] \u2192 " + get_output_target(output)


def build_plain_environment_variable_mapping_display(output: tuple) -> str:
    return "environment variable: [value] \u2192 " + get_output_target(output) + "=[value]"


def build_grouped_environment_variable_mapping_display(output: tuple) -> str:
    if get_output_sub_argument(output) != "": return "environment variable: [value] \u2192 " + get_output_target(output) + "=..." + get_output_separator(output) + get_output_sub_argument(output) + get_output_separator(output) + "..."
    if get_output_sub_environment_variable(output) != "": return "environment variable: [value] \u2192 " + get_output_target(output) + "=..." + get_output_separator(output) + get_output_sub_environment_variable(output) + "[value]" + get_output_separator(output) + "..."
    return "environment variable: [value] \u2192 " + get_output_target(output) + "=..." + get_output_separator(output) + "[value]" + get_output_separator(output) + "..."


def build_environment_variable_mapping_display(output: tuple) -> str:
    if get_output_separator(output) != "": return build_grouped_environment_variable_mapping_display(output)
    return build_plain_environment_variable_mapping_display(output)


def build_setting_mapping_display(category_name: str, setting_name: str) -> str:
    if is_render_selector_setting(category_name, setting_name): return "render selector: [value] \u2192 device environment variables"
    if is_output_type_argument(get_setting_output(category_name, setting_name)): return build_argument_mapping_display(get_setting_output(category_name, setting_name))
    if is_output_type_environment_variable(get_setting_output(category_name, setting_name)): return build_environment_variable_mapping_display(get_setting_output(category_name, setting_name))
    if is_output_type_option(get_setting_output(category_name, setting_name)): return "option: [value] \u2192 application preference"
    return ""


def is_identity_input_pair(pair_text: str) -> bool:
    if "=" not in pair_text.strip(): return True
    return pair_text.strip().split("=", 1)[0].strip() == pair_text.strip().split("=", 1)[1].strip()


def is_toggle_setting_input(inputs_text: str) -> bool:
    if "," in inputs_text: return False
    if "=" not in inputs_text: return False
    return inputs_text.strip().split("=", 1)[0].strip() == "value"


def format_input_pair_display(pair_text: str) -> str:
    if "=" not in pair_text.strip(): return pair_text.strip()
    if is_identity_input_pair(pair_text): return pair_text.strip().split("=", 1)[0].strip()
    return pair_text.strip().split("=", 1)[0].strip() + " = " + pair_text.strip().split("=", 1)[1].strip()


def build_setting_values_display(inputs_text: str) -> str:
    if is_toggle_setting_input(inputs_text) is True: return "any value that isn\u2019t unset"
    return ", ".join(format_input_pair_display(pair) for pair in inputs_text.split(",") if pair.strip() != "")


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
