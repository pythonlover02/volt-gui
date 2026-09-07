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
                ("text", "Every setting in this application is written to a profile file at ~/.config/volt-gui/. The volt Vulkan layer reads that profile when a game starts and rewrites the Vulkan calls the game makes: samplers for texture filtering and mip selection, the swapchain for vsync, image count and compositing, device enumeration for GPU selection, presents for the frame limiter, and pipelines for the rendering toggles."),
                ("text", "Settings are read once when a game starts and never change while it runs. Press Apply, then start the game again. The probe runs again on Apply so the lists here stay in step."),
            ),
            "What it Will Not Do": (
                ("text", "volt only changes what the game asks Vulkan for. It never draws anything itself, so sharpening, upscaling, frame generation, forced MSAA and overlays are all out of scope. Use MangoHud for an overlay and LACT for clocks and fan curves, or CoreCtrl if you also want CPU controls."),
                ("text", "It also never turns anything on that the game left off. volt enables no device feature and no extension. Where a setting needs a feature, volt reads what the game asked for and applies the setting only if the game enabled it: that is how Anisotropic Filtering, Sample Shading, Alpha To One and Depth Clamp work, and where the game left the feature clear the setting is ignored and a line is logged. A setting that cannot be reached that way at all stays out, which keeps line width and cubic filtering off the table, and forced wireframe stays out because it is a wallhack. Where a game moves state onto an extension path, volt follows it there: a hook for an extension the game never enabled is simply unreachable."),
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
                ("text", "Many of the boxes are filled in from your own hardware rather than from a list built into volt-gui. Present modes, image counts and alpha modes come from what the surface reports, the GPU list comes from what the driver enumerates, and anisotropy, mip levels and LOD bias run up to the limits your device gives. A card without the feature behind it holds nothing but default, and so does every device backed card until the probe has run: volt-gui offers no option it has not read."),
                ("text", "That means a present mode volt has never heard of shows up as soon as your driver supports it. It also means a profile written on another machine can name something this one cannot do, in which case that setting resets to default and volt-gui tells you which ones."),
                ("text", "The rest carry fixed lists, because there is nothing to read. Nearest and linear are core Vulkan with no feature and no query behind them, so every driver has both and none of them says so. The Framerate settings have nothing to read at all: a game never tells Vulkan what frame rate it wants, so there is nothing on the device to ask."),
            ),
            "The Three Filter Cards": (
                ("text", "Three sampler fields, three cards. Nothing overrides anything, and every combination is reachable."),
                ("text", "In the order magnification, minification, mipmap:\n\n- retro: nearest, nearest, nearest.\n- bilinear: linear, linear, nearest.\n- trilinear: linear, linear, linear.\n- sharp pixel art without distant shimmer: nearest, linear, linear."),
                ("text", "Magnification is what you see up close. Minification is most of the screen, and where mipmaps and anisotropic filtering do their work. Mipmap Mode is the blend between levels."),
            ),
            "The Frame Limiter": (
                ("text", "Frame Limit caps the rate at present time. Offset shifts that cap, Cadence sets which rate the limiter aims at, Method sets when it waits, Pacing sets how, and none of the four does anything until Limit is set."),
                ("text", "Offset is there for variable refresh displays, which want the cap sitting just under refresh. Pick 144, set the offset to -6, and you land on 138. volt does not read your refresh rate and never shifts a cap by itself, since most displays are not VRR."),
                ("text", "Cadence is the rate the limiter aims at. fixed is your cap and nothing else. smooth paces at the slowest of the last few frames, so the fast frames wait for the slow ones and the cadence comes out even at whatever the machine is holding. dynamic reads exactly what smooth reads and then rounds it down to a quarter step of your cap, so it sits on a set rate rather than following the load. The steps are quarter steps of your cap's frame time, so they sit close together low down and far apart up top: a 60 cap steps 60, 48, 40, 34, 30, while a 240 cap steps 240, 192, 160, 137, 120. Both come from how consoles handle a machine that cannot hold its target, which is picking a rate it can hold and staying there. A console drops resolution to get there and volt cannot touch resolution, so frame handling is the one place the idea fits. A limiter can only make frames later, which is why neither reads the average: a frame slower than the average could never be paced up to it. Both climb back on their own, and neither goes faster than your cap. The trade is frames for evenness: fixed does nothing at all once the machine falls under the cap, so what you get is whatever the machine produced, one frame long and the next short. smooth and dynamic hold the short frames back to match the long ones, which costs you the frames you would have seen and buys you even spacing. dynamic changing step is visible, but it is one change rather than a different frame time every frame. Set fixed if the machine holds the cap, or if you want every frame you can get for the input latency."),
                ("text", "Cadence and Method are separate boxes because they answer different questions, and any pair of them works together. dynamic with late holds a set rate and still reads input as close to display time as it can."),
                ("text", "Pacing runs from cheapest to tightest. sleep hands the whole wait to the kernel and costs nothing. sliced sleeps in short steps and rechecks the clock, which corrects for the kernel waking late. precise sleeps most of the interval then busy waits half a millisecond. spin busy waits the whole interval, the steadiest of the four and the only one that keeps a core awake."),
            ),
            "Every Setting Forces, Bar One": (
                ("text", "volt writes the value you picked into its own copy of the structure that carries it, so a setting lands whether or not the game consulted a query first. That holds for every card here except one."),
                ("text", "Physical Device is the exception, and it is a fact about Vulkan rather than a choice. Nothing names the device a swapchain runs on: the game already holds a physical device by the time volt sees anything it could patch. Hiding the others from enumeration is the only lever there is, so a game that ignores enumeration order keeps the device it picked."),
                ("text", "Where a query governs what is legal, volt filters that too. A present mode must be one the surface reported, so filtering the query means a game picking the first entry it is offered gets the right value without volt overriding anything, and a game that hardcodes gets it at the create call instead. Both halves, one setting."),
                ("text", "A forced value the device did not report is not forced. Where the surface turns down the present mode or the composite alpha you named, volt keeps the game's own value and logs a warning. It never passes down a value that would make the call invalid."),
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
                ("text", "Every setting gets a line, naming the value the game asked for and the value volt wrote in its place. No forced value means volt left that setting alone, either because it is default or because the game already asked for what you picked. The forced value is the one volt wrote, so a setting the device clamped shows what landed rather than what you picked."),
                ("text", "A setting that needs a device feature the game left clear names that feature instead. The Framerate settings have no asked value, since a game never tells Vulkan what frame rate it wants, so they report what volt forced or say the profile did not set them."),
                ("text", "The GPU line reports the device id as `forced N` when you set a gpu, and `asked N` when you don't."),
                ("text", "Each setting prints once per device, so 21 lines at most however many samplers, pipelines or swapchains the game creates."),
            ),
            "The Probe": (
                ("text", "volt-gui runs volt-probe under the profile you are editing. It is what fills the setting lists with your hardware. Pressing Apply runs it again so those lists match the values you just saved, and switching profiles runs it again too."),
                ("text", "It opens a one pixel window that is never mapped, creates a surface, a swapchain and a sampler so the layer sees every path it needs, records what the device reported, and exits. Nothing appears on screen and nothing is drawn."),
                ("text", "It opens an X11 surface, which every desktop has, since a Wayland session runs XWayland. That is not the only surface a game opens: Wine and Proton have native Wayland drivers, and gamescope is its own path again. The profile is written before any of them exists, so volt cannot know which one the game will pick, and reporting two backends would offer you values belonging to the path the game did not take."),
                ("text", "Present modes, image counts and alpha modes are answered against a surface rather than against the card, so your display path bounds them as much as your hardware does, and a short list there is the answer rather than a failure. Those three cards are also the only ones this touches. The lists mostly agree across backends, and where they do not, the layer already handles it: image count is clamped against the surface the game actually opened, and a present mode or alpha mode that surface turns down leaves the game's own value alone with a line in the log. Reading a native Wayland surface directly is on the list for later."),
                ("text", "volt-probe is built by make and installed next to volt and volt-gui, so there is nothing extra to fetch. It links libxcb, which every desktop already carries."),
                ("code", "volt --probe myprofile -- volt-probe", "Run it yourself:"),
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
                ("text", "Presets fill the profile you have open with a starting point, arranged as a ladder from best looking to fastest:\n\n- Quality: trilinear filtering, a slight sharpening bias, every mip level allowed, 16x anisotropy, smoothed cutout edges, classic vsync, a 4 image swapchain, and precise pacing on an early wait.\n- Balanced: trilinear still, mailbox present for vsync without the latency, 8x anisotropy, sliced pacing.\n- Performance FPS: bilinear, a blurring bias, mailbox present, the swapchain held to 4 images and the cheaper sleep pacing.\n- Performance Low Latency: the same, aimed at input lag instead, with immediate present, a 2 image swapchain, a late wait and spin pacing, the steadiest of the four.\n- Potato FPS: bilinear, anisotropy off, a full step of blurring bias, the top two mips off the table, cutout smoothing off.\n- Potato Low Latency: the same again with immediate present, a 2 image swapchain and a late wait.\n\nNo preset touches Composite Alpha or Clipped Presentation: those depend on your compositor, so they stay yours."),
                ("text", "Applying a preset replaces every value in the profile after a confirmation, so anything the preset does not set goes back to default. That includes the frame limit: the right cap depends on your display, so that choice stays yours."),
                ("text", "A preset can name something your hardware does not offer, mailbox on a surface without it for instance. That setting resets to default and volt-gui says which ones, so the rest of the preset still lands."),
                ("text", "The filter presets are also the answer to what the three filter cards should be set to. Quality and Balanced are trilinear, the rest are bilinear with hard mip cuts, and every one of them is spelled out card by card in The Three Filter Cards above."),
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
