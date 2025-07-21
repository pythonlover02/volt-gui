from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QSizePolicy, QMainWindow, QApplication
from PySide6.QtCore import Qt
from theme import ThemeManager


class WelcomeManager:
    
    @staticmethod
    def _get_welcome_sections():
        """
        Returns a list of dictionaries containing welcome information sections.
        """
        return [
            {
                "title": "Welcome to volt-gui:",
                "description": "Thanks for using my tool!!! If you have any feature request or issue please report it to the volt-gui GitHub repo :). Your current volt-gui version its 1.0.0." 
            },
            {
                "title": "Key Notes:", 
                "description": "• The apply buttons in the CPU/GPU/Disk/Kernel tabs are interconnected, meaning that pressing one of those apply buttons will apply all settings from these tabs. This its to avoid having to go tab from tab pressing apply to apply all the settings.\n"
                            "• Kernel/Disk/CPU settings apply systemwide immediately, while the GPU settings are saved on the `volt` script when pressed the apply button.\n"
                            "• Use the Options tab settings to configure program behavior.\n"
                            "• You can create, use and delete different profiles, when a profile its created it will base its settings of the current profile being used.\n"
                            "• The settings applied by the program are loss when the system its shutdown or rebooted, the only exeption its the `volt` script."
            },
            {
                "title": "Apply the GPU Configuration:",
                "description": "The GPU settings are applied through the 'volt' script. So always launch games with 'volt' script appended to use this options. Examples:\n"
                            "Lutris (Native): volt\n"
                            "Steam (Native): volt %command%\n"
                            "Flatpak Program: volt flatpak run net.pcsx2.PCSX2"
            },
            {
                "title": "Optional Dependencies",
                "description": "• scx schedulers in the case you want to make use of the CPU Pluggable Schedulers\n"
                            "• mangohud in the case you want to make use of the Render Pipeline Settings. Both the native or the Flatpak version satisfy the dependency.\n" \
                            "• glxinfo its required to use the OpenGL Render Selector.\n"
                            "• vulkaninfo and the vulkan mesa layer are required to use the Vulkan Render Selector."
            }
        ]
    
    @staticmethod
    def create_welcome_tab():
        """
        Creates and returns the welcome tab widget with information sections.
        """
        welcome_tab = QWidget()
        main_layout = QVBoxLayout(welcome_tab)
        main_layout.setContentsMargins(9, 0, 9, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 0)
        
        sections = WelcomeManager._get_welcome_sections()
        for section in sections:
            container = WelcomeManager._create_section_container(section)
            scroll_layout.addWidget(container)
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        return welcome_tab, {}
    
    @staticmethod
    def _create_section_container(section_info):
        """
        Creates a container widget for an individual welcome section.
        """
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 10, 15, 10)
        container_layout.setSpacing(5)
        
        title_label = QLabel(section_info["title"])
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        container_layout.addWidget(title_label)
        
        desc_label = QLabel(section_info["description"])
        desc_label.setAlignment(Qt.AlignLeft)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #E0E0E0; font-size: 13px; line-height: 1.4;")
        desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        container_layout.addWidget(desc_label)
        
        return container

    @staticmethod
    def create_welcome_window(main_window):
        """
        Creates a separate welcome window with the welcome content.
        """
        welcome_window = QMainWindow()
        welcome_window.setWindowTitle("volt-gui - Welcome")
        welcome_window.setMinimumSize(600, 500)
        welcome_window.setAttribute(Qt.WA_DeleteOnClose, False)
        welcome_tab, _ = WelcomeManager.create_welcome_tab()
        welcome_window.setCentralWidget(welcome_tab)
        
        return welcome_window