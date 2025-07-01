import webbrowser
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QTabWidget, QSizePolicy, QLabel
from PySide6.QtCore import Qt


class ExtrasManager:
    
    @staticmethod
    def _get_useful_links():
        """
        Returns a list of dictionaries containing useful link information.
        """
        return [
            {"label": "Arch Wiki", "description": "Arch Linux Wiki, might help with extra information even if you dont use Arch.", "url": "https://wiki.archlinux.org/title/Main_page"},
            {"label": "Gentoo Wiki", "description": "Gentoo Linux Wiki, might help with extra information even if you dont use Gentoo.", "url": "https://wiki.gentoo.org/wiki/"},
            {"label": "Lutris Web Game Section", "description": "Lutris game database, might help with install scripts and requirements.", "url": "https://lutris.net/games/"},
            {"label": "ProtonDB", "description": "Community driven compatibility database for Steam games on Linux.", "url": "https://www.protondb.com/"},
            {"label": "Wine Application Database", "description": "Here you can get information on application compatibility with Wine.", "url": "https://appdb.winehq.org/"},
        ]
    
    @staticmethod
    def _get_useful_programs():
        """
        Returns a list of dictionaries containing useful program information.
        """
        return [
            {"label": "Gamemode Github", "description": "Daemon/lib combo for Linux that allows games to request optimizations.", "url": "https://github.com/FeralInteractive/gamemode"},
            {"label": "Mangohud Github", "description": "A Vulkan and OpenGL overlay for monitoring FPS, temperatures, etc.", "url": "https://github.com/flightlessmango/MangoHud"},
            {"label": "SCX Github", "description": "Linux kernel feature for implementing thread schedulers in BPF.", "url": "https://github.com/sched-ext/scx"},
            {"label": "ProtonPlus Github", "description": "A modern compatibility tools manager for Linux.", "url": "https://github.com/Vysp3r/ProtonPlus"},
            {"label": "ProtonUp-Qt Github", "description": "Install and manage GE-Proton, Luxtorpeda for Steam and Lutris.", "url": "https://github.com/DavidoTek/ProtonUp-Qt"},
            {"label": "Proton Github", "description": "Valve's compatibility layer for running Windows games on Linux.", "url": "https://github.com/ValveSoftware/Proton"},
            {"label": "Proton-GE Github", "description": "Community fork of Proton with additional patches.", "url": "https://github.com/GloriousEggroll/proton-ge-custom"},
            {"label": "Proton-Sarek Github", "description": "Proton fork with improvements for older PCs.", "url": "https://github.com/ValveSoftware/Proton/tree/experimental_sarek"},
            {"label": "DXVK Github", "description": "Vulkan-based translation layer for Direct3D 8/9/10/11.", "url": "https://github.com/doitsujin/dxvk"},
            {"label": "DXVK-Sarek Github", "description": "DXVK version for older PCs.", "url": "https://github.com/doitsujin/dxvk/tree/sarek"},
            {"label": "VKD3D Proton Github", "description": "Vulkan translation layer for Direct3D 12, used on Proton.", "url": "https://github.com/HansKristian-Work/vkd3d-proton"},
        ]
    
    @staticmethod
    def create_extras_tab():
        """
        Creates and returns the extras tab widget with subtabs for links and programs.
        """
        extras_tab = QWidget()
        extras_layout = QVBoxLayout(extras_tab)
        extras_layout.setSpacing(10)
        
        extras_subtabs = QTabWidget()
        useful_links_tab = ExtrasManager._create_scrollable_tab(ExtrasManager._get_useful_links())
        useful_programs_tab = ExtrasManager._create_scrollable_tab(ExtrasManager._get_useful_programs())
        
        extras_subtabs.addTab(useful_links_tab, "Useful Links")
        extras_subtabs.addTab(useful_programs_tab, "Useful Programs")
        extras_layout.addWidget(extras_subtabs)
        
        return extras_tab, {}

    @staticmethod
    def _create_scrollable_tab(items):
        """
        Creates a scrollable tab widget containing the provided items.
        """
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        for item in items:
            container = ExtrasManager._create_item_container(item)
            scroll_layout.addWidget(container)
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        return tab
    
    @staticmethod
    def _create_item_container(item_info):
        """
        Creates a container widget for an individual link/program item.
        """
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(5)
        
        title_label = QLabel(item_info["label"])
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        container_layout.addWidget(title_label)
        
        desc_label = QLabel(item_info["description"])
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #999; font-weight: 300;")
        container_layout.addWidget(desc_label)
        
        button = QPushButton("Open")
        button.setMinimumHeight(30)
        button.setMinimumWidth(100)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.clicked.connect(lambda checked, url=item_info["url"]: webbrowser.open(url))
        
        button_container = QWidget()
        button_container_layout = QHBoxLayout(button_container)
        button_container_layout.setContentsMargins(0, 0, 0, 0)
        button_container_layout.addStretch()
        button_container_layout.addWidget(button)
        button_container_layout.addStretch()
        
        container_layout.addWidget(button_container)
        return container