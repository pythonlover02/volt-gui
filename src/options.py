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

    @staticmethod
    def create_options_tab(main_window):
        """
        Creates and returns the options management tab widget.
        """
        options_tab = QWidget()
        main_layout = QVBoxLayout(options_tab)
        main_layout.setContentsMargins(9, 0, 9, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 0)
        
        widgets = {}
        
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Selected Theme:")
        theme_label.setWordWrap(True)
        theme_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['theme_combo'] = QComboBox()
        widgets['theme_combo'].addItems(["amd", "intel", "nvidia"])
        widgets['theme_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(widgets['theme_combo'])
        scroll_layout.addLayout(theme_layout)

        transparency_layout = QHBoxLayout()
        transparency_label = QLabel("Transparency:")
        transparency_label.setWordWrap(True)
        transparency_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['transparency_combo'] = QComboBox()
        widgets['transparency_combo'].addItems(["enable", "disable"])
        widgets['transparency_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        transparency_layout.addWidget(transparency_label)
        transparency_layout.addWidget(widgets['transparency_combo'])
        scroll_layout.addLayout(transparency_layout)

        tray_layout = QHBoxLayout()
        tray_label = QLabel("Run in System Tray:")
        tray_label.setWordWrap(True)
        tray_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['tray_combo'] = QComboBox()
        widgets['tray_combo'].addItems(["enable", "disable"])
        widgets['tray_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        tray_layout.addWidget(tray_label)
        tray_layout.addWidget(widgets['tray_combo'])
        scroll_layout.addLayout(tray_layout)

        start_minimized_layout = QHBoxLayout()
        start_minimized_label = QLabel("Open Minimized:")
        start_minimized_label.setWordWrap(True)
        start_minimized_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['start_minimized_combo'] = QComboBox()
        widgets['start_minimized_combo'].addItems(["enable", "disable"])
        widgets['start_minimized_combo'].setCurrentText("disable")
        widgets['start_minimized_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        start_minimized_layout.addWidget(start_minimized_label)
        start_minimized_layout.addWidget(widgets['start_minimized_combo'])
        scroll_layout.addLayout(start_minimized_layout)

        start_maximized_layout = QHBoxLayout()
        start_maximized_label = QLabel("Open Maximized:")
        start_maximized_label.setWordWrap(True)
        start_maximized_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['start_maximized_combo'] = QComboBox()
        widgets['start_maximized_combo'].addItems(["enable", "disable"])
        widgets['start_maximized_combo'].setCurrentText("disable")
        widgets['start_maximized_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        start_maximized_layout.addWidget(start_maximized_label)
        start_maximized_layout.addWidget(widgets['start_maximized_combo'])
        scroll_layout.addLayout(start_maximized_layout)

        welcome_message_layout = QHBoxLayout()
        welcome_message_label = QLabel("Welcome Message:")
        welcome_message_label.setWordWrap(True)
        welcome_message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['welcome_message_combo'] = QComboBox()
        widgets['welcome_message_combo'].addItems(["enable", "disable"])
        widgets['welcome_message_combo'].setCurrentText("enable")
        widgets['welcome_message_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        welcome_message_layout.addWidget(welcome_message_label)
        welcome_message_layout.addWidget(widgets['welcome_message_combo'])
        scroll_layout.addLayout(welcome_message_layout)
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        OptionsManager.create_option_apply_button(main_layout, widgets, main_window)
        
        widgets['main_window'] = main_window
        widgets['options_path'] = Path(os.path.expanduser("~/.config/volt-gui/volt-options.ini"))
        widgets['options_path'].parent.mkdir(parents=True, exist_ok=True)
        
        OptionsManager.set_default_values(widgets)
        
        return options_tab, widgets

    @staticmethod
    def create_option_apply_button(parent_layout, widgets, main_window):
        """
        Creates and adds the options apply button to the layout.
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(11, 10, 11, 0)

        widgets['options_apply_button'] = QPushButton("Apply")
        widgets['options_apply_button'].setMinimumSize(100, 30)
        widgets['options_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets['options_apply_button'])
        button_layout.addStretch(1)
        
        parent_layout.addWidget(button_container)
        parent_layout.addSpacing(9)

    @staticmethod
    def set_default_values(widgets):
        """
        Set default values for all widgets.
        """
        widgets['theme_combo'].setCurrentText("amd")
        widgets['tray_combo'].setCurrentText("disable")
        widgets['transparency_combo'].setCurrentText("disable")
        widgets['start_minimized_combo'].setCurrentText("disable")
        widgets['start_maximized_combo'].setCurrentText("disable")
        widgets['welcome_message_combo'].setCurrentText("enable")

    @staticmethod
    def load_options(widgets):
        """
        Load options from the configuration file.
        """
        OptionsManager.set_default_values(widgets)
        
        if not widgets['options_path'].exists():
            OptionsManager.save_options(widgets)
            return
            
        options = configparser.ConfigParser()
        options.read(widgets['options_path'])
        
        OptionsManager.apply_options_values(options, widgets)
        OptionsManager.apply_all_options(widgets)

    @staticmethod
    def save_options(widgets):
        """
        Save current options to the configuration file.
        """
        options = configparser.ConfigParser()
        
        main_window = widgets['main_window']
        
        options['Theme'] = {'ActiveTheme': widgets['theme_combo'].currentText()}
        options['SystemTray'] = {'Enable': widgets['tray_combo'].currentText()}
        options['Transparency'] = {'Enable': widgets['transparency_combo'].currentText()}
        options['StartupMinimized'] = {'Enable': widgets['start_minimized_combo'].currentText()}
        options['StartupMaximized'] = {'Enable': widgets['start_maximized_combo'].currentText()}
        options['WelcomeMessage'] = {'Show': widgets['welcome_message_combo'].currentText()}
        options['Profile'] = {'LastActiveProfile': getattr(main_window, 'current_profile', 'Default')}
        
        os.makedirs(os.path.dirname(widgets['options_path']), exist_ok=True)
        
        with open(widgets['options_path'], 'w') as optionsfile:
            options.write(optionsfile)
            
        OptionsManager.apply_all_options(widgets)

    @staticmethod
    def apply_options_values(options, widgets):
        """
        Apply values from options file to widgets.
        """
        main_window = widgets['main_window']
        
        widgets['theme_combo'].setCurrentText(options.get('Theme', 'ActiveTheme', fallback="amd"))
        widgets['tray_combo'].setCurrentText(options.get('SystemTray', 'Enable', fallback="disable"))
        widgets['transparency_combo'].setCurrentText(options.get('Transparency', 'Enable', fallback="disable"))
        widgets['start_minimized_combo'].setCurrentText(options.get('StartupMinimized', 'Enable', fallback="disable"))
        widgets['start_maximized_combo'].setCurrentText(options.get('StartupMaximized', 'Enable', fallback="disable"))
        widgets['welcome_message_combo'].setCurrentText(options.get('WelcomeMessage', 'Show', fallback="enable"))
        
        last_profile = options.get('Profile', 'LastActiveProfile', fallback='Default')
        index = main_window.profile_selector.findText(last_profile)
        if index >= 0:
            main_window.profile_selector.setCurrentText(last_profile)
            main_window.current_profile = last_profile

    @staticmethod
    def apply_all_options(widgets):
        """
        Apply all options to the application.
        """
        OptionsManager.apply_system_tray_options(widgets)
        OptionsManager.apply_transparency_options(widgets)
        OptionsManager.apply_theme_options(widgets)
        OptionsManager.apply_start_minimized_options(widgets)
        OptionsManager.apply_start_maximized_options(widgets)
        OptionsManager.apply_welcome_message_options(widgets)

    @staticmethod
    def apply_theme_options(widgets):
        """
        Apply the selected theme to the application.
        """
        main_window = widgets['main_window']
        if main_window:
            theme_name = widgets['theme_combo'].currentText()
            ThemeManager.apply_theme(QApplication.instance(), theme_name)
            print(f"Theme option applied: {theme_name}")

    @staticmethod
    def apply_system_tray_options(widgets):
        """
        Apply system tray options to the main window.
        """
        main_window = widgets['main_window']
        if main_window:
            run_in_tray = widgets['tray_combo'].currentText() == 'enable'
            old_option = main_window.use_system_tray
            main_window.use_system_tray = run_in_tray
            
            if old_option != run_in_tray:
                if run_in_tray:
                    if not hasattr(main_window, 'tray_icon'):
                        main_window.setup_system_tray()
                else:
                    if hasattr(main_window, 'tray_icon'):
                        main_window.tray_icon.hide()
                        main_window.tray_icon.deleteLater()
                        delattr(main_window, 'tray_icon')
                        if not main_window.isVisible():
                            main_window.show_and_activate()
                
                main_window.update_quit_behavior()
            
            print(f"System tray option applied: {run_in_tray}")
            
    @staticmethod
    def apply_transparency_options(widgets):
        """
        Apply window transparency options to the main window.
        """
        main_window = widgets['main_window']
        if main_window:
            transparency_enabled = widgets['transparency_combo'].currentText() == 'enable'
            if transparency_enabled:
                main_window.setWindowOpacity(0.9)
            else:
                main_window.setWindowOpacity(1.0)
            print(f"Transparency option applied: {transparency_enabled}")

    @staticmethod
    def apply_start_minimized_options(widgets):
        """
        Apply the start minimized option to the application.
        """
        main_window = widgets['main_window']
        if main_window:
            start_minimized = widgets['start_minimized_combo'].currentText() == 'enable'
            main_window.start_minimized = start_minimized
            print(f"Start minimized option applied: {start_minimized}")

    @staticmethod
    def apply_start_maximized_options(widgets):
        """
        Apply the start maximized option to the application.
        """
        main_window = widgets['main_window']
        if main_window:
            start_maximized = widgets['start_maximized_combo'].currentText() == 'enable'
            main_window.start_maximized = start_maximized
            print(f"Start maximized option applied: {start_maximized}")

    @staticmethod
    def apply_welcome_message_options(widgets):
        """
        Apply the welcome message option to the application.
        """
        main_window = widgets['main_window']
        if main_window:
            show_welcome = widgets['welcome_message_combo'].currentText() == 'enable'
            main_window.show_welcome = show_welcome
            print(f"Welcome message option applied: {show_welcome}")

    @staticmethod
    def get_welcome_message_setting(widgets):
        """
        Get the current welcome message setting.
        """
        return widgets['welcome_message_combo'].currentText() == 'enable'

    @staticmethod
    def save_and_apply_options(widgets):
        """
        Save current options and apply them to the application.
        """
        main_window = widgets['main_window']
        OptionsManager.save_options(widgets)
        
        if main_window and hasattr(main_window, 'tray_icon'):
            main_window.tray_icon.showMessage("volt-gui", "Options saved successfully", main_window.tray_icon.MessageIcon.Information, 2000)
        else:
            QMessageBox.information(main_window, "volt-gui", "Options saved successfully")