from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

class ThemeManager:
    AMD_COLORS = {
        'bg_color': "#141414",
        'darker_bg': "#0A0A0A",
        'lighter_bg': "#1E1E1E",
        'text_color': "#E0E0E0",
        'accent_color': "#ED1C24",
        'accent_hover': "#FF4D54",
        'accent_pressed': "#C41319",
        'border_color': "#333333",
        'disabled_bg': "#1A1A1A",
        'disabled_text': "#777777",
    }
    
    INTEL_COLORS = {
        'bg_color': "#141414",
        'darker_bg': "#0A0A0A",
        'lighter_bg': "#1E1E1E",
        'text_color': "#E0E0E0",
        'accent_color': "#0071C5",
        'accent_hover': "#0091FF",
        'accent_pressed': "#005694",
        'border_color': "#333333",
        'disabled_bg': "#1A1A1A",
        'disabled_text': "#777777",
    }
    
    NVIDIA_COLORS = {
        'bg_color': "#141414",
        'darker_bg': "#0A0A0A",
        'lighter_bg': "#1E1E1E",
        'text_color': "#E0E0E0",
        'accent_color': "#76B900",
        'accent_hover': "#8BD41F",
        'accent_pressed': "#5C8F00",
        'border_color': "#333333",
        'disabled_bg': "#1A1A1A",
        'disabled_text': "#777777",
    }
    
    COLORS = AMD_COLORS
    CURRENT_THEME = "amd"

    @classmethod
    def set_theme(cls, theme_name):
        if theme_name == "intel":
            cls.COLORS = cls.INTEL_COLORS
            cls.CURRENT_THEME = "intel"
        elif theme_name == "nvidia":
            cls.COLORS = cls.NVIDIA_COLORS
            cls.CURRENT_THEME = "nvidia"
        else:
            cls.COLORS = cls.AMD_COLORS
            cls.CURRENT_THEME = "amd"
            
    @classmethod
    def get_theme_style_sheet(cls):
        return f"""
        QWidget {{
            background-color: {cls.COLORS['bg_color']};
            color: {cls.COLORS['text_color']};
            font-size: 10pt;
            font-family: "Segoe UI", sans-serif;
        }}
        
        QLabel {{
            color: {cls.COLORS['text_color']};
            background-color: transparent;
            qproperty-wordWrap: true;
        }}
        
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}
        
        QWidget[scrollContainer="true"] {{
            background-color: transparent;
        }}
        
        QWidget[buttonContainer="true"] {{
            background-color: transparent;
            min-height: 50px;
        }}
        
        QMainWindow {{
            background-color: {cls.COLORS['bg_color']};
            border: none;
        }}
        
        QTabWidget::pane {{
            border: none;
            background-color: {cls.COLORS['bg_color']};
        }}
        
        QTabWidget {{
            background-color: {cls.COLORS['bg_color']};
        }}
        
        QTabBar {{
            background-color: {cls.COLORS['bg_color']};
            qproperty-drawBase: 0;
        }}
        
        QTabBar::tab {{
            background-color: {cls.COLORS['bg_color']};
            color: {cls.COLORS['text_color']};
            border: none;
            padding: 10px 20px;
            margin-right: 2px;
            font-weight: bold;
        }}
        
        QTabBar::tab:selected {{
            background-color: {cls.COLORS['bg_color']};
            border-bottom: 3px solid {cls.COLORS['accent_color']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {cls.COLORS['bg_color']};
        }}
        
        QScrollBar:vertical {{
            background: {cls.COLORS['bg_color']};
            width: 8px;
            margin: 0px;
            border-radius: 0px;
        }}

        QScrollBar::handle:vertical {{
            background: {cls.COLORS['border_color']};
            min-height: 20px;
            border-radius: 0px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {cls.COLORS['accent_color']};            
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
            height: 0px;
        }}

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        
        QScrollBar:horizontal {{
            background: {cls.COLORS['bg_color']};
            height: 8px;
            margin: 0px;
            border-radius: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background: {cls.COLORS['border_color']};
            min-width: 40px;
            border-radius: 0px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {cls.COLORS['accent_color']};            
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            background: none;
            width: 0px;
        }}

        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        
        QPushButton {{
            background-color: {cls.COLORS['bg_color']};
            color: {cls.COLORS['text_color']};
            border: 1px solid {cls.COLORS['border_color']};
            padding: 6px 12px;
            min-width: 80px;
            border-radius: 0px;
        }}
        
        QPushButton:default {{
            border: 2px solid {cls.COLORS['accent_color']};
        }}
        
        QPushButton:hover {{
            background-color: {cls.COLORS['lighter_bg']};
            border-color: {cls.COLORS['accent_color']};
            color: {cls.COLORS['accent_color']};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.COLORS['accent_pressed']};
            border-color: {cls.COLORS['accent_hover']};
            color: {cls.COLORS['accent_hover']};
        }}
        
        QComboBox {{
            background-color: {cls.COLORS['bg_color']};
            color: {cls.COLORS['text_color']};
            border: 1px solid {cls.COLORS['border_color']};
            border-radius: 0px;
            padding: 8px;
            min-width: 6em;
            selection-background-color: {cls.COLORS['accent_color']};
        }}
        
        QComboBox:hover {{
            border: 1px solid {cls.COLORS['accent_color']};
        }}
        
        QComboBox:disabled {{
            background-color: {cls.COLORS['disabled_bg']};
            color: {cls.COLORS['disabled_text']};
            border-color: {cls.COLORS['border_color']};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 1px solid {cls.COLORS['border_color']};
            background-color: transparent;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {cls.COLORS['bg_color']};
            color: {cls.COLORS['text_color']};
            border: 1px solid {cls.COLORS['accent_color']};
            selection-background-color: {cls.COLORS['accent_color']};
            selection-color: white;
            border-radius: 0px;
        }}
        
        QSpinBox, QDoubleSpinBox {{
            background-color: {cls.COLORS['bg_color']};
            color: {cls.COLORS['text_color']};
            border: 1px solid {cls.COLORS['border_color']};
            border-radius: 0px;
            padding: 8px;
        }}
        
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border: 1px solid {cls.COLORS['accent_color']};
        }}
        
        QSpinBox:disabled, QDoubleSpinBox:disabled {{
            background-color: {cls.COLORS['disabled_bg']};
            color: {cls.COLORS['disabled_text']};
            border-color: {cls.COLORS['border_color']};
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: {cls.COLORS['lighter_bg']};
            width: 20px;
            border: none;
            border-radius: 0px;
        }}
        
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {cls.COLORS['accent_color']};
        }}
        
        QLabel[isHeader="true"] {{
            font-weight: bold;
            color: {cls.COLORS['accent_color']};
            font-size: 12pt;
            padding-top: 10px;
            padding-bottom: 5px;
        }}
        
        QCheckBox {{
            color: {cls.COLORS['text_color']};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {cls.COLORS['border_color']};
            background-color: {cls.COLORS['bg_color']};
        }}
        
        QCheckBox::indicator:unchecked:hover {{
            border: 1px solid {cls.COLORS['accent_color']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {cls.COLORS['accent_color']};
            border: 1px solid {cls.COLORS['accent_color']};
        }}

        QLineEdit {{
            background-color: {cls.COLORS['bg_color']};
            color: {cls.COLORS['text_color']};
            border: 1px solid {cls.COLORS['border_color']};
            border-radius: 0px;
            padding: 8px;
            selection-background-color: {cls.COLORS['accent_color']};
            selection-color: white;
        }}
        
        QLineEdit:hover {{
            border: 1px solid {cls.COLORS['accent_color']};
        }}
        
        QLineEdit:disabled {{
            background-color: {cls.COLORS['disabled_bg']};
            color: {cls.COLORS['disabled_text']};
            border-color: {cls.COLORS['border_color']};
        }}

        QWidget[statusContainer="true"] {{
            background-color: {cls.COLORS['bg_color']};
            color: {cls.COLORS['text_color']};
            border: 1px solid {cls.COLORS['border_color']};
            border-radius: 0px;
        }}
        
        QWidget[statusContainer="true"] QLabel {{
            background-color: transparent;
            color: {cls.COLORS['text_color']};
            padding: 2px;
        }}
        """

    @classmethod
    def get_theme_palette(cls):
        palette = QPalette()
        
        palette.setColor(QPalette.Window, QColor(cls.COLORS['bg_color']))
        palette.setColor(QPalette.WindowText, QColor(cls.COLORS['text_color']))
        palette.setColor(QPalette.Base, QColor(cls.COLORS['bg_color']))
        palette.setColor(QPalette.AlternateBase, QColor(cls.COLORS['lighter_bg']))
        palette.setColor(QPalette.ToolTipBase, QColor(cls.COLORS['bg_color']))
        palette.setColor(QPalette.ToolTipText, QColor(cls.COLORS['text_color']))
        palette.setColor(QPalette.Text, QColor(cls.COLORS['text_color']))
        palette.setColor(QPalette.Button, QColor(cls.COLORS['bg_color']))
        palette.setColor(QPalette.ButtonText, QColor(cls.COLORS['text_color']))
        palette.setColor(QPalette.Link, QColor(cls.COLORS['accent_color']))
        palette.setColor(QPalette.Highlight, QColor(cls.COLORS['accent_color']))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(cls.COLORS['disabled_text']))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(cls.COLORS['disabled_text']))
        palette.setColor(QPalette.Disabled, QPalette.Window, QColor(cls.COLORS['disabled_bg']))
        palette.setColor(QPalette.Disabled, QPalette.Base, QColor(cls.COLORS['disabled_bg']))
        
        return palette

    @classmethod
    def apply_theme(cls, app, theme_name=None):
        if theme_name:
            cls.set_theme(theme_name)
            
        if app:
            app.setStyleSheet(cls.get_theme_style_sheet())
            app.setPalette(cls.get_theme_palette())
