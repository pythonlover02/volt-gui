from PySide6.QtGui import QPalette, QColor
from database import *


def get_style_palette_roles() -> tuple:
    return (
        (QPalette.Window, "background"),
        (QPalette.WindowText, "text_primary"),
        (QPalette.Base, "surface"),
        (QPalette.AlternateBase, "background_lighter"),
        (QPalette.Text, "text_primary"),
        (QPalette.BrightText, "text_primary"),
        (QPalette.Button, "surface"),
        (QPalette.ButtonText, "text_primary"),
        (QPalette.Highlight, "accent"),
        (QPalette.HighlightedText, "text_primary"),
        (QPalette.ToolTipBase, "surface"),
        (QPalette.ToolTipText, "text_primary"),
    )


def get_style_palette_disabled_roles() -> tuple:
    return (
        (QPalette.Text, "text_disabled"),
        (QPalette.ButtonText, "text_disabled"),
        (QPalette.WindowText, "text_disabled"),
        (QPalette.Window, "background_darker"),
        (QPalette.Base, "background_darker"),
        (QPalette.Button, "background_darker"),
    )


def get_accent_border_width() -> int:
    return 3


def get_standard_button_width() -> int:
    return 90


def get_standard_button_height() -> int:
    return 36


def get_style_stylesheet_template() -> str:
    return """
QWidget {{ background-color: {background}; color: {text_primary}; font-size: 10pt; font-family: "Segoe UI", "SF Pro Display", sans-serif; border: none; }}
QLabel {{ color: {text_primary}; background-color: transparent; border: none; qproperty-wordWrap: true; }}
QScrollArea {{ background-color: transparent; border: none; }}
QScrollArea > QWidget > QWidget {{ background-color: transparent; }}
QWidget[scrollContainer="true"], QWidget[buttonContainer="true"] {{ background-color: transparent; border: none; }}
QWidget[buttonContainer="true"] {{ background-color: {background}; }}
QMainWindow {{ background-color: {background}; border: none; }}
QScrollBar:vertical {{ background-color: {background}; width: 6px; margin: 0px; border: none; }}
QScrollBar::handle:vertical {{ background-color: {surface}; min-height: 40px; margin: 2px; border-radius: 3px; }}
QScrollBar::handle:vertical:hover {{ background-color: {accent}; }}
QScrollBar::handle:vertical:pressed {{ background-color: {accent_pressed}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ background: none; height: 0px; border: none; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QScrollBar:horizontal {{ background-color: {background}; height: 6px; margin: 0px; border: none; }}
QScrollBar::handle:horizontal {{ background-color: {surface}; min-width: 40px; margin: 2px; border-radius: 3px; }}
QScrollBar::handle:horizontal:hover {{ background-color: {accent}; }}
QScrollBar::handle:horizontal:pressed {{ background-color: {accent_pressed}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ background: none; width: 0px; border: none; }}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}
QPushButton {{ background-color: {surface}; color: {text_primary}; border: none; border-left: 3px solid transparent; outline: none; padding: 0px 14px; font-weight: 500; border-radius: 6px; }}
QPushButton:disabled {{ background-color: {background_darker}; color: {text_disabled}; border: none; border-left: 3px solid transparent; border-radius: 6px; }}
QPushButton:hover {{ background-color: {background_lighter}; color: {text_primary}; border: none; border-left: 3px solid {accent}; border-radius: 6px; }}
QPushButton:pressed {{ background-color: {accent_pressed}; color: white; border: none; border-left: 3px solid {accent}; border-radius: 6px; }}
QLineEdit {{ background-color: {surface}; color: {text_primary}; border: none; border-left: 3px solid transparent; padding: 0px 12px; selection-background-color: {accent}; border-radius: 6px; }}
QLineEdit:hover {{ background-color: {background_lighter}; border: none; border-left: 3px solid {accent}; border-radius: 6px; }}
QLineEdit:focus {{ background-color: {background_lighter}; border: none; border-left: 3px solid {accent}; border-radius: 6px; }}
QLineEdit:disabled {{ background-color: {background_darker}; color: {text_disabled}; border: none; border-left: 3px solid transparent; border-radius: 6px; }}
QComboBox {{ background-color: {surface}; color: {text_primary}; border: none; border-left: 3px solid transparent; padding: 0px 12px; selection-background-color: transparent; selection-color: {text_primary}; min-width: 60px; border-radius: 6px; }}
QComboBox:hover {{ background-color: {background_lighter}; border: none; border-left: 3px solid {accent}; border-radius: 6px; }}
QComboBox:focus {{ background-color: {background_lighter}; border: none; border-left: 3px solid {accent}; border-radius: 6px; }}
QComboBox:on {{ background-color: {background_lighter}; border: none; border-left: 3px solid {accent}; border-radius: 6px; }}
QComboBox:disabled {{ background-color: {background_darker}; color: {text_disabled}; border: none; border-left: 3px solid transparent; border-radius: 6px; }}
QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: top right; width: 20px; border: none; background-color: transparent; }}
QComboBox QAbstractItemView {{ background-color: {background}; color: {text_primary}; border: none; border-left: 3px solid {accent}; outline: none; padding: 4px 0px; selection-background-color: {background_lighter}; selection-color: {text_primary}; border-radius: 6px; }}
QComboBox QAbstractItemView::item {{ padding: 6px 12px; border: none; margin: 0px; background-color: {background}; }}
QComboBox QAbstractItemView::item:hover {{ background-color: {surface}; color: {text_primary}; }}
QComboBox QAbstractItemView::item:selected {{ background-color: {background_lighter}; color: {text_primary}; }}
QWidget[statusContainer="true"] {{ background-color: {card_background}; color: {text_primary}; border: none; border-left: 3px solid transparent; padding: 8px; border-radius: 6px; }}
QWidget[statusContainer="true"] QLabel {{ background-color: transparent; color: {text_primary}; padding: 4px; border: none; }}
QMenu {{ background-color: {background}; color: {text_primary}; border: none; border-left: 3px solid {accent}; padding: 6px; border-radius: 6px; }}
QMenu::item {{ padding: 6px 20px; border: none; border-left: 3px solid transparent; margin: 1px 0px; border-radius: 4px; }}
QMenu::item:selected {{ background-color: {surface}; color: {text_primary}; border: none; border-left: 3px solid {accent}; }}
QMenu::separator {{ height: 1px; background-color: {surface}; margin: 6px 0px; }}
QToolTip {{ background-color: {background}; color: {text_primary}; border: none; border-left: 3px solid {accent}; padding: 8px 12px; font-size: 10pt; border-radius: 6px; }}
QListWidget {{ background-color: {background}; border: none; outline: none; padding: 0px; }}
QListWidget::item {{ background-color: transparent; color: {text_secondary}; border: none; border-left: 3px solid transparent; padding: 8px 14px; margin: 1px 4px; border-radius: 6px; }}
QListWidget::item:selected {{ background-color: {surface}; color: {text_primary}; border: none; border-left: 3px solid {accent}; }}
QListWidget::item:hover:!selected {{ background-color: {surface}; color: {text_primary}; border: none; border-left: 3px solid {accent_hover}; }}
QFrame[settingCard="true"] {{ background-color: {card_background}; border: none; border-left: 3px solid transparent; border-radius: 6px; }}
QFrame[settingCard="true"]:hover {{ border: none; border-left: 3px solid {accent}; border-radius: 6px; }}
QInputDialog {{ background-color: {background}; }}
QInputDialog QLineEdit {{ background-color: {surface}; color: {text_primary}; border: none; border-left: 3px solid transparent; padding: 0px 12px; min-height: 36px; max-height: 36px; selection-background-color: {accent}; border-radius: 6px; }}
QInputDialog QLineEdit:hover {{ background-color: {background_lighter}; border: none; border-left: 3px solid {accent}; border-radius: 6px; }}
QInputDialog QLineEdit:focus {{ background-color: {background_lighter}; border: none; border-left: 3px solid {accent}; border-radius: 6px; }}
QInputDialog QPushButton {{ min-width: 90px; min-height: 36px; max-height: 36px; padding: 0px 12px; border-radius: 6px; }}
QMessageBox {{ background-color: {background}; }}
QMessageBox QPushButton {{ min-width: 90px; min-height: 36px; max-height: 36px; padding: 0px 12px; border-radius: 6px; }}
"""


def build_theme_colors(theme_name: str) -> dict:
    return {
        "background": "#161616",
        "background_darker": "#0e0e0e",
        "background_lighter": "#262626",
        "surface": "#1e1e1e",
        "text_primary": "#E8E8E8",
        "text_secondary": "#9A9A9A",
        "text_disabled": "#444444",
        "card_background": "#1a1a1a",
        "card_border": "#1a1a1a",
        "accent": get_accent_colors(theme_name)[0],
        "accent_hover": get_accent_colors(theme_name)[1],
        "accent_pressed": get_accent_colors(theme_name)[2],
    }


def process_theme_application(application_instance, theme_name: str) -> None:
    if application_instance is None: return None
    color_map = build_theme_colors(theme_name)
    application_instance.setStyleSheet(get_style_stylesheet_template().format(**color_map))
    palette_instance = QPalette()
    for palette_role, color_key in get_style_palette_roles():
        palette_instance.setColor(palette_role, QColor(color_map.get(color_key, "#E8E8E8")))
    for palette_role, color_key in get_style_palette_disabled_roles():
        palette_instance.setColor(QPalette.Disabled, palette_role, QColor(color_map[color_key]))
    application_instance.setPalette(palette_instance)
    return None
