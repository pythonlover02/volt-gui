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
    Check if the application is being run with sudo and exit if so.
    """

    if os.environ.get('SUDO_USER'):
        print("Error: This application should not be run with sudo.")
        print("Please run as a regular user. The application will request")
        print("elevated privileges when needed through pkexec.")
        sys.exit(1)

class SingletonSignals(QObject):
    """
    Signals for single instance application communication.
    """
    show_window = Signal()


class SingleInstanceChecker:
    """
    Ensures only one instance of the application is running.
    """
    
    def __init__(self, port=47832):
        """
        Initialize the instance checker.  
        Args:
            port: Port number to use for inter-process communication
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
        Returns:
            bool: True if another instance is running, False otherwise
        """
        try:
            self.sock.bind(self.server_address)
            self.start_listener()
            return False
        except socket.error:
            self.signal_first_instance()
            return True
    
    def start_listener(self):
        """Start listening for show window signals."""
        self.sock.listen(1)
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_for_signals, daemon=True)
        self.listener_thread.start()
    
    def listen_for_signals(self):
        """
        Listen for signals from other instances.
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
        Clean up resources.
        """
        self.running = False
        try:
            self.sock.close()
        except:
            pass


class MainWindow(QMainWindow):
    """
    Main application window for volt-gui.
    """
    
    def __init__(self, instance_checker):
        """
        Initialize the main window.    
        Args:
            instance_checker: SingleInstanceChecker instance
        """
        super().__init__()
        self.instance_checker = instance_checker
        self.instance_checker.signals.show_window.connect(self.handle_show_window_signal)
        
        # Window properties
        self.setWindowTitle("volt-gui")
        self.setMinimumSize(640, 480)
        
        # Default settings
        self.use_system_tray = True
        self.start_minimized = False
        self.restore_cpu_on_close = True
        self.restore_kernel_on_close = True
        self.restore_disk_on_close = True
        
        # Initialize widget dictionaries and managers
        self.cpu_widgets = {}
        self.kernel_widgets = {}
        self.disk_widgets = {}
        self.gpu_manager = GPULaunchManager()
        self.extras_manager = ExtrasManager()
        
        # Setup UI and load settings
        self.setAttribute(Qt.WA_DontShowOnScreen, True)
        self.apply_dark_theme()
        self.setup_ui()
        self.load_options_settings()
        
        # Setup system tray if enabled
        if self.use_system_tray:
            self.setup_system_tray()
        
        # Set quit behavior based on system tray usage
        self.update_quit_behavior()
        
        # Start refresh timer
        self.setup_refresh_timer()
        self.load_saved_settings()
        
        # Store original values for restoration
        self.original_governor = CPUManager.get_current_governor()
        self.original_scheduler = CPUManager.get_current_scheduler()
        
        # Show window if not starting minimized
        self.setAttribute(Qt.WA_DontShowOnScreen, False)
        if not self.start_minimized:
            QTimer.singleShot(0, self.show_and_activate)

    def update_quit_behavior(self):
        """
        Update the application's quit behavior based on system tray usage.
        """
        app = QApplication.instance()
        if app:
            app.setQuitOnLastWindowClosed(not self.use_system_tray)

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
            
            # Load system tray setting
            if 'SystemTray' in config and 'run_in_tray' in config['SystemTray']:
                self.use_system_tray = config['SystemTray']['run_in_tray'] == 'enable'
            
            # Load start minimized setting
            if 'StartupBehavior' in config and 'start_minimized' in config['StartupBehavior']:
                # Only start minimized if system tray is enabled
                if self.use_system_tray:
                    self.start_minimized = config['StartupBehavior'].get('start_minimized', 'disable') == 'enable'
                else:
                    self.start_minimized = False
            
            # Load CPU restore setting
            if 'CPUBehavior' in config and 'restore_on_close' in config['CPUBehavior']:
                self.restore_cpu_on_close = config['CPUBehavior']['restore_on_close'] == 'enable'
            
            # Load kernel restore setting
            if 'KernelBehavior' in config and 'restore_on_close' in config['KernelBehavior']:
                self.restore_kernel_on_close = config['KernelBehavior']['restore_on_close'] == 'enable'
            
            # Load disk restore setting
            if 'DiskBehavior' in config and 'restore_on_close' in config['DiskBehavior']:
                self.restore_disk_on_close = config['DiskBehavior']['restore_on_close'] == 'enable'

        except Exception as e:
            print(f"Warning: Failed to load options settings: {e}")

    def setup_system_tray(self):
        """
        Setup system tray icon and menu.
        """
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("preferences-system"))
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Add show action
        tray_menu.addAction(QAction("Show", self, triggered=self.show_and_activate))
        
        # Add apply actions
        tray_menu.addAction(QAction("Apply CPU Settings", self, triggered=self.apply_cpu_settings))
        tray_menu.addAction(QAction("Apply Disk Settings", self, triggered=self.apply_disk_settings))  # Add disk action
        tray_menu.addAction(QAction("Apply Kernel Settings", self, triggered=self.apply_kernel_settings))
        tray_menu.addAction(QAction("Apply GPU and Launch Settings", self, triggered=self.apply_gpu_settings))
        
        # Add quit action
        tray_menu.addSeparator()
        tray_menu.addAction(QAction("Quit", self, triggered=self.quit_application))
        
        # Setup tray icon
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Set tray icon reference for GPU manager
        if hasattr(self.gpu_manager, 'tray_icon'):
            self.gpu_manager.tray_icon = self.tray_icon

    def setup_ui(self):
        """
        Setup the main window UI.
        """
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        # Setup tabs
        self.setup_cpu_tab()
        self.setup_gpu_tab()
        self.setup_disk_tab()
        self.setup_kernel_tab()
        self.setup_launch_options_tab()
        self.setup_extras_tab()
        
        # Add options tab
        self.options_tab = OptionsTab(self.tab_widget, self)
        self.tab_widget.addTab(self.options_tab, "Options")
        
        # Set central widget
        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(central_widget)
    
    def setup_cpu_tab(self):
        """
        Setup the CPU management tab.
        """
        # Create CPU tab using CPUManager
        cpu_tab, self.cpu_widgets = CPUManager.create_cpu_tab()
        
        # Connect the apply button signal (button is now created in CPUManager)
        if 'cpu_apply_button' in self.cpu_widgets:
            self.cpu_widgets['cpu_apply_button'].clicked.connect(self.apply_cpu_settings)
        
        # Initialize CPU values
        CPUManager.refresh_cpu_values(self.cpu_widgets)
        
        # Add tab to tab widget
        self.tab_widget.addTab(cpu_tab, "CPU")
    
    def setup_disk_tab(self):
        """
        Setup the disk management tab.
        """
        # Create disk tab using DiskManager
        disk_tab, self.disk_widgets = DiskManager.create_disk_tab()
        
        # Connect the apply button signal
        if 'disk_apply_button' in self.disk_widgets:
            self.disk_widgets['disk_apply_button'].clicked.connect(self.apply_disk_settings)
        
        # Initialize disk values
        DiskManager.refresh_disk_values(self.disk_widgets)
        
        # Add tab to tab widget
        self.tab_widget.addTab(disk_tab, "Disk")
    
    def setup_gpu_tab(self):
        """
        Setup the GPU tab.
        """
        # Create GPU settings tab (Mesa, NVIDIA, Render Selector)
        gpu_tab, gpu_subtabs = GPULaunchManager._create_gpu_settings_tab()
        
        # Store the widgets in the gpu_manager - access them from class variables
        self.gpu_manager.mesa_widgets = GPULaunchManager.mesa_widgets
        self.gpu_manager.nvidia_widgets = GPULaunchManager.nvidia_widgets
        self.gpu_manager.render_selector_widgets = GPULaunchManager.render_selector_widgets
        
        # Connect apply button signals
        if GPULaunchManager.mesa_widgets and 'mesa_apply_button' in GPULaunchManager.mesa_widgets:
            GPULaunchManager.mesa_widgets['mesa_apply_button'].clicked.connect(self.apply_gpu_settings)
        
        if GPULaunchManager.nvidia_widgets and 'nvidia_apply_button' in GPULaunchManager.nvidia_widgets:
            GPULaunchManager.nvidia_widgets['nvidia_apply_button'].clicked.connect(self.apply_gpu_settings)
        
        if GPULaunchManager.render_selector_widgets and 'render_selector_apply_button' in GPULaunchManager.render_selector_widgets:
            GPULaunchManager.render_selector_widgets['render_selector_apply_button'].clicked.connect(self.apply_gpu_settings)
        
        self.tab_widget.addTab(gpu_tab, "GPU")
    
    def setup_launch_options_tab(self):
        """
        Setup the launch Options Tab.
        """
        launch_options_tab = GPULaunchManager._create_launch_options_tab()
        
        # Connect the apply button signal
        if hasattr(self.gpu_manager, 'launch_options_widgets') and 'apply_button' in self.gpu_manager.launch_options_widgets:
            self.gpu_manager.launch_options_widgets['apply_button'].clicked.connect(self.apply_gpu_settings)
        
        self.tab_widget.addTab(launch_options_tab, "Launch Options")
    
    def setup_kernel_tab(self):
        """
        Setup the kernel management tab.
        """
        kernel_tab, self.kernel_widgets = KernelManager.create_kernel_tab(self)
        
        # Connect signals
        if 'kernel_apply_button' in self.kernel_widgets:
            self.kernel_widgets['kernel_apply_button'].clicked.connect(self.apply_kernel_settings)
        
        # Install event filters for kernel settings inputs
        if hasattr(KernelManager, 'KERNEL_SETTINGS'):
            for setting_name in KernelManager.KERNEL_SETTINGS.keys():
                widget_key = f'{setting_name}_input'
                if widget_key in self.kernel_widgets:
                    self.kernel_widgets[widget_key].installEventFilter(self)
        
        # Initialize values
        KernelManager.refresh_kernel_values(self.kernel_widgets)
        self.tab_widget.addTab(kernel_tab, "Kernel")
    
    def setup_extras_tab(self):
        """
        Setup the extras tab.
        """
        extras_tab, _ = self.extras_manager.create_extras_tab()  # Use instance method
        self.tab_widget.addTab(extras_tab, "Extras")
        
    def setup_refresh_timer(self):
        """
        Setup timer for periodic UI refreshes.
        """
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_cpu_values)
        self.refresh_timer.timeout.connect(self.refresh_disk_values)  # Add disk refresh
        self.refresh_timer.timeout.connect(self.refresh_kernel_values)
        self.refresh_timer.start(5000)
    
    def show_and_activate(self):
        """
        Show and activate the main window.
        """
        self.showMaximized()
        self.activateWindow()
        self.raise_()
    
    def tray_icon_activated(self, reason):
        """
        Handle tray icon activation.        
        Args:
            reason: Activation reason (click, double-click, etc.)
        """
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.hide() if self.isVisible() else self.show_and_activate()
    
    def changeEvent(self, event):
        """
        Handle window state change events.
        Args:
            event: Change event
        """
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            event.ignore()
            self.hide()
            return
        
        super().changeEvent(event)
    
    def load_saved_settings(self):
        """
        Load saved settings from configuration file.
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
    
    def apply_cpu_settings(self):
        """
        Apply CPU governor and scheduler settings using CPUManager.
        """
        CPUManager.apply_cpu_settings(self.cpu_widgets, self)
        self.save_settings()
    
    def refresh_cpu_values(self):
        """
        Refresh CPU governor and current scheduler information in UI.
        """
        CPUManager.refresh_cpu_values(self.cpu_widgets)
    
    def apply_disk_settings(self):
        """
        Apply disk scheduler settings using DiskManager.
        """
        DiskManager.apply_disk_settings(self.disk_widgets, self)
        self.save_settings()
    
    def refresh_disk_values(self):
        """
        Refresh disk scheduler information in UI.
        """
        DiskManager.refresh_disk_values(self.disk_widgets)
    
    def refresh_kernel_values(self):
        """
        Refresh kernel settings information in UI.
        """
        KernelManager.refresh_kernel_values(self.kernel_widgets)
    
    def apply_kernel_settings(self):
        """
        Apply kernel settings using KernelManager.
        """
        KernelManager.apply_kernel_settings(self.kernel_widgets, self)
        self.save_settings()
    
    def apply_gpu_settings(self):
        """
        Apply GPU and launch settings.
        """
        # Ensure the class variables are set with the current instance widgets
        if hasattr(GPULaunchManager, 'mesa_widgets'):
            GPULaunchManager.mesa_widgets = self.gpu_manager.mesa_widgets
        if hasattr(GPULaunchManager, 'nvidia_widgets'):
            GPULaunchManager.nvidia_widgets = self.gpu_manager.nvidia_widgets
        
        success = GPULaunchManager.apply_gpu_launch_settings(
            self.tray_icon if hasattr(self, 'tray_icon') else None
        )
        
        # Save settings after applying
        if success:
            self.save_settings()
    
    def apply_dark_theme(self):
        """
        Apply dark theme to the application.
        """
        ThemeManager.apply_theme(QApplication.instance(), "amd")

    def quit_application(self):
        """
        Clean up and quit the application.
        """
        # Restore CPU settings if needed
        if self.restore_cpu_on_close:
            CPUManager.restore_cpu_settings(self.cpu_widgets)
        
        # Restore kernel settings if needed
        if self.restore_kernel_on_close and hasattr(self, 'kernel_widgets'):
            KernelManager.restore_kernel_settings(self.kernel_widgets)

        # Restore disk settings if needed
        if self.restore_disk_on_close and hasattr(self, 'disk_widgets'):
            DiskManager.restore_disk_settings(self.disk_widgets)
        
        # Save settings and clean up
        self.save_settings()
        self.instance_checker.cleanup()
        QApplication.quit()

    def handle_show_window_signal(self):
        """
        Handle signal to show the main window.
        """
        self.show_and_activate()

    def eventFilter(self, obj, event):
        """
        Filter events for kernel settings inputs.
        Args:
            obj: Object that received the event
            event: Event object
        Returns:
            bool: True if event should be filtered, False otherwise
        """
        if event.type() == QEvent.FocusOut:
            if hasattr(KernelManager, 'KERNEL_SETTINGS'):
                for setting_name in KernelManager.KERNEL_SETTINGS.keys():
                    widget_key = f'{setting_name}_input'
                    if widget_key in self.kernel_widgets and obj == self.kernel_widgets[widget_key]:
                        obj.clearFocus()
        return super().eventFilter(obj, event)

def main():
    """
    Main application entry point.
    """
    # DONT RUN WITH SUDO FFS
    check_sudo_execution()

    # Create application instance
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setQuitOnLastWindowClosed(False)
    
    # Handle scheduler command if launched as a scheduler
    if len(sys.argv) > 1:
        scheduler_name = sys.argv[0].split('/')[-1]
        if scheduler_name in ["scx_bpfland", "scx_flash", "scx_lavd", "scx_rusty"]:
            sys.exit(subprocess.run([scheduler_name] + sys.argv[1:]).returncode)
    
    # Check for existing instance
    instance_checker = SingleInstanceChecker()
    if instance_checker.is_already_running():
        QMessageBox.information(None, "volt-gui", "The application is already running and will be displayed.")
        sys.exit(0)
    
    # Create and show main window
    main_window = MainWindow(instance_checker)
    app.setQuitOnLastWindowClosed(not main_window.use_system_tray)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()