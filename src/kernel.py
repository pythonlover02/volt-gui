import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QSizePolicy, QLineEdit, QFrame
)
from PySide6.QtCore import Qt, QProcess

class KernelManager:
    KERNEL_SETTINGS = {
        'compaction_proactiveness': {'path': '/proc/sys/vm/compaction_proactiveness', 'recommended': '0'},
        'watermark_boost_factor': {'path': '/proc/sys/vm/watermark_boost_factor', 'recommended': '1'},
        'min_free_kbytes': {'path': '/proc/sys/vm/min_free_kbytes', 'recommended': 'do not set this below 1024 KB or above 5% of your systems memory'},
        'swappiness': {'path': '/proc/sys/vm/swappiness', 'recommended': '10'},
        'zone_reclaim_mode': {'path': '/proc/sys/vm/zone_reclaim_mode', 'recommended': '0'},
        'page_lock_unfairness': {'path': '/proc/sys/vm/page_lock_unfairness', 'recommended': '1'}
    }

    @staticmethod
    def create_kernel_tab():
        kernel_tab = QWidget()
        kernel_layout = QVBoxLayout(kernel_tab)
        widgets = {}
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 10)
        
        for setting_name, setting_info in KernelManager.KERNEL_SETTINGS.items():
            KernelManager._create_setting_section(scroll_layout, widgets, setting_name, setting_info)
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        kernel_layout.addWidget(scroll_area)
        
        KernelManager._create_apply_button(kernel_layout, widgets)
        
        return kernel_tab, widgets

    @staticmethod
    def _create_setting_section(kernel_layout, widgets, setting_name, setting_info):
        setting_container = QWidget()
        setting_container.setProperty("settingContainer", True)
        setting_layout = QVBoxLayout(setting_container)
        
        path_label = QLabel(f"{setting_info['path']}:")
        path_label.setWordWrap(True)
        setting_layout.addWidget(path_label)
        
        current_value_label = QLabel("Updating...")
        setting_layout.addWidget(current_value_label)
        
        input_widget = QLineEdit()
        input_widget.setPlaceholderText(f"enter value (recommended: {setting_info['recommended']})")
        setting_layout.addWidget(input_widget)
        
        widgets[f'{setting_name}_input'] = input_widget
        widgets[f'{setting_name}_current_value'] = current_value_label
        kernel_layout.addWidget(setting_container)

    @staticmethod
    def _create_apply_button(kernel_layout, widgets):
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 5)
        
        widgets['kernel_apply_button'] = QPushButton("Apply")
        widgets['kernel_apply_button'].setMinimumSize(100, 30)
        widgets['kernel_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        button_layout.addStretch(1)
        button_layout.addWidget(widgets['kernel_apply_button'])
        button_layout.addStretch(1)
        
        kernel_layout.addWidget(button_container)

    @staticmethod
    def get_current_value(setting_path):
        try:
            with open(setting_path, 'r') as f:
                return f.read().strip()
        except:
            return "Error"

    @staticmethod
    def refresh_values(widgets):
        for name in KernelManager.KERNEL_SETTINGS:
            widgets[f'{name}_current_value'].setText("Updating...")
        
        widgets['kernel_apply_button'].setEnabled(False)
        
        try:
            for name, info in KernelManager.KERNEL_SETTINGS.items():
                current = KernelManager.get_current_value(info['path'])
                widgets[f'{name}_current_value'].setText(f"current: {current}")
        finally:
            widgets['kernel_apply_button'].setEnabled(True)

    @staticmethod
    def apply_kernel_settings(widgets):
        try:
            settings = []
            originals = {}
            
            for name, info in KernelManager.KERNEL_SETTINGS.items():
                value = widgets[f'{name}_input'].text().strip()
                if value:
                    path = info['path']
                    originals[name] = KernelManager.get_current_value(path)
                    settings.append(f"{path}:{value}")
            
            if settings:
                process = QProcess()
                process.start("pkexec", ["volt-kernel"] + settings)
                process.waitForFinished()
                
                if process.exitCode() == 0:
                    widgets['original_values'] = originals
                    KernelManager.refresh_values(widgets)

        except Exception as e:
            print(f"Apply error: {str(e)}")

    @staticmethod
    def restore_kernel_settings(widgets):
        if 'original_values' not in widgets:
            return
            
        try:
            originals = widgets['original_values']
            restore = [f"{KernelManager.KERNEL_SETTINGS[name]['path']}:{val}" 
                      for name, val in originals.items()]
            
            process = QProcess()
            process.start("pkexec", ["volt-kernel"] + restore)
            process.waitForFinished()
            
            if process.exitCode() == 0:
                del widgets['original_values']
                KernelManager.refresh_values(widgets)

        except Exception as e:
            print(f"Restore error: {str(e)}")