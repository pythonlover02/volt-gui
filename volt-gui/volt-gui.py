import configparser
import json
import os
import signal
import socket
import sys
import urllib.request

from typing import Final

from PySide6.QtCore import QProcess
from PySide6.QtCore import Qt
from PySide6.QtCore import QThread
from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QInputDialog
from PySide6.QtWidgets import QListView
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from database import ALL_TABS
from database import APP_VERSION
from database import DEFAULT_PROFILE
from database import DEFAULT_VALUE
from database import OPTIONS_DB
from database import get_about_data
from database import get_option_default_value
from database import get_option_description
from database import get_option_label
from database import get_option_options
from database import resolve_option_value
from presets import build_preset_combo_items
from presets import get_preset_placeholder_label
from presets import is_valid_preset_name
from presets import process_preset_apply
from probe import call_probe_stamp
from profiles import build_config_dir
from profiles import build_options_path
from profiles import find_all_profiles
from profiles import is_reserved_profile_name
from profiles import process_profile_delete
from profiles import process_profile_options_rebuild
from profiles import process_profile_save
from profiles import process_profile_widget_load
from themes import get_standard_button_height
from themes import get_standard_button_width
from themes import process_theme_application
from ui import create_code_block_widget
from ui import create_scrollable_content_area
from ui import create_tab_content_widget
from ui import build_sidebar_container_widget
from ui import get_header_vertical_margin
from welcome import create_welcome_window_widget

UPDATE_URL: Final[str] = "https://api.github.com/repos/pythonlover02/volt-gui/releases/latest"
UPDATE_TIMEOUT_S: Final[int] = 5
SINGLETON_PORT: Final[int] = 47832
OPTIONS_SAVE_DEBOUNCE_MS: Final[int] = 500
NEW_PROFILE_LABEL: Final[str] = "New Profile..."
DELETE_PROFILE_LABEL: Final[str] = "Delete Current"
SCALE_MIN: Final[float] = 0.5
SCALE_MAX: Final[float] = 3.0
DEFAULT_SCALE: Final[str] = "1.0"
PREVIEW_BIN: Final[str] = "volt"
PREVIEW_TARGET: Final[str] = "vkgears"
PREVIEW_POLL_MS: Final[int] = 750
PREVIEW_START_MS: Final[int] = 300
PREVIEW_STOP_MS: Final[int] = 1500
PROBE_FAILED_ERROR: Final[str] = "Could not probe this device.\n\nThe vkgears window failed to run, so volt-gui has nothing to read your hardware with. Every setting fed by the device holds nothing but default until it does, because volt-gui offers no option it has not read.\n\nInstall mesa-demos, which provides vkgears, then restart volt-gui."


def build_preview_args(profile_name: str) -> list:
    return ["--probe", profile_name, "--", PREVIEW_TARGET]


def build_launch_command(profile_name: str) -> str:
    match profile_name == DEFAULT_PROFILE:
        case True:
            return "volt -- %command%"
        case False:
            return "volt " + profile_name + " -- %command%"


def get_persisted_option_value(option_key: str) -> str:
    match build_options_path().exists():
        case False:
            return get_option_default_value(option_key)
        case True:
            parser_instance = configparser.ConfigParser(interpolation=None)
            parser_instance.read(build_options_path())
            saved = parser_instance.get("Options", option_key, fallback="").strip()
            match saved == "":
                case True:
                    return get_option_default_value(option_key)
                case False:
                    return saved


def is_scale_text(raw: str) -> bool:
    return raw.replace(".", "", 1).isdigit()


def resolve_scale_factor(raw: str) -> str:
    match is_scale_text(raw) and SCALE_MIN <= float(raw) <= SCALE_MAX:
        case True:
            return raw
        case False:
            return DEFAULT_SCALE


def get_persisted_option_resolved(option_key: str) -> str:
    return resolve_option_value(option_key, get_persisted_option_value(option_key))


def calculate_initial_scale() -> None:
    os.environ["QT_SCALE_FACTOR"] = resolve_scale_factor(
        get_persisted_option_resolved("interface_scale_factor"))
    return None


def get_widget_option_text(main_window, option_key: str) -> str:
    match main_window.options_widgets.get(option_key):
        case None:
            return DEFAULT_VALUE
        case widget:
            return widget.currentText().strip()


def get_resolved_option_value(main_window, option_key: str) -> str:
    return resolve_option_value(option_key, get_widget_option_text(main_window, option_key))


def is_option_enabled(main_window, option_key: str) -> bool:
    return get_resolved_option_value(main_window, option_key) == "on"


def create_options_tab_widget() -> dict:
    from PySide6.QtWidgets import QFrame
    from PySide6.QtWidgets import QLabel
    from PySide6.QtWidgets import QSizePolicy
    from ui import create_combo_widget
    widget = QWidget()
    options_widgets = {}
    main_layout = QVBoxLayout(widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    container_widget = QWidget()
    container_widget.setProperty("scrollContainer", True)
    content_layout = QVBoxLayout(container_widget)
    content_layout.setSpacing(6)
    content_layout.setContentsMargins(12, 12, 8, 12)
    for option_key in OPTIONS_DB:
        card = QFrame()
        card.setProperty("settingCard", True)
        card.setFrameStyle(QFrame.Box)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(4)
        title_label = QLabel(get_option_label(option_key))
        title_label.setStyleSheet("font-weight: 500; font-size: 11pt;")
        card_layout.addWidget(title_label)
        combo = create_combo_widget(get_option_options(option_key))
        card_layout.addWidget(combo)
        description_label = QLabel(get_option_description(option_key))
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #585858; font-size: 9pt;")
        card_layout.addWidget(description_label)
        content_layout.addWidget(card)
        options_widgets[option_key] = combo
    main_layout.addWidget(create_scrollable_content_area(container_widget), 1)
    return {"tab": widget, "widgets": options_widgets}


def process_profile_list_update(main_window) -> None:
    main_window.profile_selector.blockSignals(True)
    main_window.profile_selector.clear()
    for profile_name in find_all_profiles():
        main_window.profile_selector.addItem(profile_name)
    main_window.profile_selector.insertSeparator(main_window.profile_selector.count())
    main_window.profile_selector.addItem(NEW_PROFILE_LABEL)
    main_window.profile_selector.addItem(DELETE_PROFILE_LABEL)
    main_window.profile_selector.blockSignals(False)
    return None


def process_profile_selector_restore(main_window) -> None:
    main_window.profile_selector.blockSignals(True)
    main_window.profile_selector.setCurrentText(main_window.current_profile)
    main_window.profile_selector.blockSignals(False)
    return None


def process_launch_line_update(main_window) -> None:
    main_window.launch_block.code_editor.setPlainText(build_launch_command(main_window.current_profile))
    return None


def process_profile_change(main_window, profile_name: str) -> None:
    match getattr(main_window, "initial_setup_complete", False):
        case False:
            return None
        case True:
            process_profile_save(main_window.all_widgets, main_window.current_profile)
            main_window.current_profile = profile_name
            process_dropped_notice(
                main_window,
                process_profile_widget_load(main_window.all_widgets, profile_name))
            process_launch_line_update(main_window)
            process_tray_menu_update(main_window)
            process_preview_start(main_window)
            return None


def process_yes_no_dialog(parent_widget, title: str, message: str) -> bool:
    dialog = QMessageBox(parent_widget)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    button_box = dialog.findChild(QDialogButtonBox)
    match button_box is None:
        case False:
            button_box.setCenterButtons(True)
        case True:
            pass
    return dialog.exec() == QMessageBox.Yes


def is_new_profile_name_valid(profile_name: str) -> bool:
    match (profile_name.strip() == "", is_reserved_profile_name(profile_name), profile_name.strip() in find_all_profiles(), "/" in profile_name or "\\" in profile_name or ".." in profile_name):
        case (False, False, False, False):
            return True
        case _:
            return False


def process_new_profile_save(main_window) -> None:
    profile_name, accepted = QInputDialog.getText(main_window, "New Profile", "Profile name:")
    match (accepted, profile_name is not None and is_new_profile_name_valid(profile_name)):
        case (True, True):
            process_profile_save(main_window.all_widgets, main_window.current_profile)
            main_window.current_profile = profile_name.strip()
            process_profile_save(main_window.all_widgets, profile_name.strip())
            process_profile_list_update(main_window)
            process_profile_selector_restore(main_window)
            process_launch_line_update(main_window)
            process_tray_menu_update(main_window)
            process_notification_display(main_window, "Profile '" + profile_name.strip() + "' created.", False)
            return None
        case (True, False):
            process_notification_display(main_window, "Profile name invalid or already exists.", True)
            return None
        case _:
            return None


def process_current_profile_delete(main_window) -> None:
    match main_window.current_profile == DEFAULT_PROFILE:
        case True:
            process_notification_display(main_window, "Cannot delete default profile.", True)
            return None
        case False:
            match process_yes_no_dialog(main_window, "Delete Profile", "Delete profile '" + main_window.current_profile + "'?"):
                case False:
                    return None
                case True:
                    process_profile_delete(main_window.current_profile)
                    main_window.current_profile = DEFAULT_PROFILE
                    process_profile_list_update(main_window)
                    process_profile_selector_restore(main_window)
                    process_profile_widget_load(main_window.all_widgets, DEFAULT_PROFILE)
                    process_launch_line_update(main_window)
                    process_tray_menu_update(main_window)
                    process_notification_display(main_window, "Profile deleted.", False)
                    return None


def process_profile_combo_change(main_window, selected_text: str) -> None:
    match selected_text:
        case s if s == NEW_PROFILE_LABEL:
            process_profile_selector_restore(main_window)
            process_new_profile_save(main_window)
        case s if s == DELETE_PROFILE_LABEL:
            process_profile_selector_restore(main_window)
            process_current_profile_delete(main_window)
        case s:
            process_profile_change(main_window, s)
    return None


def process_preset_combo_change(main_window, selected_text: str) -> None:
    match (selected_text == get_preset_placeholder_label(), is_valid_preset_name(selected_text)):
        case (True, _):
            return None
        case (False, False):
            build_preset_combo_items(main_window.preset_selector)
            return None
        case (False, True):
            match process_yes_no_dialog(main_window, "Apply Preset", "Apply '" + selected_text + "' to '" + main_window.current_profile + "'? All values will be replaced."):
                case True:
                    dropped = process_preset_apply(main_window.all_widgets, selected_text)
                    process_profile_save(main_window.all_widgets, main_window.current_profile)
                    process_notification_display(main_window, "Preset '" + selected_text + "' applied to profile '" + main_window.current_profile + "'.", False)
                    process_dropped_notice(main_window, dropped)
                case False:
                    pass
            build_preset_combo_items(main_window.preset_selector)
            return None


def create_system_tray_widget(main_window) -> None:
    match QSystemTrayIcon.isSystemTrayAvailable():
        case False:
            return None
        case True:
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
    match hasattr(main_window, "profile_submenu"):
        case False:
            return None
        case True:
            main_window.profile_submenu.clear()
            for profile_name in find_all_profiles():
                action = QAction("Apply " + profile_name, main_window)
                action.triggered.connect(lambda checked, bound_profile_name=profile_name: process_profile_apply_from_tray(main_window, bound_profile_name))
                main_window.profile_submenu.addAction(action)
            return None


def process_tray_activation(main_window, activation_reason) -> None:
    match activation_reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
        case False:
            return None
        case True:
            match main_window.isVisible():
                case True:
                    main_window.hide()
                case False:
                    process_window_show(main_window)
            return None


def process_window_show(main_window) -> None:
    match main_window.start_maximized:
        case True:
            main_window.showMaximized()
        case False:
            main_window.show()
    main_window.activateWindow()
    main_window.raise_()
    return None


def process_profile_apply_from_tray(main_window, profile_name: str) -> None:
    match profile_name != main_window.current_profile:
        case True:
            process_profile_save(main_window.all_widgets, main_window.current_profile)
            main_window.current_profile = profile_name
            process_profile_selector_restore(main_window)
            process_profile_widget_load(main_window.all_widgets, profile_name)
            process_launch_line_update(main_window)
        case False:
            pass
    process_all_settings_apply(main_window)
    return None


def process_notification_display(main_window, notification_message: str, is_error: bool) -> None:
    match is_error:
        case True:
            QMessageBox.warning(main_window, "volt-gui", notification_message)
        case False:
            QMessageBox.information(main_window, "volt-gui", notification_message)
    return None


def process_tray_option_update(main_window, tray_enabled: bool) -> None:
    match (main_window.use_system_tray == tray_enabled, tray_enabled, hasattr(main_window, "tray_icon")):
        case (True, _, _):
            main_window.use_system_tray = tray_enabled
        case (False, True, False):
            main_window.use_system_tray = tray_enabled
            create_system_tray_widget(main_window)
        case (False, False, True):
            main_window.use_system_tray = tray_enabled
            main_window.tray_icon.hide()
            main_window.tray_icon.deleteLater()
            delattr(main_window, "tray_icon")
            match main_window.isVisible():
                case False:
                    process_window_show(main_window)
                case True:
                    pass
        case _:
            main_window.use_system_tray = tray_enabled
    match QApplication.instance() is None:
        case False:
            QApplication.instance().setQuitOnLastWindowClosed(not main_window.use_system_tray)
        case True:
            pass
    return None


def process_options_application(main_window) -> None:
    process_theme_application(QApplication.instance(), get_resolved_option_value(main_window, "application_theme"))
    match is_option_enabled(main_window, "window_transparency"):
        case True:
            main_window.setWindowOpacity(0.95)
        case False:
            main_window.setWindowOpacity(1.0)
    process_tray_option_update(main_window, is_option_enabled(main_window, "system_tray_behavior"))
    main_window.start_minimized = is_option_enabled(main_window, "start_window_minimized")
    main_window.start_maximized = is_option_enabled(main_window, "start_window_maximized")
    main_window.show_welcome = is_option_enabled(main_window, "welcome_message_display")
    main_window.check_updates = is_option_enabled(main_window, "automatic_update_check")
    return None


def process_options_save_timer_trigger(main_window) -> None:
    match getattr(main_window, "options_save_timer", None):
        case None:
            main_window.options_save_timer = QTimer(main_window)
            main_window.options_save_timer.setSingleShot(True)
            main_window.options_save_timer.timeout.connect(lambda: process_application_options_save(main_window))
        case _:
            pass
    main_window.options_save_timer.start(OPTIONS_SAVE_DEBOUNCE_MS)
    return None


def process_option_change(main_window) -> None:
    match getattr(main_window, "initial_setup_complete", False):
        case True:
            process_options_save_timer_trigger(main_window)
        case False:
            pass
    return None


def process_application_options_save(main_window) -> None:
    parser_instance = configparser.ConfigParser(interpolation=None)
    parser_instance["Options"] = {
        option_key: main_window.options_widgets[option_key].currentText().strip()
        for option_key in OPTIONS_DB
        if option_key in main_window.options_widgets}
    parser_instance["Profile"] = {"last_active_profile": main_window.current_profile}
    os.makedirs(build_config_dir(), exist_ok=True)
    with open(build_options_path(), "w") as file_handle:
        parser_instance.write(file_handle)
    return None


def process_application_options_load(main_window) -> None:
    parser_instance = configparser.ConfigParser(interpolation=None)
    parser_instance.read(build_options_path())
    for option_key in OPTIONS_DB:
        match option_key in main_window.options_widgets:
            case False:
                continue
            case True:
                saved = parser_instance.get("Options", option_key, fallback=get_option_default_value(option_key))
                main_window.options_widgets[option_key].setCurrentText(saved)
    last_profile = parser_instance.get("Profile", "last_active_profile", fallback=DEFAULT_PROFILE)
    match main_window.profile_selector.findText(last_profile) >= 0:
        case True:
            main_window.profile_selector.blockSignals(True)
            main_window.profile_selector.setCurrentText(last_profile)
            main_window.profile_selector.blockSignals(False)
            main_window.current_profile = last_profile
        case False:
            pass
    process_options_application(main_window)
    return None


def process_preview_stop(main_window) -> None:
    match getattr(main_window, "preview_process", None):
        case None:
            return None
        case worker:
            worker.kill()
            worker.waitForFinished(PREVIEW_STOP_MS)
            main_window.preview_process = None
            return None


def process_probe_failure(main_window) -> None:
    match main_window.probe_error_shown:
        case True:
            return None
        case False:
            main_window.probe_error_shown = True
            process_notification_display(main_window, PROBE_FAILED_ERROR, True)
            return None


def process_preview_error(main_window, process_error) -> None:
    match process_error == QProcess.ProcessError.FailedToStart:
        case True:
            process_probe_failure(main_window)
            return None
        case False:
            return None


def process_preview_exit(main_window, exit_code: int, exit_status) -> None:
    match (exit_status == QProcess.ExitStatus.NormalExit, exit_code):
        case (True, 0):
            return None
        case (True, _):
            process_probe_failure(main_window)
            return None
        case _:
            return None


def process_preview_start(main_window) -> None:
    process_preview_stop(main_window)
    worker = QProcess(main_window)
    worker.errorOccurred.connect(
        lambda process_error: process_preview_error(main_window, process_error))
    worker.finished.connect(
        lambda exit_code, exit_status: process_preview_exit(main_window, exit_code, exit_status))
    worker.start(PREVIEW_BIN, build_preview_args(main_window.current_profile))
    main_window.preview_process = worker
    return None


def process_dropped_notice(main_window, dropped: tuple) -> None:
    match len(dropped):
        case 0:
            return None
        case _:
            process_notification_display(
                main_window,
                "This device cannot provide "
                + ", ".join(key.split(":")[-1].split(".")[-1] for key in dropped)
                + ", reset to default.",
                True)
            return None


def process_probe_rebuild(main_window) -> None:
    process_profile_options_rebuild(main_window.all_widgets)
    process_dropped_notice(
        main_window,
        process_profile_widget_load(main_window.all_widgets, main_window.current_profile))
    return None


def process_probe_poll(main_window) -> None:
    match call_probe_stamp():
        case stamp if stamp == main_window.probe_stamp:
            return None
        case stamp:
            main_window.probe_stamp = stamp
            process_probe_rebuild(main_window)
            return None


def process_all_settings_apply(main_window) -> None:
    process_application_options_save(main_window)
    process_profile_save(main_window.all_widgets, main_window.current_profile)
    process_preview_start(main_window)
    process_notification_display(main_window, "Profile '" + main_window.current_profile + "' saved. Start a game again to pick it up.", False)
    return None


def process_window_close(main_window, singleton_socket, close_event) -> None:
    match (main_window.use_system_tray, hasattr(main_window, "tray_icon")):
        case (True, True):
            main_window.hide()
            close_event.ignore()
            return None
        case _:
            process_cleanup(main_window, singleton_socket)
            QApplication.quit()
            close_event.accept()
            return None


def process_cleanup(main_window, singleton_socket) -> None:
    match getattr(main_window, "options_save_timer", None):
        case None:
            pass
        case timer:
            timer.stop()
    process_preview_stop(main_window)
    process_profile_save(main_window.all_widgets, main_window.current_profile)
    process_application_options_save(main_window)
    match singleton_socket is None:
        case False:
            singleton_socket.close()
        case True:
            pass
    match main_window.welcome_window is None:
        case False:
            main_window.welcome_window.close()
            main_window.welcome_window = None
        case True:
            pass
    return None


def process_application_quit(main_window) -> None:
    process_cleanup(main_window, main_window.singleton_socket)
    QApplication.quit()
    return None


def process_welcome_show(main_window) -> None:
    match main_window.welcome_window is None:
        case True:
            main_window.welcome_window = create_welcome_window_widget()
        case False:
            pass
    main_window.welcome_window.show()
    main_window.welcome_window.activateWindow()
    main_window.welcome_window.raise_()
    return None


def call_fetch_latest_tag() -> str:
    try:
        with urllib.request.urlopen(UPDATE_URL, timeout=UPDATE_TIMEOUT_S) as response:
            payload = json.loads(response.read().decode())
            return str(payload.get("tag_name", "")).lstrip("v")
    except (urllib.error.URLError, ValueError, OSError):
        return ""


def process_updates_check_worker(main_window, worker_thread) -> None:
    latest_tag = call_fetch_latest_tag()
    match latest_tag not in ("", APP_VERSION):
        case True:
            QTimer.singleShot(0, main_window, lambda bound_tag=latest_tag: process_notification_display(main_window, "New version available: " + bound_tag, False))
        case False:
            pass
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
    match lock_socket.connect_ex(lock_name) != 0:
        case True:
            lock_socket.close()
            lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            lock_socket.bind(lock_name)
            return {"socket": lock_socket, "running": False}
        case False:
            lock_socket.close()
            return {"socket": None, "running": True}


def process_signal_handler(main_window, signal_number: int) -> None:
    print("\nReceived signal " + str(signal_number) + ", closing...")
    process_cleanup(main_window, main_window.singleton_socket)
    QApplication.quit()
    sys.exit(0)


def process_signal_handlers_setup(main_window) -> None:
    signal.signal(signal.SIGINT, lambda signal_number, frame: process_signal_handler(main_window, signal_number))
    signal.signal(signal.SIGTERM, lambda signal_number, frame: process_signal_handler(main_window, signal_number))
    return None


def process_create_tab(stacked_widget, all_widgets: dict, options_widgets: dict, tab_name: str) -> None:
    match tab_name:
        case "Options":
            tab_result = create_options_tab_widget()
            options_widgets.update(tab_result["widgets"])
            stacked_widget.addWidget(tab_result["tab"])
        case "About":
            stacked_widget.addWidget(create_tab_content_widget(tab_name, get_about_data())["tab"])
        case _:
            tab_result_settings = create_tab_content_widget(tab_name, None)
            all_widgets.update(tab_result_settings["widgets"])
            stacked_widget.addWidget(tab_result_settings["tab"])
    return None


def create_main_window_widget(singleton_socket):
    window = QMainWindow()
    window.singleton_socket = singleton_socket
    window.check_updates = False
    window.start_maximized = False
    window.start_minimized = False
    window.show_welcome = True
    window.use_system_tray = False
    window.current_profile = DEFAULT_PROFILE
    window.welcome_window = None
    window.preview_process = None
    window.probe_error_shown = False
    window.probe_stamp = call_probe_stamp()
    window.setWindowTitle("volt-gui")
    window.setMinimumSize(620, 380)
    window.setAttribute(Qt.WA_DontShowOnScreen, True)
    process_theme_application(QApplication.instance(), get_persisted_option_resolved("application_theme"))
    central_widget = QWidget()
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(8, 8, 8, 8)
    main_layout.setSpacing(8)
    content_layout = QHBoxLayout()
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(0)
    stacked_widget = QStackedWidget()
    all_widgets = {}
    options_widgets = {}
    for tab_name in ALL_TABS:
        process_create_tab(stacked_widget, all_widgets, options_widgets, tab_name)
    sidebar_container, tab_list = build_sidebar_container_widget(ALL_TABS, stacked_widget)
    window.sidebar_tab_list = tab_list
    content_layout.addWidget(sidebar_container)
    right_content_widget = QWidget()
    right_content_layout = QVBoxLayout(right_content_widget)
    right_content_layout.setContentsMargins(0, 0, 0, 0)
    right_content_layout.setSpacing(0)
    window.launch_block = create_code_block_widget(build_launch_command(DEFAULT_PROFILE))
    launch_wrapper = QWidget()
    launch_wrapper_layout = QVBoxLayout(launch_wrapper)
    launch_wrapper_layout.setContentsMargins(12, get_header_vertical_margin(), 8, 8)
    launch_wrapper_layout.setSpacing(0)
    launch_wrapper_layout.addWidget(window.launch_block)
    right_content_layout.addWidget(launch_wrapper)
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
    bottom_bar_layout.addStretch(1)
    bottom_bar_layout.addWidget(preset_combo, 0, Qt.AlignBottom)
    bottom_bar_layout.addWidget(apply_button, 0, Qt.AlignBottom)
    bottom_bar_layout.addWidget(profile_combo, 0, Qt.AlignBottom)
    bottom_bar_layout.addStretch(1)
    main_layout.addWidget(bottom_bar_widget)
    window.setCentralWidget(central_widget)
    window.all_widgets = all_widgets
    window.options_widgets = options_widgets
    process_profile_list_update(window)
    process_profile_selector_restore(window)
    window.profile_selector.currentTextChanged.connect(lambda text: process_profile_combo_change(window, text))
    window.preset_selector.currentTextChanged.connect(lambda text: process_preset_combo_change(window, text))
    for option_key in options_widgets:
        options_widgets[option_key].currentTextChanged.connect(lambda text, bound_window=window: process_option_change(bound_window))
    process_application_options_load(window)
    process_dropped_notice(
        window,
        process_profile_widget_load(window.all_widgets, window.current_profile))
    process_launch_line_update(window)
    window.initial_setup_complete = True
    window.setAttribute(Qt.WA_DontShowOnScreen, False)
    match QApplication.instance() is None:
        case False:
            QApplication.instance().setQuitOnLastWindowClosed(not window.use_system_tray)
        case True:
            pass
    match window.show_welcome:
        case True:
            QTimer.singleShot(100, lambda: process_welcome_show(window))
        case False:
            pass
    match window.check_updates:
        case True:
            QTimer.singleShot(200, lambda: process_updates_check_async(window))
        case False:
            pass
    match window.start_minimized and window.use_system_tray:
        case False:
            QTimer.singleShot(0, lambda: process_window_show(window))
        case True:
            pass
    window.probe_timer = QTimer(window)
    window.probe_timer.timeout.connect(lambda: process_probe_poll(window))
    window.probe_timer.start(PREVIEW_POLL_MS)
    QTimer.singleShot(PREVIEW_START_MS, lambda: process_preview_start(window))
    window.closeEvent = lambda close_event: process_window_close(window, singleton_socket, close_event)
    return window


def main() -> None:
    match os.environ.get("SUDO_USER") is not None:
        case True:
            print("Error: Do not run with sudo.\nRun as regular user.")
            sys.exit(1)
        case False:
            pass
    singleton_result = validate_singleton_instance(SINGLETON_PORT)
    match singleton_result["running"]:
        case True:
            print("volt-gui is already running.")
            sys.exit(0)
        case False:
            pass
    os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.theme.gnome=false")
    calculate_initial_scale()
    application = QApplication(sys.argv)
    application.setStyle("Fusion")
    application.setQuitOnLastWindowClosed(False)
    window = create_main_window_widget(singleton_result["socket"])
    process_signal_handlers_setup(window)
    sys.exit(application.exec())


match __name__:
    case "__main__":
        main()
