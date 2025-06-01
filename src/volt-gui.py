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
from extras import ExtrasManager
from options import OptionsTab
from kernel import KernelManager


class ConfigManager:
    """
    Handles saving and loading of application configuration settings.
    """
    
    @staticmethod
    def get_config_path():
        """
        Get the path to the configuration file.
        Returns:
            Path: Path object pointing to the config file
        """
        config_dir = Path(os.path.expanduser("~/.config/volt-gui"))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "volt-config.ini"
    
    @staticmethod
    def save_settings(cpu_widgets, mesa_widgets, nvidia_widgets, kernel_widgets=None):
        """
        Save current settings to the configuration file.
        Args:
            cpu_widgets: Dictionary of CPU settings widgets
            mesa_widgets: Dictionary of Mesa settings widgets
            nvidia_widgets: Dictionary of NVIDIA settings widgets
            kernel_widgets: Dictionary of kernel settings widgets (optional)
        """
        config = configparser.ConfigParser()
        
        # Save CPU settings
        config['CPU'] = {
            'governor': cpu_widgets['gov_combo'].currentText(),
            'scheduler': cpu_widgets['sched_combo'].currentText()
        }
        
        # Save Mesa settings
        config['Mesa'] = {
            'vsync_gl': mesa_widgets['mesa_vsync_gl_combo'].currentText(),
            'vsync_vk': mesa_widgets['mesa_vsync_vk_combo'].currentText(),
            'thread_opt': mesa_widgets['mesa_thread_opt_combo'].currentText(),
            'dither': mesa_widgets['mesa_dither_combo'].currentText(),
            'shader_cache': mesa_widgets['mesa_shader_cache_combo'].currentText(),
            'cache_size': mesa_widgets['mesa_cache_size_combo'].currentText(),
            'error_check': mesa_widgets['mesa_error_check_combo'].currentText(),
            'fake_gl': mesa_widgets['mesa_fake_gl_combo'].currentText(),
            'fake_glsl': mesa_widgets['mesa_fake_glsl_combo'].currentText(),
            'fake_vk': mesa_widgets['mesa_fake_vk_combo'].currentText()
        }
        
        # Save NVIDIA settings
        config['NVIDIA'] = {
            'vsync_gl': nvidia_widgets['nvidia_vsync_gl_combo'].currentText(),
            'thread_opt': nvidia_widgets['nvidia_thread_opt_combo'].currentText(),
            'tex_quality': nvidia_widgets['nvidia_tex_quality_combo'].currentText(),
            'fsaa': nvidia_widgets['nvidia_fsaa_combo'].currentText(),
            'fxaa': nvidia_widgets['nvidia_fxaa_combo'].currentText(),
            'aniso': nvidia_widgets['nvidia_aniso_combo'].currentText(),
            'gsync': nvidia_widgets['nvidia_gsync_combo'].currentText(),
            'shader_cache': nvidia_widgets['nvidia_shader_cache_combo'].currentText(),
            'cache_size': nvidia_widgets['nvidia_cache_size_combo'].currentText(),
            'glsl_ext': nvidia_widgets['nvidia_glsl_ext_combo'].currentText(),
            'glx': nvidia_widgets['nvidia_glx_combo'].currentText()
        }
        
        # Save render selector settings if available
        if GPULaunchManager.render_selector_widgets:
            config['RenderSelector'] = {
                'opengl_render': GPULaunchManager.render_selector_widgets['opengl_render_combo'].currentText(),
                'vulkan_render': GPULaunchManager.render_selector_widgets['vulkan_render_combo'].currentText()
            }
            
        # Save launch options if available
        if hasattr(GPULaunchManager, 'launch_options_widgets'):
            launch_options = GPULaunchManager.launch_options_widgets['launch_options_input'].text().replace('%', '%%')
            config['LaunchOptions'] = {'launch_options': launch_options}
            
        # Save kernel settings if provided
        if kernel_widgets:
            kernel_settings = {}
            for setting_name in KernelManager.KERNEL_SETTINGS.keys():
                value = kernel_widgets[f'{setting_name}_input'].text().strip()
                if value:
                    kernel_settings[setting_name] = value
            if kernel_settings:
                config['Kernel'] = kernel_settings
        
        # Write config to file
        with open(ConfigManager.get_config_path(), 'w') as configfile:
            config.write(configfile)
    
    @staticmethod
    def load_settings(cpu_widgets, mesa_widgets, nvidia_widgets, kernel_widgets=None):
        """
        Load settings from the configuration file.
        Args:
            cpu_widgets: Dictionary of CPU settings widgets to update
            mesa_widgets: Dictionary of Mesa settings widgets to update
            nvidia_widgets: Dictionary of NVIDIA settings widgets to update
            kernel_widgets: Dictionary of kernel settings widgets to update (optional)
        Returns:
            bool: True if settings were loaded successfully, False otherwise
        """
        config = configparser.ConfigParser()
        config_path = ConfigManager.get_config_path()
        
        if not config_path.exists():
            return False
        
        config.read(config_path)
        
        # Load CPU settings
        if 'CPU' in config:
            cpu_widgets['gov_combo'].setCurrentText(config['CPU'].get('governor', 'unset'))
            cpu_widgets['sched_combo'].setCurrentText(config['CPU'].get('scheduler', 'unset'))
        
        # Mapping for Mesa settings
        mesa_mappings = {
            'vsync_gl': 'mesa_vsync_gl_combo',
            'vsync_vk': 'mesa_vsync_vk_combo',
            'thread_opt': 'mesa_thread_opt_combo',
            'dither': 'mesa_dither_combo',
            'shader_cache': 'mesa_shader_cache_combo',
            'cache_size': 'mesa_cache_size_combo',
            'error_check': 'mesa_error_check_combo',
            'fake_gl': 'mesa_fake_gl_combo',
            'fake_glsl': 'mesa_fake_glsl_combo',
            'fake_vk': 'mesa_fake_vk_combo'
        }
        
        # Load Mesa settings
        if 'Mesa' in config:
            for key, widget_key in mesa_mappings.items():
                if key in config['Mesa']:
                    mesa_widgets[widget_key].setCurrentText(config['Mesa'][key])
        
        # Mapping for NVIDIA settings
        nvidia_mappings = {
            'vsync_gl': 'nvidia_vsync_gl_combo',
            'thread_opt': 'nvidia_thread_opt_combo',
            'tex_quality': 'nvidia_tex_quality_combo',
            'fsaa': 'nvidia_fsaa_combo',
            'fxaa': 'nvidia_fxaa_combo',
            'aniso': 'nvidia_aniso_combo',
            'gsync': 'nvidia_gsync_combo',
            'shader_cache': 'nvidia_shader_cache_combo',
            'cache_size': 'nvidia_cache_size_combo',
            'glsl_ext': 'nvidia_glsl_ext_combo',
            'glx': 'nvidia_glx_combo'
        }
        
        # Load NVIDIA settings
        if 'NVIDIA' in config:
            for key, widget_key in nvidia_mappings.items():
                if key in config['NVIDIA']:
                    nvidia_widgets[widget_key].setCurrentText(config['NVIDIA'][key])
        
        # Load render selector settings
        if 'RenderSelector' in config and GPULaunchManager.render_selector_widgets:
            GPULaunchManager.render_selector_widgets['opengl_render_combo'].setCurrentText(
                config['RenderSelector'].get('opengl_render', 'unset'))
            GPULaunchManager.render_selector_widgets['vulkan_render_combo'].setCurrentText(
                config['RenderSelector'].get('vulkan_render', 'unset'))
                
        # Load launch options
        if 'LaunchOptions' in config and hasattr(GPULaunchManager, 'launch_options_widgets'):
            launch_options = config['LaunchOptions'].get('launch_options', '').replace('%%', '%')
            GPULaunchManager.launch_options_widgets['launch_options_input'].setText(launch_options)
                
        # Load kernel settings
        if kernel_widgets and 'Kernel' in config:
            for setting_name, value in config['Kernel'].items():
                if setting_name in KernelManager.KERNEL_SETTINGS:
                    input_widget = kernel_widgets[f'{setting_name}_input']
                    input_widget.setText(value)
                    kernel_widgets[f'{setting_name}_current_value'].setText(f"current value: {value}")
        
        return True


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
        self.sock.close()


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
        
        # Initialize attributes
        self.governor_actions = {}
        self.scheduler_actions = {}
        self.process = None
        self.is_process_running = False
        self.scheduler_process = None
        self.current_scheduler = None
        self.cpu_settings_applied = False
        self.cpu_governor_labels = {}
        
        # Setup UI and load settings
        self.setAttribute(Qt.WA_DontShowOnScreen, True)
        self.apply_dark_theme()
        self.setup_ui()
        self.load_options_settings()
        
        # Setup system tray if enabled
        if self.use_system_tray:
            self.setup_system_tray()
        
        # Start refresh timer
        self.setup_refresh_timer()
        self.load_saved_settings()
        
        # Get original CPU settings
        self.app = QApplication.instance()
        self.setAttribute(Qt.WA_DontShowOnScreen, False)

        try:
            self.original_governor = CPUManager.get_current_governor()
            self.original_scheduler = CPUManager.get_current_scheduler()
        except Exception:
            self.original_governor = "powersave"
            self.original_scheduler = "none"
        
        # Show window if not starting minimized
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
        
        # Add CPU governor menu
        governor_menu = QMenu("CPU Governor", self)
        self.governor_actions = {
            g: QAction(g, self, checkable=True, triggered=lambda _, g=g: self.handle_governor_selection(g))
            for g in CPUManager.get_available_governors()
        }
        for action in self.governor_actions.values():
            governor_menu.addAction(action)
        tray_menu.addMenu(governor_menu)
        
        # Add CPU scheduler menu
        scheduler_menu = QMenu("Pluggable CPU Scheduler", self)
        self.scheduler_actions = {
            s: QAction(s, self, checkable=True, triggered=lambda _, s=s: self.handle_scheduler_selection(s))
            for s in CPUManager.get_available_schedulers()
        }
        for action in self.scheduler_actions.values():
            scheduler_menu.addAction(action)
        tray_menu.addMenu(scheduler_menu)
        
        # Add apply actions
        tray_menu.addAction(QAction("Apply CPU Settings", self, triggered=self.apply_cpu_settings))
        tray_menu.addAction(QAction("Apply Kernel Settings", self, 
            triggered=lambda: KernelManager.apply_kernel_settings(self.kernel_widgets, self)))
        
        # Add quit action
        tray_menu.addSeparator()
        tray_menu.addAction(QAction("Quit", self, triggered=self.quit_application))
        
        # Setup tray icon
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.update_tray_menu_state()

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
        cpu_tab, self.cpu_widgets = CPUManager.create_cpu_tab()
        self.gov_combo = self.cpu_widgets['gov_combo']
        self.sched_combo = self.cpu_widgets['sched_combo']
        self.cpu_apply_button = self.cpu_widgets['cpu_apply_button']
        self.current_sched_value = self.cpu_widgets['current_sched_value']

        # Connect signals
        self.cpu_apply_button.clicked.connect(lambda: self.button_clicked_animation(self.cpu_apply_button))
        self.schedulers = ["none", "scx_bpfland", "scx_flash", "scx_lavd", "scx_rusty"]

        # Initialize values
        self.refresh_cpu_governors()
        self.refresh_current_scheduler()
        self.tab_widget.addTab(cpu_tab, "CPU")
    
    def setup_gpu_tab(self):
        """
        Setup the GPU management tab.
        """
        gpu_tab, _, self.mesa_widgets, self.nvidia_widgets = GPULaunchManager.create_gpu_tab()
        self.mesa_apply_button = self.mesa_widgets['mesa_apply_button']
        self.nvidia_apply_button = self.nvidia_widgets['nvidia_apply_button']
        self.render_selector_apply_button = GPULaunchManager.render_selector_widgets['render_selector_apply_button']

        # Connect signals
        self.mesa_apply_button.clicked.connect(lambda: self.button_clicked_animation(self.mesa_apply_button))
        self.nvidia_apply_button.clicked.connect(lambda: self.button_clicked_animation(self.nvidia_apply_button))
        self.render_selector_apply_button.clicked.connect(
            lambda: self.button_clicked_animation(self.render_selector_apply_button))
        
        self.tab_widget.addTab(gpu_tab, "GPU")
    
    def setup_kernel_tab(self):
        """
        Setup the kernel management tab.
        """
        kernel_tab, self.kernel_widgets = KernelManager.create_kernel_tab()
        self.kernel_apply_button = self.kernel_widgets['kernel_apply_button']
        
        # Connect signals
        self.kernel_apply_button.clicked.connect(lambda: (
            self.button_clicked_animation(self.kernel_apply_button),
            KernelManager.apply_kernel_settings(self.kernel_widgets, self)
        ))
        
        # Install event filters for kernel settings inputs
        for setting_name in KernelManager.KERNEL_SETTINGS.keys():
            self.kernel_widgets[f'{setting_name}_input'].installEventFilter(self)
        
        self.tab_widget.addTab(kernel_tab, "Kernel")
    
    def setup_launch_options_tab(self):
        """
        Setup the launch options tab.
        """
        launch_options_tab = GPULaunchManager.create_launch_options_tab()
        self.launch_options_apply_button = GPULaunchManager.launch_options_widgets['apply_button']
        
        # Connect signals
        self.launch_options_apply_button.clicked.connect(
            lambda: self.button_clicked_animation(self.launch_options_apply_button))
        
        self.tab_widget.addTab(launch_options_tab, "Launch Options")
    
    def setup_extras_tab(self):
        """
        Setup the extras tab.
        """
        extras_tab, _ = ExtrasManager.create_extras_tab()
        self.tab_widget.addTab(extras_tab, "Extras")
        
    def setup_refresh_timer(self):
        """
        Setup timer for periodic UI refreshes.
        """
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_cpu_governors)
        self.refresh_timer.timeout.connect(self.refresh_current_scheduler)
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
    
    def closeEvent(self, event):
        """
        Handle window close event.
        Args:
            event: Close event
        """
        if getattr(self, '_quitting', False):
            event.accept()
            return
        
        if self.use_system_tray:
            event.ignore()
            self.hide()
            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "volt-gui", 
                    "Application is still running in the system tray", 
                    QSystemTrayIcon.MessageIcon.Information, 
                    2000
                )
        else:
            self._quitting = True
            self.quit_application()
            event.accept()
    
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
        ConfigManager.load_settings(
            self.cpu_widgets, 
            self.mesa_widgets, 
            self.nvidia_widgets, 
            self.kernel_widgets
        )
    
    def save_settings(self):
        """
        Save current settings to configuration file.
        """
        ConfigManager.save_settings(
            self.cpu_widgets, 
            self.mesa_widgets, 
            self.nvidia_widgets, 
            self.kernel_widgets
        )
    
    def apply_cpu_settings(self):
        """
        Apply CPU governor and scheduler settings.
        """
        if self.is_process_running:
            return

        governor = self.gov_combo.currentText()
        scheduler = self.sched_combo.currentText()
        current_running_scheduler = CPUManager.get_current_scheduler()

        # Handle case where scheduler is already running
        if scheduler != "unset" and scheduler == current_running_scheduler:
            current_governor = CPUManager.get_current_governor()
            if governor != "unset" and governor != current_governor:
                self.animate_button_click(self.cpu_apply_button)
                self.cpu_apply_button.setEnabled(False)
                self.process = QProcess()
                self.process.start("pkexec", ["/usr/local/bin/volt-cpu", governor, "unset"])
                self.process.finished.connect(self.on_process_finished)
                self.is_process_running = True
                self.cpu_settings_applied = True
                self.save_settings()
            else:
                self.save_settings()
                if hasattr(self, 'tray_icon'):
                    self.tray_icon.showMessage(
                        "volt-gui", 
                        "Settings already applied", 
                        QSystemTrayIcon.MessageIcon.Information, 
                        2000
                    )
            return

        # Apply both governor and scheduler
        self.animate_button_click(self.cpu_apply_button)
        self.cpu_apply_button.setEnabled(False)

        self.process = QProcess()
        self.process.start("pkexec", ["/usr/local/bin/volt-cpu", governor, scheduler])
        self.process.finished.connect(self.on_process_finished)
        self.is_process_running = True
        self.cpu_settings_applied = True
        self.current_scheduler = scheduler if scheduler != "unset" else None
        self.save_settings()
    
    def reset_cpu_governor(self):
        """
        Reset CPU governor to original setting.
        """
        if self.restore_cpu_on_close and self.cpu_settings_applied:
            process = QProcess()
            process.start("pkexec", ["/usr/local/bin/volt-cpu", self.original_governor, self.original_scheduler])
            process.waitForFinished()

    def refresh_cpu_governors(self):
        """
        Refresh CPU governor information in UI.
        """
        CPUManager.refresh_cpu_governors(self.cpu_widgets)
        self.update_tray_menu_state()

    def refresh_current_scheduler(self):
        """
        Refresh current scheduler information in UI.
        """
        self.current_scheduler = CPUManager.refresh_current_scheduler(self.cpu_widgets)
        self.update_tray_menu_state()
    
    def refresh_kernel_values(self):
        """
        Refresh kernel settings information in UI.
        """
        KernelManager.refresh_values(self.kernel_widgets)
    
    def apply_gpu_settings(self):
        """
        Apply GPU settings.
        """
        if self.is_process_running:
            return
        
        try:
            script_path = GPULaunchManager.write_volt_script_with_all_settings(
                self.mesa_widgets, self.nvidia_widgets)
            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "volt-gui", 
                    f"Settings applied and saved to {script_path}", 
                    QSystemTrayIcon.MessageIcon.Information, 
                    2000
                )
            self.save_settings()
        except Exception as e:
            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "volt-gui", 
                    f"Error: {e}", 
                    QSystemTrayIcon.MessageIcon.Critical, 
                    2000
                )
    
    def on_process_finished(self, exit_code, exit_status):
        """
        Handle process completion.
        """
        self.is_process_running = False
        self.cpu_apply_button.setEnabled(True)
        self.mesa_apply_button.setEnabled(True)
        self.nvidia_apply_button.setEnabled(True)
        
        # Refresh UI
        self.refresh_cpu_governors()
        self.refresh_current_scheduler()
        
        # Show notification
        if hasattr(self, 'tray_icon'):
            self.tray_icon.showMessage(
                "volt-gui", 
                "Settings applied successfully" if exit_code == 0 else "Error applying settings",
                QSystemTrayIcon.MessageIcon.Information if exit_code == 0 else QSystemTrayIcon.MessageIcon.Critical,
                2000
            )
        
        # Clean up process
        if self.process:
            self.process.deleteLater()
            self.process = None
    
    def apply_dark_theme(self):
        """
        Apply dark theme to the application.
        """
        ThemeManager.apply_theme(QApplication.instance())

    def animate_button_click(self, button):
        """
        Animate button click effect.
        """
        shrink_anim = QPropertyAnimation(button, b"size", duration=100, 
            startValue=button.size(), endValue=QSize(button.width()*0.95, button.height()*0.95),
            easingCurve=QEasingCurve.OutQuad)
        
        grow_anim = QPropertyAnimation(button, b"size", duration=100, 
            startValue=QSize(button.width()*0.95, button.height()*0.95), endValue=button.size(),
            easingCurve=QEasingCurve.OutBounce)
        
        shrink_anim.finished.connect(grow_anim.start)
        shrink_anim.start()

    def button_clicked_animation(self, button):
        """
        Handle button click animation and action.
        Args:
            button: Button that was clicked
        """
        self.animate_button_click(button)
        if button in [self.mesa_apply_button, self.nvidia_apply_button, 
                    self.render_selector_apply_button, self.launch_options_apply_button]:
            self.apply_gpu_settings()
        elif button == self.cpu_apply_button:
            self.apply_cpu_settings()

    def quit_application(self):
        """
        Clean up and quit the application.
        """
        self._quitting = True
        
        # Restore CPU settings if needed
        if self.cpu_settings_applied and self.restore_cpu_on_close:
            self.reset_cpu_governor()
        
        # Restore kernel settings if needed
        if self.restore_kernel_on_close and hasattr(self, 'kernel_widgets'):
            try:
                if 'original_values' in self.kernel_widgets:
                    settings_to_restore = [
                        f"{KernelManager.KERNEL_SETTINGS[name]['path']}:{val}"
                        for name, val in self.kernel_widgets['original_values'].items()
                    ]
                    process = QProcess()
                    process.start("pkexec", ["volt-kernel"] + settings_to_restore)
                    process.waitForFinished()
            except Exception as e:
                pass
        
        # Save settings and clean up
        self.save_settings()
        self.instance_checker.cleanup()
        QApplication.quit()

    def handle_show_window_signal(self):
        """
        Handle signal to show the main window.
        """
        self.show_and_activate()

    def update_tray_menu_state(self):
        """
        Update tray menu state based on current settings.
        """
        if not hasattr(self, 'governor_actions') or not hasattr(self, 'scheduler_actions'):
            return
            
        current_governor = self.gov_combo.currentText()
        for governor, action in self.governor_actions.items():
            action.setChecked(governor == current_governor)
        
        current_scheduler = self.sched_combo.currentText()
        for scheduler, action in self.scheduler_actions.items():
            action.setChecked(scheduler == current_scheduler)

    def handle_governor_selection(self, governor):
        """
        Handle CPU governor selection from tray menu.
        Args:
            governor: Selected governor name
        """
        self.gov_combo.setCurrentText(governor)
        self.update_tray_menu_state()
        self.save_settings()

    def handle_scheduler_selection(self, scheduler):
        """
        Handle CPU scheduler selection from tray menu.
        Args:
            scheduler: Selected scheduler name
        """
        self.sched_combo.setCurrentText(scheduler)
        self.update_tray_menu_state()
        self.save_settings()

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
            for setting_name in KernelManager.KERNEL_SETTINGS.keys():
                if obj == self.kernel_widgets[f'{setting_name}_input']:
                    obj.clearFocus()
        return super().eventFilter(obj, event)


def main():
    """
    Main application entry point.
    """
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