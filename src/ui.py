from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QFrame, QInputDialog, QScrollArea, QSizePolicy, QStackedWidget, QTextEdit, QGraphicsOpacityEffect, QListWidget, QListWidgetItem, QLayout, QListView
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QCursor, QFont
from database import *
from detection import *


def create_line_edit_widget(is_locked: bool) -> QLineEdit:
    line_edit = QLineEdit()
    line_edit.setEnabled(not is_locked)
    line_edit.setFixedHeight(36)
    line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    line_edit.setPlaceholderText("empty = skip, unset = remove from environment")
    return line_edit


def create_render_selector_widget(setting_name: str, is_locked: bool) -> QLineEdit:
    api_type = "opengl" if setting_name == "opengl_rendering_device" else "vulkan"
    line_edit = QLineEdit()
    line_edit.setFixedHeight(36)
    line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    line_edit.setEnabled(not is_locked)
    line_edit.device_map = find_render_devices(api_type).get("device_map", {})
    line_edit.index_map = {}
    for device_index, device_name in enumerate(find_render_devices(api_type).get("devices", ()), 1):
        line_edit.index_map[str(device_index)] = device_name
    line_edit.setPlaceholderText("empty = skip, unset = remove from environment")
    return line_edit


def create_setting_card_widget(category_name: str, setting_key: str) -> dict:
    lock_status = validate_setting_availability(category_name, setting_key)
    card = QFrame()
    card.setProperty("settingCard", True)
    card.setFrameStyle(QFrame.Box)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(14, 10, 14, 10)
    card_layout.setSpacing(4)
    title_label = QLabel(get_setting_label(category_name, setting_key))
    title_label.setStyleSheet("font-weight: 500; font-size: 11pt;")
    title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    card_layout.addWidget(title_label)
    if is_render_selector_setting(category_name, setting_key):
        input_widget = create_render_selector_widget(setting_key, lock_status["locked"])
    else:
        input_widget = create_line_edit_widget(lock_status["locked"])
    card_layout.addWidget(input_widget)
    if lock_status["locked"] and lock_status["message"] != "":
        lock_label = QLabel(lock_status["message"])
        lock_label.setWordWrap(True)
        lock_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lock_label.setStyleSheet("color: #686868; font-size: 9pt;")
        card_layout.addWidget(lock_label)
    description_label = QLabel(get_setting_description(category_name, setting_key))
    description_label.setWordWrap(True)
    description_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    description_label.setStyleSheet("color: #686868; font-size: 9pt;")
    card_layout.addWidget(description_label)
    inputs_text = get_setting_inputs(category_name, setting_key)
    if inputs_text != "dynamic":
        mapping_line = build_setting_mapping_display(category_name, setting_key)
        values_line = build_setting_values_display(inputs_text)
        display_text = mapping_line + "\n  " + values_line + "\n  empty = skip, unset = remove from environment"
        inputs_label = QLabel(display_text)
        inputs_label.setWordWrap(True)
        inputs_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        inputs_label.setStyleSheet("color: #505050; font-size: 8pt; font-family: monospace;")
        card_layout.addWidget(inputs_label)
    else:
        api_type = "opengl" if setting_key == "opengl_rendering_device" else "vulkan"
        devices = find_render_devices(api_type).get("devices", ())
        device_str = ", ".join(str(i + 1) + "=" + name for i, name in enumerate(devices)) if devices else "detecting devices..."
        display_text = "render selector: [value] \u2192 device environment variables\n  " + device_str + "\n  empty = skip, unset = remove from environment"
        inputs_label = QLabel(display_text)
        inputs_label.setWordWrap(True)
        inputs_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        inputs_label.setStyleSheet("color: #505050; font-size: 8pt; font-family: monospace;")
        input_widget.device_label = inputs_label
        card_layout.addWidget(inputs_label)
    return {"card": card, "widgets": {"main": input_widget, "category": category_name, "setting": setting_key}}


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


def get_default_widget_height() -> int:
    reference = QLineEdit()
    return reference.sizeHint().height()


def build_copy_button_stylesheet(button_size: int) -> str:
    return "QPushButton { min-width: " + str(button_size) + "px; max-width: " + str(button_size) + "px; min-height: " + str(button_size) + "px; max-height: " + str(button_size) + "px; padding: 0px; font-size: 10pt; font-weight: bold; border-left: 2px solid transparent; } QPushButton:hover { border-left: 2px solid palette(highlight); }"


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
    widget_height = get_default_widget_height()
    text_edit.setFixedHeight(widget_height)
    text_edit.setStyleSheet("QTextEdit { background-color: #242424; color: #C0C0C0; border: none; border-left: 2px solid transparent; padding: 8px 12px; selection-background-color: #505050; } QTextEdit:hover { border-left: 2px solid palette(highlight); }")
    copy_button = QPushButton("Copy")
    copy_button.setCursor(QCursor(Qt.PointingHandCursor))
    copy_button.setFixedSize(widget_height, widget_height)
    copy_button.setStyleSheet(build_copy_button_stylesheet(widget_height))
    copy_button.clicked.connect(lambda: process_copy_button_action(copy_button, code_text))
    layout.addWidget(text_edit, 1)
    layout.addWidget(copy_button, 0)
    return frame


def create_info_card_widget(label_text: str, card_data) -> QFrame:
    card = QFrame()
    card.setProperty("settingCard", True)
    card.setFrameStyle(QFrame.Box)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 12, 14, 12)
    layout.setSpacing(6)
    layout.setSizeConstraint(QLayout.SetMinimumSize)
    title_label = QLabel(label_text)
    title_label.setStyleSheet("font-weight: 500; font-size: 11pt;")
    title_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
    layout.addWidget(title_label)
    if isinstance(card_data, str):
        description_label = QLabel(card_data)
        description_label.setWordWrap(True)
        description_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        description_label.setStyleSheet("color: #686868; font-size: 9pt;")
        layout.addWidget(description_label)
        return card
    if isinstance(card_data, dict):
        description_label = QLabel(card_data.get("description", ""))
        description_label.setWordWrap(True)
        description_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        description_label.setStyleSheet("color: #686868; font-size: 9pt;")
        layout.addWidget(description_label)
        return card
    if isinstance(card_data, tuple):
        for item_entry in card_data:
            if item_entry[0] == "text":
                text_label = QLabel(item_entry[1])
                text_label.setWordWrap(True)
                text_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
                text_label.setStyleSheet("color: #686868; font-size: 9pt;")
                layout.addWidget(text_label)
            elif item_entry[0] == "code":
                if len(item_entry) > 2 and item_entry[2] != "":
                    code_label = QLabel(item_entry[2])
                    code_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
                    code_label.setStyleSheet("color: #686868; font-size: 9pt; margin-top: 4px;")
                    layout.addWidget(code_label)
                layout.addWidget(create_code_block_widget(item_entry[1]))
        return card
    return card


def create_tab_content_widget(tab_name: str, info_items, add_stretch: bool) -> dict:
    widget = QWidget()
    all_widgets = {}
    main_layout = QVBoxLayout(widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(False)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    original_resize = scroll_area.resizeEvent
    def sync_width(event):
        original_resize(event)
        viewport_width = scroll_area.viewport().width()
        scroll_area.widget().setFixedWidth(viewport_width)
    scroll_area.resizeEvent = sync_width
    container_widget = QWidget()
    container_widget.setProperty("scrollContainer", True)
    content_layout = QVBoxLayout(container_widget)
    content_layout.setSpacing(6)
    content_layout.setContentsMargins(12, 12, 8, 12 if info_items is not None else 8)
    if info_items is not None:
        for label_text, card_data in info_items.items():
            content_layout.addWidget(create_info_card_widget(label_text, card_data))
        if add_stretch: content_layout.addStretch()
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area, 1)
        return {"tab": widget, "widgets": all_widgets}
    all_cards = {}
    for setting_key in find_settings_for_tab(tab_name):
        card_result = create_setting_card_widget(tab_name, setting_key)
        content_layout.addWidget(card_result["card"])
        all_widgets[tab_name + ":" + setting_key] = card_result["widgets"]["main"]
        all_cards[tab_name + ":" + setting_key] = card_result["card"]
    scroll_area.setWidget(container_widget)
    main_layout.addWidget(scroll_area, 1)
    return {"tab": widget, "widgets": all_widgets, "cards": all_cards}


def create_options_tab_content_widget() -> dict:
    widget = QWidget()
    options_widgets = {}
    main_layout = QVBoxLayout(widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(False)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    original_resize = scroll_area.resizeEvent
    def sync_width(event):
        original_resize(event)
        viewport_width = scroll_area.viewport().width()
        scroll_area.widget().setFixedWidth(viewport_width)
    scroll_area.resizeEvent = sync_width
    container_widget = QWidget()
    container_widget.setProperty("scrollContainer", True)
    content_layout = QVBoxLayout(container_widget)
    content_layout.setSpacing(6)
    content_layout.setContentsMargins(12, 12, 8, 12)
    for setting_key in find_settings_for_tab("Options"):
        card_result = create_setting_card_widget("Options", setting_key)
        content_layout.addWidget(card_result["card"])
        options_widgets[setting_key] = card_result["widgets"]["main"]
    scroll_area.setWidget(container_widget)
    main_layout.addWidget(scroll_area, 1)
    return {"tab": widget, "widgets": options_widgets}


def create_sidebar_widget(tab_names: tuple, stacked_widget) -> QListWidget:
    sidebar = QListWidget()
    sidebar.setFixedWidth(160)
    sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    sidebar.setFocusPolicy(Qt.NoFocus)
    for tab_name in tab_names:
        item = QListWidgetItem(tab_name)
        item.setSizeHint(item.sizeHint().__class__(item.sizeHint().width(), 40))
        sidebar.addItem(item)
    sidebar.setCurrentRow(0)
    sidebar.currentRowChanged.connect(stacked_widget.setCurrentIndex)
    return sidebar
