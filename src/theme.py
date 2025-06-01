from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


class ThemeManager:
    """
    Manages application themes including colors, stylesheets and palettes.    
    Provides class methods to apply themes, get style information, and manage
    theme-related settings across the application.
    """
    
    # AMD brand color scheme
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
    
    # Intel brand color scheme
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
    
    # NVIDIA brand color scheme
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
    
    # Available themes mapping
    THEMES = {
        "amd": AMD_COLORS,
        "intel": INTEL_COLORS,
        "nvidia": NVIDIA_COLORS
    }
    
    # Current theme settings
    COLORS = AMD_COLORS
    CURRENT_THEME = "amd"

    @classmethod
    def set_theme(cls, theme_name):
        """
        Set the current application theme.
        Args:
            theme_name: Name of the theme to set (amd, intel, nvidia)
        """
        theme_name = theme_name.lower()
        if theme_name in cls.THEMES:
            cls.COLORS = cls.THEMES[theme_name]
            cls.CURRENT_THEME = theme_name
        else:
            # Fallback to AMD theme if invalid name provided
            cls.COLORS = cls.AMD_COLORS
            cls.CURRENT_THEME = "amd"
            
    @classmethod
    def get_theme_style_sheet(cls):
        """
        Generate the Qt stylesheet for the current theme.
        Returns:
            str: CSS-like stylesheet string for the current theme
        """
        c = cls.COLORS
        return f"""
        /* Base widget styling */
        QWidget {{
            background-color: {c['bg_color']};
            color: {c['text_color']};
            font-size: 10pt;
            font-family: "Segoe UI", sans-serif;
        }}
        
        /* Label styling */
        QLabel {{
            color: {c['text_color']};
            background-color: transparent;
            qproperty-wordWrap: true;
        }}
        
        /* Scroll area styling */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}
        
        /* Custom widget properties */
        QWidget[scrollContainer="true"], 
        QWidget[buttonContainer="true"] {{
            background-color: transparent;
        }}
        
        QWidget[buttonContainer="true"] {{
            min-height: 50px;
        }}
        
        /* Main window and tab styling */
        QMainWindow, QTabWidget, QTabWidget::pane {{
            background-color: {c['bg_color']};
            border: none;
        }}
        
        QTabBar {{
            background-color: {c['bg_color']};
            qproperty-drawBase: 0;
        }}
        
        QTabBar::tab {{
            background-color: {c['bg_color']};
            color: {c['text_color']};
            border: none;
            padding: 10px 20px;
            margin-right: 2px;
            font-weight: bold;
        }}
        
        QTabBar::tab:selected {{
            background-color: {c['bg_color']};
            border-bottom: 3px solid {c['accent_color']};
        }}
        
        /* Vertical scrollbar styling */
        QScrollBar:vertical {{
            background: {c['bg_color']};
            width: 8px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background: {c['border_color']};
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {c['accent_color']};            
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
            height: 0px;
        }}
        
        /* Horizontal scrollbar styling */
        QScrollBar:horizontal {{
            background: {c['bg_color']};
            height: 8px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background: {c['border_color']};
            min-width: 40px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {c['accent_color']};            
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
            width: 0px;
        }}
        
        /* Button styling */
        QPushButton {{
            background-color: {c['bg_color']};
            color: {c['text_color']};
            border: 1px solid {c['border_color']};
            padding: 6px 12px;
            min-width: 80px;
        }}
        
        QPushButton:default {{
            border: 2px solid {c['accent_color']};
        }}
        
        QPushButton:hover {{
            background-color: {c['lighter_bg']};
            border-color: {c['accent_color']};
            color: {c['accent_color']};
        }}
        
        QPushButton:pressed {{
            background-color: {c['accent_pressed']};
            border-color: {c['accent_hover']};
            color: {c['accent_hover']};
        }}
        
        /* Input controls styling */
        QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {{
            background-color: {c['bg_color']};
            color: {c['text_color']};
            border: 1px solid {c['border_color']};
            padding: 8px;
        }}
        
        QComboBox {{
            min-width: 6em;
            selection-background-color: {c['accent_color']};
        }}
        
        QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover, QLineEdit:hover {{
            border: 1px solid {c['accent_color']};
        }}
        
        QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QLineEdit:disabled {{
            background-color: {c['disabled_bg']};
            color: {c['disabled_text']};
            border-color: {c['border_color']};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 1px solid {c['border_color']};
            background-color: transparent;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {c['bg_color']};
            color: {c['text_color']};
            border: 1px solid {c['accent_color']};
            selection-background-color: {c['accent_color']};
            selection-color: white;
        }}
        
        /* Spin box buttons */
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: {c['lighter_bg']};
            width: 20px;
            border: none;
        }}
        
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {c['accent_color']};
        }}
        
        /* Line edit selection */
        QLineEdit {{
            selection-background-color: {c['accent_color']};
            selection-color: white;
        }}
        
        /* Header labels */
        QLabel[isHeader="true"] {{
            font-weight: bold;
            color: {c['accent_color']};
            font-size: 12pt;
            padding-top: 10px;
            padding-bottom: 5px;
        }}
        
        /* Checkbox styling */
        QCheckBox {{
            color: {c['text_color']};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {c['border_color']};
            background-color: {c['bg_color']};
        }}
        
        QCheckBox::indicator:unchecked:hover {{
            border: 1px solid {c['accent_color']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {c['accent_color']};
            border: 1px solid {c['accent_color']};
        }}

        /* Status container styling */
        QWidget[statusContainer="true"] {{
            background-color: {c['bg_color']};
            color: {c['text_color']};
            border: 1px solid {c['border_color']};
        }}
        
        QWidget[statusContainer="true"] QLabel {{
            background-color: transparent;
            color: {c['text_color']};
            padding: 2px;
        }}
        """

    @classmethod
    def get_theme_palette(cls):
        """
        Generate the QPalette for the current theme.
        Returns:
            QPalette: Configured palette for the current theme
        """
        palette = QPalette()
        c = cls.COLORS
        
        # Set palette colors for various UI states
        palette.setColor(QPalette.Window, QColor(c['bg_color']))
        palette.setColor(QPalette.WindowText, QColor(c['text_color']))
        palette.setColor(QPalette.Base, QColor(c['bg_color']))
        palette.setColor(QPalette.AlternateBase, QColor(c['lighter_bg']))
        palette.setColor(QPalette.ToolTipBase, QColor(c['bg_color']))
        palette.setColor(QPalette.ToolTipText, QColor(c['text_color']))
        palette.setColor(QPalette.Text, QColor(c['text_color']))
        palette.setColor(QPalette.Button, QColor(c['bg_color']))
        palette.setColor(QPalette.ButtonText, QColor(c['text_color']))
        palette.setColor(QPalette.Link, QColor(c['accent_color']))
        palette.setColor(QPalette.Highlight, QColor(c['accent_color']))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        
        # Disabled state colors
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(c['disabled_text']))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(c['disabled_text']))
        palette.setColor(QPalette.Disabled, QPalette.Window, QColor(c['disabled_bg']))
        palette.setColor(QPalette.Disabled, QPalette.Base, QColor(c['disabled_bg']))
        
        return palette

    @classmethod
    def apply_theme(cls, app, theme_name=None):
        """
        Apply the specified theme to the application.
        Args:
            app: QApplication instance to apply the theme to
            theme_name: Name of the theme to apply (optional)
        """
        if theme_name:
            cls.set_theme(theme_name)
            
        if app:
            app.setStyleSheet(cls.get_theme_style_sheet())
            app.setPalette(cls.get_theme_palette())

    @classmethod
    def get_available_themes(cls):
        """
        Get list of available theme names.
        Returns:
            list: Names of available themes
        """
        return list(cls.THEMES.keys())