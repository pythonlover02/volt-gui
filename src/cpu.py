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
    CPU_GOVERNOR_PATH = "/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
    DEFAULT_GOVERNOR = "powersave"
    AVAILABLE_GOVERNORS = ["unset", "performance", "powersave", "userspace", "ondemand", "conservative", "schedutil"]
    AVAILABLE_SCHEDULERS = ["unset", "none", "scx_bpfland", "scx_flash", "scx_lavd", "scx_rusty"]
    
    @staticmethod
    def create_cpu_tab():
        cpu_tab = QWidget()
        cpu_layout = QVBoxLayout(cpu_tab)
        widgets = {}
        
        CPUManager._create_governor_section(cpu_layout, widgets)
        CPUManager._create_scheduler_section(cpu_layout, widgets)
        cpu_layout.addStretch(1)
        CPUManager._create_apply_button(cpu_layout, widgets)
        
        return cpu_tab, widgets
    
    @staticmethod
    def _create_governor_section(cpu_layout, widgets):
        gov_layout = QHBoxLayout()
        gov_label = QLabel("CPU Governor:")
        gov_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['gov_combo'] = QComboBox()
        widgets['gov_combo'].addItems(CPUManager.AVAILABLE_GOVERNORS)
        widgets['gov_combo'].setCurrentText("unset")
        widgets['gov_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        gov_layout.addWidget(gov_label)
        gov_layout.addWidget(widgets['gov_combo'])
        
        widgets['current_gov_value'] = QLabel("Updating...")
        
        cpu_layout.addLayout(gov_layout)
        cpu_layout.addWidget(widgets['current_gov_value'])

    @staticmethod
    def _create_scheduler_section(cpu_layout, widgets):
        sched_layout = QHBoxLayout()
        sched_label = QLabel("Pluggable CPU Scheduler:")
        sched_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['sched_combo'] = QComboBox()
        widgets['sched_combo'].addItems(CPUManager.AVAILABLE_SCHEDULERS)
        widgets['sched_combo'].setCurrentText("unset")
        widgets['sched_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        sched_layout.addWidget(sched_label)
        sched_layout.addWidget(widgets['sched_combo'])
        
        widgets['current_sched_value'] = QLabel("Updating...")
        
        cpu_layout.addLayout(sched_layout)
        cpu_layout.addWidget(widgets['current_sched_value'])
    
    @staticmethod
    def _create_apply_button(cpu_layout, widgets):
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        cpu_apply_layout = QHBoxLayout(button_container)
        cpu_apply_layout.setContentsMargins(10, 10, 10, 5)
        
        widgets['cpu_apply_button'] = QPushButton("Apply")
        widgets['cpu_apply_button'].setMinimumSize(100, 30)
        widgets['cpu_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        cpu_apply_layout.addStretch(1)
        cpu_apply_layout.addWidget(widgets['cpu_apply_button'])
        cpu_apply_layout.addStretch(1)
        
        cpu_layout.addWidget(button_container)
    
    @staticmethod
    def get_available_governors():
        return CPUManager.AVAILABLE_GOVERNORS

    @staticmethod
    def get_available_schedulers():
        return CPUManager.AVAILABLE_SCHEDULERS

    @staticmethod
    def get_current_governor():
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", "r") as f:
                return f.read().strip()
        except Exception:
            return CPUManager.DEFAULT_GOVERNOR

    @staticmethod
    def get_current_scheduler():
        try:
            return CPUManager._find_running_scheduler()
        except subprocess.CalledProcessError:
            return "none"
    
    @staticmethod
    def refresh_cpu_governors(widgets):
        widgets['current_gov_value'].setText("Updating...")
        try:
            current_governor = CPUManager.get_current_governor()
            widgets['current_gov_value'].setText(f"current: {current_governor}")
        except Exception:
            widgets['current_gov_value'].setText("Error")
    
    @staticmethod
    def refresh_current_scheduler(widgets):
        widgets['current_sched_value'].setText("Updating...")
        try:
            running_scheduler = CPUManager._find_running_scheduler()
            schedulers = CPUManager.AVAILABLE_SCHEDULERS.copy()
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
        """Refresh all CPU values - similar to kernel manager"""
        CPUManager.refresh_cpu_governors(widgets)
        CPUManager.refresh_current_scheduler(widgets)
    
    @staticmethod
    def _find_running_scheduler():
        result = subprocess.run(
            ["ps", "-eo", "comm"],
            capture_output=True,
            text=True,
            check=True
        )
        processes = result.stdout.strip().splitlines()
        return next((p.strip() for p in processes if p.strip().startswith("scx_")), "none")