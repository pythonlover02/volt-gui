import re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QLineEdit
from PySide6.QtCore import Qt


class KernelManager:
    """
    Main class for managing kernel settings.
    """
    
    KERNEL_SETTINGS = {
        'compaction_proactiveness': {
            'path': '/proc/sys/vm/compaction_proactiveness',
            'text': 'Controls memory compaction proactiveness. Lower values reduce CPU overhead.\nRecommended values: 0',
            'is_dynamic': False
        },
        'watermark_boost_factor': {
            'path': '/proc/sys/vm/watermark_boost_factor',
            'text': 'Controls memory reclaim aggressiveness. Lower values prevent excessive reclaim.\nRecommended values: 1',
            'is_dynamic': False
        },
        'min_free_kbytes': {
            'path': '/proc/sys/vm/min_free_kbytes',
            'text': 'Minimum free memory to maintain. Do not set below 1024 KB or above 5% of system memory.\nRecommended values: 1024-...',
            'is_dynamic': False
        },
        'max_map_count': {
            'path': '/proc/sys/vm/max_map_count',
            'text': 'Maximum number of memory map areas a process can have. For performance and compatibility.\nRecommended values: 1048576',
            'is_dynamic': False
        },
        'swappiness': {
            'path': '/proc/sys/vm/swappiness',
            'text': 'Controls how aggressively the kernel swaps memory pages. Lower values prefer RAM over swap.\nRecommended values: 10',
            'is_dynamic': False
        },
        'dirty_ratio': {
            'path': '/proc/sys/vm/dirty_ratio',
            'text': 'Percentage of system memory that can be filled with dirty pages before processes are forced to write.\nRecommended values: 15-20',
            'is_dynamic': False
        },
        'dirty_background_ratio': {
            'path': '/proc/sys/vm/dirty_background_ratio',
            'text': 'Percentage of system memory at which background writeback starts.\nRecommended values: 5-10',
            'is_dynamic': False
        },
        'dirty_expire_centisecs': {
            'path': '/proc/sys/vm/dirty_expire_centisecs',
            'text': 'How long dirty data can remain in memory before being written (in centiseconds).\nRecommended values: 1500-3000',
            'is_dynamic': False
        },
        'dirty_writeback_centisecs': {
            'path': '/proc/sys/vm/dirty_writeback_centisecs',
            'text': 'Interval between periodic writeback wakeups (in centiseconds).\nRecommended values: 500-1500',
            'is_dynamic': False
        },
        'vfs_cache_pressure': {
            'path': '/proc/sys/vm/vfs_cache_pressure',
            'text': 'Controls tendency of kernel to reclaim directory and inode cache memory. Lower values keep caches longer.\nRecommended values: 50-80',
            'is_dynamic': False
        },
        'thp_enabled': {
            'path': '/sys/kernel/mm/transparent_hugepage/enabled',
            'text': 'Controls transparent huge pages. Can improve performance but may increase memory usage.',
            'is_dynamic': True
        },
        'thp_shmem_enabled': {
            'path': '/sys/kernel/mm/transparent_hugepage/shmem_enabled',
            'text': 'Controls transparent huge pages for shared memory. May improve performance for memory-intensive applications.',
            'is_dynamic': True
        },
        'thp_defrag': {
            'path': '/sys/kernel/mm/transparent_hugepage/defrag',
            'text': 'Controls when kernel attempts to make huge pages available through memory compaction.',
            'is_dynamic': True
        },
        'zone_reclaim_mode': {
            'path': '/proc/sys/vm/zone_reclaim_mode',
            'text': 'Controls zone reclaim behavior in NUMA systems. Disabling improves performance on most systems.\nRecommended values: 0',
            'is_dynamic': False
        },
        'page_lock_unfairness': {
            'path': '/proc/sys/vm/page_lock_unfairness',
            'text': 'Controls page lock unfairness to prevent lock starvation.\nRecommended values: 1',
            'is_dynamic': False
        },
        'sched_cfs_bandwidth_slice_us': {
            'path': '/proc/sys/kernel/sched_cfs_bandwidth_slice_us',
            'text': 'CFS bandwidth slice duration in microseconds. Affects scheduler responsiveness.\nRecommended values: 3000',
            'is_dynamic': False
        },
        'sched_autogroup_enabled': {
            'path': '/proc/sys/kernel/sched_autogroup_enabled',
            'text': 'Enables automatic process grouping for better desktop responsiveness.\nRecommended values: 1',
            'is_dynamic': False
        },
        'watchdog': {
            'path': '/proc/sys/kernel/watchdog',
            'text': 'Enables soft lockup detector. \nRecommended values: 0',
            'is_dynamic': False
        },
        'nmi_watchdog': {
            'path': '/proc/sys/kernel/nmi_watchdog',
            'text': 'Enables NMI watchdog for hard lockup detection. \nRecommended values: 0',
            'is_dynamic': False
        },
        'laptop_mode': {
            'path': '/proc/sys/vm/laptop_mode',
            'text': 'Enables laptop power-saving mode for disk I/O. \nRecommended values: 0',
            'is_dynamic': False
        }
    }

    @staticmethod
    def get_current_value(setting_path):
        """
        Get current value of a kernel setting.
        """
        try:
            with open(setting_path, 'r') as f:
                return f.read().strip()
        except Exception as e:
            return None

    @staticmethod
    def get_dynamic_current_value(setting_path):
        """
        Get current value of a dynamic setting (extracts value in brackets).
        """
        try:
            with open(setting_path, 'r') as f:
                content = f.read().strip()
            
            match = re.search(r'\[([^\]]+)\]', content)
            if match:
                return match.group(1)
            else:
                values = content.split()
                if values:
                    return values[0]
                else:
                    return None
        except Exception as e:
            return None

    @staticmethod
    def get_dynamic_possible_values(setting_path):
        """
        Get all possible values for a dynamic setting.
        Returns a list of possible values extracted from the system file.
        """
        try:
            with open(setting_path, 'r') as f:
                content = f.read().strip()
            
            clean_content = re.sub(r'[\[\]]', '', content)
            possible_values = clean_content.split()
            
            if possible_values:
                return possible_values
            else:
                return None
        except Exception as e:
            return None

    @staticmethod
    def get_dynamic_text_with_values(base_text, setting_path):
        """
        Generate dynamic text that includes the possible values from the system.
        """
        possible_values = KernelManager.get_dynamic_possible_values(setting_path)
        if possible_values:
            values_text = " ".join(possible_values)
            return f"{base_text}\nPossible values: {values_text}"
        else:
            return f"{base_text}\nPossible values: Unable to read from system"

    @staticmethod
    def get_available_setting(setting_path):
        """
        Check if a kernel setting file is available.
        """
        try:
            with open(setting_path, 'r') as f:
                f.read()
            return True
        except Exception:
            return False

    @staticmethod
    def create_kernel_tab(main_window):
        """
        Create and return the kernel settings tab widget.
        """
        kernel_tab = QWidget()
        kernel_layout = QVBoxLayout(kernel_tab)
        kernel_layout.setContentsMargins(9, 0, 9, 0)
        widgets = {}
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 0)
        
        for setting_name, setting_info in KernelManager.KERNEL_SETTINGS.items():
            KernelManager.create_setting_section(scroll_layout, widgets, setting_name, setting_info)
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        kernel_layout.addWidget(scroll_area)
        
        KernelManager.create_kernel_apply_button(kernel_layout, widgets, main_window)

        widgets['kernel_settings_applied'] = False
        widgets['is_process_running'] = False
        widgets['process'] = None
        
        return kernel_tab, widgets

    @staticmethod
    def create_setting_section(kernel_layout, widgets, setting_name, setting_info):
        """
        Create a UI section for a single kernel setting.
        """
        setting_container = QWidget()
        setting_container.setProperty("settingContainer", True)
        setting_layout = QVBoxLayout(setting_container)
        setting_layout.setContentsMargins(0, 10, 0, 0)
        
        path_label = QLabel(f"{setting_info['path']}:")
        path_label.setWordWrap(True)
        setting_layout.addWidget(path_label)
        
        current_value_label = QLabel("Updating...")
        setting_layout.addWidget(current_value_label)
        is_accessible = KernelManager.get_available_setting(setting_info['path'])
        
        if setting_info['is_dynamic']:
            if is_accessible:
                display_text = KernelManager.get_dynamic_text_with_values(setting_info['text'], setting_info['path'])
            else:
                display_text = f"{setting_info['text']}\nPossible values: not available"
        else:
            display_text = setting_info['text']

        text_label = QLabel(display_text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 5px;")
        setting_layout.addWidget(text_label)
        
        input_widget = QLineEdit()
        input_widget.setPlaceholderText("enter value")
        setting_layout.addWidget(input_widget)
        
        if not is_accessible:
            input_widget.setEnabled(False)
            input_widget.setToolTip(f"Setting file its not available - {setting_name} disabled")
        
        widgets[f'{setting_name}_input'] = input_widget
        widgets[f'{setting_name}_current_value'] = current_value_label
        widgets[f'{setting_name}_text_label'] = text_label
        kernel_layout.addWidget(setting_container)

    @staticmethod
    def create_kernel_apply_button(kernel_layout, widgets, main_window):
        """
        Create the apply button UI element and connect its signal.
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(11, 10, 11, 0)
        
        widgets['kernel_apply_button'] = QPushButton("Apply")
        widgets['kernel_apply_button'].setMinimumSize(100, 30)
        widgets['kernel_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        button_layout.addStretch(1)
        button_layout.addWidget(widgets['kernel_apply_button'])
        button_layout.addStretch(1)
        
        kernel_layout.addWidget(button_container)
        kernel_layout.addSpacing(9)

    @staticmethod
    def refresh_kernel_values(widgets):
        """
        Refresh all kernel setting values in the UI.
        Also updates dynamic text labels with current possible values.
        """
        for name, info in KernelManager.KERNEL_SETTINGS.items():
            if not KernelManager.get_available_setting(info['path']):
                widgets[f'{name}_current_value'].setText("current value: not available")
                continue
                
            if info['is_dynamic']:
                current = KernelManager.get_dynamic_current_value(info['path'])
            else:
                current = KernelManager.get_current_value(info['path'])
            
            if current is not None:
                widgets[f'{name}_current_value'].setText(f"current value: {current}")
            else:
                widgets[f'{name}_current_value'].setText("current value: Error reading")
            
            if info['is_dynamic'] and f'{name}_text_label' in widgets:
                updated_text = KernelManager.get_dynamic_text_with_values(info['text'], info['path'])
                widgets[f'{name}_text_label'].setText(updated_text)