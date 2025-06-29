import glob
import re
import subprocess
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QScrollArea, QFrame, QSizePolicy, QSystemTrayIcon)
from PySide6.QtCore import (Qt, QProcess, QPropertyAnimation, QEasingCurve, QSize)

class DiskManager:
    """
    Main Disk management class that handles disk I/O schedulers.
    """
    
    DISK_SCHEDULER_PATH_PATTERN = "/sys/block/*/queue/scheduler"
    DEFAULT_SCHEDULER = "mq-deadline"
    BASE_OPTIONS = ["unset"]

    @staticmethod
    def get_disk_scheduler_info():
        """
        Gets information about all disk schedulers with improved format handling.
        """
        disk_info = {}
        
        try:
            scheduler_files = glob.glob(DiskManager.DISK_SCHEDULER_PATH_PATTERN)
            
            for file_path in scheduler_files:
                disk_name = file_path.split('/')[-3]
                
                try:
                    with open(file_path, 'r') as f:
                        content = f.read().strip()
                    
                    scheduler_info = DiskManager._parse_scheduler_content(content)
                    
                    if scheduler_info:
                        scheduler_info['path'] = file_path
                        disk_info[disk_name] = scheduler_info
                    
                except Exception as e:
                    print(f"Warning: Failed to read scheduler info for {disk_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Warning: Failed to get disk scheduler info: {e}")
        
        return disk_info

    @staticmethod
    def _parse_scheduler_content(content):
        """
        Parse scheduler content with improved error handling for various formats.
        """
        if not content or not content.strip():
            print("Warning: Empty scheduler content")
            return None
        
        try:
            tokens = content.split()
            if not tokens:
                print("Warning: No scheduler tokens found")
                return None
            
            available = DiskManager.BASE_OPTIONS.copy()
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
                print(f"Warning: No current scheduler found in brackets for content: '{content}'")
                
                if len(available) > 1:
                    current = available[1]
                    print(f"Warning: Using '{current}' as fallback current scheduler")
                else:
                    current = DiskManager.DEFAULT_SCHEDULER
                    if current not in available:
                        available.append(current)
                    print(f"Warning: Using default scheduler '{current}' as fallback")
            
            if current not in available:
                available.append(current)
            
            seen = set()
            unique_available = []
            for scheduler in available:
                if scheduler not in seen:
                    seen.add(scheduler)
                    unique_available.append(scheduler)
            
            return {'current': current, 'available': unique_available}
            
        except Exception as e:
            print(f"Error parsing scheduler content '{content}': {e}")
            fallback_available = DiskManager.BASE_OPTIONS + [DiskManager.DEFAULT_SCHEDULER]
            return {'current': DiskManager.DEFAULT_SCHEDULER, 'available': fallback_available}

    @staticmethod
    def create_disk_tab():
        """
        Creates and returns the disk management tab widget.
        """
        disk_tab = QWidget()
        main_layout = QVBoxLayout(disk_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 0)
        
        widgets = {}
        widgets['disk_combos'] = {}
        widgets['disk_labels'] = {}
        
        disk_info = DiskManager.get_disk_scheduler_info()
        
        sorted_disk_names = sorted(disk_info.keys())
        
        for disk_name in sorted_disk_names:
            scheduler_info = disk_info[disk_name]
            
            disk_layout = QHBoxLayout()
            
            disk_label = QLabel(f"{disk_name} scheduler:")
            disk_label.setWordWrap(True)
            disk_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            
            disk_combo = QComboBox()
            available_schedulers = scheduler_info['available']
            if 'unset' in available_schedulers:
                sorted_schedulers = ['unset'] + sorted([s for s in available_schedulers if s != 'unset'])
            else:
                sorted_schedulers = sorted(available_schedulers)
            
            disk_combo.addItems(sorted_schedulers)
            disk_combo.setCurrentText("unset")
            disk_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            
            disk_layout.addWidget(disk_label)
            disk_layout.addWidget(disk_combo)
            scroll_layout.addLayout(disk_layout)
            
            current_scheduler = scheduler_info['current']
            current_display = f"current: {current_scheduler}"
            current_label = QLabel(current_display)
            current_label.setContentsMargins(0, 0, 0, 10)
            scroll_layout.addWidget(current_label)
            
            widgets['disk_combos'][disk_name] = disk_combo
            widgets['disk_labels'][disk_name] = current_label

        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        DiskManager.create_disk_apply_button(main_layout, widgets)
        
        main_layout.addSpacing(9)
        
        widgets['disk_settings_applied'] = False
        widgets['is_process_running'] = False
        widgets['process'] = None
        
        return disk_tab, widgets

    @staticmethod
    def create_disk_apply_button(parent_layout, widgets):
        """
        Creates and adds the disk apply button to the layout.
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 0)

        widgets['disk_apply_button'] = QPushButton("Apply")
        widgets['disk_apply_button'].setMinimumSize(100, 30)
        widgets['disk_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets['disk_apply_button'])
        button_layout.addStretch(1)
        
        parent_layout.addWidget(button_container)

    @staticmethod
    def refresh_disk_values(widgets):
        """
        Updates the UI with current disk scheduler information.
        """
        disk_info = DiskManager.get_disk_scheduler_info()
        
        for disk_name, scheduler_info in disk_info.items():
            if disk_name in widgets['disk_labels'] and disk_name in widgets['disk_combos']:
                label = widgets['disk_labels'][disk_name]
                current_scheduler = scheduler_info['current']
                
                label.setText(f"current: {current_scheduler}")