from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from themes import get_standard_button_height
from themes import get_standard_button_width
from ui import create_simple_sidebar_widget
from ui import create_tab_content_widget


def get_welcome_settings() -> dict:
    return {
        "Welcome": {
            "Welcome to volt gui": (
                ("text", "volt-gui is my AMD Adrenaline / NVIDIA Settings Linux Alternative.\n\nSettings are applied by volt, a Vulkan implicit layer, so they work on every Vulkan driver: RADV, ANV, NVK, AMDVLK, the NVIDIA proprietary driver, and anything else that supports Vulkan 1.0."),
                ("text", "The layer sticks to core Vulkan 1.0 and the swapchain extension, so nothing here behaves differently from one driver to the next."),
            )
        },
        "How it Works": {
            "The volt Layer": (
                ("text", "Every setting in this application is written to a profile file at ~/.config/volt-gui/. The volt Vulkan layer reads that profile when a game starts and rewrites the Vulkan calls the game makes: samplers for texture filtering and mip selection, the swapchain for vsync and image count, the surface format list for color depth, device enumeration for GPU selection, presents for the frame limiter, and pipelines for the rendering toggles."),
                ("text", "The layer watches the profile for changes. Press Apply while a game is running and the new values take effect live, without restarting the game."),
            ),
            "What it Will Not Do": (
                ("text", "volt only changes what the game asks Vulkan for. It never draws anything itself, so sharpening, upscaling, frame generation, forced MSAA and overlays are all out of scope. Use MangoHud for an overlay and CoreCtrl for clocks and fan curves."),
            )
        },
        "Settings": {
            "Force, Minimum and Maximum": (
                ("text", "Most settings have three boxes. Force replaces whatever the game asked for. Minimum and Maximum leave the game's own value alone while it stays inside the range, and pull it back to the nearest end when it does not. Set Force and a bound together and Force wins."),
                ("text", "Use the bounds when you want to rule out the extremes but still let the game pick. On a setting with only two values there is nothing in between, so a Minimum or a Maximum ends up doing the same job as Force."),
                ("text", "A Minimum set above its own Maximum does nothing. Both are dropped, a warning is logged, and the game keeps its own value."),
            ),
            "Where the Lists Come From": (
                ("text", "Most of the boxes are filled in from your own hardware rather than from a list built into volt-gui. Present modes and colour depths come from what the surface reports, the GPU list comes from what the driver enumerates, and anisotropy, mip levels and LOD bias run up to the limits your device gives. A card without the feature behind it holds nothing but default."),
                ("text", "That means a mode or a format volt has never heard of shows up as soon as your driver supports it. It also means a profile written on another machine can name something this one cannot do, in which case that setting resets to default and volt-gui tells you which ones."),
                ("text", "The three Framerate settings are the exception. They are volt's own, so their list is fixed."),
            ),
            "Settings Without Bounds": (
                ("text", "The three Framerate settings have no bounds, because a game never tells Vulkan what frame rate it wants. There is no value to bound, so those three only decide how the layer itself waits, and they share one Frame Limiter card."),
            ),
            "Settings That Hide a List": (
                ("text", "Color Depth and Physical Device work differently. Instead of changing a value they hide entries from the list the game is shown, so a game that takes the first surface format or the first device gets the one you picked."),
                ("text", "If your choice leaves nothing behind, the layer puts the whole list back and logs a warning. The game always has at least one format and one device to work with."),
            )
        },
        "Usage": {
            "Launching Games": (
                ("text", "Prepend the volt launcher to your game command. It activates the layer for that process only and selects the profile:"),
                ("code", "volt -- %command%", "Steam (Launch Options, default profile):"),
                ("code", "volt myprofile -- %command%", "Steam (named profile):"),
                ("code", "volt -- ./game", "Terminal:"),
                ("code", "volt -- flatpak run com.example.Game", "Flatpak:"),
            ),
            "Default Behavior": (
                ("text", "Every setting defaults to \"default\", which means the layer does not touch that value and the application keeps its own choice. A profile with everything on default is a true passthrough."),
            ),
            "Seeing What Applied": (
                ("text", "Run the game from a terminal with VOLT_LOG=info and the layer prints what it applied, what the surface or the device turned down, and when it picked up a changed profile."),
                ("code", "VOLT_LOG=info volt -- ./game", ""),
            ),
            "The Preview Window": (
                ("text", "volt-gui keeps a small vkgears window running under the profile you are editing. It is what fills the setting lists with your hardware, and it doubles as a live look at the profile, since the layer picks up an Apply without a restart. Switching profiles restarts it."),
                ("text", "Close it whenever you like. volt-gui carries on with what it learned the last time it ran, and starts a fresh one when you change profile. If vkgears is not installed the lists fall back to sensible defaults, so nothing breaks."),
                ("code", "volt --probe myprofile -- vkgears", "Run it yourself:"),
            )
        },
        "Profiles": {
            "Profiles": (
                ("text", "Create profiles to switch between configurations per game.\n\n1. Open the profile selector and choose New Profile.\n2. Configure and Apply settings.\n3. Launch the game with that profile name, or switch profiles from the System Tray."),
                ("text", "The launch command shown next to the Apply button always matches the selected profile and can be copied directly into Steam."),
            )
        },
        "Presets": {
            "Presets": (
                ("text", "Presets are curated starting points that populate the currently active profile, arranged as a ladder from maximum fidelity to maximum frames:\n\n- Quality: trilinear filtering, 16x anisotropy, sharpening bias, full sample shading, classic vsync.\n- Balanced: trilinear, 8x anisotropy, mailbox present for low latency vsync.\n- Performance FPS: 4x anisotropy, softer mips, mailbox present, capped swapchain depth.\n- Performance Low Latency: the same stance biased for input latency with immediate present and a 2 image swapchain.\n- Potato FPS and Potato Low Latency: bilinear filtering, anisotropy off, blurrier mips, frames above all."),
                ("text", "Presets mostly set Force values, and use a Maximum where a cap is the point, as with the swapchain image counts. Applying one replaces every value in the profile after a confirmation, so anything the preset does not set goes back to default. That includes the frame limit: the right cap depends on your display, so that choice stays yours."),
            )
        },
        "Options": {
            "Options": (
                ("text", "Changes to Options are saved automatically but only take effect after restarting volt-gui. This includes the theme, scaling, tray behavior, and all other preferences."),
            )
        },
    }


def create_welcome_window_widget() -> QMainWindow:
    window = QMainWindow()
    window.setWindowTitle("volt-gui Welcome")
    window.setMinimumSize(620, 380)
    central_widget = QWidget()
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(8, 8, 8, 8)
    main_layout.setSpacing(8)
    content_layout = QHBoxLayout()
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(0)
    welcome_settings = get_welcome_settings()
    stacked_widget = QStackedWidget()
    for section_data in welcome_settings.values():
        stacked_widget.addWidget(create_tab_content_widget("", section_data)["tab"])
    content_layout.addWidget(create_simple_sidebar_widget(tuple(welcome_settings.keys()), stacked_widget))
    content_layout.addWidget(stacked_widget, 1)
    main_layout.addLayout(content_layout, 1)
    button_container = QWidget()
    button_container.setProperty("buttonContainer", True)
    button_layout = QHBoxLayout(button_container)
    button_layout.setContentsMargins(8, 8, 8, 8)
    button_layout.setSpacing(8)
    button_layout.setAlignment(Qt.AlignVCenter)
    close_button = QPushButton("Close")
    close_button.setFixedSize(get_standard_button_width(), get_standard_button_height())
    close_button.clicked.connect(window.close)
    button_layout.addStretch(1)
    button_layout.addWidget(close_button, 0, Qt.AlignVCenter)
    button_layout.addStretch(1)
    main_layout.addWidget(button_container)
    window.setCentralWidget(central_widget)
    return window
