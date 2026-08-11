from PySide6.QtCore import QEasingCurve
from PySide6.QtCore import QPropertyAnimation
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtGui import QCursor
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QListView
from PySide6.QtWidgets import QListWidget
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from database import APP_VERSION
from database import find_cards_for_tab
from themes import get_standard_button_height


def get_sidebar_width() -> int:
    return 200


def get_header_vertical_margin() -> int:
    return 14


def get_copy_button_width() -> int:
    return 70


def get_combo_minimum_width() -> int:
    return 104


def create_combo_widget(options: tuple) -> QComboBox:
    combo = QComboBox()
    combo.setView(QListView())
    combo.setFixedHeight(get_standard_button_height())
    combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    combo.setFocusPolicy(Qt.ClickFocus)
    for value, label in options:
        combo.addItem(label, value)
    combo.setCurrentIndex(0)
    return combo


def create_divider_widget() -> QFrame:
    divider = QFrame()
    divider.setFrameShape(QFrame.HLine)
    divider.setFrameShadow(QFrame.Plain)
    divider.setFixedHeight(1)
    divider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    divider.setStyleSheet("QFrame { background-color: #262626; border: none; }")
    return divider


def create_setting_card_widget(label_text: str, description_text: str, options: tuple) -> dict:
    card = QFrame()
    card.setProperty("settingCard", True)
    card.setFrameStyle(QFrame.Box)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(14, 10, 14, 10)
    card_layout.setSpacing(4)
    title_label = QLabel(label_text)
    title_label.setWordWrap(False)
    title_label.setStyleSheet("font-weight: 500; font-size: 11pt;")
    title_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
    card_layout.addWidget(title_label)
    input_widget = create_combo_widget(options)
    input_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    input_widget.setMinimumWidth(get_combo_minimum_width())
    card_layout.addWidget(input_widget)
    description_label = QLabel(description_text)
    description_label.setWordWrap(True)
    description_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
    description_label.setStyleSheet("color: #585858; font-size: 9pt;")
    card_layout.addWidget(description_label)
    return {"card": card, "widget": input_widget}


def build_monospace_font() -> QFont:
    monospace_font = QFont("Consolas", 10)
    monospace_font.setFamily("monospace")
    return monospace_font


def process_copy_button_action(copy_button, clipboard_text: str) -> None:
    QApplication.clipboard().setText(clipboard_text)
    copy_button.setText("Copied!")
    effect = QGraphicsOpacityEffect(copy_button)
    copy_button.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(200)
    animation.setStartValue(0.7)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    animation.start()
    QTimer.singleShot(1000, lambda: copy_button.setText("Copy"))
    return None


def build_copy_button_stylesheet(button_width: int, button_height: int) -> str:
    return "QPushButton { min-width: " + str(button_width) + "px; max-width: " + str(button_width) + "px; min-height: " + str(button_height) + "px; max-height: " + str(button_height) + "px; padding: 0px; font-size: 10pt; font-weight: bold; border: none; border-left: 3px solid transparent; border-radius: 6px; } QPushButton:hover { border: none; border-left: 3px solid palette(highlight); border-radius: 6px; }"


def create_code_block_widget(code_text: str) -> QFrame:
    frame = QFrame()
    frame.setFrameStyle(QFrame.NoFrame)
    frame.setStyleSheet("QFrame { background-color: transparent; }")
    frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    text_edit = QTextEdit()
    text_edit.setPlainText(code_text)
    text_edit.setReadOnly(True)
    text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    text_edit.setLineWrapMode(QTextEdit.NoWrap)
    text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    text_edit.document().setDocumentMargin(0)
    text_edit.setFont(build_monospace_font())
    text_edit.setFixedHeight(get_standard_button_height())
    text_edit.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #C0C0C0; border: none; border-left: 3px solid transparent; padding: 8px 12px; selection-background-color: #505050; border-radius: 6px; } QTextEdit:hover { border: none; border-left: 3px solid palette(highlight); border-radius: 6px; }")
    copy_button = QPushButton("Copy")
    copy_button.setCursor(QCursor(Qt.PointingHandCursor))
    copy_button.setFixedSize(get_copy_button_width(), get_standard_button_height())
    copy_button.setStyleSheet(build_copy_button_stylesheet(get_copy_button_width(), get_standard_button_height()))
    copy_button.clicked.connect(lambda: process_copy_button_action(copy_button, text_edit.toPlainText()))
    layout.addWidget(text_edit, 1)
    layout.addWidget(copy_button, 0)
    frame.code_editor = text_edit
    return frame


def _add_info_text(layout, text: str) -> None:
    text_label = QLabel(text)
    text_label.setWordWrap(True)
    text_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
    text_label.setStyleSheet("color: #585858; font-size: 9pt;")
    layout.addWidget(text_label)
    return None


def _add_info_code(layout, item_entry: tuple) -> None:
    match len(item_entry) > 2 and item_entry[2] != "":
        case True:
            code_label = QLabel(item_entry[2])
            code_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
            code_label.setStyleSheet("color: #585858; font-size: 9pt; margin-top: 4px;")
            layout.addWidget(code_label)
        case False:
            pass
    layout.addWidget(create_code_block_widget(item_entry[1]))
    return None


def _add_info_entry(layout, item_entry) -> None:
    match item_entry[0]:
        case "text":
            _add_info_text(layout, item_entry[1])
        case "code":
            _add_info_code(layout, item_entry)
    return None


def create_info_card_widget(label_text: str, card_data) -> QFrame:
    card = QFrame()
    card.setProperty("settingCard", True)
    card.setFrameStyle(QFrame.Box)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 12, 14, 12)
    layout.setSpacing(6)
    title_label = QLabel(label_text)
    title_label.setStyleSheet("font-weight: 500; font-size: 11pt;")
    title_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
    layout.addWidget(title_label)
    match isinstance(card_data, str):
        case True:
            _add_info_text(layout, card_data)
        case False:
            for item_entry in card_data:
                _add_info_entry(layout, item_entry)
    return card


def process_container_relayout(container_widget) -> None:
    match (container_widget.layout() is None, container_widget.width() <= 0):
        case (False, False):
            match container_widget.layout().heightForWidth(container_widget.width()) < 0:
                case False:
                    container_widget.setFixedHeight(container_widget.layout().heightForWidth(container_widget.width()))
                case True:
                    pass
        case _:
            pass
    return None


def process_scroll_area_resize_sync(event, original_resize_handler, scroll_area_widget, content_container_widget) -> None:
    original_resize_handler(event)
    content_container_widget.setFixedWidth(scroll_area_widget.viewport().width())
    process_container_relayout(content_container_widget)
    return None


def create_scrollable_content_area(container_widget) -> QScrollArea:
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(False)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    original_resize = scroll_area.resizeEvent
    scroll_area.resizeEvent = lambda event: process_scroll_area_resize_sync(event, original_resize, scroll_area, container_widget)
    scroll_area.setWidget(container_widget)
    return scroll_area


def _build_content_container(info_items) -> QWidget:
    container_widget = QWidget()
    container_widget.setProperty("scrollContainer", True)
    content_layout = QVBoxLayout(container_widget)
    content_layout.setSpacing(6)
    content_layout.setContentsMargins(12, 12, 8, 12)
    match info_items is None:
        case False:
            for label_text, card_data in info_items.items():
                content_layout.addWidget(create_info_card_widget(label_text, card_data))
            content_layout.addStretch()
        case True:
            pass
    return container_widget


def create_tab_content_widget(tab_name: str, info_items) -> dict:
    widget = QWidget()
    all_widgets = {}
    all_cards = {}
    main_layout = QVBoxLayout(widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    container_widget = _build_content_container(info_items)
    match info_items is None:
        case True:
            for widget_key, label_text, description_text, options in find_cards_for_tab(tab_name):
                card_result = create_setting_card_widget(label_text, description_text, options)
                container_widget.layout().addWidget(card_result["card"])
                container_widget.layout().addWidget(create_divider_widget())
                all_widgets[widget_key] = card_result["widget"]
                all_cards[widget_key] = card_result["card"]
        case False:
            pass
    main_layout.addWidget(create_scrollable_content_area(container_widget), 1)
    return {"tab": widget, "widgets": all_widgets, "cards": all_cards}


def create_sidebar_tab_list(tab_names: tuple, stacked_widget) -> QListWidget:
    tab_list = QListWidget()
    tab_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    tab_list.setFocusPolicy(Qt.NoFocus)
    for tab_name in tab_names:
        item = QListWidgetItem(tab_name)
        item.setSizeHint(item.sizeHint().__class__(item.sizeHint().width(), 36))
        tab_list.addItem(item)
    tab_list.setCurrentRow(0)
    tab_list.currentRowChanged.connect(stacked_widget.setCurrentIndex)
    return tab_list


def build_sidebar_header_widget() -> QWidget:
    header_widget = QWidget()
    header_widget.setStyleSheet("background-color: transparent;")
    header_layout = QHBoxLayout(header_widget)
    header_layout.setContentsMargins(14, get_header_vertical_margin(), 14, get_header_vertical_margin())
    header_layout.setSpacing(0)
    volt_label = QLabel("volt")
    volt_label.setStyleSheet("font-weight: bold; font-size: 13pt; color: palette(highlight); background: transparent;")
    gui_label = QLabel("-gui")
    gui_label.setStyleSheet("font-weight: bold; font-size: 13pt; background: transparent;")
    version_label = QLabel("v" + APP_VERSION)
    version_label.setStyleSheet("font-size: 8pt; color: #9A9A9A; background: transparent;")
    version_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    header_layout.addWidget(volt_label, 0)
    header_layout.addWidget(gui_label, 0)
    header_layout.addStretch()
    header_layout.addWidget(version_label, 0)
    return header_widget


def build_sidebar_container_widget(tab_names: tuple, stacked_widget) -> tuple:
    sidebar_container = QWidget()
    sidebar_container.setFixedWidth(get_sidebar_width())
    sidebar_layout = QVBoxLayout(sidebar_container)
    sidebar_layout.setContentsMargins(0, 0, 0, 0)
    sidebar_layout.setSpacing(0)
    sidebar_layout.addWidget(build_sidebar_header_widget())
    tab_list = create_sidebar_tab_list(tab_names, stacked_widget)
    sidebar_layout.addWidget(tab_list, 1)
    return (sidebar_container, tab_list)


def create_simple_sidebar_widget(tab_names: tuple, stacked_widget) -> QWidget:
    return build_sidebar_container_widget(tab_names, stacked_widget)[0]
