import sys, os, signal, socket, stat, configparser, requests
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QSystemTrayIcon, QMenu, QMessageBox, QFrame, QInputDialog, QSizePolicy, QStackedWidget, QListView, QDialogButtonBox
from PySide6.QtCore import Qt, QProcess, QTimer, QThread
from PySide6.QtGui import QIcon, QCursor, QAction
from database import *
from detection import *
from profiles import *
from presets import *
from themes import *
from ui import *
from welcome import *


def get_application_helper_script_content() -> str:
    return r"""#!/usr/bin/env python3
import sys, os


def process_environment_script_write(volt_script_path, environment_arguments, launch_command):
    unset_lines = []
    set_lines = []
    for environment_argument in environment_arguments:
        if "=" not in environment_argument:
            continue
        env_key = environment_argument.split("=", 1)[0]
        env_value = environment_argument.split("=", 1)[1]
        if env_value == "":
            unset_lines.append("os.environ.pop(" + repr(env_key) + ", None)")
        else:
            set_lines.append("os.environ[" + repr(env_key) + "] = " + repr(env_value))
    script_parts = ["#!/usr/bin/env python3", "import os, sys", ""]
    for line in unset_lines:
        script_parts.append(line)
    if len(unset_lines) > 0:
        script_parts.append("")
    for line in set_lines:
        script_parts.append(line)
    if len(set_lines) > 0:
        script_parts.append("")
    if launch_command != "":
        prefix_items = launch_command.split()
        script_parts.append("prefix = [" + ", ".join(repr(p) for p in prefix_items) + "]")
        script_parts.append("os.execvp(prefix[0], prefix + sys.argv[1:])")
    else:
        script_parts.append("os.execvp(sys.argv[1], sys.argv[1:])")
    open(volt_script_path, "w").write("\n".join(script_parts) + "\n")
    os.chmod(volt_script_path, 0o755)


if __name__ == "__main__":
    current_mode = None
    environment_arguments = []
    script_path = ""
    launch_command = ""
    for command_argument in sys.argv[1:]:
        if command_argument in ("-p", "--path"):
            current_mode = "path"
        elif command_argument in ("-e", "--env"):
            current_mode = "env"
        elif current_mode == "path":
            script_path = command_argument
            current_mode = None
        elif current_mode == "env":
            if command_argument.startswith("launch:"):
                launch_command = command_argument[7:]
            else:
                environment_arguments.append(command_argument)
    if script_path != "":
        process_environment_script_write(script_path, environment_arguments, launch_command)
"""


def get_resolved_option_value(main_window, option_key: str) -> str:
    if main_window.options_widgets.get(option_key) is None: return get_option_default_value(option_key)
    if (main_window.options_widgets[option_key].text().strip() if hasattr(main_window.options_widgets[option_key], "text") else main_window.options_widgets[option_key].currentText().strip()) == "": return get_option_default_value(option_key)
    return main_window.options_widgets[option_key].text().strip() if hasattr(main_window.options_widgets[option_key], "text") else main_window.options_widgets[option_key].currentText().strip()


def is_option_enabled(main_window, option_key: str) -> bool:
    return get_resolved_option_value(main_window, option_key) == "on"


def get_persisted_option_value(option_key: str) -> str:
    if not build_options_path().exists(): return get_option_default_value(option_key)
    parser_instance = configparser.ConfigParser(interpolation=None)
    parser_instance.read(build_options_path())
    if parser_instance.get("Options", option_key, fallback=None) is None: return get_option_default_value(option_key)
    if parser_instance.get("Options", option_key, fallback="").strip() == "": return get_option_default_value(option_key)
    return parser_instance.get("Options", option_key, fallback="").strip()


def calculate_initial_scale() -> float:
    if not str(get_persisted_option_value("interface_scale_factor")).replace(".", "", 1).isdigit(): os.environ["QT_SCALE_FACTOR"] = "1.0"; return 1.0
    os.environ["QT_SCALE_FACTOR"] = str(get_persisted_option_value("interface_scale_factor"))
    return float(get_persisted_option_value("interface_scale_factor"))


def calculate_initial_theme() -> str:
    return get_persisted_option_value("application_theme")


def process_device_detection_complete(main_window, api_type: str) -> None:
    if not hasattr(main_window, "all_widgets"): return None
    setting_key = "opengl_rendering_device" if api_type == "opengl" else "vulkan_rendering_device"
    widget_key = "Render Selector:" + setting_key
    if widget_key not in main_window.all_widgets: return None
    line_edit = main_window.all_widgets[widget_key]
    devices = find_render_devices(api_type).get("devices", ())
    line_edit.index_map = {}
    for device_index, device_name in enumerate(devices, 1):
        line_edit.index_map[str(device_index)] = device_name
    line_edit.device_map = find_render_devices(api_type).get("device_map", {})
    if hasattr(line_edit, "device_label"):
        device_str = ", ".join(str(i + 1) + "=" + name for i, name in enumerate(devices)) if devices else "no devices detected"
        line_edit.device_label.setText("render selector: [value] \u2192 device environment variables\n  " + device_str + "\n  empty = skip, unset = remove from environment")
    return None


def get_profile_action_new_label() -> str:
    return "New Profile..."


def get_profile_action_delete_label() -> str:
    return "Delete Current"


def is_profile_action_item(selected_text: str) -> bool:
    if selected_text == get_profile_action_new_label(): return True
    if selected_text == get_profile_action_delete_label(): return True
    return False


def create_main_sidebar_widget(tab_names: tuple, stacked_widget, main_window) -> QWidget:
    sidebar_container, tab_list = build_sidebar_container_widget(tab_names, stacked_widget)
    main_window.sidebar_tab_list = tab_list
    return sidebar_container


def process_profile_list_update(main_window) -> None:
    main_window.profile_selector.blockSignals(True)
    main_window.profile_selector.clear()
    for profile_name in find_all_profiles():
        main_window.profile_selector.addItem(profile_name)
    main_window.profile_selector.insertSeparator(main_window.profile_selector.count())
    main_window.profile_selector.addItem(get_profile_action_new_label())
    main_window.profile_selector.addItem(get_profile_action_delete_label())
    main_window.profile_selector.blockSignals(False)
    return None


def process_profile_selector_restore(main_window) -> None:
    main_window.profile_selector.blockSignals(True)
    main_window.profile_selector.setCurrentText(main_window.current_profile)
    main_window.profile_selector.blockSignals(False)
    return None


def process_profile_combo_change(main_window, selected_text: str) -> None:
    if selected_text == get_profile_action_new_label():
        process_profile_selector_restore(main_window)
        process_new_profile_save(main_window)
        return None
    if selected_text == get_profile_action_delete_label():
        process_profile_selector_restore(main_window)
        process_current_profile_delete(main_window)
        return None
    process_profile_change(main_window, selected_text)
    return None


def process_profile_change(main_window, profile_name: str) -> None:
    if getattr(main_window, "initial_setup_complete", False) is not True: return None
    process_profile_save(main_window.all_widgets, main_window.current_profile)
    main_window.current_profile = profile_name
    process_profile_widget_load(main_window.all_widgets, profile_name)
    process_tray_menu_update(main_window)
    return None


def process_new_profile_save(main_window) -> None:
    profile_name, accepted = QInputDialog.getText(main_window, "New Profile", "Profile name:")
    if accepted is not True: return None
    if profile_name is None: return None
    if profile_name.strip() == "": return None
    if profile_name.strip().lower() == "default" or profile_name.strip() in find_all_profiles():
        process_notification_display(main_window, "Profile already exists or is reserved.", True)
        return None
    process_profile_save(main_window.all_widgets, main_window.current_profile)
    main_window.current_profile = profile_name.strip()
    process_profile_save(main_window.all_widgets, profile_name.strip())
    process_profile_list_update(main_window)
    main_window.profile_selector.blockSignals(True)
    main_window.profile_selector.setCurrentText(profile_name.strip())
    main_window.profile_selector.blockSignals(False)
    process_tray_menu_update(main_window)
    process_notification_display(main_window, "Profile '" + profile_name.strip() + "' created.", False)
    return None


def process_yes_no_dialog(parent_widget, title: str, message: str) -> bool:
    dialog = QMessageBox(parent_widget)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    button_box = dialog.findChild(QDialogButtonBox)
    if button_box is not None:
        button_box.setCenterButtons(True)
    return dialog.exec() == QMessageBox.Yes


def process_current_profile_delete(main_window) -> None:
    if main_window.current_profile == "Default":
        process_notification_display(main_window, "Cannot delete Default profile.", True)
        return None
    if not process_yes_no_dialog(main_window, "Delete Profile", "Delete profile '" + main_window.current_profile + "'?"):
        return None
    if not process_profile_delete(main_window.current_profile): return None
    main_window.current_profile = "Default"
    process_profile_list_update(main_window)
    main_window.profile_selector.blockSignals(True)
    main_window.profile_selector.setCurrentText("Default")
    main_window.profile_selector.blockSignals(False)
    process_profile_widget_load(main_window.all_widgets, "Default")
    process_tray_menu_update(main_window)
    process_notification_display(main_window, "Profile deleted.", False)
    return None


def create_system_tray_widget(main_window) -> None:
    if not QSystemTrayIcon.isSystemTrayAvailable(): return None
    main_window.tray_icon = QSystemTrayIcon(main_window)
    main_window.tray_icon.setIcon(QIcon.fromTheme("preferences-system"))
    menu = QMenu()
    menu.addAction(QAction("Show", main_window, triggered=lambda: process_window_show(main_window)))
    main_window.profile_submenu = QMenu("Apply Profile", menu)
    process_tray_menu_update(main_window)
    menu.addMenu(main_window.profile_submenu)
    menu.addSeparator()
    menu.addAction(QAction("Quit", main_window, triggered=lambda: process_application_quit(main_window)))
    main_window.tray_icon.setContextMenu(menu)
    main_window.tray_icon.show()
    main_window.tray_icon.activated.connect(lambda activation_reason: process_tray_activation(main_window, activation_reason))
    return None


def process_tray_menu_update(main_window) -> None:
    if not hasattr(main_window, "profile_submenu"): return None
    main_window.profile_submenu.clear()
    for profile_name in find_all_profiles():
        action = QAction("Apply " + profile_name, main_window)
        action.triggered.connect(lambda checked, bound_profile_name=profile_name: process_profile_apply_from_tray(main_window, bound_profile_name))
        main_window.profile_submenu.addAction(action)
    return None


def process_tray_activation(main_window, activation_reason) -> None:
    if activation_reason not in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick): return None
    if main_window.isVisible():
        main_window.hide()
        return None
    process_window_show(main_window)
    return None


def process_window_show(main_window) -> None:
    if main_window.start_maximized: main_window.showMaximized()
    else: main_window.show()
    main_window.activateWindow()
    main_window.raise_()
    return None


def process_profile_apply_from_tray(main_window, profile_name: str) -> None:
    if profile_name != main_window.current_profile:
        process_profile_save(main_window.all_widgets, main_window.current_profile)
        main_window.current_profile = profile_name
        main_window.profile_selector.blockSignals(True)
        main_window.profile_selector.setCurrentText(profile_name)
        main_window.profile_selector.blockSignals(False)
        process_profile_widget_load(main_window.all_widgets, profile_name)
    process_all_settings_apply(main_window)
    return None


def process_preset_combo_change(main_window, selected_text: str) -> None:
    if selected_text == get_preset_placeholder_label(): return None
    if not is_valid_preset_name(selected_text):
        build_preset_combo_items(main_window.preset_selector)
        return None
    if not process_yes_no_dialog(main_window, "Apply Preset", "Apply '" + selected_text + "' to '" + main_window.current_profile + "'? All values will be replaced."):
        build_preset_combo_items(main_window.preset_selector)
        return None
    process_preset_apply(main_window.all_widgets, selected_text)
    process_profile_save(main_window.all_widgets, main_window.current_profile)
    build_preset_combo_items(main_window.preset_selector)
    process_notification_display(main_window, "Preset '" + selected_text + "' applied to profile '" + main_window.current_profile + "'.", False)
    return None


def process_notification_display(main_window, notification_message: str, is_error: bool) -> None:
    if hasattr(main_window, "tray_icon"):
        main_window.tray_icon.showMessage("volt-gui", notification_message, QSystemTrayIcon.MessageIcon.Critical if is_error else QSystemTrayIcon.MessageIcon.Information, 2000)
    elif is_error: QMessageBox.warning(main_window, "volt-gui", notification_message)
    else: QMessageBox.information(main_window, "volt-gui", notification_message)
    return None


def process_options_application(main_window) -> None:
    process_theme_application(QApplication.instance(), get_resolved_option_value(main_window, "application_theme"))
    main_window.setWindowOpacity(0.95 if is_option_enabled(main_window, "window_transparency") else 1.0)
    process_tray_option_update(main_window, is_option_enabled(main_window, "system_tray_behavior"))
    main_window.start_minimized = is_option_enabled(main_window, "start_window_minimized")
    main_window.start_maximized = is_option_enabled(main_window, "start_window_maximized")
    main_window.show_welcome = is_option_enabled(main_window, "welcome_message_display")
    main_window.check_updates = is_option_enabled(main_window, "automatic_update_check")
    main_window.volt_path = get_resolved_option_value(main_window, "volt_script_location")
    raw_scale = get_resolved_option_value(main_window, "interface_scale_factor")
    main_window.scaling_factor = float(raw_scale) if raw_scale.replace(".", "", 1).isdigit() else 1.0
    os.environ["QT_SCALE_FACTOR"] = str(main_window.scaling_factor)
    return None


def process_tray_option_update(main_window, tray_enabled: bool) -> None:
    if main_window.use_system_tray == tray_enabled:
        main_window.use_system_tray = tray_enabled
        return None
    main_window.use_system_tray = tray_enabled
    if tray_enabled:
        if not hasattr(main_window, "tray_icon"): create_system_tray_widget(main_window)
    else:
        if hasattr(main_window, "tray_icon"):
            main_window.tray_icon.hide()
            main_window.tray_icon.deleteLater()
            delattr(main_window, "tray_icon")
            if not main_window.isVisible(): process_window_show(main_window)
    if QApplication.instance() is not None: QApplication.instance().setQuitOnLastWindowClosed(not main_window.use_system_tray)
    return None


def get_options_save_debounce_ms() -> int:
    return 500


def process_options_save_timer_trigger(main_window) -> None:
    if getattr(main_window, "options_save_timer", None) is None:
        main_window.options_save_timer = QTimer(main_window)
        main_window.options_save_timer.setSingleShot(True)
        main_window.options_save_timer.timeout.connect(lambda: process_application_options_save(main_window))
    main_window.options_save_timer.start(get_options_save_debounce_ms())
    return None


def process_option_change(main_window, option_key: str) -> None:
    if getattr(main_window, "initial_setup_complete", False) is not True: return None
    process_options_save_timer_trigger(main_window)
    return None


def process_application_options_save(main_window) -> None:
    parser_instance = configparser.ConfigParser(interpolation=None)
    parser_instance["Options"] = {}
    for setting_key in find_settings_for_tab("Options"):
        if setting_key not in main_window.options_widgets: continue
        widget = main_window.options_widgets[setting_key]
        text = widget.text().strip() if hasattr(widget, "text") else widget.currentText().strip()
        parser_instance["Options"][setting_key] = text
    parser_instance["Profile"] = {"last_active_profile": main_window.current_profile}
    os.makedirs(os.path.dirname(build_options_path()), exist_ok=True)
    with open(build_options_path(), "w") as file_handle:
        parser_instance.write(file_handle)
    return None


def process_application_options_load(main_window) -> None:
    for setting_key in find_settings_for_tab("Options"):
        if setting_key not in main_window.options_widgets: continue
        main_window.options_widgets[setting_key].setText(get_option_default_value(setting_key))
    if not build_options_path().exists():
        process_application_options_save(main_window)
        return None
    parser_instance = configparser.ConfigParser(interpolation=None)
    parser_instance.read(build_options_path())
    for setting_key in find_settings_for_tab("Options"):
        if setting_key not in main_window.options_widgets: continue
        saved_value = parser_instance.get("Options", setting_key, fallback=get_option_default_value(setting_key))
        main_window.options_widgets[setting_key].setText(saved_value if saved_value is not None else "")
    last_profile = parser_instance.get("Profile", "last_active_profile", fallback="Default")
    if main_window.profile_selector.findText(last_profile) >= 0:
        main_window.profile_selector.setCurrentText(last_profile)
        main_window.current_profile = last_profile
    process_options_application(main_window)
    return None


def build_apply_command(volt_path: str, apply_arguments: tuple) -> list:
    if is_path_writable_without_elevation(volt_path):
        return ["/tmp/volt-helper", "-p", volt_path, "-e"] + list(apply_arguments)
    return ["pkexec", "/tmp/volt-helper", "-p", volt_path, "-e"] + list(apply_arguments)


def process_all_settings_apply(main_window) -> None:
    main_window.all_widgets["main_apply_button"].setEnabled(False)
    process_application_options_save(main_window)
    process_profile_save(main_window.all_widgets, main_window.current_profile)
    open("/tmp/volt-helper", "w").write(get_application_helper_script_content())
    os.chmod("/tmp/volt-helper", (stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH))
    command = build_apply_command(main_window.volt_path, build_apply_results_from_widgets(main_window.all_widgets))
    process_instance = QProcess(main_window)
    process_instance.setEnvironment(build_environment_list_from_dict(build_clean_process_environment()))
    process_instance.start(command[0], command[1:])
    process_instance.finished.connect(lambda: process_all_apply_completion(main_window, process_instance.exitCode()))
    return None


def process_all_apply_completion(main_window, exit_code: int) -> None:
    main_window.all_widgets["main_apply_button"].setEnabled(True)
    process_notification_display(main_window, "Settings applied successfully" if exit_code == 0 else "Failed to apply settings", exit_code != 0)
    return None


def process_window_close(main_window, singleton_socket, close_event) -> None:
    if main_window.use_system_tray and hasattr(main_window, "tray_icon"):
        main_window.hide()
        close_event.ignore()
        return None
    process_cleanup(main_window, singleton_socket)
    QApplication.quit()
    close_event.accept()
    return None


def process_cleanup(main_window, singleton_socket) -> None:
    if getattr(main_window, "options_save_timer", None) is not None:
        main_window.options_save_timer.stop()
    process_profile_save(main_window.all_widgets, main_window.current_profile)
    process_application_options_save(main_window)
    if singleton_socket is not None: singleton_socket.close()
    if hasattr(main_window, "welcome_window") and main_window.welcome_window is not None:
        main_window.welcome_window.close()
        main_window.welcome_window = None
    return None


def process_application_quit(main_window) -> None:
    process_cleanup(main_window, main_window.singleton_socket)
    QApplication.quit()
    return None


def process_welcome_show(main_window) -> None:
    if main_window.welcome_window is None: main_window.welcome_window = create_welcome_window_widget()
    main_window.welcome_window.show()
    main_window.welcome_window.activateWindow()
    main_window.welcome_window.raise_()
    return None


def get_update_check_url() -> str:
    return "https://api.github.com/repos/pythonlover02/volt-gui/releases/latest"


def get_update_check_timeout() -> int:
    return 5


def fetch_release_response(url: str, timeout_seconds: int):
    try: return requests.get(url, timeout=timeout_seconds)
    except Exception: return None


def parse_response_json(response):
    if response is None: return None
    if response.status_code != 200: return None
    try: return response.json()
    except Exception: return None


def extract_tag_from_payload(payload) -> str:
    if payload is None: return ""
    if not isinstance(payload, dict): return ""
    if "tag_name" not in payload: return ""
    if payload["tag_name"] is None: return ""
    return str(payload["tag_name"]).lstrip("v")


def fetch_latest_release_tag() -> str:
    return extract_tag_from_payload(parse_response_json(fetch_release_response(get_update_check_url(), get_update_check_timeout())))


def process_updates_check_worker(main_window, worker_thread) -> None:
    latest_tag = fetch_latest_release_tag()
    if latest_tag == "":
        worker_thread.quit()
        return None
    if latest_tag == get_about_version():
        worker_thread.quit()
        return None
    QTimer.singleShot(0, main_window, lambda bound_tag=latest_tag: process_notification_display(main_window, "New version available: " + bound_tag, False))
    worker_thread.quit()
    return None


def process_updates_check_async(main_window) -> None:
    worker_thread = QThread(main_window)
    worker_thread.started.connect(lambda: process_updates_check_worker(main_window, worker_thread))
    worker_thread.finished.connect(worker_thread.deleteLater)
    worker_thread.start()
    return None


def validate_singleton_instance(singleton_port: int) -> dict:
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    lock_name = "\0volt-gui-singleton-" + str(singleton_port)
    bind_result = lock_socket.connect_ex(lock_name)
    if bind_result != 0:
        lock_socket.close()
        lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        lock_socket.bind(lock_name)
        return {"socket": lock_socket, "running": False}
    lock_socket.close()
    return {"socket": None, "running": True}


def process_create_tab(stacked_widget, all_widgets: dict, all_cards: dict, options_widgets: dict, main_window, tab_name: str) -> None:
    if tab_name == "Options":
        tab_result = create_options_tab_content_widget()
        options_widgets.update(tab_result["widgets"])
        stacked_widget.addWidget(tab_result["tab"])
        return None
    if tab_name == "About":
        stacked_widget.addWidget(create_tab_content_widget(tab_name, get_about_data(), True)["tab"])
        return None
    if has_settings(tab_name):
        tab_result_settings = create_tab_content_widget(tab_name, None, False)
        all_widgets.update(tab_result_settings["widgets"])
        all_cards.update(tab_result_settings["cards"])
        stacked_widget.addWidget(tab_result_settings["tab"])
    return None


def build_search_index(main_window) -> None:
    main_window.search_index = {}
    for tab_name in get_tabs_with_profile_support():
        for setting_key in find_settings_for_tab(tab_name):
            card_key = tab_name + ":" + setting_key
            if card_key not in main_window.all_cards: continue
            searchable = " ".join((
                setting_key,
                get_setting_label(tab_name, setting_key),
                get_setting_inputs(tab_name, setting_key),
                get_setting_description(tab_name, setting_key),
            )).lower()
            main_window.search_index[card_key] = searchable
    return None


def matches_search_query(tab_name: str, setting_key: str, query: str) -> bool:
    query_lower = query.lower()
    if query_lower in setting_key.lower(): return True
    if query_lower in get_setting_label(tab_name, setting_key).lower(): return True
    if query_lower in get_setting_inputs(tab_name, setting_key).lower(): return True
    if query_lower in get_setting_description(tab_name, setting_key).lower(): return True
    return False


def process_search_filter(main_window, query: str) -> None:
    query_lower = query.strip().lower()
    affected_containers = set()
    for card_key, card_widget in main_window.all_cards.items():
        if query_lower == "":
            card_widget.setVisible(True)
        else:
            card_widget.setVisible(query_lower in main_window.search_index.get(card_key, ""))
        if card_widget.parentWidget() is not None: affected_containers.add(card_widget.parentWidget())
    for container in affected_containers:
        process_container_relayout(container)
    return None


def create_search_bar_widget(main_window) -> QLineEdit:
    search_bar = QLineEdit()
    search_bar.setPlaceholderText("Search settings...")
    search_bar.setFixedHeight(get_standard_button_height())
    search_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    search_bar.setStyleSheet(
        "QLineEdit { background-color: palette(base); color: palette(text); border: none; border-left: 3px solid transparent; padding: 0px 12px; selection-background-color: palette(highlight); border-radius: 6px; }"
        "QLineEdit:hover { background-color: palette(alternate-base); border: none; border-left: 3px solid palette(highlight); border-radius: 6px; }"
        "QLineEdit:focus { background-color: palette(alternate-base); border: none; border-left: 3px solid palette(highlight); border-radius: 6px; }"
    )
    main_window.search_debounce_timer = QTimer()
    main_window.search_debounce_timer.setSingleShot(True)
    main_window.search_debounce_timer.setInterval(150)
    main_window.search_debounce_timer.timeout.connect(lambda: process_search_filter(main_window, search_bar.text()))
    search_bar.textChanged.connect(lambda query: main_window.search_debounce_timer.start())
    return search_bar


def process_signal_handlers_setup(main_window) -> None:
    signal.signal(signal.SIGINT, lambda signal_number, frame: process_signal_handler(main_window, signal_number))
    signal.signal(signal.SIGTERM, lambda signal_number, frame: process_signal_handler(main_window, signal_number))
    return None


def process_signal_handler(main_window, signal_number: int) -> None:
    print("\nReceived signal " + str(signal_number) + ", closing...")
    process_cleanup(main_window, main_window.singleton_socket)
    QApplication.quit()
    sys.exit(0)


def create_main_window_widget(singleton_socket):
    window = QMainWindow()
    window.singleton_socket = singleton_socket
    window.volt_path = get_option_default_value("volt_script_location")
    window.check_updates = get_option_default_value("automatic_update_check") == "on"
    window.start_maximized = get_option_default_value("start_window_maximized") == "on"
    window.start_minimized = get_option_default_value("start_window_minimized") == "on"
    window.show_welcome = get_option_default_value("welcome_message_display") == "on"
    window.use_system_tray = get_option_default_value("system_tray_behavior") == "on"
    window.scaling_factor = 1.0
    window.current_profile = "Default"
    window.welcome_window = None
    window.setWindowTitle("volt-gui")
    window.setMinimumSize(540, 380)
    window.setAttribute(Qt.WA_DontShowOnScreen, True)
    process_theme_application(QApplication.instance(), calculate_initial_theme())
    process_opengl_detection_async(lambda: process_device_detection_complete(window, "opengl"))
    process_vulkan_detection_async(lambda: process_device_detection_complete(window, "vulkan"))
    central_widget = QWidget()
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(8, 8, 8, 8)
    main_layout.setSpacing(8)
    content_layout = QHBoxLayout()
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(0)
    stacked_widget = QStackedWidget()
    all_widgets = {}
    all_cards = {}
    options_widgets = {}
    for tab_name in get_all_tab_names():
        process_create_tab(stacked_widget, all_widgets, all_cards, options_widgets, window, tab_name)
    content_layout.addWidget(create_main_sidebar_widget(get_all_tab_names(), stacked_widget, window))
    right_content_widget = QWidget()
    right_content_layout = QVBoxLayout(right_content_widget)
    right_content_layout.setContentsMargins(0, 0, 0, 0)
    right_content_layout.setSpacing(0)
    window.search_bar = create_search_bar_widget(window)
    search_wrapper = QWidget()
    search_wrapper_layout = QVBoxLayout(search_wrapper)
    search_wrapper_layout.setContentsMargins(12, get_header_vertical_margin(), 8, 8)
    search_wrapper_layout.setSpacing(0)
    search_wrapper_layout.addWidget(window.search_bar)
    right_content_layout.addWidget(search_wrapper)
    right_content_layout.addWidget(stacked_widget, 1)
    content_layout.addWidget(right_content_widget, 1)
    main_layout.addLayout(content_layout, 1)
    bottom_bar_widget = QWidget()
    bottom_bar_widget.setProperty("buttonContainer", True)
    bottom_bar_layout = QHBoxLayout(bottom_bar_widget)
    bottom_bar_layout.setContentsMargins(8, 8, 8, 8)
    bottom_bar_layout.setSpacing(8)
    bottom_bar_layout.setAlignment(Qt.AlignBottom)
    preset_combo = QComboBox()
    preset_combo.setView(QListView())
    preset_combo.setFixedSize(get_standard_button_width(), get_standard_button_height())
    preset_combo.setFocusPolicy(Qt.ClickFocus)
    window.preset_selector = preset_combo
    build_preset_combo_items(preset_combo)
    profile_combo = QComboBox()
    profile_combo.setView(QListView())
    profile_combo.setFixedSize(get_standard_button_width(), get_standard_button_height())
    profile_combo.setFocusPolicy(Qt.ClickFocus)
    window.profile_selector = profile_combo
    apply_button = QPushButton("Apply")
    apply_button.setFixedSize(get_standard_button_width(), get_standard_button_height())
    apply_button.clicked.connect(lambda: process_all_settings_apply(window))
    selectors_container = QWidget()
    selectors_container.setFixedWidth(get_sidebar_width() - 32)
    selectors_container_layout = QVBoxLayout(selectors_container)
    selectors_container_layout.setContentsMargins(0, 0, 0, 0)
    selectors_container_layout.setSpacing(4)
    preset_row = QWidget()
    preset_row_layout = QHBoxLayout(preset_row)
    preset_row_layout.setContentsMargins(0, 0, 0, 0)
    preset_row_layout.setSpacing(0)
    preset_row_layout.addStretch(1)
    preset_row_layout.addWidget(preset_combo, 0, Qt.AlignBottom)
    preset_row_layout.addStretch(1)
    profile_row = QWidget()
    profile_row_layout = QHBoxLayout(profile_row)
    profile_row_layout.setContentsMargins(0, 0, 0, 0)
    profile_row_layout.setSpacing(0)
    profile_row_layout.addStretch(1)
    profile_row_layout.addWidget(profile_combo, 0, Qt.AlignBottom)
    profile_row_layout.addStretch(1)
    selectors_container_layout.addWidget(preset_row, 0, Qt.AlignBottom)
    selectors_container_layout.addWidget(profile_row, 0, Qt.AlignBottom)
    bottom_bar_layout.addWidget(selectors_container, 0, Qt.AlignBottom)
    bottom_bar_layout.addStretch(1)
    bottom_bar_layout.addWidget(apply_button, 0, Qt.AlignBottom)
    bottom_bar_layout.addStretch(1)

    main_layout.addWidget(bottom_bar_widget)
    all_widgets["main_apply_button"] = apply_button
    window.setCentralWidget(central_widget)
    window.all_widgets = all_widgets
    window.all_cards = all_cards
    window.options_widgets = options_widgets
    process_profile_list_update(window)
    window.profile_selector.setCurrentText(window.current_profile)
    window.profile_selector.currentTextChanged.connect(lambda text: process_profile_combo_change(window, text))
    window.preset_selector.currentTextChanged.connect(lambda text: process_preset_combo_change(window, text))
    for option_key in options_widgets:
        widget = options_widgets[option_key]
        if hasattr(widget, "textChanged"):
            widget.textChanged.connect(lambda text, bound_key=option_key: process_option_change(window, bound_key))
        elif hasattr(widget, "currentTextChanged"):
            widget.currentTextChanged.connect(lambda text, bound_key=option_key: process_option_change(window, bound_key))
    if QApplication.instance() is not None: QApplication.instance().setQuitOnLastWindowClosed(not window.use_system_tray)
    timer_instance = QTimer(window)
    timer_instance.start(5000)
    window.refresh_timer = timer_instance
    process_application_options_load(window)
    process_profile_widget_load(window.all_widgets, window.current_profile)
    window.initial_setup_complete = True
    build_search_index(window)
    window.setAttribute(Qt.WA_DontShowOnScreen, False)
    if window.show_welcome: QTimer.singleShot(100, lambda: process_welcome_show(window))
    if window.check_updates: QTimer.singleShot(200, lambda: process_updates_check_async(window))
    if not (window.start_minimized and window.use_system_tray): QTimer.singleShot(0, lambda: process_window_show(window))
    window.closeEvent = lambda close_event: process_window_close(window, singleton_socket, close_event)
    return window


def main() -> None:
    if os.environ.get("SUDO_USER") is not None:
        print("Error: Do not run with sudo.\nRun as regular user.")
        sys.exit(1)
    singleton_result = validate_singleton_instance(47832)
    if singleton_result["running"]:
        print("volt-gui is already running.")
        sys.exit(0)
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    calculate_initial_scale()
    application = QApplication(sys.argv)
    application.setStyle("Fusion")
    application.setQuitOnLastWindowClosed(False)
    window = create_main_window_widget(singleton_result["socket"])
    application.setQuitOnLastWindowClosed(not window.use_system_tray)
    process_signal_handlers_setup(window)
    sys.exit(application.exec())


if __name__ == "__main__":
    main()
