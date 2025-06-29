import sys
import os
import glob
import subprocess
import signal
import socket
import threading
import configparser
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QSystemTrayIcon, QMenu, QMessageBox, QTabWidget, QCheckBox, QSpinBox, QDoubleSpinBox, QScrollArea, QFrame, QInputDialog)
from PySide6.QtCore import Qt, QEvent, QProcess, Signal, QObject, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QIcon, QAction
from theme import ThemeManager
from gpu_launch import GPULaunchManager
from cpu import CPUManager
from disk import DiskManager
from extras import ExtrasManager
from options import OptionsTab
from kernel import KernelManager
from config import ConfigManager


def check_sudo_execution():
    """
    Check if the application is run with sudo and exit if it is.
    """
    if os.environ.get('SUDO_USER'):
        print("Error: This application should not be run with sudo.")
        print("Please run as a regular user. The application will request")
        print("elevated privileges when needed through pkexec.")
        sys.exit(1)


class SingletonSignals(QObject):
    show_window = Signal()


class SingleInstanceChecker:
    def __init__(self, port=47832):
        """
        Initialize the single instance checker with a specific port.
        """
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', self.port)
        self.signals = SingletonSignals()
        self.listener_thread = None
        self.running = False

    def is_already_running(self):
        """
        Check if another instance is already running.
        """
        try:
            self.sock.bind(self.server_address)
            self.start_listener()
            return False
        except socket.error:
            self.signal_first_instance()
            return True

    def start_listener(self):
        """
        Start listening for signals from other instances.
        """
        self.sock.listen(1)
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_for_signals, daemon=True)
        self.listener_thread.start()

    def listen_for_signals(self):
        """
        Listen for incoming connections from other instances.
        """
        while self.running:
            try:
                connection, _ = self.sock.accept()
                try:
                    self.signals.show_window.emit()
                finally:
                    connection.close()
            except:
                break

    def signal_first_instance(self):
        """
        Signal the first instance to show its window.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(self.server_address)
        except:
            pass

    def cleanup(self):
        """
        Clean up the socket connection.
        """
        self.running = False
        try:
            self.sock.close()
        except:
            pass


class MainWindow(QMainWindow):
    def __init__(self, instance_checker):
        """
        Initialize the main window with all components.
        """
        super().__init__()
        self.instance_checker = instance_checker
        self.use_system_tray = True
        self.start_minimized = False
        self.current_profile = "Default"
        self.cpu_widgets = {}
        self.kernel_widgets = {}
        self.disk_widgets = {}
        self.gpu_manager = GPULaunchManager()
        self.extras_manager = ExtrasManager()

        self.instance_checker.signals.show_window.connect(self.handle_show_window_signal)
        self.setWindowTitle("volt-gui")
        self.setMinimumSize(540, 380)
        self.setAttribute(Qt.WA_DontShowOnScreen, True)

        self.apply_dark_theme()
        self.setup_ui()
        self.load_options_settings()

        if self.use_system_tray:
            self.setup_system_tray()

        self.update_quit_behavior()
        self.setup_refresh_timer()
        self.load_saved_settings()
        self._initial_setup_complete = True

        self.setAttribute(Qt.WA_DontShowOnScreen, False)
        if not self.start_minimized:
            QTimer.singleShot(0, self.show_and_activate)

    def closeEvent(self, event):
        """
        Handle the window close event to save settings and current profile.
        """
        if self.use_system_tray and hasattr(self, 'tray_icon'):
            event.ignore()
            self.hide()
        else:
            self.save_settings()
            self.save_current_profile_preference()
            self.options_tab.options_manager.save_options()
            event.accept()
            self.instance_checker.cleanup()

    def save_current_profile_preference(self):
        """
        Save the currently selected profile as the last used profile.
        """
        config_dir = Path(os.path.expanduser("~/.config/volt-gui"))
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_path = config_dir / "volt-session.ini"
        config = configparser.ConfigParser()
        
        if config_path.exists():
            try:
                config.read(config_path)
            except:
                pass
        
        if not config.has_section('Session'):
            config.add_section('Session')
        
        config.set('Session', 'last_profile', self.current_profile)
        
        try:
            with open(config_path, 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"Warning: Failed to save session config: {e}")

    def load_current_profile_preference(self):
        """
        Load the last used profile from session config.
        """
        config_path = Path(os.path.expanduser("~/.config/volt-gui/volt-session.ini"))
        
        if not config_path.exists():
            return "Default"
        
        config = configparser.ConfigParser()
        try:
            config.read(config_path)
            if config.has_section('Session') and config.has_option('Session', 'last_profile'):
                last_profile = config.get('Session', 'last_profile')
                available_profiles = ConfigManager.get_available_profiles()
                if last_profile in available_profiles:
                    return last_profile
        except Exception as e:
            print(f"Warning: Failed to load session config: {e}")
        
        return "Default"

    def load_options_settings(self):
        """
        Load options settings from configuration file.
        """
        config_path = Path(os.path.expanduser("~/.config/volt-gui/volt-options.ini"))

        if not config_path.exists():
            return

        config = configparser.ConfigParser()
        try:
            config.read(config_path)

            if 'SystemTray' in config and 'run_in_tray' in config['SystemTray']:
                self.use_system_tray = config['SystemTray']['run_in_tray'] == 'enable'

            if 'StartupBehavior' in config and 'start_minimized' in config['StartupBehavior']:
                if self.use_system_tray:
                    self.start_minimized = config['StartupBehavior'].get('start_minimized', 'disable') == 'enable'
                else:
                    self.start_minimized = False

        except Exception as e:
            print(f"Warning: Failed to load options settings: {e}")

    def load_saved_settings(self):
        """
        Load previously saved settings from configuration file.
        """
        try:
            last_profile = self.load_current_profile_preference()
            self.current_profile = last_profile
            
            ConfigManager.load_config(self.cpu_widgets, self.gpu_manager, self.kernel_widgets, self.disk_widgets, self.current_profile)
        except Exception as e:
            print(f"Warning: Failed to load settings: {e}")

    def setup_ui(self):
        """
        Set up the main user interface with all tabs.
        """
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        profile_frame = self.setup_profile_selector()
        main_layout.addWidget(profile_frame)

        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        self.setup_cpu_tab()
        self.setup_gpu_tab()
        self.setup_disk_tab()
        self.setup_kernel_tab()
        self.setup_launch_options_tab()
        self.setup_extras_tab()

        self.options_tab = OptionsTab(self.tab_widget, self)
        self.tab_widget.addTab(self.options_tab, "Options")

        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(central_widget)

    def setup_profile_selector(self):
        """
        Set up the profile selector UI components.
        """
        profile_frame = QFrame()
        profile_frame.setFrameStyle(QFrame.Box)
        profile_frame.setLineWidth(1)
        profile_frame.setObjectName("profileFrame")

        profile_layout = QHBoxLayout(profile_frame)
        profile_layout.setContentsMargins(10, 8, 10, 8)
        profile_layout.setSpacing(10)

        profile_label = QLabel("Profile:")
        profile_label.setMinimumWidth(60)

        self.profile_selector = QComboBox()
        self.profile_selector.setMinimumWidth(200)
        self.update_profile_list()
        self.profile_selector.setCurrentText(self.current_profile)
        self.profile_selector.currentTextChanged.connect(self.on_profile_changed)

        self.save_profile_btn = QPushButton("New Profile")
        self.save_profile_btn.setMaximumWidth(120)
        self.save_profile_btn.clicked.connect(self.save_new_profile)

        self.delete_profile_btn = QPushButton("Delete Profile")
        self.delete_profile_btn.setMaximumWidth(100)
        self.delete_profile_btn.clicked.connect(self.delete_current_profile)

        profile_layout.addWidget(profile_label)
        profile_layout.addWidget(self.profile_selector)
        profile_layout.addStretch()
        profile_layout.addWidget(self.save_profile_btn)
        profile_layout.addWidget(self.delete_profile_btn)
        self.profile_selector.setFocusPolicy(Qt.ClickFocus)

        return profile_frame

    def setup_cpu_tab(self):
        """
        Set up the CPU management tab.
        """
        cpu_tab, self.cpu_widgets = CPUManager.create_cpu_tab()
        if 'cpu_apply_button' in self.cpu_widgets:
            self.cpu_widgets['cpu_apply_button'].clicked.connect(self.apply_all_settings)
        CPUManager.refresh_cpu_values(self.cpu_widgets)
        self.tab_widget.addTab(cpu_tab, "CPU")

    def setup_disk_tab(self):
        """
        Set up the disk management tab.
        """
        disk_tab, self.disk_widgets = DiskManager.create_disk_tab()
        if 'disk_apply_button' in self.disk_widgets:
            self.disk_widgets['disk_apply_button'].clicked.connect(self.apply_all_settings)
        DiskManager.refresh_disk_values(self.disk_widgets)
        self.tab_widget.addTab(disk_tab, "Disk")

    def setup_gpu_tab(self):
        """
        Set up the GPU management tab.
        """
        gpu_tab, gpu_subtabs = GPULaunchManager._create_gpu_settings_tab()
        self.gpu_manager.mesa_widgets = GPULaunchManager.mesa_widgets
        self.gpu_manager.nvidia_widgets = GPULaunchManager.nvidia_widgets
        self.gpu_manager.render_selector_widgets = GPULaunchManager.render_selector_widgets
        self.gpu_manager.frame_control_widgets = GPULaunchManager.frame_control_widgets

        if GPULaunchManager.mesa_widgets and 'mesa_apply_button' in GPULaunchManager.mesa_widgets:
            GPULaunchManager.mesa_widgets['mesa_apply_button'].clicked.connect(self.apply_all_settings)
        if GPULaunchManager.nvidia_widgets and 'nvidia_apply_button' in GPULaunchManager.nvidia_widgets:
            GPULaunchManager.nvidia_widgets['nvidia_apply_button'].clicked.connect(self.apply_all_settings)
        if GPULaunchManager.render_selector_widgets and 'render_selector_apply_button' in GPULaunchManager.render_selector_widgets:
            GPULaunchManager.render_selector_widgets['render_selector_apply_button'].clicked.connect(self.apply_all_settings)
        if GPULaunchManager.frame_control_widgets and 'frame_control_apply_button' in GPULaunchManager.frame_control_widgets:
            GPULaunchManager.frame_control_widgets['frame_control_apply_button'].clicked.connect(self.apply_all_settings)

        self.tab_widget.addTab(gpu_tab, "GPU")

    def setup_launch_options_tab(self):
        """
        Set up the launch options tab.
        """
        launch_options_tab = GPULaunchManager._create_launch_options_tab()

        if 'launch_apply_button' in self.gpu_manager.launch_options_widgets:
            self.gpu_manager.launch_options_widgets['launch_apply_button'].clicked.connect(self.apply_all_settings)

        self.tab_widget.addTab(launch_options_tab, "Launch Options")

    def setup_kernel_tab(self):
        """
        Set up the kernel management tab.
        """
        kernel_tab, self.kernel_widgets = KernelManager.create_kernel_tab(self)

        if 'kernel_apply_button' in self.kernel_widgets:
            self.kernel_widgets['kernel_apply_button'].clicked.connect(self.apply_all_settings)

        if 'KERNEL_SETTINGS' in KernelManager.__dict__:
            for setting_name in KernelManager.KERNEL_SETTINGS.keys():
                widget_key = f'{setting_name}_input'
                if widget_key in self.kernel_widgets:
                    self.kernel_widgets[widget_key].installEventFilter(self)

        KernelManager.refresh_kernel_values(self.kernel_widgets)
        self.tab_widget.addTab(kernel_tab, "Kernel")

    def setup_extras_tab(self):
        """
        Set up the extras/additional features tab.
        """
        extras_tab, _ = self.extras_manager.create_extras_tab()
        self.tab_widget.addTab(extras_tab, "Extras")

    def setup_system_tray(self):
        """
        Set up the system tray icon and menu.
        """
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("preferences-system"))

        tray_menu = QMenu()
        tray_menu.addAction(QAction("Show", self, triggered=self.show_and_activate))

        self.profile_submenu = QMenu("Apply Profile", tray_menu)
        self.update_tray_profile_menu()
        tray_menu.addMenu(self.profile_submenu)

        tray_menu.addSeparator()
        tray_menu.addAction(QAction("Quit", self, triggered=self.quit_application))

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)

        if 'tray_icon' in self.gpu_manager.__dict__:
            self.gpu_manager.tray_icon = self.tray_icon

    def setup_refresh_timer(self):
        """
        Set up the timer for periodic value refresh.
        """
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_cpu_values)
        self.refresh_timer.timeout.connect(self.refresh_disk_values)
        self.refresh_timer.timeout.connect(self.refresh_kernel_values)
        self.refresh_timer.start(5000)

    def update_profile_list(self):
        """
        Update the profile selector with available profiles.
        """
        current_selection = self.profile_selector.currentText()
        self.profile_selector.blockSignals(True)
        self.profile_selector.clear()
        profiles = ConfigManager.get_available_profiles()
        self.profile_selector.addItems(profiles)

        if current_selection in profiles:
            self.profile_selector.setCurrentText(current_selection)
        else:
            self.profile_selector.setCurrentText("Default")

        self.profile_selector.blockSignals(False)
        self.update_tray_profile_menu()

    def update_tray_profile_menu(self):
        """
        Update the tray profile menu with available profiles.
        """
        if not hasattr(self, 'profile_submenu'):
            return

        self.profile_submenu.clear()
        profiles = ConfigManager.get_available_profiles()

        for profile in profiles:
            action = QAction(f"Apply {profile} Profile", self)
            action.triggered.connect(lambda checked, p=profile: self.apply_profile_from_tray(p))
            self.profile_submenu.addAction(action)

    def update_quit_behavior(self):
        """
        Update application quit behavior based on tray usage.
        """
        app = QApplication.instance()
        if app:
            app.setQuitOnLastWindowClosed(not self.use_system_tray)

    def refresh_cpu_values(self):
        """
        Refresh CPU related values in the interface.
        """
        CPUManager.refresh_cpu_values(self.cpu_widgets)

    def refresh_disk_values(self):
        """
        Refresh disk related values in the interface.
        """
        DiskManager.refresh_disk_values(self.disk_widgets)

    def refresh_kernel_values(self):
        """
        Refresh kernel related values in the interface.
        """
        KernelManager.refresh_kernel_values(self.kernel_widgets)

    def save_settings(self):
        """
        Save current settings to configuration file.
        """
        try:
            ConfigManager.save_config(self.cpu_widgets, self.gpu_manager, self.kernel_widgets, self.disk_widgets, self.current_profile)
        except Exception as e:
            print(f"Warning: Failed to save settings: {e}")

    def on_profile_changed(self, profile_name):
        """
        Handle profile selection changes.
        """
        if not profile_name or profile_name == self.current_profile or profile_name.isspace():
            return

        if hasattr(self, '_initial_setup_complete') and self._initial_setup_complete:
            try:
                ConfigManager.save_config(self.cpu_widgets, self.gpu_manager, self.kernel_widgets, self.disk_widgets, self.current_profile)
            except Exception as e:
                print(f"Warning: Failed to save current profile settings: {e}")

        self.current_profile = profile_name
        self.save_current_profile_preference()
        ConfigManager.load_config(self.cpu_widgets, self.gpu_manager, self.kernel_widgets, self.disk_widgets, profile_name)

    def save_new_profile(self):
        """
        Save current settings as a new profile.
        """
        profile_name, ok = QInputDialog.getText(self, "Save New Profile", "Enter profile name:", text="")

        if ok and profile_name and profile_name.strip():
            profile_name = profile_name.strip()

            if not profile_name or profile_name.isspace():
                QMessageBox.warning(self, "Invalid Name", "Profile name cannot be empty or contain only spaces.")
                return

            if profile_name in ConfigManager.get_available_profiles():
                reply = QMessageBox.question(self, "Profile Exists", f"Profile '{profile_name}' already exists. Overwrite?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return

            try:
                ConfigManager.save_config(self.cpu_widgets, self.gpu_manager, self.kernel_widgets, self.disk_widgets, self.current_profile)
                ConfigManager.save_config(self.cpu_widgets, self.gpu_manager, self.kernel_widgets, self.disk_widgets, profile_name)

                self.current_profile = profile_name
                self.save_current_profile_preference()
                self.update_profile_list()
                self.profile_selector.setCurrentText(profile_name)

                if hasattr(self, 'tray_icon') and self.use_system_tray:
                    self.update_tray_profile_menu()

                QMessageBox.information(self, "Profile Saved", f"Profile '{profile_name}' has been saved.")

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save profile '{profile_name}': {str(e)}")

    def delete_current_profile(self):
        """
        Delete the selected profile.
        """
        current_profile = self.profile_selector.currentText()

        if current_profile == "Default":
            QMessageBox.warning(self, "Cannot Delete", "The Default profile cannot be deleted.")
            return

        if not current_profile or current_profile.isspace():
            QMessageBox.warning(self, "Invalid Profile", "Cannot delete an empty or invalid profile.")
            return

        reply = QMessageBox.question(self, "Delete Profile", f"Are you sure you want to delete the '{current_profile}' profile?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                config_dir = Path(os.path.expanduser("~/.config/volt-gui"))
                profile_file = config_dir / f"volt-config-{current_profile}.ini"

                if profile_file.exists():
                    profile_file.unlink()

                    self.current_profile = "Default"
                    self.save_current_profile_preference()
                    self.update_profile_list()
                    self.profile_selector.setCurrentText("Default")

                    ConfigManager.load_config(self.cpu_widgets, self.gpu_manager, self.kernel_widgets, self.disk_widgets, "Default")

                    self.refresh_cpu_values()
                    self.refresh_disk_values()
                    self.refresh_kernel_values()

                    if hasattr(self, 'tray_icon') and self.use_system_tray:
                        self.update_tray_profile_menu()

                    QMessageBox.information(self, "Profile Deleted", f"Profile '{current_profile}' has been deleted.")
                else:
                    QMessageBox.warning(self, "Error", f"Profile file for '{current_profile}' not found.")

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete profile '{current_profile}': {str(e)}")

    def apply_profile_from_tray(self, profile_name):
        """
        Apply a specific profile from the system tray.
        """
        if profile_name != self.current_profile:
            try:
                ConfigManager.save_config(self.cpu_widgets, self.gpu_manager, self.kernel_widgets, self.disk_widgets, self.current_profile)
            except Exception as e:
                print(f"Warning: Failed to save current profile settings: {e}")

            self.current_profile = profile_name
            self.save_current_profile_preference()
            self.profile_selector.setCurrentText(profile_name)
            ConfigManager.load_config(self.cpu_widgets, self.gpu_manager, self.kernel_widgets, self.disk_widgets, profile_name)

            self.refresh_cpu_values()
            self.refresh_disk_values()
            self.refresh_kernel_values()

        self.apply_all_settings()

    def apply_dark_theme(self):
        """
        Apply the default dark theme to the application.
        """
        ThemeManager.apply_theme(QApplication.instance(), "amd")

    def show_and_activate(self):
        """
        Show the window and bring it to the foreground.
        """
        self.show()
        self.activateWindow()
        self.raise_()

    def handle_show_window_signal(self):
        """
        Handle the signal to show the window from another instance.
        """
        self.show_and_activate()

    def tray_icon_activated(self, reason):
        """
        Handle system tray icon activation events.
        """
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.hide() if self.isVisible() else self.show_and_activate()

    def apply_all_settings(self):
        """
        Collects all settings (CPU, Disk, GPU, Kernel) and applies them in one go using volt-helper.
        """
        if (self.cpu_widgets.get('is_process_running', False) or 
            self.disk_widgets.get('is_process_running', False) or 
            self.kernel_widgets.get('is_process_running', False)):
            return

        try:
            self.save_settings()

            cpu_args = []
            cpu_governor = self.cpu_widgets['gov_combo'].currentText()
            cpu_scheduler = self.cpu_widgets['sched_combo'].currentText()
            cpu_parts = []

            if cpu_governor != "unset":
                cpu_parts.append(f"governor:{cpu_governor}")
            if cpu_scheduler != "unset":
                cpu_parts.append(f"scheduler:{cpu_scheduler}")

            if cpu_parts:
                cpu_args.append("-c")
                cpu_args.extend(cpu_parts)

            disk_args = []
            for disk_name, combo in self.disk_widgets['disk_combos'].items():
                selected_scheduler = combo.currentText()
                if selected_scheduler and selected_scheduler != "" and selected_scheduler != "unset":
                    if not disk_args:
                        disk_args.append("-d")
                    disk_args.append(f"{disk_name}:{selected_scheduler}")

            kernel_args = []
            kernel_has_settings = False
            for name, info in KernelManager.KERNEL_SETTINGS.items():
                value = self.kernel_widgets[f'{name}_input'].text().strip()
                if value:
                    if not kernel_args:
                        kernel_args.append("-k")
                    kernel_args.append(f"{info['path']}:{value}")
                    kernel_has_settings = True

            gpu_args = []
            settings_file = GPULaunchManager._write_settings_file()
            if settings_file:
                gpu_args.extend(["-g", settings_file])

            all_args = ["pkexec", "/usr/local/bin/volt-helper"] + cpu_args + disk_args + kernel_args + gpu_args

            process = QProcess()
            process.start(all_args[0], all_args[1:])
            process.finished.connect(lambda: self.on_settings_applied(process.exitCode()))

            if 'cpu_apply_button' in self.cpu_widgets:
                self.cpu_widgets['cpu_apply_button'].setEnabled(False)
            if 'disk_apply_button' in self.disk_widgets:
                self.disk_widgets['disk_apply_button'].setEnabled(False)
            if 'kernel_apply_button' in self.kernel_widgets:
                self.kernel_widgets['kernel_apply_button'].setEnabled(False)
            if 'mesa_apply_button' in self.gpu_manager.mesa_widgets:
                self.gpu_manager.mesa_widgets['mesa_apply_button'].setEnabled(False)
            if 'nvidia_apply_button' in self.gpu_manager.nvidia_widgets:
                self.gpu_manager.nvidia_widgets['nvidia_apply_button'].setEnabled(False)
            if 'render_selector_apply_button' in self.gpu_manager.render_selector_widgets:
                self.gpu_manager.render_selector_widgets['render_selector_apply_button'].setEnabled(False)
            if 'frame_control_apply_button' in self.gpu_manager.frame_control_widgets:
                self.gpu_manager.frame_control_widgets['frame_control_apply_button'].setEnabled(False)
            if 'launch_apply_button' in self.gpu_manager.launch_options_widgets:
                self.gpu_manager.launch_options_widgets['launch_apply_button'].setEnabled(False)

        except Exception as e:
            print(f"Error applying settings: {e}")
            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage("volt-gui", f"Failed to apply settings: {e}", QSystemTrayIcon.MessageIcon.Critical, 2000)
            else:
                QMessageBox.warning(self, "volt-gui", f"Failed to apply settings: {e}")

    def on_settings_applied(self, exit_code):
        """
        Handle the completion of the settings application process.
        """
        if 'cpu_apply_button' in self.cpu_widgets:
            self.cpu_widgets['cpu_apply_button'].setEnabled(True)
        if 'disk_apply_button' in self.disk_widgets:
            self.disk_widgets['disk_apply_button'].setEnabled(True)
        if 'kernel_apply_button' in self.kernel_widgets:
            self.kernel_widgets['kernel_apply_button'].setEnabled(True)
        if 'mesa_apply_button' in self.gpu_manager.mesa_widgets:
            self.gpu_manager.mesa_widgets['mesa_apply_button'].setEnabled(True)
        if 'nvidia_apply_button' in self.gpu_manager.nvidia_widgets:
            self.gpu_manager.nvidia_widgets['nvidia_apply_button'].setEnabled(True)
        if 'render_selector_apply_button' in self.gpu_manager.render_selector_widgets:
            self.gpu_manager.render_selector_widgets['render_selector_apply_button'].setEnabled(True)
        if 'frame_control_apply_button' in self.gpu_manager.frame_control_widgets:
            self.gpu_manager.frame_control_widgets['frame_control_apply_button'].setEnabled(True)
        if 'launch_apply_button' in self.gpu_manager.launch_options_widgets:
            self.gpu_manager.launch_options_widgets['launch_apply_button'].setEnabled(True)

        self.refresh_cpu_values()
        self.refresh_disk_values()
        self.refresh_kernel_values()

        if hasattr(self, 'tray_icon'):
            self.tray_icon.showMessage("volt-gui", "Settings applied successfully" if exit_code == 0 else "Failed to apply settings", QSystemTrayIcon.MessageIcon.Information if exit_code == 0 else QSystemTrayIcon.MessageIcon.Critical, 2000)
        else:
            QMessageBox.information(self, "volt-gui", "Settings applied successfully")

    def quit_application(self):
        """
        Quit the application properly, ensuring all settings are saved.
        """
        self.save_settings()
        self.save_current_profile_preference()
        self.options_tab.options_manager.save_options()
        self.instance_checker.cleanup()
        QApplication.quit()


def main():
    """
    Main application entry point.
    """
    check_sudo_execution()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setQuitOnLastWindowClosed(False)

    instance_checker = SingleInstanceChecker()
    if instance_checker.is_already_running():
        QMessageBox.information(None, "volt-gui", "The application is already running and will be displayed.")
        sys.exit(0)

    main_window = MainWindow(instance_checker)
    app.setQuitOnLastWindowClosed(not main_window.use_system_tray)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()