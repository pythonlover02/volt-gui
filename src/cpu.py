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

class CPUManager:
    """
    Main CPU management class that handles CPU governors and schedulers.
    Provides static methods to create UI elements and manage CPU settings.
    """
    
    # Path pattern to CPU governor files
    CPU_GOVERNOR_PATH = "/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
    
    # Default governor fallback
    DEFAULT_GOVERNOR = "powersave"
    
    # Available CPU governors
    AVAILABLE_GOVERNORS = [
        "unset", "performance", "powersave", 
        "userspace", "ondemand", "conservative", 
        "schedutil"
    ]
    
    # Paths to search for scx_ schedulers (easy to extend)
    SCHEDULER_SEARCH_PATHS = [
        "/usr/bin/",
        "/usr/local/bin/"
    ]
    
    # Base available CPU schedulers (always present)
    BASE_SCHEDULERS = ["unset", "none"]

    @staticmethod
    def find_available_schedulers():
        """
        Dynamically find available scx_ schedulers in the configured paths.
        Returns:
            list: List of available schedulers including base schedulers
        """
        schedulers = CPUManager.BASE_SCHEDULERS.copy()
        
        for search_path in CPUManager.SCHEDULER_SEARCH_PATHS:
            try:
                # Use glob to find all scx_* files in the path
                scx_files = glob.glob(os.path.join(search_path, "scx_*"))
                for file_path in scx_files:
                    scheduler_name = os.path.basename(file_path)
                    # Check if it's executable and not already in list
                    if os.access(file_path, os.X_OK) and scheduler_name not in schedulers:
                        schedulers.append(scheduler_name)
            except Exception:
                # Skip paths that can't be accessed
                continue
        
        return schedulers

    @staticmethod
    def create_cpu_tab():
        """
        Creates and returns the CPU management tab widget.
        Returns:
            tuple: (QWidget, dict) The tab widget and a dictionary of UI elements
        """
        cpu_tab = QWidget()
        main_layout = QVBoxLayout(cpu_tab)
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
        
        # Governor section
        gov_layout = QHBoxLayout()
        gov_label = QLabel("CPU Governor:")
        gov_label.setWordWrap(True)
        gov_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['gov_combo'] = QComboBox()
        widgets['gov_combo'].addItems(CPUManager.AVAILABLE_GOVERNORS)
        widgets['gov_combo'].setCurrentText("unset")
        widgets['gov_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        gov_layout.addWidget(gov_label)
        gov_layout.addWidget(widgets['gov_combo'])
        scroll_layout.addLayout(gov_layout)
        
        widgets['current_gov_value'] = QLabel("Updating...")
        widgets['current_gov_value'].setContentsMargins(0, 0, 0, 10)
        scroll_layout.addWidget(widgets['current_gov_value'])
        
        # Scheduler section
        sched_layout = QHBoxLayout()
        sched_label = QLabel("Pluggable CPU Scheduler:")
        sched_label.setWordWrap(True)
        sched_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['sched_combo'] = QComboBox()
        # Populate with dynamically found schedulers
        available_schedulers = CPUManager.find_available_schedulers()
        widgets['sched_combo'].addItems(available_schedulers)
        widgets['sched_combo'].setCurrentText("unset")
        widgets['sched_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Store the list of schedulers that were available at creation time
        widgets['available_schedulers'] = available_schedulers
        
        # Check if no scx schedulers were found (only base schedulers exist)
        scx_schedulers_found = len([s for s in available_schedulers if s.startswith("scx_")]) > 0
        if not scx_schedulers_found:
            widgets['sched_combo'].setEnabled(False)
            widgets['scheduler_locked'] = True
        else:
            widgets['scheduler_locked'] = False
        
        sched_layout.addWidget(sched_label)
        sched_layout.addWidget(widgets['sched_combo'])
        scroll_layout.addLayout(sched_layout)
        
        widgets['current_sched_value'] = QLabel("Updating...")
        widgets['current_sched_value'].setContentsMargins(0, 0, 0, 10)
        scroll_layout.addWidget(widgets['current_sched_value'])
        
        # Finalize scroll area
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Add apply button
        CPUManager.create_cpu_apply_button(main_layout, widgets)
        
        # Store original values for restoration
        widgets['original_governor'] = CPUManager.get_current_governor()
        widgets['original_scheduler'] = CPUManager.get_current_scheduler()
        widgets['cpu_settings_applied'] = False
        widgets['is_process_running'] = False
        widgets['process'] = None
        
        return cpu_tab, widgets

    @staticmethod
    def create_cpu_apply_button(parent_layout, widgets):
        """
        Creates and adds the CPU apply button to the layout.
        Args:
            parent_layout: Layout to add the button to
            widgets: Dictionary of widgets to store the button reference
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 10)

        widgets['cpu_apply_button'] = QPushButton("Apply")
        widgets['cpu_apply_button'].setMinimumSize(100, 30)
        widgets['cpu_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets['cpu_apply_button'])
        button_layout.addStretch(1)
        
        parent_layout.addWidget(button_container)

    @staticmethod
    def refresh_cpu_values(widgets):
        """
        Updates the UI with current CPU governor and scheduler information.
        Args:
            widgets: Dictionary containing UI widgets to update
        """
        # Update governor
        widgets['current_gov_value'].setText("Updating...")
        try:
            current_governor = CPUManager.get_current_governor()
            widgets['current_gov_value'].setText(f"current: {current_governor}")
        except Exception:
            widgets['current_gov_value'].setText("Error")
        
        # Update scheduler
        widgets['current_sched_value'].setText("Updating...")
        try:
            running_scheduler = CPUManager._find_running_scheduler()
            
            # Filter out zombie processes (<defunc>)
            if running_scheduler != "none" and "<defunc>" in running_scheduler:
                running_scheduler = "none"
            
            # Check if we need to update the combo box with new schedulers
            current_available = CPUManager.find_available_schedulers()
            
            # If schedulers are locked (no scx found initially), check if any are now available
            if widgets.get('scheduler_locked', False):
                scx_schedulers_found = len([s for s in current_available if s.startswith("scx_")]) > 0
                if scx_schedulers_found:
                    # Unlock and update the combo box
                    widgets['sched_combo'].setEnabled(True)
                    widgets['scheduler_locked'] = False
                    widgets['available_schedulers'] = current_available
                    current_selection = widgets['sched_combo'].currentText()
                    widgets['sched_combo'].clear()
                    widgets['sched_combo'].addItems(current_available)
                    # Try to restore previous selection
                    if current_selection in current_available:
                        widgets['sched_combo'].setCurrentText(current_selection)
            else:
                # Normal update: add new schedulers if found
                if running_scheduler not in widgets['available_schedulers'] and running_scheduler != "none":
                    widgets['available_schedulers'].append(running_scheduler)
                    current_selection = widgets['sched_combo'].currentText()
                    widgets['sched_combo'].clear()
                    widgets['sched_combo'].addItems(widgets['available_schedulers'])
                    widgets['sched_combo'].setCurrentText(current_selection)
            
            widgets['current_sched_value'].setText(f"current: {running_scheduler}")
            
        except Exception:
            widgets['current_sched_value'].setText("Error")

    @staticmethod
    def check_if_cpu_settings_already_applied(widgets):
        """
        Check if the selected CPU settings are already applied.
        Args:
            widgets: Dictionary containing UI widgets
        Returns:
            tuple: (bool, str) - (settings_already_applied, message)
        """
        governor = widgets['gov_combo'].currentText()
        scheduler = widgets['sched_combo'].currentText()
        
        current_governor = CPUManager.get_current_governor()
        current_scheduler = CPUManager.get_current_scheduler()
        
        # Check if both settings match current state
        governor_matches = (governor == "unset" or governor == current_governor)
        scheduler_matches = (scheduler == "unset" or scheduler == current_scheduler)
        
        if governor_matches and scheduler_matches:
            return True, "Settings already applied"
        
        # Check if scheduler is already running but governor needs change
        if scheduler != "unset" and scheduler == current_scheduler:
            if governor != "unset" and governor != current_governor:
                return False, "Governor needs update"
        
        return False, "Settings need to be applied"

    @staticmethod
    def apply_cpu_settings(widgets, main_window):
        """
        Apply CPU governor and scheduler settings.
        Args:
            widgets: Dictionary containing UI widgets
            main_window: Reference to main window for system tray notifications
        """
        if widgets['is_process_running']:
            return

        governor = widgets['gov_combo'].currentText()
        scheduler = widgets['sched_combo'].currentText()
        
        # Check if settings are already applied
        already_applied, message = CPUManager.check_if_cpu_settings_already_applied(widgets)
        
        if already_applied:
            if main_window and hasattr(main_window, 'tray_icon'):
                main_window.tray_icon.showMessage(
                    "volt-gui", 
                    message, 
                    QSystemTrayIcon.MessageIcon.Information, 
                    2000
                )
            return

        current_running_scheduler = CPUManager.get_current_scheduler()

        # Handle case where scheduler is already running but governor needs change
        if scheduler != "unset" and scheduler == current_running_scheduler:
            current_governor = CPUManager.get_current_governor()
            if governor != "unset" and governor != current_governor:
                widgets['cpu_apply_button'].setEnabled(False)
                widgets['process'] = QProcess()
                widgets['process'].start("pkexec", ["/usr/local/bin/volt-helper", "-c", governor, "unset"])
                widgets['process'].finished.connect(
                    lambda: CPUManager._on_process_finished(widgets, main_window)
                )
                widgets['is_process_running'] = True
                widgets['cpu_settings_applied'] = True
                return

        # Apply both governor and scheduler
        widgets['cpu_apply_button'].setEnabled(False)

        widgets['process'] = QProcess()
        widgets['process'].start("pkexec", ["/usr/local/bin/volt-helper", "-c", governor, scheduler])
        widgets['process'].finished.connect(
            lambda: CPUManager._on_process_finished(widgets, main_window)
        )
        widgets['is_process_running'] = True
        widgets['cpu_settings_applied'] = True

    @staticmethod
    def restore_cpu_settings(widgets):
        """
        Restore CPU settings to original values.
        Args:
            widgets: Dictionary containing UI widgets with original values
        """
        if widgets['cpu_settings_applied']:
            try:
                process = QProcess()
                process.start("pkexec", [
                    "/usr/local/bin/volt-helper", 
                    "-c",
                    widgets['original_governor'], 
                    widgets['original_scheduler']
                ])
                process.waitForFinished()
            except Exception:
                pass

    @staticmethod
    def get_current_governor():
        """
        Gets the current CPU governor setting.
        Returns:
            str: Current governor or default if error occurs
        """
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", "r") as f:
                return f.read().strip()
        except Exception:
            return CPUManager.DEFAULT_GOVERNOR

    @staticmethod
    def get_current_scheduler():
        """
        Gets the currently running CPU scheduler.
        Returns:
            str: Running scheduler name or "none" if error occurs
        """
        try:
            return CPUManager._find_running_scheduler()
        except subprocess.CalledProcessError:
            return "none"
    
    @staticmethod
    def _find_running_scheduler():
        """
        Internal method to detect the currently running CPU scheduler.
        Returns:
            str: Name of running scheduler or "none" if not found
        Raises:
            subprocess.CalledProcessError: If ps command fails
        """
        result = subprocess.run(
            ["ps", "-eo", "comm"],
            capture_output=True,
            text=True,
            check=True
        )
        processes = result.stdout.strip().splitlines()
        return next((p.strip() for p in processes if p.strip().startswith("scx_")), "none")

    @staticmethod
    def _on_process_finished(widgets, main_window):
        """
        Handle process completion.
        Args:
            widgets: Dictionary containing UI widgets
            main_window: Reference to main window for notifications
        """
        widgets['is_process_running'] = False
        widgets['cpu_apply_button'].setEnabled(True)
        
        # Get exit code from the process
        exit_code = 0
        if widgets['process']:
            exit_code = widgets['process'].exitCode()
        
        # Refresh UI
        CPUManager.refresh_cpu_values(widgets)
        
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