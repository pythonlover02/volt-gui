import glob
import re
import subprocess
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QProcess


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
    
    # Available CPU schedulers
    AVAILABLE_SCHEDULERS = [
        "unset", "none", "scx_bpfland", 
        "scx_flash", "scx_lavd", "scx_rusty"
    ]
    
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
        scroll_layout.setContentsMargins(10, 10, 10, 0)  # Added horizontal margins here
        
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
        widgets['current_gov_value'].setContentsMargins(0, 0, 0, 10)  # Added bottom margin
        scroll_layout.addWidget(widgets['current_gov_value'])
        
        # Scheduler section
        sched_layout = QHBoxLayout()
        sched_label = QLabel("Pluggable CPU Scheduler:")
        sched_label.setWordWrap(True)
        sched_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['sched_combo'] = QComboBox()
        widgets['sched_combo'].addItems(CPUManager.AVAILABLE_SCHEDULERS)
        widgets['sched_combo'].setCurrentText("unset")
        widgets['sched_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        sched_layout.addWidget(sched_label)
        sched_layout.addWidget(widgets['sched_combo'])
        scroll_layout.addLayout(sched_layout)
        
        widgets['current_sched_value'] = QLabel("Updating...")
        widgets['current_sched_value'].setContentsMargins(0, 0, 0, 10)  # Added bottom margin
        scroll_layout.addWidget(widgets['current_sched_value'])
        
        # Finalize scroll area
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Apply button
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 10)  # Consistent with other tabs

        widgets['cpu_apply_button'] = QPushButton("Apply")
        widgets['cpu_apply_button'].setMinimumSize(100, 30)
        widgets['cpu_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets['cpu_apply_button'])
        button_layout.addStretch(1)
        
        main_layout.addWidget(button_container)
        
        return cpu_tab, widgets

    @staticmethod
    def get_available_governors():
        """
        Returns the list of available CPU governors.
        Returns:
            list: Available CPU governors
        """
        return CPUManager.AVAILABLE_GOVERNORS

    @staticmethod
    def get_available_schedulers():
        """
        Returns the list of available CPU schedulers.
        Returns:
            list: Available CPU schedulers
        """
        return CPUManager.AVAILABLE_SCHEDULERS

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
    def refresh_cpu_governors(widgets):
        """
        Updates the UI with current governor information.
        Args:
            widgets: Dictionary containing UI widgets to update
        """
        widgets['current_gov_value'].setText("Updating...")
        try:
            current_governor = CPUManager.get_current_governor()
            widgets['current_gov_value'].setText(f"current: {current_governor}")
        except Exception:
            widgets['current_gov_value'].setText("Error")
    
    @staticmethod
    def refresh_current_scheduler(widgets):
        """
        Updates the UI with current scheduler information.
        Args:
            widgets: Dictionary containing UI widgets to update
        Returns:
            str: The detected running scheduler or None on error
        """
        widgets['current_sched_value'].setText("Updating...")
        try:
            running_scheduler = CPUManager._find_running_scheduler()
            schedulers = CPUManager.AVAILABLE_SCHEDULERS.copy()
            
            # Filter out zombie processes (<defunc>)
            if running_scheduler != "none" and "<defunc>" in running_scheduler:
                running_scheduler = "none"
            
            # Only add new scheduler if it's not a zombie and not already in the list
            if running_scheduler != "none" and running_scheduler not in schedulers:
                schedulers.append(running_scheduler)
                widgets['sched_combo'].clear()
                widgets['sched_combo'].addItems(schedulers)
            
            widgets['current_sched_value'].setText(f"current: {running_scheduler}")
            return running_scheduler
            
        except Exception:
            widgets['current_sched_value'].setText("Error")
            return None
    
    @staticmethod
    def refresh_values(widgets):
        """
        Refreshes all CPU-related values in the UI.
        Args:
            widgets: Dictionary containing UI widgets to update
        """
        CPUManager.refresh_cpu_governors(widgets)
        CPUManager.refresh_current_scheduler(widgets)
    
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