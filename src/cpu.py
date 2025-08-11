import glob
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, QProcess
from workarounds import WorkaroundManager


class CPUManager:
    """
    Main CPU management class that handles CPU governors and schedulers.
    """
    
    SCHEDULER_SEARCH_PATHS = ["/usr/bin/", "/usr/local/bin/"]
    BASE_SCHEDULERS = ["unset", "none"]

    @staticmethod
    def get_available_setting(setting_path):
        """
        Check if a CPU setting file is available.
        """
        try:
            with open(setting_path, "r") as f:
                f.read()
            return True
        except Exception:
            return False

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
            return ["unset"]

    @staticmethod
    def get_cpuinfo_min_freq():
        """
        Gets the minimum possible CPU frequency in MHz.
        """
        if not CPUManager.get_available_setting("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq"):
            return None
        with open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq", "r") as f:
            return int(f.read().strip()) // 1000

    @staticmethod
    def get_cpuinfo_max_freq():
        """
        Gets the maximum possible CPU frequency in MHz.
        """
        if not CPUManager.get_available_setting("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"):
            return None
        with open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", "r") as f:
            return int(f.read().strip()) // 1000

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
    def get_current_scaling_min_freq():
        """
        Gets the current scaling minimum CPU frequency in MHz.
        """
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq", "r") as f:
                return int(f.read().strip()) // 1000
        except (IOError, ValueError, FileNotFoundError) as e:
            print(f"Error reading scaling_min_freq: {e}")
            return None

    @staticmethod
    def get_current_scaling_max_freq():
        """
        Gets the current scaling maximum CPU frequency in MHz.
        """
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq", "r") as f:
                return int(f.read().strip()) // 1000
        except (IOError, ValueError, FileNotFoundError) as e:
            print(f"Error reading scaling_max_freq: {e}")
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
        
        gov_accessible = CPUManager.get_available_setting("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
        if not gov_accessible:
            widgets['gov_combo'].setEnabled(False)
            widgets['gov_combo'].setToolTip("CPU Governor file its not available - Governor selection disabled")
        
        gov_layout.addWidget(gov_label)
        gov_layout.addWidget(widgets['gov_combo'])
        scroll_layout.addLayout(gov_layout)
        
        widgets['current_gov_value'] = QLabel("Updating...")
        widgets['current_gov_value'].setContentsMargins(0, 0, 0, 10)
        scroll_layout.addWidget(widgets['current_gov_value'])

        min_freq_mhz = CPUManager.get_cpuinfo_min_freq()
        max_freq_mhz = CPUManager.get_cpuinfo_max_freq()
        freq_info_accessible = min_freq_mhz is not None and max_freq_mhz is not None

        max_freq_layout = QHBoxLayout()
        max_freq_label = QLabel("CPU Max Frequency (MHz):")
        max_freq_label.setWordWrap(True)
        max_freq_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['max_freq_combo'] = QComboBox()
        if freq_info_accessible:
            freq_range = [str(f) for f in range(min_freq_mhz, max_freq_mhz + 100, 100)]
            widgets['max_freq_combo'].addItems(["unset"] + list(reversed(freq_range)))
        else:
            widgets['max_freq_combo'].addItems(["unset"])
        
        widgets['max_freq_combo'].setCurrentText("unset")
        widgets['max_freq_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        max_freq_accessible = CPUManager.get_available_setting("/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq")
        if not max_freq_accessible or not freq_info_accessible:
            widgets['max_freq_combo'].setEnabled(False)
            if not freq_info_accessible:
                widgets['max_freq_combo'].setToolTip("CPU frequency info files not available - Max Frequency selection disabled")
            else:
                widgets['max_freq_combo'].setToolTip("CPU max frequency file its not available - Max Frequency selection disabled")
        
        max_freq_layout.addWidget(max_freq_label)
        max_freq_layout.addWidget(widgets['max_freq_combo'])
        scroll_layout.addLayout(max_freq_layout)

        widgets['current_max_freq_value'] = QLabel("Updating...")
        widgets['current_max_freq_value'].setContentsMargins(0, 0, 0, 10)
        scroll_layout.addWidget(widgets['current_max_freq_value'])

        min_freq_layout = QHBoxLayout()
        min_freq_label = QLabel("CPU Min Frequency (MHz):")
        min_freq_label.setWordWrap(True)
        min_freq_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        widgets['min_freq_combo'] = QComboBox()
        
        if freq_info_accessible:
            widgets['min_freq_combo'].addItems(["unset"] + freq_range)
        else:
            widgets['min_freq_combo'].addItems(["unset"])
        
        widgets['min_freq_combo'].setCurrentText("unset")
        widgets['min_freq_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        min_freq_accessible = CPUManager.get_available_setting("/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq")
        if not min_freq_accessible or not freq_info_accessible:
            widgets['min_freq_combo'].setEnabled(False)
            if not freq_info_accessible:
                widgets['min_freq_combo'].setToolTip("CPU frequency info files not available - Min Frequency selection disabled")
            else:
                widgets['min_freq_combo'].setToolTip("CPU min frequency file its not available - Min Frequency selection disabled")

        min_freq_layout.addWidget(min_freq_label)
        min_freq_layout.addWidget(widgets['min_freq_combo'])
        scroll_layout.addLayout(min_freq_layout)

        widgets['current_min_freq_value'] = QLabel("Updating...")
        widgets['current_min_freq_value'].setContentsMargins(0, 0, 0, 10)
        scroll_layout.addWidget(widgets['current_min_freq_value'])
        
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
        button_layout.setContentsMargins(11, 10, 11, 0)

        widgets['cpu_apply_button'] = QPushButton("Apply")
        widgets['cpu_apply_button'].setMinimumSize(100, 30)
        widgets['cpu_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets['cpu_apply_button'])
        button_layout.addStretch(1)
        
        parent_layout.addWidget(button_container)
        parent_layout.addSpacing(9)

    @staticmethod
    def refresh_cpu_values(widgets):
        """
        Updates the UI with current CPU governor and scheduler information.
        """
        if not CPUManager.get_available_setting("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"):
            widgets['current_gov_value'].setText("current: unset")
        else:
            widgets['current_gov_value'].setText("Updating...")
            try:
                current_governor = CPUManager.get_current_governor()
                if current_governor is not None:
                    widgets['current_gov_value'].setText(f"current: {current_governor}")
                else:
                    widgets['current_gov_value'].setText("current: Error reading")
            except Exception:
                widgets['current_gov_value'].setText("current: Error")

        if widgets.get('max_freq_combo'):
            if not CPUManager.get_available_setting("/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq"):
                widgets['current_max_freq_value'].setText("current: unset")
            else:
                widgets['current_max_freq_value'].setText("Updating...")
                try:
                    current_max_freq = CPUManager.get_current_scaling_max_freq()
                    if current_max_freq is not None:
                        widgets['current_max_freq_value'].setText(f"current: {current_max_freq}")
                    else:
                        widgets['current_max_freq_value'].setText("current: Error reading")
                except Exception:
                    widgets['current_max_freq_value'].setText("current: Error")

        if widgets.get('min_freq_combo'):
            if not CPUManager.get_available_setting("/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq"):
                widgets['current_min_freq_value'].setText("current: unset")
            else:
                widgets['current_min_freq_value'].setText("Updating...")
                try:
                    current_min_freq = CPUManager.get_current_scaling_min_freq()
                    if current_min_freq is not None:
                        widgets['current_min_freq_value'].setText(f"current: {current_min_freq}")
                    else:
                        widgets['current_min_freq_value'].setText("current: Error reading")
                except Exception:
                    widgets['current_min_freq_value'].setText("current: Error")
        
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
            
            if running_scheduler is not None:
                widgets['current_sched_value'].setText(f"current: {running_scheduler}")
            else:
                widgets['current_sched_value'].setText("current: Error reading")
            
        except Exception:
            widgets['current_sched_value'].setText("current: Error")