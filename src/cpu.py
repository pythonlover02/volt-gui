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
        
        cpu_governors_layout = QVBoxLayout()
        governors_scroll = QScrollArea()
        governors_scroll.setWidgetResizable(True)
        governors_scroll.setFrameShape(QFrame.NoFrame)
        
        governors_container = QWidget()
        governors_container.setProperty("statusContainer", "true")
        widgets['governors_layout'] = QVBoxLayout(governors_container)
        widgets['governors_layout'].setSpacing(5)
        widgets['governors_layout'].setContentsMargins(8, 8, 8, 8)
        
        governors_scroll.setWidget(governors_container)
        governors_scroll.setMaximumHeight(150)
        
        cpu_governors_layout.addWidget(governors_scroll)
        cpu_layout.addLayout(gov_layout)
        cpu_layout.addLayout(cpu_governors_layout)

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
        
        sched_status_layout = QVBoxLayout()
        sched_status_scroll = QScrollArea()
        sched_status_scroll.setWidgetResizable(True)
        sched_status_scroll.setFrameShape(QFrame.NoFrame)
        
        sched_status_container = QWidget()
        sched_status_container.setProperty("statusContainer", "true")
        widgets['sched_status_layout'] = QVBoxLayout(sched_status_container)
        widgets['sched_status_layout'].setSpacing(5)
        widgets['sched_status_layout'].setContentsMargins(8, 8, 8, 8)
        
        widgets['current_sched_value'] = QLabel("Checking...")
        widgets['sched_status_layout'].addWidget(widgets['current_sched_value'])
        
        sched_status_scroll.setWidget(sched_status_container)
        sched_status_scroll.setMaximumHeight(48)
        
        sched_status_layout.addWidget(sched_status_scroll)
        cpu_layout.addLayout(sched_layout)
        cpu_layout.addLayout(sched_status_layout)
    
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
            result = subprocess.run(
                ["cat", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"],
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return CPUManager.DEFAULT_GOVERNOR

    @staticmethod
    def get_current_scheduler():
        try:
            result = subprocess.run(
                ["ps", "-eo", "comm"],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.strip().split('\n'):
                process_name = line.strip()
                if process_name.startswith("scx_"):
                    return process_name
            
            return "none"
        except subprocess.CalledProcessError:
            return "none"
    
    @staticmethod
    def refresh_cpu_governors(governors_layout, cpu_governor_labels):
        CPUManager._clear_governor_labels(governors_layout, cpu_governor_labels)
        path_info = CPUManager._get_cpu_core_paths()
        cpu_count = CPUManager._create_governor_status_labels(governors_layout, cpu_governor_labels, path_info)
        
        if cpu_count == 0:
            label = QLabel("No CPU governors found")
            cpu_governor_labels[-1] = label
            governors_layout.addWidget(label)
    
    @staticmethod
    def _clear_governor_labels(governors_layout, cpu_governor_labels):
        if cpu_governor_labels:
            for label in cpu_governor_labels.values():
                governors_layout.removeWidget(label)
                label.deleteLater()
            cpu_governor_labels.clear()
    
    @staticmethod
    def _get_cpu_core_paths():
        cpu_paths = glob.glob(CPUManager.CPU_GOVERNOR_PATH)
        path_info = []
        
        for cpu_path in cpu_paths:
            match = re.search(r'cpu(\d+)', cpu_path)
            if match:
                cpu_num = int(match.group(1))
                path_info.append((cpu_num, cpu_path))
        
        return sorted(path_info)
    
    @staticmethod
    def _create_governor_status_labels(governors_layout, cpu_governor_labels, path_info):
        cpu_count = 0
        
        for cpu_num, cpu_path in path_info:
            try:
                with open(cpu_path, 'r') as f:
                    governor = f.read().strip()
            except Exception as e:
                governor = "unknown"
                print(f"Error reading governor for CPU{cpu_num}: {e}")
            
            label = QLabel(f"cpu{cpu_num}: {governor}")
            cpu_governor_labels[cpu_num] = label
            governors_layout.addWidget(label)
            cpu_count += 1
        
        return cpu_count
    
    @staticmethod
    def refresh_current_scheduler(current_sched_value, schedulers, sched_combo):
        try:
            running_scheduler = CPUManager._find_running_scheduler()
            
            if running_scheduler != "none" and running_scheduler not in schedulers:
                print(f"Found unlisted scheduler: {running_scheduler}")
                schedulers.append(running_scheduler)
                sched_combo.clear()
                sched_combo.addItems(schedulers)
            
            current_sched_value.setText(f"Current: {running_scheduler}")
            return running_scheduler
            
        except Exception as e:
            print(f"Error checking current scheduler: {e}")
            current_sched_value.setText("Error")
            return None
    
    @staticmethod
    def _find_running_scheduler():
        result = subprocess.run(
            ["ps", "-eo", "comm"],
            capture_output=True,
            text=True,
            check=True
        )
        
        for line in result.stdout.strip().split('\n'):
            process_name = line.strip()
            if process_name.startswith("scx_"):
                return process_name
        
        return "none"
    
    @staticmethod
    def create_cpu_scripts():
        return CPUManager._create_apply_script(), CPUManager._create_reset_script()
    
    @staticmethod
    def _create_apply_script():
        return """#!/bin/bash

apply_governor() {
    local governor="$1"
    if [ "$governor" != "unset" ]; then
        echo "Applying CPU governor: $governor"
        for CPU_PATH in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
            echo "$governor" > "$CPU_PATH"
            echo "  Applied to $CPU_PATH"
        done
    else
        echo "Governor set to unset, skipping governor application"
    fi
}

handle_scheduler() {
    local scheduler="$1"
    
    if [ "$scheduler" != "unset" ]; then
        echo "Terminating existing SCX schedulers..."
        for proc in $(ps -eo comm | grep "^scx_"); do
            echo "Attempting to terminate $proc"
            pkill -INT -f "$proc"
            sleep 0.5
            
            if pgrep -f "$proc" > /dev/null; then
                pkill -TERM -f "$proc"
                sleep 0.5
                
                if pgrep -f "$proc" > /dev/null; then
                    pkill -KILL -f "$proc"
                    sleep 0.2
                fi
            fi
        done
        
        if [ "$scheduler" != "none" ]; then
            echo "Starting scheduler: $scheduler"
            "$scheduler" &
        fi
    else
        echo "Scheduler set to unset, skipping scheduler changes"
    fi
}

GOVERNOR="$1"
SCHEDULER="$2"

apply_governor "$GOVERNOR"
handle_scheduler "$SCHEDULER"

exit 0
"""
    
    @staticmethod
    def _create_reset_script():
        return """#!/bin/bash

apply_governor() {
    local governor="$1"
    echo "Resetting CPU governor to: $governor"
    for CPU_PATH in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo "$governor" > "$CPU_PATH"
        echo "  Reset on $CPU_PATH"
    done
}

terminate_schedulers() {
    echo "Terminating all SCX schedulers..."
    for proc in $(ps -eo comm | grep "^scx_"); do
        echo "Attempting to terminate $proc"
        pkill -INT -f "$proc"
        sleep 0.5
        
        if pgrep -f "$proc" > /dev/null; then
            pkill -TERM -f "$proc"
            sleep 0.5
            
            if pgrep -f "$proc" > /dev/null; then
                pkill -KILL -f "$proc"
                sleep 0.2
            fi
        fi
    done
}

GOVERNOR="$1"

apply_governor "$GOVERNOR"
terminate_schedulers

exit 0
"""
    
    @staticmethod
    def write_and_execute_script(script_content, script_name, args):
        script_path = f"/tmp/{script_name}"
        
        with open(script_path, "w") as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        process = QProcess()
        process.start("pkexec", [script_path] + args)
        return process
