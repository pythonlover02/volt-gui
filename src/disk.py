import glob, re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt

class DiskManager:

    DISK_SCHEDULER_PATH_PATTERN = "/sys/block/*/queue/scheduler"

    DISK_SETTINGS_CATEGORIES = {
        "Scheduler": {
            'sched': {
                'label': "Scheduler:",
                'items': ["unset"]
            }
        }
    }

    DISK_SETTINGS = {}
    for category in DISK_SETTINGS_CATEGORIES.values():
        DISK_SETTINGS.update(category)

    @staticmethod
    def get_schedulers():
        """
        Get scheduler information for all available disks.
        """
        disk_info = {}
        try:
            scheduler_files = glob.glob(DiskManager.DISK_SCHEDULER_PATH_PATTERN)
            for file_path in scheduler_files:
                disk_name = file_path.split('/')[-3]
                try:
                    with open(file_path, 'r') as f:
                        content = f.read().strip()
                        scheduler_info = DiskManager.parse_scheduler_content(content)
                        if scheduler_info:
                            scheduler_info['path'] = file_path
                            disk_info[disk_name] = scheduler_info
                except Exception:
                    continue
        except Exception:
            pass
        return disk_info

    @staticmethod
    def parse_scheduler_content(content):
        """
        Parse scheduler content to extract available and current schedulers.
        """
        if not content or not content.strip():
            return None

        try:
            tokens = content.split()
            if not tokens:
                return None

            available = DiskManager.DISK_SETTINGS_CATEGORIES["Scheduler"]['sched']['items'].copy()
            current = None
            bracket_pattern = re.compile(r'\[([^\]]+)\]')

            for token in tokens:
                bracket_match = bracket_pattern.search(token)
                if bracket_match:
                    current = bracket_match.group(1)
                    if current not in available:
                        available.append(current)
                else:
                    if token not in available:
                        available.append(token)

            if current is None:
                return None

            if current not in available:
                available.append(current)

            seen = set()
            unique_available = []
            for scheduler in available:
                if scheduler not in seen:
                    seen.add(scheduler)
                    unique_available.append(scheduler)

            return {'current': current, 'available': unique_available}

        except Exception:
            return None

    @staticmethod
    def create_disk_tab():
        """
        Create the disk management tab with all its widgets.
        """
        disk_tab = QWidget()
        main_layout = QVBoxLayout(disk_tab)
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
        widgets['disk_settings'] = {}

        disk_info = DiskManager.get_schedulers()
        sorted_disk_names = sorted(disk_info.keys())

        for disk_name in sorted_disk_names:
            scheduler_info = disk_info[disk_name]

            disk_widgets = {}

            for setting_key, setting_info in DiskManager.DISK_SETTINGS_CATEGORIES["Scheduler"].items():
                layout = QHBoxLayout()
                label = QLabel(f"{disk_name} {setting_info['label']}")
                label.setWordWrap(True)
                label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

                disk_widgets[setting_key] = QComboBox()

                available_schedulers = scheduler_info['available']
                if setting_info['items'][0] in available_schedulers:
                    sorted_schedulers = [setting_info['items'][0]] + sorted([s for s in available_schedulers if s != setting_info['items'][0]])
                else:
                    sorted_schedulers = sorted(available_schedulers)

                disk_widgets[setting_key].addItems(sorted_schedulers)
                disk_widgets[setting_key].setCurrentText(setting_info['items'][0])
                disk_widgets[setting_key].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                layout.addWidget(label)
                layout.addWidget(disk_widgets[setting_key])
                scroll_layout.addLayout(layout)

                current_scheduler = scheduler_info['current']
                current_value_label = QLabel(f"current: {current_scheduler}")
                current_value_label.setContentsMargins(0, 0, 0, 10)
                scroll_layout.addWidget(current_value_label)
                disk_widgets[f'current_{setting_key}_value'] = current_value_label

            widgets['disk_settings'][disk_name] = disk_widgets

        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        DiskManager.create_disk_apply_button(main_layout, widgets)

        widgets['disk_settings_applied'] = False
        widgets['is_process_running'] = False
        widgets['process'] = None

        return disk_tab, widgets

    @staticmethod
    def create_disk_apply_button(parent_layout, widgets):
        """
        Create and add the disk apply button to the layout.
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(11, 10, 11, 0)

        widgets['disk_apply_button'] = QPushButton("Apply")
        widgets['disk_apply_button'].setMinimumSize(100, 30)
        widgets['disk_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets['disk_apply_button'])
        button_layout.addStretch(1)

        parent_layout.addWidget(button_container)
        parent_layout.addSpacing(9)

    @staticmethod
    def refresh_disk_values(widgets):
        """
        Refresh the current disk scheduler values displayed in the interface.
        """
        disk_info = DiskManager.get_schedulers()

        for disk_name, scheduler_info in disk_info.items():
            if disk_name in widgets['disk_settings']:
                disk_widgets = widgets['disk_settings'][disk_name]
                current_scheduler = scheduler_info['current']
                disk_widgets['current_sched_value'].setText(f"current: {current_scheduler}")
