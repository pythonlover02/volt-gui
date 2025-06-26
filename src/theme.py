from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


class ThemeManager:
    """
    Defines the application themes.
    """
    
    AMD_COLORS = {
        'bg_color': "#1A1A1A",
        'darker_bg': "#0F0F0F",
        'lighter_bg': "#252525",
        'surface_bg': "#202020",
        'text_color': "#FFFFFF",
        'text_secondary': "#B0B0B0",
        'accent_color': "#FF0000",
        'accent_hover': "#FF3333",
        'accent_pressed': "#CC0000",
        'disabled_text': "#666666",
        'selection_bg': "#FF0000",
    }
    
    INTEL_COLORS = {
        'bg_color': "#1A1A1A",
        'darker_bg': "#0F0F0F",
        'lighter_bg': "#252525",
        'surface_bg': "#202020",
        'text_color': "#FFFFFF",
        'text_secondary': "#B0B0B0",
        'accent_color': "#0071C5",
        'accent_hover': "#3399FF",
        'accent_pressed': "#004D87",
        'disabled_text': "#666666",
        'selection_bg': "#0071C5",
    }
    
    NVIDIA_COLORS = {
        'bg_color': "#1A1A1A",
        'darker_bg': "#0F0F0F",
        'lighter_bg': "#252525",
        'surface_bg': "#202020",
        'text_color': "#FFFFFF",
        'text_secondary': "#B0B0B0",
        'accent_color': "#76B900",
        'accent_hover': "#9AE62C",
        'accent_pressed': "#5A8A00",
        'disabled_text': "#666666",
        'selection_bg': "#76B900",
    }
    
    THEMES = {
        "amd": AMD_COLORS,
        "intel": INTEL_COLORS,
        "nvidia": NVIDIA_COLORS
    }
    
    @classmethod
    def set_theme(cls, theme_name):
        """
        Set the current theme colors and name.
        """
        cls.COLORS = cls.THEMES[theme_name]
        cls.CURRENT_THEME = theme_name
    
    @classmethod
    def get_theme_style_sheet(cls):
        """
        Generate the complete stylesheet for the current theme.
        """
        c = cls.COLORS
        return f"""
        QWidget {{
            background-color: {c['bg_color']};
            color: {c['text_color']};
            font-size: 10pt;
            font-family: "Segoe UI", sans-serif;
        }}
        
        QLabel {{
            color: {c['text_color']};
            background-color: transparent;
            border: none;
            qproperty-wordWrap: true;
        }}
        
        QScrollArea {{
            background-color: transparent;
            border: none;
        }}
        
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}
        
        QWidget[scrollContainer="true"], 
        QWidget[buttonContainer="true"] {{
            background-color: transparent;
            border: none;
        }}
        
        QWidget[buttonContainer="true"] {{
            min-height: 50px;
            background-color: {c['bg_color']};
        }}
        
        QMainWindow {{
            background-color: {c['bg_color']};
            border: none;
        }}
        
        QTabWidget {{
            background-color: {c['bg_color']};
            border: none;
        }}
        
        QTabWidget::pane {{
            background-color: {c['bg_color']};
            border: none;
        }}
        
        QTabBar {{
            background-color: {c['bg_color']};
            qproperty-drawBase: 0;
            border: none;
        }}
        
        QTabBar::tab {{
            background-color: {c['bg_color']};
            color: {c['text_secondary']};
            border: none;
            padding: 12px 24px;
            margin: 0px;
            font-weight: 500;
        }}
        
        QTabBar::tab:selected {{
            background-color: {c['bg_color']};
            color: {c['text_color']};
            border-bottom: 3px solid {c['accent_color']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {c['lighter_bg']};
            color: {c['text_color']};
        }}
        
        QScrollBar:vertical {{
            background: transparent;
            width: 12px;
            margin: 0px;
            border: none;
        }}

        QScrollBar::handle:vertical {{
            background: {c['text_secondary']};
            min-height: 30px;
            border: none;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {c['accent_color']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
            height: 0px;
            border: none;
        }}
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        
        QScrollBar:horizontal {{
            background: transparent;
            height: 12px;
            margin: 0px;
            border: none;
        }}

        QScrollBar::handle:horizontal {{
            background: {c['text_secondary']};
            min-width: 30px;
            border: none;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {c['accent_color']};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            background: none;
            width: 0px;
            border: none;
        }}
        
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        
        QPushButton {{
            background-color: {c['surface_bg']};
            color: {c['text_color']};
            border: none;
            outline: none;
            padding: 10px 16px;
            min-width: 80px;
            font-weight: 500;
        }}
        
        QPushButton:default {{
            background-color: {c['accent_color']};
            color: white;
            border: none;
            outline: none;
        }}
        
        QPushButton:hover {{
            background-color: {c['lighter_bg']};
            border: none;
            outline: none;
        }}
        
        QPushButton:default:hover {{
            background-color: {c['accent_hover']};
            border: none;
            outline: none;
        }}
        
        QPushButton:pressed {{
            background-color: {c['accent_pressed']};
            border: none;
            outline: none;
        }}
        
        QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {{
            background-color: {c['surface_bg']};
            color: {c['text_color']};
            border: none;
            padding: 10px 12px;
            selection-background-color: {c['selection_bg']};
            selection-color: white;
        }}
        
        QComboBox {{
            min-width: 100px;
        }}
        
        QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover, QLineEdit:hover {{
            background-color: {c['lighter_bg']};
        }}
        
        QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {{
            background-color: {c['lighter_bg']};
            border-bottom: 2px solid {c['accent_color']};
        }}
        
        QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QLineEdit:disabled {{
            background-color: {c['darker_bg']};
            color: {c['disabled_text']};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border: none;
            background-color: transparent;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {c['surface_bg']};
            color: {c['text_color']};
            border: none;
            selection-background-color: {c['accent_color']};
            selection-color: white;
            outline: none;
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: transparent;
            width: 20px;
            border: none;
        }}
        
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {c['accent_color']};
        }}
        
        QLabel[isHeader="true"] {{
            font-weight: 600;
            color: {c['accent_color']};
            font-size: 13pt;
            padding: 12px 0px 8px 0px;
            background-color: transparent;
            border: none;
        }}
        
        QCheckBox {{
            color: {c['text_color']};
            spacing: 10px;
            border: none;
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            background-color: {c['surface_bg']};
            border: none;
        }}
        
        QCheckBox::indicator:unchecked:hover {{
            background-color: {c['lighter_bg']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {c['accent_color']};
            border: none;
        }}
        
        QCheckBox::indicator:checked:hover {{
            background-color: {c['accent_hover']};
        }}

        QWidget[statusContainer="true"] {{
            background-color: {c['surface_bg']};
            color: {c['text_color']};
            border: none;
            padding: 8px;
        }}
        
        QWidget[statusContainer="true"] QLabel {{
            background-color: transparent;
            color: {c['text_color']};
            padding: 4px;
            border: none;
        }}
        
        QGroupBox {{
            background-color: transparent;
            color: {c['text_color']};
            border: none;
            font-weight: 600;
            font-size: 11pt;
            padding-top: 20px;
        }}

        QGroupBox::title {{
            color: {c['accent_color']};
            subcontrol-origin: margin;
            left: 0px;
            padding: 0px 0px 8px 0px;
        }}

        QFrame#profileFrame {{
            border: 1px solid {c['accent_color']};
            background-color: {c['bg_color']};
        }}
        
        QMenu {{
            background-color: {c['surface_bg']};
            color: {c['text_color']};
            border: none;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 16px;
            border: none;
        }}
        
        QMenu::item:selected {{
            background-color: {c['accent_color']};
            color: white;
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {c['lighter_bg']};
            margin: 4px 0px;
        }}
        
        QProgressBar {{
            background-color: {c['surface_bg']};
            color: {c['text_color']};
            border: none;
            text-align: center;
            padding: 2px;
        }}
        
        QProgressBar::chunk {{
            background-color: {c['accent_color']};
            border: none;
        }}
        """

    @classmethod
    def get_theme_palette(cls):
        """
        Create a QPalette with theme colors for the application.
        """
        palette = QPalette()
        c = cls.COLORS
        
        palette.setColor(QPalette.Window, QColor(c['bg_color']))
        palette.setColor(QPalette.WindowText, QColor(c['text_color']))
        palette.setColor(QPalette.Base, QColor(c['surface_bg']))
        palette.setColor(QPalette.AlternateBase, QColor(c['lighter_bg']))
        palette.setColor(QPalette.Text, QColor(c['text_color']))
        palette.setColor(QPalette.BrightText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Button, QColor(c['surface_bg']))
        palette.setColor(QPalette.ButtonText, QColor(c['text_color']))
        palette.setColor(QPalette.Highlight, QColor(c['accent_color']))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(c['disabled_text']))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(c['disabled_text']))
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(c['disabled_text']))
        palette.setColor(QPalette.Disabled, QPalette.Window, QColor(c['darker_bg']))
        palette.setColor(QPalette.Disabled, QPalette.Base, QColor(c['darker_bg']))
        palette.setColor(QPalette.Disabled, QPalette.Button, QColor(c['darker_bg']))
        
        return palette

    @classmethod
    def apply_theme(cls, app, theme_name):
        """
        Apply the specified theme to the application.
        """
        if theme_name:
            cls.set_theme(theme_name)
            
        if app:
            app.setStyleSheet(cls.get_theme_style_sheet())
            app.setPalette(cls.get_theme_palette())