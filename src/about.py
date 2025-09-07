from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PySide6.QtCore import Qt

class AboutManager:
    
    @staticmethod
    def get_about_info():
        """
        Returns a list of dictionaries containing the about information.
        """
        return [
            {"label": "Description", "text": "Simple GUI program for modifying and creating the `volt` script and more. Providing an intuitive interface for configuration management, with the objective of getting the maximum performance posible of a PC"},
            {"label": "License", "text": "GPL-3.0 License"},
            {"label": "Author", "text": "pythonlover02"},
            {"label": "Version", "text": "1.2.1"},
        ]
    
    @staticmethod
    def create_about_tab():
        """
        Creates and returns the about tab widget.
        """
        about_tab = QWidget()
        main_layout = QVBoxLayout(about_tab)
        main_layout.setContentsMargins(9, 0, 9, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 0)
        
        for item in AboutManager.get_about_info():
            container = AboutManager.create_info_container(item)
            scroll_layout.addWidget(container)
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        return about_tab, {}
    
    @staticmethod
    def create_info_container(info_item):
        """
        Creates a container widget for an individual info item.
        """
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(5)
        
        label_text = QLabel(info_item["label"])
        label_text.setAlignment(Qt.AlignCenter)
        label_text.setStyleSheet("font-weight: bold; font-size: 16px;")
        container_layout.addWidget(label_text)
        
        text_label = QLabel(info_item["text"])
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #E0E0E0; font-size: 13px; line-height: 1.4;")
        container_layout.addWidget(text_label)
        
        return container