import os
import configparser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QScrollArea,
    QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt
from theme import ThemeManager
from pathlib import Path
from PySide6.QtWidgets import QApplication


class OptionsManager:
    """
    Manages application settings and preferences.
    Handles loading, saving, and applying various application settings
    including themes, system tray behavior, and window appearance.
    """

    def __init__(self, main_window):
        """
        Initialize the OptionsManager.
        Args:
            main_window: Reference to the main application window
        """
        self.config_path = Path(os.path.expanduser("~/.config/volt-gui/volt-options.ini"))
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.widgets = {}
        self.main_window = main_window
        
    def save_settings(self):
        """
        Save current settings to the configuration file.
        
        Writes all current settings from the UI widgets to the config file
        and applies the settings to the running application.
        """
        config = configparser.ConfigParser()
        
        config['Theme'] = {
            'selected_theme': self.widgets['theme_combo'].currentText()
        }
        config['SystemTray'] = {
            'run_in_tray': self.widgets['tray_combo'].currentText()
        }
        config['Appearance'] = {
            'transparency': self.widgets['transparency_combo'].currentText()
        }
        config['StartupBehavior'] = {
            'start_minimized': self.widgets['start_minimized_combo'].currentText()
        }
        config['CPUBehavior'] = {
            'restore_on_close': self.widgets['restore_cpu_combo'].currentText()
        }
        config['KernelBehavior'] = {
            'restore_on_close': self.widgets['restore_kernel_combo'].currentText()
        }
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w') as configfile:
            config.write(configfile)
            
        if self.main_window:
            self.apply_system_tray_settings()
            self.apply_transparency_settings()
            self.apply_theme_settings()
            self.apply_start_minimized_settings()
            self.apply_restore_cpu_settings()
            self.apply_restore_kernel_settings()
            
    def apply_system_tray_settings(self):
        """
        Apply system tray settings to the main window.
        Enables or disables the system tray icon based on current settings.
        """
        if self.main_window and hasattr(self.main_window, 'use_system_tray'):
            run_in_tray = self.widgets['tray_combo'].currentText() == 'enable'
            old_setting = self.main_window.use_system_tray
            self.main_window.use_system_tray = run_in_tray
            
            if old_setting != run_in_tray:
                if run_in_tray:
                    if not hasattr(self.main_window, 'tray_icon'):
                        self.main_window.setup_system_tray()
                else:
                    if hasattr(self.main_window, 'tray_icon'):
                        self.main_window.tray_icon.hide()
                        self.main_window.tray_icon.deleteLater()
                        delattr(self.main_window, 'tray_icon')
                        if not self.main_window.isVisible():
                            self.main_window.show_and_activate()
            
            print(f"System tray setting applied: {run_in_tray}")
            
    def apply_transparency_settings(self):
        """
        Apply window transparency settings to the main window.
        """
        if self.main_window:
            transparency_enabled = self.widgets['transparency_combo'].currentText() == 'enable'
            if transparency_enabled:
                self.main_window.setWindowOpacity(0.9)
            else:
                self.main_window.setWindowOpacity(1.0)
            print(f"Transparency setting applied: {transparency_enabled}")
            
    def apply_theme_settings(self):
        """
        Apply the selected theme to the application.
        """
        if self.main_window:
            theme_name = self.widgets['theme_combo'].currentText()
            ThemeManager.apply_theme(QApplication.instance(), theme_name)
            print(f"Theme setting applied: {theme_name}")
    
    def apply_start_minimized_settings(self):
        """
        Apply the start minimized setting to the application.
        """
        if self.main_window:
            start_minimized = self.widgets['start_minimized_combo'].currentText() == 'enable'
            self.main_window.start_minimized = start_minimized
            print(f"Start minimized setting applied: {start_minimized}")
    
    def apply_restore_cpu_settings(self):
        """
        Apply the CPU restore on close setting.
        """
        if self.main_window and hasattr(self.main_window, 'restore_cpu_on_close'):
            restore_cpu = self.widgets['restore_cpu_combo'].currentText() == 'enable'
            self.main_window.restore_cpu_on_close = restore_cpu
            print(f"CPU restore setting applied: {restore_cpu}")
    
    def apply_restore_kernel_settings(self):
        """
        Apply the kernel restore on close setting.
        """
        if self.main_window and hasattr(self.main_window, 'restore_kernel_on_close'):
            restore_kernel = self.widgets['restore_kernel_combo'].currentText() == 'enable'
            self.main_window.restore_kernel_on_close = restore_kernel
            print(f"Kernel restore setting applied: {restore_kernel}")

    def create_option_apply_button(self, parent_layout):
        """
        Create and setup the apply button for options.
        Args:
            parent_layout: The layout to add the button container to
        Returns:
            QPushButton: The created apply button
        """
        # Apply button
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 0)

        apply_button = QPushButton("Apply")
        apply_button.setMinimumSize(100, 30)
        apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(apply_button)
        button_layout.addStretch(1)
        
        parent_layout.addWidget(button_container)
        parent_layout.addSpacing(9)
        
        return apply_button
    
    def load_settings(self):
        """
        Load settings from the configuration file.
        Reads settings from the config file and updates the UI widgets.
        If no config file exists, creates one with default values.
        """
        # Set default values
        self.widgets['theme_combo'].setCurrentText("amd")
        self.widgets['tray_combo'].setCurrentText("enable")
        self.widgets['transparency_combo'].setCurrentText("enable")
        self.widgets['start_minimized_combo'].setCurrentText("disable")
        self.widgets['restore_cpu_combo'].setCurrentText("enable")
        self.widgets['restore_kernel_combo'].setCurrentText("enable")
        
        if not self.config_path.exists():
            self.save_settings()
            return
            
        config = configparser.ConfigParser()
        config.read(self.config_path)
        
        if 'Theme' in config and 'selected_theme' in config['Theme']:
            self.widgets['theme_combo'].setCurrentText(config['Theme']['selected_theme'])
            
        if 'SystemTray' in config and 'run_in_tray' in config['SystemTray']:
            self.widgets['tray_combo'].setCurrentText(config['SystemTray']['run_in_tray'])
            
        if 'Appearance' in config and 'transparency' in config['Appearance']:
            self.widgets['transparency_combo'].setCurrentText(config['Appearance']['transparency'])
        
        if 'StartupBehavior' in config and 'start_minimized' in config['StartupBehavior']:
            self.widgets['start_minimized_combo'].setCurrentText(
                config['StartupBehavior'].get('start_minimized', 'disable')
            )
            
        if 'CPUBehavior' in config and 'restore_on_close' in config['CPUBehavior']:
            self.widgets['restore_cpu_combo'].setCurrentText(
                config['CPUBehavior']['restore_on_close']
            )
            
        if 'KernelBehavior' in config and 'restore_on_close' in config['KernelBehavior']:
            self.widgets['restore_kernel_combo'].setCurrentText(
                config['KernelBehavior']['restore_on_close']
            )
        
        # Apply loaded settings
        self.apply_system_tray_settings()
        self.apply_transparency_settings()
        self.apply_theme_settings()
        self.apply_start_minimized_settings()
        self.apply_restore_cpu_settings()
        self.apply_restore_kernel_settings()


class OptionsTab(QWidget):
    """
    Options tab widget for the application.
    Provides a user interface for modifying application settings and preferences.
    """

    def __init__(self, parent, main_window):
        """
        Initialize the OptionsTab.
        Args:
            parent: Parent widget (optional)
            main_window: Reference to the main application window (optional)
        """
        super().__init__(parent)
        self.main_window = main_window
        self.options_manager = OptionsManager(main_window)
        self.setup_ui()
        
    def setup_ui(self):
        """
        Set up the user interface for the options tab.
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # Create scroll area for settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Selected Theme:")
        theme_label.setWordWrap(True)
        theme_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["amd", "intel", "nvidia"])
        self.theme_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        scroll_layout.addLayout(theme_layout)
        
        # System tray option
        tray_layout = QHBoxLayout()
        tray_label = QLabel("Run in System Tray:")
        tray_label.setWordWrap(True)
        tray_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.tray_combo = QComboBox()
        self.tray_combo.addItems(["enable", "disable"])
        self.tray_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        tray_layout.addWidget(tray_label)
        tray_layout.addWidget(self.tray_combo)
        scroll_layout.addLayout(tray_layout)
        
        # Transparency option
        transparency_layout = QHBoxLayout()
        transparency_label = QLabel("Transparency:")
        transparency_label.setWordWrap(True)
        transparency_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.transparency_combo = QComboBox()
        self.transparency_combo.addItems(["enable", "disable"])
        self.transparency_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        transparency_layout.addWidget(transparency_label)
        transparency_layout.addWidget(self.transparency_combo)
        scroll_layout.addLayout(transparency_layout)
        
        # Start minimized option
        start_minimized_layout = QHBoxLayout()
        start_minimized_label = QLabel("Open Minimized:")
        start_minimized_label.setWordWrap(True)
        start_minimized_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.start_minimized_combo = QComboBox()
        self.start_minimized_combo.addItems(["enable", "disable"])
        self.start_minimized_combo.setCurrentText("disable")
        self.start_minimized_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        start_minimized_layout.addWidget(start_minimized_label)
        start_minimized_layout.addWidget(self.start_minimized_combo)
        scroll_layout.addLayout(start_minimized_layout)
        
        # CPU restore option
        restore_cpu_layout = QHBoxLayout()
        restore_cpu_label = QLabel("Restore CPU Settings on Close:")
        restore_cpu_label.setWordWrap(True)
        restore_cpu_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.restore_cpu_combo = QComboBox()
        self.restore_cpu_combo.addItems(["enable", "disable"])
        self.restore_cpu_combo.setCurrentText("enable")
        self.restore_cpu_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        restore_cpu_layout.addWidget(restore_cpu_label)
        restore_cpu_layout.addWidget(self.restore_cpu_combo)
        scroll_layout.addLayout(restore_cpu_layout)
        
        # Kernel restore option
        restore_kernel_layout = QHBoxLayout()
        restore_kernel_label = QLabel("Restore Kernel Settings on Close:")
        restore_kernel_label.setWordWrap(True)
        restore_kernel_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.restore_kernel_combo = QComboBox()
        self.restore_kernel_combo.addItems(["enable", "disable"])
        self.restore_kernel_combo.setCurrentText("enable")
        self.restore_kernel_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        restore_kernel_layout.addWidget(restore_kernel_label)
        restore_kernel_layout.addWidget(self.restore_kernel_combo)
        scroll_layout.addLayout(restore_kernel_layout)
        
        # Finalize scroll area
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Create apply button
        self.apply_button = self.options_manager.create_option_apply_button(main_layout)
        
        # Register widgets with options manager
        self.options_manager.widgets = {
            'theme_combo': self.theme_combo,
            'tray_combo': self.tray_combo,
            'transparency_combo': self.transparency_combo,
            'start_minimized_combo': self.start_minimized_combo,
            'restore_cpu_combo': self.restore_cpu_combo,
            'restore_kernel_combo': self.restore_kernel_combo,
            'apply_button': self.apply_button
        }
        
        # Connect signals
        self.apply_button.clicked.connect(self.save_and_apply_settings)
        
        # Load existing settings
        self.options_manager.load_settings()
    
    def save_and_apply_settings(self):
        """
        Save current settings and apply them to the application.
        Triggered when the apply button is clicked.
        """
        self.options_manager.save_settings()
        
        if self.main_window and hasattr(self.main_window, 'tray_icon'):
            self.main_window.tray_icon.showMessage(
                "volt-gui",
                "Options settings saved successfully",
                self.main_window.tray_icon.MessageIcon.Information,
                2000
            )