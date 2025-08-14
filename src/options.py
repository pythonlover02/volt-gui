import os
import configparser
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QScrollArea, QPushButton, QSizePolicy, QMessageBox, QApplication
from PySide6.QtCore import Qt
from theme import ThemeManager


class OptionsManager:
    """
    Manages application settings and preferences with integrated UI.
    """

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.options_path = Path(os.path.expanduser("~/.config/volt-gui/volt-options.ini"))
        self.options_path.parent.mkdir(parents=True, exist_ok=True)
        self.widgets = {}
        self.widget = QWidget(self.parent)
        self.setup_ui()

    def get_widget(self):
        """Get the widget for adding to tab widget."""
        return self.widget

    def setup_ui(self):
        """
        Set up the user interface for the options tab.
        """
        main_layout = QVBoxLayout(self.widget)
        main_layout.setContentsMargins(9, 0, 9, 0)
        main_layout.setSpacing(10)
        
        scroll_area = self.create_scroll_area()
        main_layout.addWidget(scroll_area)
        
        self.apply_button = self.create_option_apply_button(main_layout)
        
        self.register_widgets()
        self.apply_button.clicked.connect(self.save_and_apply_options)
        self.load_options()

    def create_option_apply_button(self, parent_layout):
        """
        Create and setup the apply button for options.
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(11, 10, 11, 0)

        apply_button = QPushButton("Apply")
        apply_button.setMinimumSize(100, 30)
        apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(apply_button)
        button_layout.addStretch(1)
        
        parent_layout.addWidget(button_container)
        parent_layout.addSpacing(9)
        
        return apply_button

    def save_and_apply_options(self):
        """
        Save current options and apply them to the application.
        """
        self.save_options()
        
        if self.main_window and hasattr(self.main_window, 'tray_icon'):
            self.main_window.tray_icon.showMessage("volt-gui", "Options saved successfully", self.main_window.tray_icon.MessageIcon.Information, 2000)
        else:
            QMessageBox.information(self.main_window, "volt-gui", "Options saved successfully")

    def create_scroll_area(self):
        """
        Create and configure the scroll area with all option widgets.
        """
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 0)
        
        self.add_theme_option(scroll_layout)
        self.add_transparency_option(scroll_layout)
        self.add_tray_option(scroll_layout)
        self.add_start_minimized_option(scroll_layout)
        self.add_start_maximized_option(scroll_layout)
        self.add_welcome_message_option(scroll_layout)
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        return scroll_area

    def add_theme_option(self, layout):
        """
        Add theme selection option to layout.
        """
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Selected Theme:")
        theme_label.setWordWrap(True)
        theme_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["amd", "intel", "nvidia"])
        self.theme_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

    def add_transparency_option(self, layout):
        """
        Add transparency option to layout.
        """
        transparency_layout = QHBoxLayout()
        transparency_label = QLabel("Transparency:")
        transparency_label.setWordWrap(True)
        transparency_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.transparency_combo = QComboBox()
        self.transparency_combo.addItems(["enable", "disable"])
        self.transparency_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        transparency_layout.addWidget(transparency_label)
        transparency_layout.addWidget(self.transparency_combo)
        layout.addLayout(transparency_layout)

    def add_tray_option(self, layout):
        """
        Add system tray option to layout.
        """
        tray_layout = QHBoxLayout()
        tray_label = QLabel("Run in System Tray:")
        tray_label.setWordWrap(True)
        tray_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.tray_combo = QComboBox()
        self.tray_combo.addItems(["enable", "disable"])
        self.tray_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        tray_layout.addWidget(tray_label)
        tray_layout.addWidget(self.tray_combo)
        layout.addLayout(tray_layout)

    def add_start_minimized_option(self, layout):
        """
        Add start minimized option to layout.
        """
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
        layout.addLayout(start_minimized_layout)

    def add_start_maximized_option(self, layout):
        """
        Add start maximized option to layout.
        """
        start_maximized_layout = QHBoxLayout()
        start_maximized_label = QLabel("Open Maximized:")
        start_maximized_label.setWordWrap(True)
        start_maximized_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.start_maximized_combo = QComboBox()
        self.start_maximized_combo.addItems(["enable", "disable"])
        self.start_maximized_combo.setCurrentText("disable")
        self.start_maximized_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        start_maximized_layout.addWidget(start_maximized_label)
        start_maximized_layout.addWidget(self.start_maximized_combo)
        layout.addLayout(start_maximized_layout)

    def add_welcome_message_option(self, layout):
        """
        Add welcome message option to layout.
        """
        welcome_message_layout = QHBoxLayout()
        welcome_message_label = QLabel("Welcome Message:")
        welcome_message_label.setWordWrap(True)
        welcome_message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.welcome_message_combo = QComboBox()
        self.welcome_message_combo.addItems(["enable", "disable"])
        self.welcome_message_combo.setCurrentText("enable")
        self.welcome_message_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        welcome_message_layout.addWidget(welcome_message_label)
        welcome_message_layout.addWidget(self.welcome_message_combo)
        layout.addLayout(welcome_message_layout)

    def register_widgets(self):
        """
        Register all widgets with the options manager.
        """
        self.widgets = {
            'theme_combo': self.theme_combo,
            'transparency_combo': self.transparency_combo,
            'tray_combo': self.tray_combo,
            'start_minimized_combo': self.start_minimized_combo,
            'start_maximized_combo': self.start_maximized_combo,
            'welcome_message_combo': self.welcome_message_combo,
            'apply_button': self.apply_button
        }

    def load_options(self):
        """
        Load options from the configuration file.
        """
        self.set_default_values()
        
        if not self.options_path.exists():
            self.save_options()
            return
            
        options = configparser.ConfigParser()
        options.read(self.options_path)
        
        self.apply_options_values(options)
        self.apply_all_options()

    def save_options(self):
        """
        Save current options to the configuration file.
        """
        options = configparser.ConfigParser()
        
        options['Theme'] = {'ActiveTheme': self.widgets['theme_combo'].currentText()}
        options['SystemTray'] = {'Enable': self.widgets['tray_combo'].currentText()}
        options['Transparency'] = {'Enable': self.widgets['transparency_combo'].currentText()}
        options['StartupMinimized'] = {'Enable': self.widgets['start_minimized_combo'].currentText()}
        options['StartupMaximized'] = {'Enable': self.widgets['start_maximized_combo'].currentText()}
        options['WelcomeMessage'] = {'Show': self.widgets['welcome_message_combo'].currentText()}
        options['Profile'] = {'LastActiveProfile': getattr(self.main_window, 'current_profile', 'Default')}
        
        os.makedirs(os.path.dirname(self.options_path), exist_ok=True)
        
        with open(self.options_path, 'w') as optionsfile:
            options.write(optionsfile)
            
        if self.main_window:
            self.apply_all_options()

    def set_default_values(self):
        """
        Set default values for all widgets.
        """
        self.widgets['theme_combo'].setCurrentText("amd")
        self.widgets['tray_combo'].setCurrentText("disable")
        self.widgets['transparency_combo'].setCurrentText("disable")
        self.widgets['start_minimized_combo'].setCurrentText("disable")
        self.widgets['start_maximized_combo'].setCurrentText("disable")
        self.widgets['welcome_message_combo'].setCurrentText("enable")

    def apply_options_values(self, options):
        """
        Apply values from options file to widgets.
        """
        self.widgets['theme_combo'].setCurrentText(options.get('Theme', 'ActiveTheme', fallback="amd"))
        self.widgets['tray_combo'].setCurrentText(options.get('SystemTray', 'Enable', fallback="disable"))
        self.widgets['transparency_combo'].setCurrentText(options.get('Transparency', 'Enable', fallback="disable"))
        self.widgets['start_minimized_combo'].setCurrentText(options.get('StartupMinimized', 'Enable', fallback="disable"))
        self.widgets['start_maximized_combo'].setCurrentText(options.get('StartupMaximized', 'Enable', fallback="disable"))
        self.widgets['welcome_message_combo'].setCurrentText(options.get('WelcomeMessage', 'Show', fallback="enable"))
        
        last_profile = options.get('Profile', 'LastActiveProfile', fallback='Default')
        index = self.main_window.profile_selector.findText(last_profile)
        if index >= 0:
            self.main_window.profile_selector.setCurrentText(last_profile)
            self.main_window.current_profile = last_profile

    def apply_all_options(self):
        """
        Apply all options to the application.
        """
        self.apply_system_tray_options()
        self.apply_transparency_options()
        self.apply_theme_options()
        self.apply_start_minimized_options()
        self.apply_start_maximized_options()
        self.apply_welcome_message_options()

    def apply_theme_options(self):
        """
        Apply the selected theme to the application.
        """
        if self.main_window:
            theme_name = self.widgets['theme_combo'].currentText()
            ThemeManager.apply_theme(QApplication.instance(), theme_name)
            print(f"Theme option applied: {theme_name}")

    def apply_system_tray_options(self):
        """
        Apply system tray options to the main window.
        """
        if self.main_window:
            run_in_tray = self.widgets['tray_combo'].currentText() == 'enable'
            old_option = self.main_window.use_system_tray
            self.main_window.use_system_tray = run_in_tray
            
            if old_option != run_in_tray:
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
                
                self.main_window.update_quit_behavior()
            
            print(f"System tray option applied: {run_in_tray}")
            
    def apply_transparency_options(self):
        """
        Apply window transparency options to the main window.
        """
        if self.main_window:
            transparency_enabled = self.widgets['transparency_combo'].currentText() == 'enable'
            if transparency_enabled:
                self.main_window.setWindowOpacity(0.9)
            else:
                self.main_window.setWindowOpacity(1.0)
            print(f"Transparency option applied: {transparency_enabled}")

    def apply_start_minimized_options(self):
        """
        Apply the start minimized option to the application.
        """
        if self.main_window:
            start_minimized = self.widgets['start_minimized_combo'].currentText() == 'enable'
            self.main_window.start_minimized = start_minimized
            print(f"Start minimized option applied: {start_minimized}")

    def apply_start_maximized_options(self):
        """
        Apply the start maximized option to the application.
        """
        if self.main_window:
            start_maximized = self.widgets['start_maximized_combo'].currentText() == 'enable'
            self.main_window.start_maximized = start_maximized
            print(f"Start maximized option applied: {start_maximized}")

    def apply_welcome_message_options(self):
        """
        Apply the welcome message option to the application.
        """
        if self.main_window:
            show_welcome = self.widgets['welcome_message_combo'].currentText() == 'enable'
            self.main_window.show_welcome = show_welcome
            print(f"Welcome message option applied: {show_welcome}")

    def get_welcome_message_setting(self):
        """
        Get the current welcome message setting.
        """
        return self.widgets['welcome_message_combo'].currentText() == 'enable'