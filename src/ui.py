from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFrame, QInputDialog, QScrollArea, QSizePolicy, QStackedWidget, QTextEdit, QGraphicsOpacityEffect, QListWidget, QListWidgetItem, QLayout, QListView
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QCursor, QFont
from database import *
from detection import *


def build_add_button_stylesheet(button_size: int) -> str:
    return "QPushButton { min-width: " + str(button_size) + "px; max-width: " + str(button_size) + "px; min-height: " + str(button_size) + "px; max-height: " + str(button_size) + "px; padding: 0px; font-size: 10pt; font-weight: bold; border-left: 2px solid transparent; } QPushButton:hover { border-left: 2px solid palette(highlight); }"


def process_custom_value_add(combo_widget, parent_widget) -> None:
    input_value, accepted = QInputDialog.getText(parent_widget, "Add Custom Value", "Enter custom value:")
    if accepted is not True: return None
    if input_value is None: return None
    if input_value.strip() == "": return None
    combo_widget.addItem(input_value.strip())
    combo_widget.setCurrentIndex(combo_widget.count() - 1)
    combo_widget.custom_value = input_value.strip()
    return None


def create_combo_box_widget(category_name: str, setting_name: str, is_locked: bool) -> dict:
    combobox = QComboBox()
    combobox.setFocusPolicy(Qt.StrongFocus)
    combobox.setView(QListView())
    combobox.wheelEvent = lambda event: event.ignore()
    combobox.custom_value = None
    for item_display_text in find_available_setting_values(category_name, setting_name):
        combobox.addItem(item_display_text)
    combobox.setCurrentText("skip")
    combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    combobox.setEnabled(not is_locked)
    if is_render_selector_setting(category_name, setting_name):
        combobox.device_map = find_render_devices("opengl" if setting_name == "opengl_rendering_device" else "vulkan").get("device_map", {})
    add_button = QPushButton("+")
    add_button.setCursor(QCursor(Qt.PointingHandCursor))
    add_button.setEnabled(not is_locked)
    add_button.setToolTip("Add custom value")
    return {"combo": combobox, "add_button": add_button}


def build_resource_display_text(prefix_text: str, target_tuple: tuple):
    if len(target_tuple) == 0: return None
    return prefix_text + ":\n" + "\n".join("   " + target for target in target_tuple)


def create_resource_display_widget(prefix_text: str, target_tuple: tuple):
    if build_resource_display_text(prefix_text, target_tuple) is None: return None
    resource_label = QLabel(build_resource_display_text(prefix_text, target_tuple))
    resource_label.setWordWrap(True)
    resource_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
    resource_label.setStyleSheet("color: #505050; font-size: 8pt; font-family: monospace;")
    return resource_label


def create_setting_card_widget(category_name: str, setting_key: str) -> dict:
    lock_status = validate_setting_availability(category_name, setting_key)
    card = QFrame()
    card.setProperty("settingCard", True)
    card.setFrameStyle(QFrame.Box)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(14, 12, 14, 12)
    card_layout.setSpacing(6)
    card_layout.setSizeConstraint(QLayout.SetMinimumSize)
    title_label = QLabel(get_setting_label(category_name, setting_key))
    title_label.setStyleSheet("font-weight: 500; font-size: 11pt;")
    title_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
    card_layout.addWidget(title_label)
    widget_data = create_combo_box_widget(category_name, setting_key, lock_status["locked"])
    widget_data["add_button"].clicked.connect(lambda: process_custom_value_add(widget_data["combo"], card))
    widget_data["add_button"].setFixedSize(widget_data["combo"].sizeHint().height(), widget_data["combo"].sizeHint().height())
    widget_data["add_button"].setStyleSheet(build_add_button_stylesheet(widget_data["combo"].sizeHint().height()))
    combo_layout = QHBoxLayout()
    combo_layout.setContentsMargins(0, 0, 0, 0)
    combo_layout.setSpacing(6)
    combo_layout.addWidget(widget_data["combo"], 1)
    combo_layout.addWidget(widget_data["add_button"], 0)
    card_layout.addLayout(combo_layout)
    if lock_status["locked"] and lock_status["message"] != "":
        lock_label = QLabel(lock_status["message"])
        lock_label.setWordWrap(True)
        lock_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        lock_label.setStyleSheet("color: #686868; font-size: 9pt;")
        card_layout.addWidget(lock_label)
    environment_resource_widget = create_resource_display_widget("Environment Variables", find_environment_variable_targets_for_setting(category_name, setting_key))
    if environment_resource_widget is not None:
        card_layout.addWidget(environment_resource_widget)
    argument_resource_widget = create_resource_display_widget("Arguments", find_argument_targets_for_setting(category_name, setting_key))
    if argument_resource_widget is not None:
        card_layout.addWidget(argument_resource_widget)
    return {"card": card, "widgets": {"main": widget_data["combo"], "category": category_name, "setting": setting_key}}


def get_default_combo_height() -> int:
    reference_combo = QComboBox()
    reference_combo.setView(QListView())
    reference_combo.addItem("")
    return reference_combo.sizeHint().height()


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


def create_code_block_widget(code_text: str, parent_combo) -> QFrame:
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
    combo_height = parent_combo.sizeHint().height() if parent_combo is not None else get_default_combo_height()
    text_edit.setFixedHeight(combo_height)
    text_edit.setStyleSheet("QTextEdit { background-color: #141414; color: #C0C0C0; border: none; border-left: 2px solid transparent; padding: 8px 12px; selection-background-color: #4a4a4a; } QTextEdit:hover { border-left: 2px solid palette(highlight); }")
    copy_button = QPushButton("Copy")
    copy_button.setCursor(QCursor(Qt.PointingHandCursor))
    copy_button.setFixedSize(combo_height, combo_height)
    copy_button.setStyleSheet(build_add_button_stylesheet(combo_height))
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
        description_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        description_label.setStyleSheet("color: #686868; font-size: 9pt;")
        layout.addWidget(description_label)
        return card
    if isinstance(card_data, dict):
        description_label = QLabel(card_data.get("description", ""))
        description_label.setWordWrap(True)
        description_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        description_label.setStyleSheet("color: #686868; font-size: 9pt;")
        layout.addWidget(description_label)
        return card
    if isinstance(card_data, tuple):
        reference_combo = QComboBox()
        reference_combo.setView(QListView())
        reference_combo.addItem("")
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
                layout.addWidget(create_code_block_widget(item_entry[1], reference_combo))
        return card
    return card


def create_tab_content_widget(tab_name: str, info_items, add_stretch: bool) -> dict:
    widget = QWidget()
    all_widgets = {}
    main_layout = QVBoxLayout(widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
    for setting_key in find_settings_for_tab(tab_name):
        card_result = create_setting_card_widget(tab_name, setting_key)
        content_layout.addWidget(card_result["card"])
        all_widgets[tab_name + ":" + setting_key] = card_result["widgets"]["main"]
    content_layout.addStretch(1)
    scroll_area.setWidget(container_widget)
    main_layout.addWidget(scroll_area, 1)
    return {"tab": widget, "widgets": all_widgets}


def create_options_tab_content_widget() -> dict:
    widget = QWidget()
    options_widgets = {}
    main_layout = QVBoxLayout(widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    container_widget = QWidget()
    container_widget.setProperty("scrollContainer", True)
    content_layout = QVBoxLayout(container_widget)
    content_layout.setSpacing(6)
    content_layout.setContentsMargins(12, 12, 8, 12)
    for setting_key in find_settings_for_tab("Options"):
        card_result = create_setting_card_widget("Options", setting_key)
        content_layout.addWidget(card_result["card"])
        options_widgets[setting_key] = card_result["widgets"]["main"]
    content_layout.addStretch(1)
    scroll_area.setWidget(container_widget)
    main_layout.addWidget(scroll_area, 1)
    return {"tab": widget, "widgets": options_widgets}


def create_sidebar_widget(tab_names: tuple, stacked_widget) -> QListWidget:
    sidebar = QListWidget()
    sidebar.setFixedWidth(160)
    sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    sidebar.setFocusPolicy(Qt.NoFocus)
    for tab_name in tab_names:
        sidebar.addItem(QListWidgetItem(tab_name))
    sidebar.setCurrentRow(0)
    sidebar.currentRowChanged.connect(stacked_widget.setCurrentIndex)
    return sidebar
