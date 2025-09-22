import os, configparser
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QScrollArea, QPushButton, QSizePolicy, QMessageBox, QApplication
from PySide6.QtCore import Qt, QTimer
from theme import ThemeManager


class OptionsManager:

    OPTIONS_SETTINGS = {
        'theme': {
            'label': 'Selected Theme:',
            'text': 'Choose the visual theme for the application interface. AMD (red), Intel (blue), or NVIDIA (green) color schemes.',
            'section': 'Theme',
            'config_key': 'ActiveTheme',
            'items': ["amd", "intel", "nvidia"],
            'default': 'amd'
        },
        'transparency': {
            'label': 'Transparency:',
            'text': 'Enable window transparency to make the application semi-transparent.',
            'section': 'Transparency',
            'config_key': 'Enable',
            'items': ["enable", "disable"],
            'default': 'disable'
        },
        'tray': {
            'label': 'Run in System Tray:',
            'text': 'Run the application in system tray. When enabled, closing the window minimizes to tray instead of exiting.',
            'section': 'SystemTray',
            'config_key': 'Enable',
            'items': ["enable", "disable"],
            'default': 'disable'
        },
        'start_minimized': {
            'label': 'Open Minimized:',
            'text': 'Start the application minimized to taskbar or system tray when launched.',
            'section': 'StartupMinimized',
            'config_key': 'Enable',
            'items': ["enable", "disable"],
            'default': 'disable'
        },
        'start_maximized': {
            'label': 'Open Maximized:',
            'text': 'Start the application in maximized window mode when launched.',
            'section': 'StartupMaximized',
            'config_key': 'Enable',
            'items': ["enable", "disable"],
            'default': 'disable'
        },
        'scaling': {
            'label': 'Interface Scaling:',
            'text': 'Scale the interface size for high-DPI displays or better readability.',
            'section': 'Scaling',
            'config_key': 'Factor',
            'items': ["1.0", "1.25", "1.5", "1.75", "2.0"],
            'default': '1.0'
        },
        'welcome_message': {
            'label': 'Welcome Message:',
            'text': 'Show the welcome message dialog when starting the application for the first time or after updates.',
            'section': 'WelcomeMessage',
            'config_key': 'Show',
            'items': ["enable", "disable"],
            'default': 'enable'
        }
    }

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

        for option_key, option_info in OptionsManager.OPTIONS_SETTINGS.items():
            option_layout = QHBoxLayout()
            option_label = QLabel(option_info['label'])
            option_label.setWordWrap(True)
            option_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            widgets[option_key] = QComboBox()
            widgets[option_key].addItems(option_info['items'])
            widgets[option_key].setCurrentText(option_info['default'])
            widgets[option_key].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            if 'text' in option_info:
                widgets[option_key].setToolTip(option_info['text'])

            option_layout.addWidget(option_label)
            option_layout.addWidget(widgets[option_key])
            scroll_layout.addLayout(option_layout)

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
        for option_key, option_info in OptionsManager.OPTIONS_SETTINGS.items():
            widgets[option_key].setCurrentText(option_info['default'])

    @staticmethod
    def get_early_scaling_factor():
        """
        Get the scaling factor before the main application starts.
        This method is called early in the main function.
        """
        config_path = Path(os.path.expanduser("~/.config/volt-gui/volt-options.ini"))
        scaling_factor = OptionsManager.OPTIONS_SETTINGS['scaling']['default']

        if config_path.exists():
            options = configparser.ConfigParser()
            options.read(config_path)
            scaling_factor = options.get(
                OptionsManager.OPTIONS_SETTINGS['scaling']['section'],
                OptionsManager.OPTIONS_SETTINGS['scaling']['config_key'],
                fallback=OptionsManager.OPTIONS_SETTINGS['scaling']['default']
            )

        os.environ['QT_SCALE_FACTOR'] = scaling_factor
        return scaling_factor

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

        for option_key, option_info in OptionsManager.OPTIONS_SETTINGS.items():
            if option_info['section'] not in options:
                options[option_info['section']] = {}
            options[option_info['section']][option_info['config_key']] = widgets[option_key].currentText()

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

        for option_key, option_info in OptionsManager.OPTIONS_SETTINGS.items():
            value = options.get(option_info['section'], option_info['config_key'], fallback=option_info['default'])
            widgets[option_key].setCurrentText(value)

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
        OptionsManager.apply_scaling_options(widgets)
        OptionsManager.apply_welcome_message_options(widgets)

    @staticmethod
    def apply_theme_options(widgets):
        """
        Apply the selected theme to the application.
        """
        main_window = widgets['main_window']
        theme_name = widgets['theme'].currentText()
        ThemeManager.apply_theme(QApplication.instance(), theme_name)

    @staticmethod
    def apply_system_tray_options(widgets):
        """
        Apply system tray options to the main window.
        """
        main_window = widgets['main_window']
        run_in_tray = widgets['tray'].currentText() == OptionsManager.OPTIONS_SETTINGS['tray']['items'][0]
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

    @staticmethod
    def apply_transparency_options(widgets):
        """
        Apply window transparency options to the main window.
        """
        main_window = widgets['main_window']
        transparency_enabled = widgets['transparency'].currentText() == OptionsManager.OPTIONS_SETTINGS['transparency']['items'][0]
        if transparency_enabled:
            main_window.setWindowOpacity(0.9)
        else:
            main_window.setWindowOpacity(1.0)

    @staticmethod
    def apply_start_minimized_options(widgets):
        """
        Apply the start minimized option to the application.
        """
        main_window = widgets['main_window']
        start_minimized = widgets['start_minimized'].currentText() == OptionsManager.OPTIONS_SETTINGS['start_minimized']['items'][0]
        main_window.start_minimized = start_minimized

    @staticmethod
    def apply_start_maximized_options(widgets):
        """
        Apply the start maximized option to the application.
        """
        main_window = widgets['main_window']
        start_maximized = widgets['start_maximized'].currentText() == OptionsManager.OPTIONS_SETTINGS['start_maximized']['items'][0]
        main_window.start_maximized = start_maximized

    @staticmethod
    def apply_welcome_message_options(widgets):
        """
        Apply the welcome message option to the application.
        """
        main_window = widgets['main_window']
        show_welcome = widgets['welcome_message'].currentText() == OptionsManager.OPTIONS_SETTINGS['welcome_message']['items'][0]
        main_window.show_welcome = show_welcome

    @staticmethod
    def apply_scaling_options(widgets):
        """
        Apply interface scaling options to the application.
        """
        main_window = widgets['main_window']
        scaling_factor = float(widgets['scaling'].currentText())
        os.environ['QT_SCALE_FACTOR'] = str(scaling_factor)
        main_window.scaling_factor = scaling_factor

    @staticmethod
    def get_welcome_message_setting(widgets):
        """
        Get the current welcome message setting.
        """
        return widgets['welcome_message'].currentText() == OptionsManager.OPTIONS_SETTINGS['welcome_message']['items'][0]

    @staticmethod
    def save_and_apply_options(widgets):
        """
        Save current options and apply them to the application.
        """
        main_window = widgets['main_window']

        old_scaling = getattr(main_window, 'scaling_factor', 1.0)
        new_scaling = float(widgets['scaling'].currentText())
        scaling_changed = old_scaling != new_scaling

        widgets['options_apply_button'].setEnabled(False)

        try:
            OptionsManager.save_options(widgets)

            message = "Options saved successfully"
            if scaling_changed:
                message += ".\nInterface scaling will take full effect after restarting the application."

            if hasattr(main_window, 'tray_icon'):
                main_window.tray_icon.showMessage("volt-gui", message, main_window.tray_icon.MessageIcon.Information, 3000)
            else:
                QMessageBox.information(main_window, "volt-gui", message)

            QTimer.singleShot(1000, lambda: widgets['options_apply_button'].setEnabled(True))

        except Exception as e:
            error_message = f"Failed to save options: {str(e)}"
            if hasattr(main_window, 'tray_icon'):
                main_window.tray_icon.showMessage("volt-gui", error_message, main_window.tray_icon.MessageIcon.Critical, 3000)
            else:
                QMessageBox.warning(main_window, "volt-gui", error_message)

            widgets['options_apply_button'].setEnabled(True)
