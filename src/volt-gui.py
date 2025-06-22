import sys
import os
import glob
import subprocess
import signal
import socket
import threading
import configparser
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QSystemTrayIcon, QMenu, QMessageBox,
    QTabWidget, QCheckBox, QSpinBox, QDoubleSpinBox, QScrollArea, QFrame
)
from PySide6.QtCore import (
    Qt, QEvent, QProcess, Signal, QObject, QTimer, 
    QPropertyAnimation, QEasingCurve, QSize
)
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
    """
    Qt signals for singleton communication.
    """
    show_window = Signal()


class SingleInstanceChecker:
    """
    Ensures only one instance of the application runs at a time.
    """
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
    """
    Main application window with all tabs and functionality.
    """
    def __init__(self, instance_checker):
        """
        Initialize the main window with all components.
        """
        super().__init__()
        self.instance_checker = instance_checker
        self.instance_checker.signals.show_window.connect(self.handle_show_window_signal)
        
        self.setWindowTitle("volt-gui")
        self.setMinimumSize(640, 480)
        
        self.use_system_tray = True
        self.start_minimized = False
        self.restore_cpu_on_close = True
        self.restore_kernel_on_close = True
        self.restore_disk_on_close = True
        
        self.cpu_widgets = {}
        self.kernel_widgets = {}
        self.disk_widgets = {}
        self.gpu_manager = GPULaunchManager()
        self.extras_manager = ExtrasManager()
        
        self.setAttribute(Qt.WA_DontShowOnScreen, True)
        self.apply_dark_theme()
        self.setup_ui()
        self.load_options_settings()
        
        if self.use_system_tray:
            self.setup_system_tray()
        
        self.update_quit_behavior()
        
        self.setup_refresh_timer()
        self.load_saved_settings()
        
        self.original_governor = CPUManager.get_current_governor()
        self.original_scheduler = CPUManager.get_current_scheduler()
        
        self.setAttribute(Qt.WA_DontShowOnScreen, False)
        if not self.start_minimized:
            QTimer.singleShot(0, self.show_and_activate)

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
            
            if 'CPUBehavior' in config and 'restore_on_close' in config['CPUBehavior']:
                self.restore_cpu_on_close = config['CPUBehavior']['restore_on_close'] == 'enable'
            
            if 'KernelBehavior' in config and 'restore_on_close' in config['KernelBehavior']:
                self.restore_kernel_on_close = config['KernelBehavior']['restore_on_close'] == 'enable'
            
            if 'DiskBehavior' in config and 'restore_on_close' in config['DiskBehavior']:
                self.restore_disk_on_close = config['DiskBehavior']['restore_on_close'] == 'enable'

        except Exception as e:
            print(f"Warning: Failed to load options settings: {e}")

    def load_saved_settings(self):
        """
        Load previously saved settings from configuration file.
        """
        try:
            ConfigManager.load_settings(
                self.cpu_widgets, 
                self.gpu_manager, 
                self.kernel_widgets,
                self.disk_widgets
            )
        except Exception as e:
            print(f"Warning: Failed to load settings: {e}")
    
    def save_settings(self):
        """
        Save current settings to configuration file.
        """
        try:
            ConfigManager.save_settings(
                self.cpu_widgets, 
                self.gpu_manager, 
                self.kernel_widgets,
                self.disk_widgets
            )
        except Exception as e:
            print(f"Warning: Failed to save settings: {e}")

    def setup_ui(self):
        """
        Set up the main user interface with all tabs.
        """
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
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
    
    def setup_cpu_tab(self):
        """
        Set up the CPU management tab.
        """
        cpu_tab, self.cpu_widgets = CPUManager.create_cpu_tab()
        
        if 'cpu_apply_button' in self.cpu_widgets:
            self.cpu_widgets['cpu_apply_button'].clicked.connect(self.apply_cpu_settings)
        
        CPUManager.refresh_cpu_values(self.cpu_widgets)
        
        self.tab_widget.addTab(cpu_tab, "CPU")
    
    def setup_disk_tab(self):
        """
        Set up the disk management tab.
        """
        disk_tab, self.disk_widgets = DiskManager.create_disk_tab()
        
        if 'disk_apply_button' in self.disk_widgets:
            self.disk_widgets['disk_apply_button'].clicked.connect(self.apply_disk_settings)
        
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
        
        if GPULaunchManager.mesa_widgets and 'mesa_apply_button' in GPULaunchManager.mesa_widgets:
            GPULaunchManager.mesa_widgets['mesa_apply_button'].clicked.connect(self.apply_gpu_settings)
        
        if GPULaunchManager.nvidia_widgets and 'nvidia_apply_button' in GPULaunchManager.nvidia_widgets:
            GPULaunchManager.nvidia_widgets['nvidia_apply_button'].clicked.connect(self.apply_gpu_settings)
        
        if GPULaunchManager.render_selector_widgets and 'render_selector_apply_button' in GPULaunchManager.render_selector_widgets:
            GPULaunchManager.render_selector_widgets['render_selector_apply_button'].clicked.connect(self.apply_gpu_settings)
        
        self.tab_widget.addTab(gpu_tab, "GPU")
    
    def setup_launch_options_tab(self):
        """
        Set up the launch options tab.
        """
        launch_options_tab = GPULaunchManager._create_launch_options_tab()
        
        if hasattr(self.gpu_manager, 'launch_options_widgets') and 'apply_button' in self.gpu_manager.launch_options_widgets:
            self.gpu_manager.launch_options_widgets['apply_button'].clicked.connect(self.apply_gpu_settings)
        
        self.tab_widget.addTab(launch_options_tab, "Launch Options")
    
    def setup_kernel_tab(self):
        """
        Set up the kernel management tab.
        """
        kernel_tab, self.kernel_widgets = KernelManager.create_kernel_tab(self)
        
        if 'kernel_apply_button' in self.kernel_widgets:
            self.kernel_widgets['kernel_apply_button'].clicked.connect(self.apply_kernel_settings)
        
        if hasattr(KernelManager, 'KERNEL_SETTINGS'):
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
        
        tray_menu.addAction(QAction("Apply CPU Settings", self, triggered=self.apply_cpu_settings))
        tray_menu.addAction(QAction("Apply Disk Settings", self, triggered=self.apply_disk_settings))
        tray_menu.addAction(QAction("Apply Kernel Settings", self, triggered=self.apply_kernel_settings))
        tray_menu.addAction(QAction("Apply GPU and Launch Settings", self, triggered=self.apply_gpu_settings))
        
        tray_menu.addSeparator()
        tray_menu.addAction(QAction("Quit", self, triggered=self.quit_application))
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        if hasattr(self.gpu_manager, 'tray_icon'):
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

    def update_quit_behavior(self):
        """
        Update application quit behavior based on tray usage.
        """
        app = QApplication.instance()
        if app:
            app.setQuitOnLastWindowClosed(not self.use_system_tray)

    def apply_dark_theme(self):
        """
        Apply the default dark theme to the application.
        """
        ThemeManager.apply_theme(QApplication.instance(), "amd")

    def show_and_activate(self):
        """
        Show the window and bring it to the foreground.
        """
        self.showMaximized()
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

    def apply_cpu_settings(self):
        """
        Apply CPU settings and save configuration.
        """
        CPUManager.apply_cpu_settings(self.cpu_widgets, self)
        self.save_settings()
    
    def apply_disk_settings(self):
        """
        Apply disk settings and save configuration.
        """
        DiskManager.apply_disk_settings(self.disk_widgets, self)
        self.save_settings()
    
    def apply_kernel_settings(self):
        """
        Apply kernel settings and save configuration.
        """
        KernelManager.apply_kernel_settings(self.kernel_widgets, self)
        self.save_settings()
    
    def apply_gpu_settings(self):
        """
        Apply GPU and launch settings and save configuration.
        """
        if hasattr(GPULaunchManager, 'mesa_widgets'):
            GPULaunchManager.mesa_widgets = self.gpu_manager.mesa_widgets
        if hasattr(GPULaunchManager, 'nvidia_widgets'):
            GPULaunchManager.nvidia_widgets = self.gpu_manager.nvidia_widgets
        
        success = GPULaunchManager.apply_gpu_launch_settings(
            self.tray_icon if hasattr(self, 'tray_icon') else None
        )
        
        if success:
            self.save_settings()

    def quit_application(self):
        """
        Quit the application and restore settings if configured.
        """
        if self.restore_cpu_on_close:
            CPUManager.restore_cpu_settings(self.cpu_widgets)
        
        if self.restore_kernel_on_close and hasattr(self, 'kernel_widgets'):
            KernelManager.restore_kernel_settings(self.kernel_widgets)

        if self.restore_disk_on_close and hasattr(self, 'disk_widgets'):
            DiskManager.restore_disk_settings(self.disk_widgets)
        
        self.save_settings()
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