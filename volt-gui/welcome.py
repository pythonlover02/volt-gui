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
                ("text", "Every setting in this application is written to a profile file at ~/.config/volt-gui/. The volt Vulkan layer reads that profile when a game starts and rewrites the Vulkan calls the game makes: samplers for texture filtering and mip selection, the swapchain for vsync, image count and compositing, the surface format list for color depth, color space and transfer function, device enumeration for GPU selection, presents for the frame limiter, and pipelines for the rendering toggles."),
                ("text", "Settings are read once when a game starts and never change while it runs. Press Apply, then start the game again. The preview window restarts on Apply so the lists here stay in step."),
            ),
            "What it Will Not Do": (
                ("text", "volt only changes what the game asks Vulkan for. It never draws anything itself, so sharpening, upscaling, frame generation, forced MSAA and overlays are all out of scope. Use MangoHud for an overlay and LACT for clocks and fan curves, or CoreCtrl if you also want CPU controls."),
                ("text", "It also never turns anything on that the game left off. volt enables no device feature and no extension. Where a setting needs a feature, volt reads what the game asked for and applies the setting only if the game enabled it: that is how Anisotropic Filtering and Sample Shading work, and where the game left the feature clear the setting is ignored and a line is logged. A setting that cannot be reached that way at all stays out, which keeps wireframe, line width, depth clamp, alpha to one and cubic filtering off the table. Where a game moves state onto an extension path, volt follows it there: a hook for an extension the game never enabled is simply unreachable."),
            )
        },
        "Settings": {
            "One Value Per Setting": (
                ("text", "Every setting is a single choice: the value volt forces, or default, which means volt does not touch what the game asked for. There is no range, no ordering between values, and nothing to get backwards."),
                ("text", "A value volt has no name for still appears in the list, still saves to a profile, and still applies, exactly like a named one."),
                ("text", "Where the specification admits only what a query returned, a value your device did not report is not forced. volt keeps the game's own value and logs a warning, so a profile written on another machine never makes a call invalid."),
                ("text", "Where the specification bounds a value, LOD bias against your device limit and image count against what the surface allows, volt clamps what it passes down. That clamp is correctness rather than a choice, so it is not shown here."),
            ),
            "Where the Lists Come From": (
                ("text", "Most of the boxes are filled in from your own hardware rather than from a list built into volt-gui. Present modes, colour depths, colour spaces, transfer functions and alpha modes come from what the surface reports, the GPU list comes from what the driver enumerates, and mip levels and LOD bias run up to the limits your device gives. A card without the feature behind it holds nothing but default, and so does every device backed card until the probe has run: volt-gui offers no option it has not read."),
                ("text", "That means a mode or a format volt has never heard of shows up as soon as your driver supports it. It also means a profile written on another machine can name something this one cannot do, in which case that setting resets to default and volt-gui tells you which ones."),
                ("text", "The four Framerate settings are the exception. A game never tells Vulkan what frame rate it wants, so there is nothing to read from the device and their lists are volt's own."),
            ),
            "The Frame Limiter": (
                ("text", "Frame Limit caps the rate at present time. Offset shifts that cap, Method sets when the limiter waits, Pacing sets how, and none of the three does anything until Limit is set."),
                ("text", "Offset is there for variable refresh displays, which want the cap sitting just under refresh. Pick 144, set the offset to -6, and you land on 138. volt does not read your refresh rate and never shifts a cap by itself, since most displays are not VRR."),
                ("text", "Pacing runs from cheapest to tightest. sleep hands the whole wait to the kernel and costs nothing. sliced sleeps in short steps and rechecks the clock, which corrects for the kernel waking late. precise sleeps most of the interval then busy waits half a millisecond. spin busy waits the whole interval, the steadiest of the four and the only one that keeps a core awake."),
            ),
            "Settings That Hide a List": (
                ("text", "Color Depth, Color Space, Transfer Function, Present Mode and Physical Device work differently. Instead of changing a value they hide entries from the list the game is shown, so a game that takes the first surface format or the first device gets the one you picked. The three format settings filter one list one after the other, each restoring it on its own if nothing survives."),
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
            "The Probe Window": (
                ("text", "volt-gui keeps a small vkgears window running under the profile you are editing. It is what fills the setting lists with your hardware. Pressing Apply restarts it so those lists match the values you just saved, and switching profiles restarts it too."),
                ("text", "It is not a preview. Most settings act on textures, samplers and pipelines vkgears does not have, so anisotropic filtering, LOD bias, mip levels and sample shading look identical in it however you set them. An unchanged window means the probe ran, not that the setting was ignored. Run the game with VOLT_LOG=info to see what actually applied."),
                ("text", "vkgears comes from mesa-demos and volt-gui needs it. Nothing else reads your hardware, so without it every device backed card holds nothing but default, and volt-gui tells you it could not probe. volt-gui invents no options: a list it cannot read is a list it does not offer. Close the window whenever you like once it has run, and volt-gui carries on with what it learned."),
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
                ("text", "Presets fill the profile you have open with a starting point, arranged as a ladder from best looking to fastest:\n\n- Quality: trilinear filtering, blended mips, a slight sharpening bias, every mip level allowed, smoothed cutout edges, classic vsync, a 4 image swapchain, 10 bit colour where the surface has it, and precise pacing on an early wait.\n- Balanced: trilinear and blended mips still, mailbox present for vsync without the latency, sliced pacing.\n- Performance FPS: bilinear, a blurring bias, mailbox present, the swapchain held to 4 images, colour held to 8 bit and the cheaper sleep pacing.\n- Performance Low Latency: the same, aimed at input lag instead, with immediate present, a 2 image swapchain, a late wait and spin pacing, the steadiest of the four.\n- Potato FPS: bilinear, hard mip cuts, a full step of blurring bias, the top two mips off the table, cutout smoothing off.\n- Potato Low Latency: the same again with immediate present, a 2 image swapchain and a late wait.\n\nNo preset touches Colour Space, Transfer Function, Composite Alpha or Clipped Presentation: those depend on your display and your compositor, so they stay yours."),
                ("text", "Applying a preset replaces every value in the profile after a confirmation, so anything the preset does not set goes back to default. That includes the frame limit: the right cap depends on your display, so that choice stays yours."),
                ("text", "A preset can name something your hardware does not offer, mailbox on a surface without it for instance. That setting resets to default and volt-gui says which ones, so the rest of the preset still lands."),
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
