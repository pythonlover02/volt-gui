import glob
import re
import subprocess
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QScrollArea, QFrame, QSizePolicy, QSystemTrayIcon
)
from PySide6.QtCore import (
    Qt, QProcess, QPropertyAnimation, QEasingCurve, QSize
)

class DiskManager:
    """
    Main Disk management class that handles disk I/O schedulers.
    Provides static methods to create UI elements and manage disk settings.
    """
    
    # Path pattern to disk scheduler files
    DISK_SCHEDULER_PATH_PATTERN = "/sys/block/*/queue/scheduler"
    
    # Default scheduler fallback
    DEFAULT_SCHEDULER = "mq-deadline"

    @staticmethod
    def create_disk_tab():
        """
        Creates and returns the disk management tab widget.
        Returns:
            tuple: (QWidget, dict) The tab widget and a dictionary of UI elements
        """
        disk_tab = QWidget()
        main_layout = QVBoxLayout(disk_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 0)
        
        widgets = {}
        widgets['disk_combos'] = {}
        widgets['disk_labels'] = {}
        widgets['original_schedulers'] = {}
        
        # Get all disk devices and their schedulers
        disk_info = DiskManager.get_disk_scheduler_info()
        
        # Sort disk names alphabetically for consistent ordering
        sorted_disk_names = sorted(disk_info.keys())
        
        for disk_name in sorted_disk_names:
            scheduler_info = disk_info[disk_name]
            
            # Create layout for this disk
            disk_layout = QHBoxLayout()
            
            # Create label
            disk_label = QLabel(f"{disk_name} scheduler:")
            disk_label.setWordWrap(True)
            disk_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            
            # Create combo box with available schedulers (also sorted alphabetically)
            disk_combo = QComboBox()
            sorted_schedulers = sorted(scheduler_info['available'])
            disk_combo.addItems(sorted_schedulers)
            disk_combo.setCurrentText(scheduler_info['current'])
            disk_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            
            disk_layout.addWidget(disk_label)
            disk_layout.addWidget(disk_combo)
            scroll_layout.addLayout(disk_layout)
            
            # Create current value label
            current_label = QLabel(f"current: {scheduler_info['current']}")
            current_label.setContentsMargins(0, 0, 0, 10)
            scroll_layout.addWidget(current_label)
            
            # Store widgets
            widgets['disk_combos'][disk_name] = disk_combo
            widgets['disk_labels'][disk_name] = current_label
            widgets['original_schedulers'][disk_name] = scheduler_info['current']
        
        # Store original schedulers for restoration
        DiskManager.store_original_schedulers(widgets)

        # Finalize scroll area
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Add apply button
        DiskManager.create_disk_apply_button(main_layout, widgets)
        
        main_layout.addSpacing(9)
        
        # Store additional state
        widgets['disk_settings_applied'] = False
        widgets['is_process_running'] = False
        widgets['process'] = None
        
        return disk_tab, widgets

    @staticmethod
    def create_disk_apply_button(parent_layout, widgets):
        """
        Creates and adds the disk apply button to the layout.
        Args:
            parent_layout: Layout to add the button to
            widgets: Dictionary of widgets to store the button reference
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 0)

        widgets['disk_apply_button'] = QPushButton("Apply")
        widgets['disk_apply_button'].setMinimumSize(100, 30)
        widgets['disk_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets['disk_apply_button'])
        button_layout.addStretch(1)
        
        parent_layout.addWidget(button_container)

    @staticmethod
    def refresh_disk_values(widgets):
        """
        Updates the UI with current disk scheduler information.
        Args:
            widgets: Dictionary containing UI widgets to update
        """
        disk_info = DiskManager.get_disk_scheduler_info()
        
        for disk_name, scheduler_info in disk_info.items():
            if disk_name in widgets['disk_labels']:
                widgets['disk_labels'][disk_name].setText(f"current: {scheduler_info['current']}")

    @staticmethod
    def get_disk_scheduler_info():
        """
        Gets information about all disk schedulers with improved format handling.
        Returns:
            dict: Dictionary with disk names as keys and scheduler info as values
        """
        disk_info = {}
        
        try:
            # Get all scheduler files
            scheduler_files = glob.glob(DiskManager.DISK_SCHEDULER_PATH_PATTERN)
            
            for file_path in scheduler_files:
                # Extract disk name from path (e.g., /sys/block/sda/queue/scheduler -> sda)
                disk_name = file_path.split('/')[-3]
                
                try:
                    with open(file_path, 'r') as f:
                        content = f.read().strip()
                    
                    # Parse scheduler info with improved format handling
                    scheduler_info = DiskManager._parse_scheduler_content(content)
                    
                    if scheduler_info:
                        scheduler_info['path'] = file_path
                        disk_info[disk_name] = scheduler_info
                    
                except Exception as e:
                    print(f"Warning: Failed to read scheduler info for {disk_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Warning: Failed to get disk scheduler info: {e}")
        
        return disk_info

    @staticmethod
    def _parse_scheduler_content(content):
        """
        Parse scheduler content with improved error handling for various formats.
        Handles formats like:
        - Standard: "none [mq-deadline] kyber bfq"
        - Alternative: "none kyber bfq [dash]"
        - Malformed: "none kyber bfq dash" (no brackets)
        - Single scheduler: "[mq-deadline]"
        Args:
            content: Raw content from scheduler file
        Returns:
            dict: Dictionary with 'current' and 'available' schedulers, or None if parsing fails
        """
        if not content or not content.strip():
            print("Warning: Empty scheduler content")
            return None
        
        try:
            # Split content into tokens
            tokens = content.split()
            if not tokens:
                print("Warning: No scheduler tokens found")
                return None
            
            available = []
            current = None
            
            # Look for current scheduler in brackets
            bracket_pattern = re.compile(r'\[([^\]]+)\]')
            
            for token in tokens:
                bracket_match = bracket_pattern.search(token)
                if bracket_match:
                    # Found current scheduler in brackets
                    current = bracket_match.group(1)
                    # Add the scheduler name without brackets to available list
                    available.append(current)
                else:
                    # Regular scheduler name
                    available.append(token)
            
            # If no current scheduler was found in brackets, use fallback logic
            if current is None:
                print(f"Warning: No current scheduler found in brackets for content: '{content}'")
                
                # Try to detect current scheduler by common patterns or use default
                if available:
                    # Use first available scheduler as fallback
                    current = available[0]
                    print(f"Warning: Using '{current}' as fallback current scheduler")
                else:
                    # Last resort: use default scheduler
                    current = DiskManager.DEFAULT_SCHEDULER
                    available = [current]
                    print(f"Warning: Using default scheduler '{current}' as fallback")
            
            # Ensure current scheduler is in available list
            if current not in available:
                available.append(current)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_available = []
            for scheduler in available:
                if scheduler not in seen:
                    seen.add(scheduler)
                    unique_available.append(scheduler)
            
            return {
                'current': current,
                'available': unique_available
            }
            
        except Exception as e:
            print(f"Error parsing scheduler content '{content}': {e}")
            # Return fallback values
            return {
                'current': DiskManager.DEFAULT_SCHEDULER,
                'available': [DiskManager.DEFAULT_SCHEDULER]
            }

    @staticmethod
    def store_original_schedulers(widgets):
        """
        Store original disk schedulers for restoration.
        Args:
            widgets: Dictionary containing UI widgets
        """
        disk_info = DiskManager.get_disk_scheduler_info()
        widgets['original_schedulers'] = {}
        
        for disk_name, scheduler_info in disk_info.items():
            widgets['original_schedulers'][disk_name] = scheduler_info['current']

    @staticmethod
    def check_if_disk_settings_already_applied(widgets):
        """
        Check if the selected disk settings are already applied.
        Args:
            widgets: Dictionary containing UI widgets
        Returns:
            tuple: (bool, str) - (settings_already_applied, message)
        """
        current_disk_info = DiskManager.get_disk_scheduler_info()
        settings_changed = False
        
        for disk_name, combo in widgets['disk_combos'].items():
            selected_scheduler = combo.currentText()
            
            if disk_name in current_disk_info:
                current_scheduler = current_disk_info[disk_name]['current']
                if selected_scheduler != current_scheduler:
                    settings_changed = True
                    break
        
        if not settings_changed:
            return True, "Settings already applied"
        
        return False, "Settings need to be applied"

    @staticmethod
    def apply_disk_settings(widgets, main_window):
        """
        Apply disk scheduler settings.
        Args:
            widgets: Dictionary containing UI widgets
            main_window: Reference to main window for system tray notifications
        """
        if widgets['is_process_running']:
            return

        # Check if settings are already applied
        already_applied, message = DiskManager.check_if_disk_settings_already_applied(widgets)
        
        if already_applied:
            if main_window and hasattr(main_window, 'tray_icon'):
                main_window.tray_icon.showMessage(
                    "volt-gui", 
                    message, 
                    QSystemTrayIcon.MessageIcon.Information, 
                    2000
                )
            return

        # Prepare scheduler changes
        scheduler_changes = []
        for disk_name, combo in widgets['disk_combos'].items():
            selected_scheduler = combo.currentText()
            scheduler_changes.append(f"{disk_name}:{selected_scheduler}")

        # Apply settings
        widgets['disk_apply_button'].setEnabled(False)
        widgets['process'] = QProcess()
        
        # Pass all changes as arguments to volt-helper with -d flag
        args = ["/usr/local/bin/volt-helper", "-d"] + scheduler_changes
        widgets['process'].start("pkexec", args)
        widgets['process'].finished.connect(
            lambda: DiskManager._on_process_finished(widgets, main_window)
        )
        widgets['is_process_running'] = True
        widgets['disk_settings_applied'] = True

    @staticmethod
    def restore_disk_settings(widgets):
        """
        Restore disk settings to original values.
        Args:
            widgets: Dictionary containing UI widgets with original values
        """
        if widgets['disk_settings_applied']:
            try:
                # Prepare original scheduler changes
                scheduler_changes = []
                for disk_name, original_scheduler in widgets['original_schedulers'].items():
                    scheduler_changes.append(f"{disk_name}:{original_scheduler}")
                
                process = QProcess()
                args = ["/usr/local/bin/volt-helper", "-d"] + scheduler_changes
                process.start("pkexec", args)
                process.waitForFinished()
            except Exception:
                pass

    @staticmethod
    def _on_process_finished(widgets, main_window):
        """
        Handle process completion.
        Args:
            widgets: Dictionary containing UI widgets
            main_window: Reference to main window for notifications
        """
        widgets['is_process_running'] = False
        widgets['disk_apply_button'].setEnabled(True)
        
        # Get exit code from the process
        exit_code = 0
        if widgets['process']:
            exit_code = widgets['process'].exitCode()
        
        # Refresh UI
        DiskManager.refresh_disk_values(widgets)
        
        # Show notification
        if main_window and hasattr(main_window, 'tray_icon'):
            main_window.tray_icon.showMessage(
                "volt-gui", 
                "Settings applied successfully" if exit_code == 0 else "Error applying settings",
                QSystemTrayIcon.MessageIcon.Information if exit_code == 0 else QSystemTrayIcon.MessageIcon.Critical,
                2000
            )
        
        # Clean up process
        if widgets['process']:
            widgets['process'].deleteLater()
            widgets['process'] = None