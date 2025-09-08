import glob, os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, QProcess
from workarounds import WorkaroundManager

class CPUManager:

    SCHEDULER_SEARCH_PATHS = ["/usr/bin/", "/usr/local/bin/"]

    CPU_SETTINGS_CATEGORIES = {
        "Frequency": {
            'gov': {
                'label': "Governor:",
                'items': ["unset"]
            },
            'max_freq': {
                'label': "Max Frequency (MHz):",
                'items': ["unset"]
            },
            'min_freq': {
                'label': "Min Frequency (MHz):",
                'items': ["unset"]
            }
        },
        "Scheduler": {
            'sched': {
                'label': "Pluggable Scheduler:",
                'items': ["unset", "none"]
            }
        }
    }
    
    CPU_SETTINGS = {}
    for category in CPU_SETTINGS_CATEGORIES.values():
        CPU_SETTINGS.update(category)

    @staticmethod
    def get_available_setting(setting_path):
        """
        Check if a CPU setting file is available and readable.
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
        Get the list of available CPU governors.
        """
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors", "r") as f:
                governors = f.read().strip().split()
                return CPUManager.CPU_SETTINGS_CATEGORIES["Frequency"]['gov']['items'] + governors
        except Exception:
            return CPUManager.CPU_SETTINGS_CATEGORIES["Frequency"]['gov']['items'].copy()

    @staticmethod
    def get_cpuinfo_min_freq():
        """
        Get the minimum CPU frequency from cpuinfo.
        """
        if not CPUManager.get_available_setting("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq"):
            return None
        with open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq", "r") as f:
            return int(f.read().strip()) // 1000

    @staticmethod
    def get_cpuinfo_max_freq():
        """
        Get the maximum CPU frequency from cpuinfo.
        """
        if not CPUManager.get_available_setting("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"):
            return None
        with open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", "r") as f:
            return int(f.read().strip()) // 1000

    @staticmethod
    def get_available_schedulers():
        """
        Get the list of available CPU schedulers.
        """
        schedulers = CPUManager.CPU_SETTINGS_CATEGORIES["Scheduler"]['sched']['items'].copy()
        
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
        Get the currently active CPU governor.
        """
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", "r") as f:
                return f.read().strip()
        except Exception:
            return None

    @staticmethod
    def get_current_scaling_min_freq():
        """
        Get the current minimum scaling frequency.
        """
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq", "r") as f:
                return int(f.read().strip()) // 1000
        except (IOError, ValueError, FileNotFoundError):
            return None

    @staticmethod
    def get_current_scaling_max_freq():
        """
        Get the current maximum scaling frequency.
        """
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq", "r") as f:
                return int(f.read().strip()) // 1000
        except (IOError, ValueError, FileNotFoundError):
            return None

    @staticmethod
    def get_current_scheduler():
        """
        Get the currently running CPU scheduler.
        """
        try:
            process = QProcess()
            WorkaroundManager.setup_clean_process(process)
            process.start("ps", ["-eo", "comm"])
            
            if process.waitForFinished(10000):
                output = process.readAllStandardOutput().data().decode()
                processes = output.strip().splitlines()
                return next((p.strip() for p in processes if p.strip().startswith("scx_")), "none")
            return "none"
        except Exception:
            return None

    @staticmethod
    def create_cpu_tab():
        """
        Create the CPU management tab with all its widgets.
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
        
        for category_name, category_settings in CPUManager.CPU_SETTINGS_CATEGORIES.items():
            for setting_key, setting_info in category_settings.items():
                layout = QHBoxLayout()
                label = QLabel(setting_info['label'])
                label.setWordWrap(True)
                label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                
                widgets[setting_key] = QComboBox()
                
                if setting_key == 'gov':
                    available_governors = CPUManager.get_available_governors()
                    widgets[setting_key].addItems(available_governors)
                    widgets['available_governors'] = available_governors
                    
                    gov_accessible = CPUManager.get_available_setting("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
                    if not gov_accessible:
                        widgets[setting_key].setEnabled(False)
                        widgets[setting_key].setToolTip("CPU Governor file its not available - Governor selection disabled")
                
                elif setting_key == 'max_freq' or setting_key == 'min_freq':
                    min_freq_mhz = CPUManager.get_cpuinfo_min_freq()
                    max_freq_mhz = CPUManager.get_cpuinfo_max_freq()
                    freq_info_accessible = min_freq_mhz is not None and max_freq_mhz is not None
                    
                    if freq_info_accessible:
                        freq_range = [str(f) for f in range(min_freq_mhz, max_freq_mhz + 100, 100)]
                        if setting_key == 'max_freq':
                            widgets[setting_key].addItems(setting_info['items'] + list(reversed(freq_range)))
                        else:
                            widgets[setting_key].addItems(setting_info['items'] + freq_range)
                    else:
                        widgets[setting_key].addItems(setting_info['items'])
                    
                    freq_accessible = CPUManager.get_available_setting(f"/sys/devices/system/cpu/cpu0/cpufreq/scaling_{'max' if setting_key == 'max_freq' else 'min'}_freq")
                    if not freq_accessible or not freq_info_accessible:
                        widgets[setting_key].setEnabled(False)
                        if not freq_info_accessible:
                            widgets[setting_key].setToolTip("CPU frequency info files not available - Frequency selection disabled")
                        else:
                            widgets[setting_key].setToolTip(f"CPU {'max' if setting_key == 'max_freq' else 'min'} frequency file its not available - Frequency selection disabled")
                
                elif setting_key == 'sched':
                    available_schedulers = CPUManager.get_available_schedulers()
                    scx_schedulers_found = len([s for s in available_schedulers if s.startswith("scx_")]) > 0
                    
                    if scx_schedulers_found:
                        widgets[setting_key].addItems(available_schedulers)
                        widgets['available_schedulers'] = available_schedulers
                    else:
                        base_items = CPUManager.CPU_SETTINGS_CATEGORIES["Scheduler"]['sched']['items']
                        widgets[setting_key].addItems(base_items)
                        widgets[setting_key].setEnabled(False)
                        widgets[setting_key].setToolTip("SCX schedulers not found - CPU scheduler selection disabled")
                        widgets['available_schedulers'] = base_items
                
                widgets[setting_key].setCurrentText(setting_info['items'][0])
                widgets[setting_key].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                
                layout.addWidget(label)
                layout.addWidget(widgets[setting_key])
                scroll_layout.addLayout(layout)
                
                current_value_label = QLabel("Updating...")
                current_value_label.setContentsMargins(0, 0, 0, 10)
                scroll_layout.addWidget(current_value_label)
                widgets[f'current_{setting_key}_value'] = current_value_label
        
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
        Create and add the CPU apply button to the layout.
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
        Refresh the current CPU values displayed in the interface.
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

        if 'max_freq' in widgets:
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

        if 'min_freq' in widgets:
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
        
        if 'sched' in widgets:
            widgets['current_sched_value'].setText("Updating...")
            try:
                running_scheduler = CPUManager.get_current_scheduler()
                
                if running_scheduler != "none" and "<defunc>" in running_scheduler:
                    running_scheduler = "none"
                
                if widgets['sched'].isEnabled():
                    current_available = CPUManager.get_available_schedulers()
                    
                    if running_scheduler not in widgets['available_schedulers'] and running_scheduler != "none":
                        widgets['available_schedulers'].append(running_scheduler)
                        current_selection = widgets['sched'].currentText()
                        widgets['sched'].clear()
                        widgets['sched'].addItems(widgets['available_schedulers'])
                        widgets['sched'].setCurrentText(current_selection)
                
                if running_scheduler is not None:
                    widgets['current_sched_value'].setText(f"current: {running_scheduler}")
                else:
                    widgets['current_sched_value'].setText("current: Error reading")
                
            except Exception:
                widgets['current_sched_value'].setText("current: Error")