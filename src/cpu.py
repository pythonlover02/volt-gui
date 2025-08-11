import glob
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, QProcess
from workarounds import WorkaroundManager


class CPUManager:
    """
    Main CPU management class that handles CPU governors and schedulers.
    """
    
    CPU_GOVERNOR_PATH = "/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
    SCHEDULER_SEARCH_PATHS = ["/usr/bin/", "/usr/local/bin/"]
    BASE_SCHEDULERS = ["unset", "none"]

    @staticmethod
    def get_available_governors():
        """
        Gets the available CPU governors from the system.
        """
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors", "r") as f:
                governors = f.read().strip().split()
                return ["unset"] + governors
        except Exception as e:
            print(f"Error reading available governors: {e}")
            return None

    @staticmethod
    def get_available_schedulers():
        """
        Dynamically find available scx_ schedulers in the configured paths.
        """
        schedulers = CPUManager.BASE_SCHEDULERS.copy()
        
        for search_path in CPUManager.SCHEDULER_SEARCH_PATHS:
            try:
                scx_files = glob.glob(os.path.join(search_path, "scx_*"))
                for file_path in scx_files:
                    scheduler_name = os.path.basename(file_path)
                    if os.access(file_path, os.X_OK) and scheduler_name not in schedulers:
                        schedulers.append(scheduler_name)
            except Exception:
                continue
        
        return schedulers

    @staticmethod
    def get_current_governor():
        """
        Gets the current CPU governor.
        """
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", "r") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading current governor: {e}")
            return None

    @staticmethod
    def get_current_scheduler():
        """
        Gets the current CPU scheduler.
        """
        try:
            process = QProcess()
            WorkaroundManager.setup_clean_process(process)
            process.start("ps", ["-eo", "comm"])
            
            if process.waitForFinished(10000):  # 10 second timeout
                output = process.readAllStandardOutput().data().decode()
                processes = output.strip().splitlines()
                return next((p.strip() for p in processes if p.strip().startswith("scx_")), "none")
            return "none"
        except Exception as e:
            print(f"Error getting current scheduler: {e}")
            return None

    @staticmethod
    def create_cpu_tab():
        """
        Creates and returns the CPU management tab widget.
        """
        cpu_tab = QWidget()
        main_layout = QVBoxLayout(cpu_tab)
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
        
        gov_layout = QHBoxLayout()
        gov_label = QLabel("CPU Governor:")
        gov_label.setWordWrap(True)
        gov_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['gov_combo'] = QComboBox()
        available_governors = CPUManager.get_available_governors()
        widgets['gov_combo'].addItems(available_governors)
        widgets['gov_combo'].setCurrentText("unset")
        widgets['gov_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        widgets['available_governors'] = available_governors
        
        gov_layout.addWidget(gov_label)
        gov_layout.addWidget(widgets['gov_combo'])
        scroll_layout.addLayout(gov_layout)
        
        widgets['current_gov_value'] = QLabel("Updating...")
        widgets['current_gov_value'].setContentsMargins(0, 0, 0, 10)
        scroll_layout.addWidget(widgets['current_gov_value'])
        
        sched_layout = QHBoxLayout()
        sched_label = QLabel("Pluggable CPU Scheduler:")
        sched_label.setWordWrap(True)
        sched_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['sched_combo'] = QComboBox()
        
        available_schedulers = CPUManager.get_available_schedulers()
        scx_schedulers_found = len([s for s in available_schedulers if s.startswith("scx_")]) > 0
        
        if scx_schedulers_found:
            widgets['sched_combo'].addItems(available_schedulers)
            widgets['sched_combo'].setCurrentText("unset")
            widgets['available_schedulers'] = available_schedulers
        else:
            widgets['sched_combo'].addItems(CPUManager.BASE_SCHEDULERS)
            widgets['sched_combo'].setCurrentText("unset")
            widgets['sched_combo'].setEnabled(False)
            widgets['sched_combo'].setToolTip("SCX schedulers not found - CPU scheduler selection disabled")
            widgets['available_schedulers'] = CPUManager.BASE_SCHEDULERS
        
        widgets['sched_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        sched_layout.addWidget(sched_label)
        sched_layout.addWidget(widgets['sched_combo'])
        scroll_layout.addLayout(sched_layout)
        
        widgets['current_sched_value'] = QLabel("Updating...")
        widgets['current_sched_value'].setContentsMargins(0, 0, 0, 10)
        scroll_layout.addWidget(widgets['current_sched_value'])
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        CPUManager.create_cpu_apply_button(main_layout, widgets)
        
        widgets['cpu_settings_applied'] = False
        widgets['is_process_running'] = False
        widgets['process'] = None
        
        return cpu_tab, widgets

    @staticmethod
    def create_cpu_apply_button(parent_layout, widgets):
        """
        Creates and adds the CPU apply button to the layout.
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(11, 10, 11, 9)

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
        """
        widgets['current_gov_value'].setText("Updating...")
        try:
            current_governor = CPUManager.get_current_governor()
            widgets['current_gov_value'].setText(f"current: {current_governor}")
        except Exception:
            widgets['current_gov_value'].setText("Error")
        
        widgets['current_sched_value'].setText("Updating...")
        try:
            running_scheduler = CPUManager.get_current_scheduler()
            
            if running_scheduler != "none" and "<defunc>" in running_scheduler:
                running_scheduler = "none"
            
            if widgets['sched_combo'].isEnabled():
                current_available = CPUManager.get_available_schedulers()
                
                if running_scheduler not in widgets['available_schedulers'] and running_scheduler != "none":
                    widgets['available_schedulers'].append(running_scheduler)
                    current_selection = widgets['sched_combo'].currentText()
                    widgets['sched_combo'].clear()
                    widgets['sched_combo'].addItems(widgets['available_schedulers'])
                    widgets['sched_combo'].setCurrentText(current_selection)
            
            widgets['current_sched_value'].setText(f"current: {running_scheduler}")
            
        except Exception:
            widgets['current_sched_value'].setText("Error")