import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QSizePolicy, QLineEdit, QFrame
)
from PySide6.QtCore import Qt, QProcess


class KernelManager:
    """
    Main class for managing kernel settings.
    Provides static methods to create UI elements, manage kernel settings,
    and handle privilege escalation for system modifications.
    """
    
    # Dictionary of kernel settings with their paths and recommended values
    KERNEL_SETTINGS = {
        'compaction_proactiveness': {
            'path': '/proc/sys/vm/compaction_proactiveness', 
            'recommended': '0'
        },
        'watermark_boost_factor': {
            'path': '/proc/sys/vm/watermark_boost_factor', 
            'recommended': '1'
        },
        'min_free_kbytes': {
            'path': '/proc/sys/vm/min_free_kbytes', 
            'recommended': 'do not set this below 1024 KB or above 5% of your systems memory'
        },
        'max_map_count': {
            'path': '/proc/sys/vm/max_map_count', 
            'recommended': 'for performance and compatibility reasons the recommended value its 1048576'
        },
        'swappiness': {
            'path': '/proc/sys/vm/swappiness', 
            'recommended': '10'
        },
        'zone_reclaim_mode': {
            'path': '/proc/sys/vm/zone_reclaim_mode', 
            'recommended': '0'
        },
        'page_lock_unfairness': {
            'path': '/proc/sys/vm/page_lock_unfairness', 
            'recommended': '1'
        }
    }

    @staticmethod
    def create_kernel_tab(main_window):
        """
        Creates and returns the kernel settings tab widget.
        Args:
            main_window: Reference to main window for connecting signals
        Returns:
            tuple: (QWidget, dict) The tab widget and a dictionary of UI elements
        """
        kernel_tab = QWidget()
        kernel_layout = QVBoxLayout(kernel_tab)
        widgets = {}
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        for setting_name, setting_info in KernelManager.KERNEL_SETTINGS.items():
            KernelManager._create_setting_section(
                scroll_layout, 
                widgets, 
                setting_name, 
                setting_info
            )
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        kernel_layout.addWidget(scroll_area)
        
        KernelManager.create_kernel_apply_button(kernel_layout, widgets, main_window)
        
        return kernel_tab, widgets

    @staticmethod
    def _create_setting_section(kernel_layout, widgets, setting_name, setting_info):
        """
        Creates a UI section for a single kernel setting.
        Args:
            kernel_layout: The parent layout to add widgets to
            widgets: Dictionary to store created widgets
            setting_name: Name of the kernel setting
            setting_info: Dictionary containing setting information
        """
        setting_container = QWidget()
        setting_container.setProperty("settingContainer", True)
        setting_layout = QVBoxLayout(setting_container)
        setting_layout.setContentsMargins(0, 10, 0, 0)
        
        path_label = QLabel(f"{setting_info['path']}:")
        path_label.setWordWrap(True)
        setting_layout.addWidget(path_label)
        
        current_value_label = QLabel("Updating...")
        setting_layout.addWidget(current_value_label)
        
        input_widget = QLineEdit()
        input_widget.setPlaceholderText(
            f"enter value (recommended: {setting_info['recommended']})"
        )
        setting_layout.addWidget(input_widget)
        
        widgets[f'{setting_name}_input'] = input_widget
        widgets[f'{setting_name}_current_value'] = current_value_label
        kernel_layout.addWidget(setting_container)

    @staticmethod
    def create_kernel_apply_button(kernel_layout, widgets, main_window):
        """
        Creates the apply button UI element and connects its signal.
        Args:
            kernel_layout: The parent layout to add widgets to
            widgets: Dictionary to store created widgets
            main_window: Reference to main window for connecting signals
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 0)
        
        widgets['kernel_apply_button'] = QPushButton("Apply")
        widgets['kernel_apply_button'].setMinimumSize(100, 30)
        widgets['kernel_apply_button'].setSizePolicy(
            QSizePolicy.Fixed, 
            QSizePolicy.Fixed
        )
        
        button_layout.addStretch(1)
        button_layout.addWidget(widgets['kernel_apply_button'])
        button_layout.addStretch(1)
        
        kernel_layout.addWidget(button_container)

    @staticmethod
    def refresh_kernel_values(widgets):
        """
        Refreshes all kernel setting values in the UI.
        Args:
            widgets: Dictionary containing UI widgets to update
        """
        for name, info in KernelManager.KERNEL_SETTINGS.items():
            current = KernelManager._get_current_value(info['path'])
            widgets[f'{name}_current_value'].setText(f"current value: {current}")

    @staticmethod
    def _get_current_value(setting_path):
        """
        Gets the current value of a kernel setting.
        Args:
            setting_path: Path to the kernel setting file
        Returns:
            str: Current value or "Error" if reading fails
        """
        try:
            with open(setting_path, 'r') as f:
                return f.read().strip()
        except Exception:
            return "Error"

    @staticmethod
    def check_if_kernel_settings_already_applied(widgets):
        """
        Check if the kernel settings that have values entered are already applied.
        Args:
            widgets: Dictionary containing UI widgets with entered values
        Returns:
            bool: True if all non-empty settings match current values, False otherwise
        """
        settings_to_check = []
        
        # Get all settings that have values entered
        for name, info in KernelManager.KERNEL_SETTINGS.items():
            value = widgets[f'{name}_input'].text().strip()
            if value:
                current_value = KernelManager._get_current_value(info['path'])
                if current_value != "Error" and current_value != value:
                    return False
                settings_to_check.append((name, value, current_value))
        
        # If no settings have values entered, return False (nothing to apply)
        if not settings_to_check:
            return False
            
        # All settings with values match current values
        return True

    @staticmethod
    def apply_kernel_settings(widgets, main_window):
        """
        Applies the kernel settings using privilege escalation and controls system tray messages.        
        Args:
            widgets: Dictionary containing UI widgets with new values
            main_window: Optional reference to main window for showing notifications
        """
        try:
            settings = []
            originals = {}
            
            # Collect settings that have values entered
            for name, info in KernelManager.KERNEL_SETTINGS.items():
                value = widgets[f'{name}_input'].text().strip()
                if value:
                    path = info['path']
                    originals[name] = KernelManager._get_current_value(path)
                    settings.append(f"{path}:{value}")
            
            # If no settings to apply, show notification and return early
            if not settings:
                if main_window and hasattr(main_window, 'tray_icon'):
                    main_window.tray_icon.showMessage(
                        "volt-gui",
                        "No kernel settings to apply",
                        main_window.tray_icon.MessageIcon.Information,
                        2000
                    )
                return
            
            # Check if settings are already applied
            if KernelManager.check_if_kernel_settings_already_applied(widgets):
                if main_window and hasattr(main_window, 'tray_icon'):
                    main_window.tray_icon.showMessage(
                        "volt-gui",
                        "Kernel settings already applied",
                        main_window.tray_icon.MessageIcon.Information,
                        2000
                    )
                return
            
            # Apply the settings
            process = QProcess()
            process.start("pkexec", ["/usr/local/bin/volt-helper", "-k"] + settings)
            process.waitForFinished()
            
            if process.exitCode() == 0:
                # Store original values for restoration
                widgets['original_values'] = originals
                
                if main_window and hasattr(main_window, 'tray_icon'):
                    main_window.tray_icon.showMessage(
                        "volt-gui",
                        "Kernel settings applied successfully",
                        main_window.tray_icon.MessageIcon.Information,
                        2000
                    )
            else:
                if main_window and hasattr(main_window, 'tray_icon'):
                    main_window.tray_icon.showMessage(
                        "volt-gui",
                        "Failed to apply kernel settings",
                        main_window.tray_icon.MessageIcon.Critical,
                        2000
                    )
        except Exception as e:
            print(f"Apply error: {str(e)}")
            if main_window and hasattr(main_window, 'tray_icon'):
                main_window.tray_icon.showMessage(
                    "volt-gui",
                    f"Error applying kernel settings: {str(e)}",
                    main_window.tray_icon.MessageIcon.Critical,
                    2000
                )

    @staticmethod
    def restore_kernel_settings(widgets):
        """
        Restores kernel settings to their original values.
        Args:
            widgets: Dictionary containing UI widgets and original values
        """
        if 'original_values' not in widgets:
            return
            
        try:
            originals = widgets['original_values']
            restore = [
                f"{KernelManager.KERNEL_SETTINGS[name]['path']}:{val}" 
                for name, val in originals.items()
            ]
            
            process = QProcess()
            process.start("pkexec", ["/usr/local/bin/volt-helper", "-k"] + restore)
            process.waitForFinished()
            
            if process.exitCode() == 0:
                del widgets['original_values']

        except Exception as e:
            print(f"Restore error: {str(e)}")