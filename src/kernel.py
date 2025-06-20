import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QSizePolicy, QLineEdit, QFrame, QSystemTrayIcon
)
from PySide6.QtCore import Qt, QProcess


class KernelManager:
    """
    Main class for managing kernel settings.
    Provides static methods to create UI elements, manage kernel settings,
    and handle privilege escalation for system modifications.
    """
    
    # kernel settings dictionary with descriptive text and recommended values
    KERNEL_SETTINGS = {
        'compaction_proactiveness': {
            'path': '/proc/sys/vm/compaction_proactiveness',
            'text': 'Controls memory compaction proactiveness. Lower values reduce CPU overhead.\nRecommended values: 0',
            'is_dynamic': False
        },
        'watermark_boost_factor': {
            'path': '/proc/sys/vm/watermark_boost_factor',
            'text': 'Controls memory reclaim aggressiveness. Lower values prevent excessive reclaim.\nRecommended values: 1',
            'is_dynamic': False
        },
        'min_free_kbytes': {
            'path': '/proc/sys/vm/min_free_kbytes',
            'text': 'Minimum free memory to maintain. Do not set below 1024 KB or above 5% of system memory.\nRecommended values: 1024-65536',
            'is_dynamic': False
        },
        'max_map_count': {
            'path': '/proc/sys/vm/max_map_count',
            'text': 'Maximum number of memory map areas a process can have. For performance and compatibility.\nRecommended values: 1048576',
            'is_dynamic': False
        },
        'swappiness': {
            'path': '/proc/sys/vm/swappiness',
            'text': 'Controls how aggressively the kernel swaps memory pages. Lower values prefer RAM over swap.\nRecommended values: 10',
            'is_dynamic': False
        },
        'dirty_ratio': {
            'path': '/proc/sys/vm/dirty_ratio',
            'text': 'Percentage of system memory that can be filled with dirty pages before processes are forced to write.\nRecommended values: 15-20',
            'is_dynamic': False
        },
        'dirty_background_ratio': {
            'path': '/proc/sys/vm/dirty_background_ratio',
            'text': 'Percentage of system memory at which background writeback starts.\nRecommended values: 5-10',
            'is_dynamic': False
        },
        'dirty_expire_centisecs': {
            'path': '/proc/sys/vm/dirty_expire_centisecs',
            'text': 'How long dirty data can remain in memory before being written (in centiseconds).\nRecommended values: 1500-3000',
            'is_dynamic': False
        },
        'dirty_writeback_centisecs': {
            'path': '/proc/sys/vm/dirty_writeback_centisecs',
            'text': 'Interval between periodic writeback wakeups (in centiseconds).\nRecommended values: 500-1500',
            'is_dynamic': False
        },
        'vfs_cache_pressure': {
            'path': '/proc/sys/vm/vfs_cache_pressure',
            'text': 'Controls tendency of kernel to reclaim directory and inode cache memory. Lower values keep caches longer.\nRecommended values: 50-80',
            'is_dynamic': False
        },
        'thp_enabled': {
            'path': '/sys/kernel/mm/transparent_hugepage/enabled',
            'text': 'Controls transparent huge pages. Can improve performance but may increase memory usage.\nPossible values: always madvise never',
            'is_dynamic': True
        },
        'thp_shmem_enabled': {
            'path': '/sys/kernel/mm/transparent_hugepage/shmem_enabled',
            'text': 'Controls transparent huge pages for shared memory. May improve performance for memory-intensive applications.\nPossible values: always within_size advise never',
            'is_dynamic': True
        },
        'thp_defrag': {
            'path': '/sys/kernel/mm/transparent_hugepage/defrag',
            'text': 'Controls when kernel attempts to make huge pages available through memory compaction.\nPossible values: always defer defer+madvise madvise never',
            'is_dynamic': True
        },
        'zone_reclaim_mode': {
            'path': '/proc/sys/vm/zone_reclaim_mode',
            'text': 'Controls zone reclaim behavior in NUMA systems. Disabling improves performance on most systems.\nRecommended values: 0',
            'is_dynamic': False
        },
        'page_lock_unfairness': {
            'path': '/proc/sys/vm/page_lock_unfairness',
            'text': 'Controls page lock unfairness to prevent lock starvation.\nRecommended values: 1',
            'is_dynamic': False
        },
        'sched_cfs_bandwidth_slice_us': {
            'path': '/proc/sys/kernel/sched_cfs_bandwidth_slice_us',
            'text': 'CFS bandwidth slice duration in microseconds. Affects scheduler responsiveness.\nRecommended values: 3000',
            'is_dynamic': False
        },
        'sched_autogroup_enabled': {
            'path': '/proc/sys/kernel/sched_autogroup_enabled',
            'text': 'Enables automatic process grouping for better desktop responsiveness.\nRecommended values: 1',
            'is_dynamic': False
        },
        'watchdog': {
            'path': '/proc/sys/kernel/watchdog',
            'text': 'Enables soft lockup detector. \nRecommended values: 0',
            'is_dynamic': False
        },
        'nmi_watchdog': {
            'path': '/proc/sys/kernel/nmi_watchdog',
            'text': 'Enables NMI watchdog for hard lockup detection. \nRecommended values: 0',
            'is_dynamic': False
        },
        'laptop_mode': {
            'path': '/proc/sys/vm/laptop_mode',
            'text': 'Enables laptop power-saving mode for disk I/O. \nRecommended values: 0',
            'is_dynamic': False
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
        
        # Add all kernel settings
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
        
        # Initialize process tracking variables like CPU manager
        widgets['kernel_settings_applied'] = False
        widgets['is_process_running'] = False
        widgets['process'] = None
        
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
        
        # Add descriptive text label
        text_label = QLabel(setting_info['text'])
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 5px;")
        setting_layout.addWidget(text_label)
        
        input_widget = QLineEdit()
        input_widget.setPlaceholderText("enter value")
        
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
            if info['is_dynamic']:
                current = KernelManager._get_dynamic_current_value(info['path'])
            else:
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
    def _get_dynamic_current_value(setting_path):
        """
        Gets the current value of a dynamic setting (extracts value in brackets).
        Args:
            setting_path: Path to the dynamic setting file
        Returns:
            str: Current value (from brackets) or "Error" if reading fails
        """
        try:
            with open(setting_path, 'r') as f:
                content = f.read().strip()
            
            # Extract value in brackets
            import re
            match = re.search(r'\[([^\]]+)\]', content)
            if match:
                return match.group(1)
            else:
                # If no brackets found, return first value as fallback
                values = content.split()
                return values[0] if values else "Error"
        except Exception:
            return "Error"

    @staticmethod
    def _get_dynamic_possible_values(setting_path):
        """
        Gets all possible values for a dynamic setting (removes brackets).
        Args:
            setting_path: Path to the dynamic setting file
        Returns:
            str: Space-separated possible values or "Error" if reading fails
        """
        try:
            with open(setting_path, 'r') as f:
                content = f.read().strip()
            
            # Remove brackets and return all values
            import re
            content = re.sub(r'[\[\]]', '', content)
            return content
        except Exception:
            return "Error"

    @staticmethod
    def check_if_kernel_settings_already_applied(widgets):
        """
        Check if the kernel settings that have values entered are already applied.
        Args:
            widgets: Dictionary containing UI widgets with entered values
        Returns:
            tuple: (bool, str) - (settings_already_applied, message)
        """
        settings_to_check = []
        
        for name, info in KernelManager.KERNEL_SETTINGS.items():
            value = widgets[f'{name}_input'].text().strip()
            if value:
                if info['is_dynamic']:
                    current_value = KernelManager._get_dynamic_current_value(info['path'])
                else:
                    current_value = KernelManager._get_current_value(info['path'])
                
                if current_value != "Error" and current_value != value:
                    return False, ""
                settings_to_check.append((name, value, current_value))
            
        # All settings with values match current values
        return True, "Kernel settings already applied"

    @staticmethod
    def apply_kernel_settings(widgets, main_window):
        """
        Applies the kernel settings using privilege escalation and controls system tray messages.        
        Args:
            widgets: Dictionary containing UI widgets with new values
            main_window: Optional reference to main window for showing notifications
        """
        if widgets['is_process_running']:
            return

        try:
            settings = []
            originals = {}
            
            # Collect kernel settings that have values entered
            for name, info in KernelManager.KERNEL_SETTINGS.items():
                value = widgets[f'{name}_input'].text().strip()
                if value:
                    path = info['path']
                    if info['is_dynamic']:
                        originals[name] = KernelManager._get_dynamic_current_value(path)
                    else:
                        originals[name] = KernelManager._get_current_value(path)
                    settings.append(f"{path}:{value}")
            
            # Check if settings are already applied or if there are no settings
            already_applied, message = KernelManager.check_if_kernel_settings_already_applied(widgets)
            
            if already_applied:
                if main_window and hasattr(main_window, 'tray_icon'):
                    main_window.tray_icon.showMessage(
                        "volt-gui", 
                        message, 
                        QSystemTrayIcon.MessageIcon.Information, 
                        2000
                    )
                return
            
            # Store original values for restoration
            widgets['original_values'] = originals
            
            # Apply the settings asynchronously
            widgets['kernel_apply_button'].setEnabled(False)
            widgets['process'] = QProcess()
            widgets['process'].start("pkexec", ["/usr/local/bin/volt-helper", "-k"] + settings)
            widgets['process'].finished.connect(
                lambda: KernelManager._on_process_finished(widgets, main_window)
            )
            widgets['is_process_running'] = True
            widgets['kernel_settings_applied'] = True
            
        except Exception as e:
            print(f"Apply error: {str(e)}")
            if main_window and hasattr(main_window, 'tray_icon'):
                main_window.tray_icon.showMessage(
                    "volt-gui",
                    f"Error applying Kernel settings: {str(e)}",
                    QSystemTrayIcon.MessageIcon.Critical,
                    2000
                )

    @staticmethod
    def restore_kernel_settings(widgets):
        """
        Restores kernel settings to their original values.
        Args:
            widgets: Dictionary containing UI widgets and original values
        """
        if widgets['kernel_settings_applied'] and 'original_values' in widgets:
            try:
                originals = widgets['original_values']
                restore = []
                
                # Restore kernel settings
                for name, val in originals.items():
                    if name in KernelManager.KERNEL_SETTINGS:
                        restore.append(f"{KernelManager.KERNEL_SETTINGS[name]['path']}:{val}")
                
                process = QProcess()
                process.start("pkexec", ["/usr/local/bin/volt-helper", "-k"] + restore)
                process.waitForFinished()
                
                if process.exitCode() == 0:
                    del widgets['original_values']

            except Exception as e:
                print(f"Restore error: {str(e)}")

    @staticmethod
    def _on_process_finished(widgets, main_window):
        """
        Handle process completion.
        Args:
            widgets: Dictionary containing UI widgets
            main_window: Reference to main window for notifications
        """
        widgets['is_process_running'] = False
        widgets['kernel_apply_button'].setEnabled(True)
        
        # Get exit code from the process
        exit_code = 0
        if widgets['process']:
            exit_code = widgets['process'].exitCode()
        
        # Refresh UI
        KernelManager.refresh_kernel_values(widgets)
        
        # Show notification
        if main_window and hasattr(main_window, 'tray_icon'):
            main_window.tray_icon.showMessage(
                "volt-gui", 
                "Kernel settings applied successfully" if exit_code == 0 else "Failed to apply kernel settings",
                QSystemTrayIcon.MessageIcon.Information if exit_code == 0 else QSystemTrayIcon.MessageIcon.Critical,
                2000
            )
        
        # Clean up process
        if widgets['process']:
            widgets['process'].deleteLater()
            widgets['process'] = None