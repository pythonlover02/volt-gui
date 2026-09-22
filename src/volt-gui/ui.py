from typing import Callable
from typing import Final
from typing import Optional

from PySide6.QtCore import QEasingCurve
from PySide6.QtCore import QPropertyAnimation
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtGui import QCursor
from PySide6.QtGui import QFont
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPaintEvent
from PySide6.QtGui import QResizeEvent
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QListWidget
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from database import APP_VERSION
from database import call_cards_for_tab
from themes import BASE_COLORS
from themes import SLIDER_HANDLE_WIDTH
from themes import STANDARD_BUTTON_HEIGHT


SIDEBAR_WIDTH: Final[int] = 200
HEADER_VERTICAL_MARGIN: Final[int] = 14
COPY_BUTTON_WIDTH: Final[int] = 70
WINDOW_MIN_WIDTH: Final[int] = 620
WINDOW_MIN_HEIGHT: Final[int] = 380
COPY_RESET_MS: Final[int] = 1000
COPY_FADE_MS: Final[int] = 200
SLIDER_SPACING: Final[int] = 2
SLIDER_PAGE_STEP: Final[int] = 1
SLIDER_TICK_HEIGHT: Final[int] = 5
SLIDER_TICK_GAP: Final[int] = 6
SLIDER_TICK_STRIDES: Final[tuple] = (1, 2, 5, 10, 25, 50, 100, 250, 500, 1000)
SLIDER_TICK_COLOR: Final[str] = "text_disabled"
STYLE_SLIDER_VALUE: Final[str] = "font-weight: 500; font-size: 10pt;"
STYLE_DIVIDER: Final[str] = "QFrame { background-color: #262626; border: none; }"
STYLE_DESCRIPTION: Final[str] = "color: #9A9A9A; font-size: 9pt;"
STYLE_CODE_LABEL: Final[str] = "color: #9A9A9A; font-size: 9pt; margin-top: 4px;"
STYLE_VERSION_LABEL: Final[str] = "font-size: 8pt; color: #9A9A9A; background: transparent;"
STYLE_CODE_EDIT: Final[str] = "QTextEdit { background-color: #1e1e1e; color: #C0C0C0; border: none; border-left: 3px solid transparent; padding: 8px 12px; selection-background-color: #505050; border-radius: 6px; } QTextEdit:hover { border: none; border-left: 3px solid palette(highlight); border-radius: 6px; }"


def process_combo_wheel_ignore(wheel_event: QWheelEvent) -> None:
    wheel_event.ignore()
    return None


def build_tick_stride(count: int, width: int) -> int:
    return next(
        (stride for stride in SLIDER_TICK_STRIDES
         if stride * (width - SLIDER_HANDLE_WIDTH) >= SLIDER_TICK_GAP * (count - 1)),
        SLIDER_TICK_STRIDES[-1])


def build_tick_positions(count: int, width: int) -> tuple:
    match count > 1 and width > SLIDER_HANDLE_WIDTH:
        case False:
            return ()
        case True:
            return tuple(
                round(SLIDER_HANDLE_WIDTH // 2 + at * (width - SLIDER_HANDLE_WIDTH) / (count - 1))
                for at in range(0, count, build_tick_stride(count, width)))


class StopSlider(QWidget):
    currentTextChanged = Signal(str)

    def __init__(self, options: tuple) -> None:
        super().__init__()
        self.stops = ()
        self.pressed_index = 0
        self.setProperty("cardRow", True)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setPageStep(SLIDER_PAGE_STEP)
        self.slider.setFocusPolicy(Qt.ClickFocus)
        self.slider.wheelEvent = process_combo_wheel_ignore
        self.slider.valueChanged.connect(self._process_value_change)
        self.slider.sliderPressed.connect(self._process_press)
        self.slider.sliderReleased.connect(self._process_release)
        self.ticks = QWidget()
        self.ticks.setProperty("cardRow", True)
        self.ticks.setFixedHeight(SLIDER_TICK_HEIGHT)
        self.ticks.paintEvent = self._process_ticks_paint
        self.value_label = QLabel()
        self.value_label.setStyleSheet(STYLE_SLIDER_VALUE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SLIDER_SPACING)
        layout.addWidget(self.slider)
        layout.addWidget(self.ticks)
        layout.addWidget(self.value_label)
        for value, label in options:
            self.addItem(label, value)
        self.setCurrentIndex(0)

    def _stop_at(self, index: int) -> Optional[tuple]:
        match 0 <= index < len(self.stops):
            case True:
                return self.stops[index]
            case False:
                return None

    def currentData(self) -> Optional[str]:
        match self._stop_at(self.slider.value()):
            case None:
                return None
            case (value, _):
                return value

    def currentText(self) -> str:
        match self._stop_at(self.slider.value()):
            case None:
                return ""
            case (_, label):
                return label

    def findData(self, value: str) -> int:
        return next((at for at, stop in enumerate(self.stops) if stop[0] == value), -1)

    def findText(self, text: str) -> int:
        return next((at for at, stop in enumerate(self.stops) if stop[1] == text), -1)

    def setCurrentIndex(self, index: int) -> None:
        self.slider.setValue(index)
        return None

    def setCurrentText(self, text: str) -> None:
        match self.findText(text):
            case -1:
                return None
            case index:
                self.setCurrentIndex(index)
                return None

    def clear(self) -> None:
        self.stops = ()
        self.slider.setRange(0, 0)
        self._process_stops_change()
        return None

    def addItem(self, label: str, value: str) -> None:
        self.stops = self.stops + ((value, label),)
        self.slider.setRange(0, len(self.stops) - 1)
        self._process_stops_change()
        return None

    def _process_stops_change(self) -> None:
        self.value_label.setText(self.currentText())
        self.ticks.update()
        return None

    def _process_value_change(self, index: int) -> None:
        self.value_label.setText(self.currentText())
        match self.slider.isSliderDown():
            case True:
                return None
            case False:
                self.currentTextChanged.emit(self.currentText())
                return None

    def _process_press(self) -> None:
        self.pressed_index = self.slider.value()
        return None

    def _process_release(self) -> None:
        match self.slider.value() == self.pressed_index:
            case True:
                return None
            case False:
                self.currentTextChanged.emit(self.currentText())
                return None

    def _process_ticks_paint(self, paint_event: QPaintEvent) -> None:
        painter = QPainter(self.ticks)
        painter.setPen(QColor(BASE_COLORS[SLIDER_TICK_COLOR]))
        for position in build_tick_positions(len(self.stops), self.ticks.width()):
            painter.drawLine(position, 0, position, SLIDER_TICK_HEIGHT)
        painter.end()
        return None


def create_slider_widget(options: tuple) -> StopSlider:
    return StopSlider(options)


def create_divider_widget() -> QFrame:
    divider = QFrame()
    divider.setFrameShape(QFrame.HLine)
    divider.setFrameShadow(QFrame.Plain)
    divider.setFixedHeight(1)
    divider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    divider.setStyleSheet(STYLE_DIVIDER)
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
    input_widget = create_slider_widget(options)
    input_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    card_layout.addWidget(input_widget)
    description_label = QLabel(description_text)
    description_label.setWordWrap(True)
    description_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
    description_label.setStyleSheet(STYLE_DESCRIPTION)
    card_layout.addWidget(description_label)
    return {"card": card, "widget": input_widget}


def build_monospace_font() -> QFont:
    monospace_font = QFont("Consolas", 10)
    monospace_font.setFamily("monospace")
    return monospace_font


def process_copy_button_action(copy_button: QPushButton, clipboard_text: str) -> None:
    QApplication.clipboard().setText(clipboard_text)
    copy_button.setText("Copied!")
    effect = QGraphicsOpacityEffect(copy_button)
    copy_button.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(COPY_FADE_MS)
    animation.setStartValue(0.7)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    animation.start()
    QTimer.singleShot(COPY_RESET_MS, lambda: copy_button.setText("Copy"))
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
    text_edit.setFixedHeight(STANDARD_BUTTON_HEIGHT)
    text_edit.setStyleSheet(STYLE_CODE_EDIT)
    copy_button = QPushButton("Copy")
    copy_button.setCursor(QCursor(Qt.PointingHandCursor))
    copy_button.setFixedSize(COPY_BUTTON_WIDTH, STANDARD_BUTTON_HEIGHT)
    copy_button.setStyleSheet(build_copy_button_stylesheet(COPY_BUTTON_WIDTH, STANDARD_BUTTON_HEIGHT))
    copy_button.clicked.connect(lambda: process_copy_button_action(copy_button, text_edit.toPlainText()))
    layout.addWidget(text_edit, 1)
    layout.addWidget(copy_button, 0)
    frame.code_editor = text_edit
    return frame


def _process_info_text(layout: QVBoxLayout, text: str) -> None:
    text_label = QLabel(text)
    text_label.setWordWrap(True)
    text_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
    text_label.setStyleSheet(STYLE_DESCRIPTION)
    layout.addWidget(text_label)
    return None


def _process_info_code(layout: QVBoxLayout, item_entry: tuple) -> None:
    match len(item_entry) > 2 and item_entry[2] != "":
        case True:
            code_label = QLabel(item_entry[2])
            code_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
            code_label.setStyleSheet(STYLE_CODE_LABEL)
            layout.addWidget(code_label)
        case False:
            pass
    layout.addWidget(create_code_block_widget(item_entry[1]))
    return None


def _process_info_entry(layout: QVBoxLayout, item_entry: tuple) -> None:
    match item_entry[0]:
        case "text":
            _process_info_text(layout, item_entry[1])
        case "code":
            _process_info_code(layout, item_entry)
    return None


def create_info_card_widget(label_text: str, card_data: str | tuple) -> QFrame:
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
            _process_info_text(layout, card_data)
        case False:
            for item_entry in card_data:
                _process_info_entry(layout, item_entry)
    return card


def process_container_relayout(container_widget: QWidget) -> None:
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


def process_scroll_area_resize_sync(event: QResizeEvent, original_resize_handler: Callable[[QResizeEvent], None], scroll_area_widget: QScrollArea, content_container_widget: QWidget) -> None:
    original_resize_handler(event)
    content_container_widget.setFixedWidth(scroll_area_widget.viewport().width())
    process_container_relayout(content_container_widget)
    return None


def create_scrollable_content_area(container_widget: QWidget) -> QScrollArea:
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(False)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    original_resize = scroll_area.resizeEvent
    scroll_area.resizeEvent = lambda event: process_scroll_area_resize_sync(event, original_resize, scroll_area, container_widget)
    scroll_area.setWidget(container_widget)
    return scroll_area


def _create_content_container(info_items: Optional[dict]) -> QWidget:
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


def create_tab_content_widget(tab_name: str, info_items: Optional[dict]) -> dict:
    widget = QWidget()
    all_widgets = {}
    all_cards = {}
    main_layout = QVBoxLayout(widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    container_widget = _create_content_container(info_items)
    match info_items is None:
        case True:
            for widget_key, label_text, description_text, options in call_cards_for_tab(tab_name):
                card_result = create_setting_card_widget(label_text, description_text, options)
                container_widget.layout().addWidget(card_result["card"])
                container_widget.layout().addWidget(create_divider_widget())
                all_widgets[widget_key] = card_result["widget"]
                all_cards[widget_key] = card_result["card"]
        case False:
            pass
    main_layout.addWidget(create_scrollable_content_area(container_widget), 1)
    return {"tab": widget, "widgets": all_widgets, "cards": all_cards}


def create_sidebar_tab_list(tab_names: tuple, stacked_widget: QStackedWidget) -> QListWidget:
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


def create_sidebar_header_widget() -> QWidget:
    header_widget = QWidget()
    header_widget.setStyleSheet("background-color: transparent;")
    header_layout = QHBoxLayout(header_widget)
    header_layout.setContentsMargins(14, HEADER_VERTICAL_MARGIN, 14, HEADER_VERTICAL_MARGIN)
    header_layout.setSpacing(0)
    volt_label = QLabel("volt")
    volt_label.setStyleSheet("font-weight: bold; font-size: 13pt; color: palette(highlight); background: transparent;")
    gui_label = QLabel("-gui")
    gui_label.setStyleSheet("font-weight: bold; font-size: 13pt; background: transparent;")
    version_label = QLabel("v" + APP_VERSION)
    version_label.setStyleSheet(STYLE_VERSION_LABEL)
    version_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    header_layout.addWidget(volt_label, 0)
    header_layout.addWidget(gui_label, 0)
    header_layout.addStretch()
    header_layout.addWidget(version_label, 0)
    return header_widget


def create_sidebar_container_widget(tab_names: tuple, stacked_widget: QStackedWidget) -> tuple:
    sidebar_container = QWidget()
    sidebar_container.setFixedWidth(SIDEBAR_WIDTH)
    sidebar_layout = QVBoxLayout(sidebar_container)
    sidebar_layout.setContentsMargins(0, 0, 0, 0)
    sidebar_layout.setSpacing(0)
    sidebar_layout.addWidget(create_sidebar_header_widget())
    tab_list = create_sidebar_tab_list(tab_names, stacked_widget)
    sidebar_layout.addWidget(tab_list, 1)
    return (sidebar_container, tab_list)


def create_simple_sidebar_widget(tab_names: tuple, stacked_widget: QStackedWidget) -> QWidget:
    return create_sidebar_container_widget(tab_names, stacked_widget)[0]
