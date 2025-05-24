from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QScrollArea,
    QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt
from theme import ThemeManager
import configparser
from pathlib import Path
import os
from PySide6.QtWidgets import QApplication

class OptionsManager:
    def __init__(self, main_window=None):
        self.config_path = Path(os.path.expanduser("~/.config/volt-gui/volt-options.ini"))
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.widgets = {}
        self.main_window = main_window
        
    def save_settings(self):
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
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w') as configfile:
            config.write(configfile)
            
        if self.main_window:
            self.apply_system_tray_settings()
            self.apply_transparency_settings()
            self.apply_theme_settings()
            self.apply_start_minimized_settings()
            self.apply_restore_cpu_settings()
            
    def apply_system_tray_settings(self):
        if self.main_window and hasattr(self.main_window, 'use_system_tray'):
            run_in_tray = self.widgets['tray_combo'].currentText() == 'enable'
            self.main_window.use_system_tray = run_in_tray
            print(f"System tray setting applied: {run_in_tray}")
            
    def apply_transparency_settings(self):
        if self.main_window:
            transparency_enabled = self.widgets['transparency_combo'].currentText() == 'enable'
            if transparency_enabled:
                self.main_window.setWindowOpacity(0.9)
            else:
                self.main_window.setWindowOpacity(1.0)
            print(f"Transparency setting applied: {transparency_enabled}")
            
    def apply_theme_settings(self):
        if self.main_window:
            theme_name = self.widgets['theme_combo'].currentText()
            ThemeManager.apply_theme(QApplication.instance(), theme_name)
            print(f"Theme setting applied: {theme_name}")
    
    def apply_start_minimized_settings(self):
        if self.main_window:
            start_minimized = self.widgets['start_minimized_combo'].currentText() == 'enable'
            self.main_window.start_minimized = start_minimized
            print(f"Start minimized setting applied: {start_minimized}")
    
    def apply_restore_cpu_settings(self):
        if self.main_window and hasattr(self.main_window, 'restore_cpu_on_close'):
            restore_cpu = self.widgets['restore_cpu_combo'].currentText() == 'enable'
            self.main_window.restore_cpu_on_close = restore_cpu
            print(f"CPU restore setting applied: {restore_cpu}")
    
    def load_settings(self):
        self.widgets['theme_combo'].setCurrentText("amd")
        self.widgets['tray_combo'].setCurrentText("enable")
        self.widgets['transparency_combo'].setCurrentText("enable")
        self.widgets['start_minimized_combo'].setCurrentText("disable")
        self.widgets['restore_cpu_combo'].setCurrentText("enable")
        
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
            self.widgets['start_minimized_combo'].setCurrentText(config['StartupBehavior']['start_minimized'])
            
        if 'CPUBehavior' in config and 'restore_on_close' in config['CPUBehavior']:
            self.widgets['restore_cpu_combo'].setCurrentText(config['CPUBehavior']['restore_on_close'])
        
        self.apply_system_tray_settings()
        self.apply_transparency_settings()
        self.apply_theme_settings()
        self.apply_start_minimized_settings()
        self.apply_restore_cpu_settings()

class OptionsTab(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.options_manager = OptionsManager(main_window)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
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
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 5)

        self.apply_button = QPushButton("Apply")
        self.apply_button.setMinimumSize(100, 30)
        self.apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(self.apply_button)
        button_layout.addStretch(1)
        
        main_layout.addWidget(button_container)
        
        main_layout.addSpacing(9)
        
        self.options_manager.widgets = {
            'theme_combo': self.theme_combo,
            'tray_combo': self.tray_combo,
            'transparency_combo': self.transparency_combo,
            'start_minimized_combo': self.start_minimized_combo,
            'restore_cpu_combo': self.restore_cpu_combo,
            'apply_button': self.apply_button
        }
        
        self.apply_button.clicked.connect(self.save_and_apply_settings)
        self.options_manager.load_settings()
    
    def save_and_apply_settings(self):
        if self.main_window and hasattr(self.main_window, 'animate_button_click'):
            self.main_window.animate_button_click(self.apply_button)
        self.options_manager.save_settings()
        
        if self.main_window and hasattr(self.main_window, 'tray_icon'):
            self.main_window.tray_icon.showMessage(
                "volt-gui",
                "Options settings saved successfully",
                self.main_window.tray_icon.MessageIcon.Information,
                2000
            )
