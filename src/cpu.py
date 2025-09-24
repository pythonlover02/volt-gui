import glob, os, re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, QProcess
from workarounds import WorkaroundManager

class CPUManager:

    CPU_SETTINGS_CATEGORIES = {
        "Frequency": {
            'scaling_governor': {
                'label': "Governor:",
                'text': "CPU frequency scaling behavior.",
                'items': ["unset"],
                'path': "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor",
                'available_path': "/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors",
                'is_dynamic': True
            },
            'scaling_max_freq': {
                'label': "Max Frequency (MHz):",
                'text': "Maximum allowed CPU frequency.",
                'items': ["unset"],
                'path': "/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq",
                'min_path': "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq",
                'max_path': "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq",
                'is_dynamic': False,
                'convert_to_mhz': True
            },
            'scaling_min_freq': {
                'label': "Min Frequency (MHz):",
                'text': "Minimum allowed CPU frequency.",
                'items': ["unset"],
                'path': "/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq",
                'min_path': "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq",
                'max_path': "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq",
                'is_dynamic': False,
                'convert_to_mhz': True
            }
        },
        "Scheduler": {
            'scheduler': {
                'label': "Pluggable Scheduler:",
                'text': "Alternative CPU schedulers optimized for specific workloads.",
                'items': ["unset", "none"],
                'search_paths': ["/usr/bin/", "/usr/local/bin/"],
                'is_dynamic': True
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
    def get_current_value(setting_info):
        """
        Get the current value for a CPU setting.
        """
        if 'path' not in setting_info:
            return None

        try:
            with open(setting_info['path'], "r") as f:
                value = f.read().strip()

                if setting_info.get('convert_to_mhz', False):
                    try:
                        value = str(int(value) // 1000)
                    except ValueError:
                        pass

                if setting_info.get('is_dynamic', False):
                    match = re.search(r'\[([^\]]+)\]', value)
                    if match:
                        return match.group(1)
                    else:
                        values = value.split()
                        return values[0] if values else None
                return value
        except Exception:
            return None

    @staticmethod
    def get_available_values(setting_info):
        """
        Get available values for a CPU setting.
        """
        base_items = setting_info.get('items', ["unset"]).copy()

        if setting_info.get('is_dynamic', False):
            if 'available_path' in setting_info:
                try:
                    with open(setting_info['available_path'], "r") as f:
                        available_values = f.read().strip().split()
                        return base_items + [item for item in available_values if item not in base_items]
                except Exception:
                    return base_items
            elif 'search_paths' in setting_info:
                schedulers = base_items.copy()
                for search_path in setting_info['search_paths']:
                    try:
                        scx_files = glob.glob(os.path.join(search_path, "scx_*"))
                        for file_path in scx_files:
                            scheduler_name = os.path.basename(file_path)
                            if os.access(file_path, os.X_OK) and scheduler_name not in schedulers:
                                schedulers.append(scheduler_name)
                    except Exception:
                        continue
                return schedulers
        else:
            try:
                with open(setting_info['min_path'], "r") as f:
                    min_freq = int(f.read().strip()) // 1000
                with open(setting_info['max_path'], "r") as f:
                    max_freq = int(f.read().strip()) // 1000
                freq_values = [str(f) for f in range(min_freq, max_freq + 100, 100)]
                return base_items + freq_values
            except Exception:
                return base_items

        return base_items

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

                is_accessible = True
                if 'path' in setting_info:
                    is_accessible = CPUManager.get_available_setting(setting_info['path'])

                available_values = CPUManager.get_available_values(setting_info)

                if setting_key == 'scaling_max_freq' and not setting_info.get('is_dynamic', False):
                    available_values = list(reversed(available_values))

                widgets[setting_key].addItems(available_values)

                if is_accessible:
                    widgets[setting_key].setToolTip(setting_info['text'])
                else:
                    widgets[setting_key].setEnabled(False)
                    if 'path' in setting_info:
                        widgets[setting_key].setToolTip(f"Setting file not available - {setting_info['label']} selection disabled")
                    else:
                        widgets[setting_key].setToolTip(f"SCX schedulers not available - {setting_info['label']} selection disabled")

                widgets[setting_key].setCurrentText("unset")
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
        for setting_key, setting_info in CPUManager.CPU_SETTINGS.items():
            current_value_label = widgets.get(f'current_{setting_key}_value')
            if not current_value_label:
                continue

            if setting_key == 'scheduler':
                current_value_label.setText("Updating...")
                try:
                    running_scheduler = CPUManager.get_current_scheduler()
                    if running_scheduler != "none" and "<defunc>" in running_scheduler:
                        running_scheduler = "none"

                    if running_scheduler is not None:
                        current_value_label.setText(f"current: {running_scheduler}")
                    else:
                        current_value_label.setText("current: Error reading")
                except Exception:
                    current_value_label.setText("current: Error")
            else:
                is_accessible = CPUManager.get_available_setting(setting_info['path'])
                if not is_accessible:
                    current_value_label.setText("current: unset")
                else:
                    current_value_label.setText("Updating...")
                    try:
                        current_value = CPUManager.get_current_value(setting_info)
                        if current_value is not None:
                            current_value_label.setText(f"current: {current_value}")
                        else:
                            current_value_label.setText("current: Error reading")
                    except Exception:
                        current_value_label.setText("current: Error")
