from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QSizePolicy, QMainWindow, QApplication, QPushButton, QStackedWidget, QFrame, QTextEdit, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QCursor, QColor


class WelcomeManager:
    """
    Main Welcome management class that handles welcome wizard and setup.
    """
    
    WELCOME_SECTIONS = [
        {
            "title": "Welcome to volt-gui:",
            "description": "First of all, thanks for using my tool! If you have any feature requests or issues, please report them to the volt-gui GitHub repository.",
            "copyable_blocks": []
        },
        {
            "title": "Optional Dependencies:",
            "description": "• scx schedulers and Linux Kernel >= 6.12 if you want to make use of the CPU Pluggable Schedulers."
                        "\n\n• MangoHud if you want to make use of the Render Pipeline Settings. Both the native or the Flatpak version satisfy the dependency. \nNote that you might need to install both versions, as the one installed with your distro package manager will be used for native programs, while the flatpak version will be used for flatpak programs. MangoHud is available on almost any distro and the flatpak version is quite easy to install with:",
            "copyable_blocks": [
                "flatpak install mangohud"
            ],
            "additional_text": "• glxinfo is required to use the OpenGL Render Selector."
                            "\n\n• vulkaninfo and the Vulkan Mesa layer are required to use the Vulkan Render Selector. One way to check if you have the Vulkan Mesa layer installed is to run this command:",
            "copyable_blocks_after_additional": [
                "MESA_VK_DEVICE_SELECT=list vulkaninfo"
            ],
            "example_output": """selectable devices:
    GPU 0: 10de:128b "NVIDIA GeForce GT 710" discrete GPU 0000:01:00.0
    GPU 1: 10005:0 "llvmpipe (LLVM 20.1.8, 256 bits)" CPU 0000:00:00.0""",
            "closing_text": "If the output doesn't look like this text above, then you don't have the Vulkan Mesa layer installed on your PC."
        },
        {
            "title": "Key Notes:", 
            "description": "• The apply buttons in the CPU/GPU/Disk/Kernel tabs are interconnected, meaning that pressing one of those apply buttons will apply all settings from these tabs. This helps avoid having to go tab by tab pressing apply to apply all the settings."
                        "\n\n• Kernel/Disk/CPU settings apply system-wide immediately, while the GPU settings are saved in the `volt` script when you press the apply button."
                        "\n\n• You can use the Options Tab settings to configure the volt-gui behavior."
                        "\n\n• You can create, use, and delete different profiles. When a profile is created, it will base its settings on the current profile being used."
                        "\n\n• The settings applied by the program are lost when the system is shut down or rebooted. The only exception is the `volt` script, as it is a physical file.",
            "copyable_blocks": []
        },
        {
            "title": "Apply the GPU Configuration:",
            "description": "The GPU settings are applied through the 'volt' script. Always launch games with the 'volt' script prepended to use these options. Examples:",
            "copyable_blocks": [
                "volt",
                "volt %command%",
                "volt flatpak run net.pcsx2.PCSX2"
            ],
            "labels": [
                "Lutris (Native):",
                "Steam (Native):",
                "Flatpak Program:"
            ]
        },
        {
            "title": "Setup Complete!",
            "description": "You can disable or enable this welcome message in the Options Tab.\n\nThanks for reading the welcome guide!",
            "copyable_blocks": []
        },
    ]

    @staticmethod
    def create_copyable_code_block(text):
        """
        Creates a copyable code block widget.
        """
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 0px;
                margin: 4px 0px;
            }
        """)
        
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(4, 3, 4, 3)
        layout.setSpacing(4)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        font = QFont("Consolas", 10)
        font.setFamily("monospace")
        text_edit.setFont(font)
        
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #e0e0e0;
                selection-background-color: #4a4a4a;
                padding: 2px;
            }
        """)
        
        layout.addWidget(text_edit, 1)
        
        copy_button = QPushButton("Copy")
        copy_button.setMaximumWidth(55)
        copy_button.setMaximumHeight(26)
        copy_button.setCursor(QCursor(Qt.PointingHandCursor))
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 2px;
                color: #ffffff;
                font-size: 11px;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #7a7a7a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        
        def copy_text():
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            original_text = copy_button.text()
            copy_button.setText("Copied!")
            
            effect = QGraphicsOpacityEffect(copy_button)
            copy_button.setGraphicsEffect(effect)
            
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(200)
            animation.setStartValue(0.7)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.start()
            
            QTimer.singleShot(1000, lambda: copy_button.setText(original_text))
        
        copy_button.clicked.connect(copy_text)
        layout.addWidget(copy_button, 0, Qt.AlignCenter)
        
        def adjust_height():
            text_edit.setMaximumHeight(16777215)
            
            doc = text_edit.document()
            doc.setTextWidth(text_edit.width() - 10)
            content_height = doc.size().height()
            
            line_count = len(text.splitlines())
            padding = 5 if line_count <= 1 else 8
            total_height = max(content_height + padding, 28)
            
            text_edit.setFixedHeight(int(total_height))
        
        QTimer.singleShot(0, adjust_height)
        
        frame.resizeEvent = lambda event: adjust_height()
        
        return frame

    @staticmethod
    def create_step_page(section_info, step_number):
        """
        Creates a page widget for a single welcome step.
        """
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(12)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(12)
        
        title_label = QLabel(section_info["title"])
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("font-weight: bold; font-size: 24px; color: #FFFFFF; margin-bottom: 8px;")
        title_label.setWordWrap(True)
        content_layout.addWidget(title_label)
        
        desc_label = QLabel(section_info["description"])
        desc_label.setAlignment(Qt.AlignLeft)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            color: #E0E0E0; 
            font-size: 14px; 
            line-height: 1.5;
            padding: 0px;
            margin: 0px;
        """)
        desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        content_layout.addWidget(desc_label)
        
        copyable_blocks = section_info.get("copyable_blocks", [])
        labels = section_info.get("labels", [])
        
        for i, block in enumerate(copyable_blocks):
            if i < len(labels):
                label = QLabel(labels[i])
                label.setStyleSheet("color: #E0E0E0; font-size: 13px; margin-top: 8px; margin-bottom: 1px;")
                content_layout.addWidget(label)
            
            code_block = WelcomeManager.create_copyable_code_block(block)
            content_layout.addWidget(code_block)
        
        if "additional_text" in section_info:
            additional_label = QLabel(section_info["additional_text"])
            additional_label.setAlignment(Qt.AlignLeft)
            additional_label.setWordWrap(True)
            additional_label.setStyleSheet("""
                color: #E0E0E0; 
                font-size: 14px; 
                line-height: 1.5;
                padding: 0px;
                margin: 6px 0px 0px 0px;
            """)
            content_layout.addWidget(additional_label)
            
            if "copyable_blocks_after_additional" in section_info:
                for block in section_info["copyable_blocks_after_additional"]:
                    code_block = WelcomeManager.create_copyable_code_block(block)
                    content_layout.addWidget(code_block)
        
        if "example_output" in section_info:
            example_block = WelcomeManager.create_copyable_code_block(section_info["example_output"])
            content_layout.addWidget(example_block)
        
        if "closing_text" in section_info:
            closing_label = QLabel(section_info["closing_text"])
            closing_label.setAlignment(Qt.AlignLeft)
            closing_label.setWordWrap(True)
            closing_label.setStyleSheet("""
                color: #E0E0E0; 
                font-size: 14px; 
                line-height: 1.5;
                padding: 0px;
                margin: 6px 0px 0px 0px;
            """)
            content_layout.addWidget(closing_label)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        page_layout.addWidget(scroll_area)
        
        return page

    @staticmethod
    def create_navigation_buttons(parent_layout, widgets):
        """
        Creates and adds the navigation buttons to the layout.
        """
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 16, 0, 0)
        
        widgets['back_button'] = QPushButton("← Back")
        widgets['back_button'].setMinimumHeight(32)
        widgets['back_button'].setCursor(QCursor(Qt.PointingHandCursor))
        widgets['back_button'].setStyleSheet("""
            QPushButton:disabled {
                color: #777777;
            }
        """)
        
        nav_layout.addWidget(widgets['back_button'])
        
        widgets['progress_label'] = QLabel()
        widgets['progress_label'].setAlignment(Qt.AlignCenter)
        widgets['progress_label'].setStyleSheet("font-size: 13px; color: #888888; margin: 0 10px;")
        nav_layout.addWidget(widgets['progress_label'], 1, Qt.AlignCenter)
        
        widgets['next_button'] = QPushButton("Next →")
        widgets['next_button'].setMinimumHeight(32)
        widgets['next_button'].setCursor(QCursor(Qt.PointingHandCursor))
        
        widgets['finish_button'] = QPushButton("Finish")
        widgets['finish_button'].setMinimumHeight(32)
        widgets['finish_button'].setCursor(QCursor(Qt.PointingHandCursor))
        widgets['finish_button'].hide()
        
        nav_layout.addWidget(widgets['next_button'])
        nav_layout.addWidget(widgets['finish_button'])
        
        parent_layout.addLayout(nav_layout)

    @staticmethod
    def update_navigation(widgets):
        """
        Updates the navigation buttons and progress indicator based on current step.
        """
        current_step = widgets['current_step']
        total_steps = len(WelcomeManager.WELCOME_SECTIONS)
        
        widgets['progress_label'].setText(f"Step {current_step + 1} of {total_steps}")
        
        widgets['back_button'].setEnabled(current_step > 0)
        
        if current_step == total_steps - 1:
            widgets['next_button'].hide()
            widgets['finish_button'].show()
        else:
            widgets['next_button'].show()
            widgets['finish_button'].hide()

    @staticmethod
    def go_back(widgets):
        """
        Go to the previous step.
        """
        if widgets['current_step'] > 0:
            widgets['current_step'] -= 1
            widgets['stacked_widget'].setCurrentIndex(widgets['current_step'])
            WelcomeManager.update_navigation(widgets)

    @staticmethod
    def go_next(widgets):
        """
        Go to the next step.
        """
        if widgets['current_step'] < len(WelcomeManager.WELCOME_SECTIONS) - 1:
            widgets['current_step'] += 1
            widgets['stacked_widget'].setCurrentIndex(widgets['current_step'])
            WelcomeManager.update_navigation(widgets)

    @staticmethod
    def finish_wizard(widgets):
        """
        Finish the wizard and emit the finished signal if available.
        """
        if 'finished_callback' in widgets and widgets['finished_callback']:
            widgets['finished_callback']()

    @staticmethod
    def create_welcome_tab():
        """
        Creates and returns the welcome tab widget.
        """
        welcome_tab = QWidget()
        main_layout = QVBoxLayout(welcome_tab)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        widgets = {}
        widgets['current_step'] = 0
        
        widgets['stacked_widget'] = QStackedWidget()
        
        for i, section in enumerate(WelcomeManager.WELCOME_SECTIONS):
            page = WelcomeManager.create_step_page(section, i)
            widgets['stacked_widget'].addWidget(page)
        
        main_layout.addWidget(widgets['stacked_widget'], 1)

        WelcomeManager.create_navigation_buttons(main_layout, widgets)
        widgets['back_button'].clicked.connect(lambda: WelcomeManager.go_back(widgets))
        widgets['next_button'].clicked.connect(lambda: WelcomeManager.go_next(widgets))
        widgets['finish_button'].clicked.connect(lambda: WelcomeManager.finish_wizard(widgets))
        
        WelcomeManager.update_navigation(widgets)
        
        return welcome_tab, widgets

    @staticmethod
    def create_welcome_window(main_window):
        """
        Creates a separate welcome window with the welcome wizard.
        """
        welcome_window = QMainWindow()
        welcome_window.setWindowTitle("volt-gui - Welcome Setup")
        welcome_window.setMinimumSize(540, 380)
        welcome_window.setAttribute(Qt.WA_DeleteOnClose, False)
        
        welcome_tab, widgets = WelcomeManager.create_welcome_tab()
        widgets['finished_callback'] = welcome_window.close
        welcome_window.setCentralWidget(welcome_tab)
        
        return welcome_window