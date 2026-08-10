pub(crate) const LAYER_NAME: &str = "VK_LAYER_VOLT_settings";
pub(crate) const LAYER_DESC: &str = "Driver style Vulkan settings layer for Linux.";

pub(crate) const ENABLE_VALUE: &str = "1";
pub(crate) const DEFAULT_PROFILE: &str = "default";
pub(crate) const EXIT_EXEC_FAILED: i32 = 127;
pub(crate) const EXIT_USAGE: i32 = 1;
pub(crate) const EXIT_OK: i32 = 0;

pub(crate) const ENV_CONFIG_NAME: &str = "VOLT_CONFIG_NAME";
pub(crate) const ENV_LOG: &str = "VOLT_LOG";
pub(crate) const ENV_ENABLE: &str = "VOLT_ENABLE";
pub(crate) const ENV_PROBE: &str = "VOLT_PROBE";
pub(crate) const ENV_HOME: &str = "HOME";

pub(crate) const HOME_FALLBACK: &str = "/tmp";
pub(crate) const HOME_UNSET_WARN: &str = "HOME is unset, reading profiles from /tmp instead";

pub(crate) const PROBE_FLAG: &str = "--probe";
pub(crate) const PROBE_FILE: &str = "probe.toml";
pub(crate) const PROBE_SECTION: &str = "[probe]";
pub(crate) const PROBE_SEP: &str = ";";
pub(crate) const PROBE_UNSET: &str = "";
pub(crate) const PROBE_WRITE_INFO: &str = "probe written to the config directory";
pub(crate) const PROBE_FAIL_WARN: &str = "probe write failed, the interface keeps its built in lists";

pub(crate) const FLATPAK_CMD: &str = "flatpak";
pub(crate) const FLATPAK_RUN: &str = "run";
pub(crate) const FLATPAK_INJECT: &str = "/usr/lib/extensions/vulkan/volt/bin/volt-flatpak";

pub(crate) const LOG_FD: i32 = 2;
pub(crate) const LOG_LEVEL_OFF: i32 = 0;
pub(crate) const LOG_LEVEL_ERROR: i32 = 1;
pub(crate) const LOG_LEVEL_WARN: i32 = 2;
pub(crate) const LOG_LEVEL_INFO: i32 = 3;
pub(crate) const DEFAULT_LOG_LEVEL: i32 = 2;

pub(crate) const NS_PER_S: f64 = 1_000_000_000.0;
pub(crate) const SPIN_MARGIN_NS: u64 = 500_000;
pub(crate) const SLICE_MARGIN_NS: u64 = 150_000;
pub(crate) const SLICE_STEP_NS: u64 = 1_000_000;
pub(crate) const FRAME_LIMIT_MIN: f32 = 1.0;
pub(crate) const LAYER_IFACE_VERSION: u32 = 2;
pub(crate) const LAYER_LINK_INFO: i32 = 0;

pub(crate) const SUFFIX_MIN: &str = "_min";
pub(crate) const SUFFIX_MAX: &str = "_max";

pub(crate) const PRESENT_ORDER: [&str; 6] = [
    "fifo",
    "fifo_relaxed",
    "mailbox",
    "immediate",
    "shared_demand_refresh",
    "shared_continuous_refresh",
];

pub(crate) const DEPTH_SUFFIX: &str = "bit";
pub(crate) const UNKNOWN_PREFIX: &str = "mode ";
pub(crate) const RED_MARK: char = 'r';

pub(crate) const FILTER_RETRO: u32 = 0;
pub(crate) const FILTER_BILINEAR: u32 = 1;
pub(crate) const FILTER_TRILINEAR: u32 = 2;

pub(crate) const MIPMAP_NEAREST: u32 = 0;
pub(crate) const MIPMAP_LINEAR: u32 = 1;

pub(crate) const TOGGLE_OFF: u32 = 0;
pub(crate) const TOGGLE_ON: u32 = 1;

pub(crate) const SETTINGS_FROZEN_INFO: &str = "settings loaded and frozen for the life of the process";
pub(crate) const PRESENT_MISS_WARN: &str = "no supported present mode matches the setting, keeping application choice";
pub(crate) const UNOWNED_QUEUE_ERROR: &str = "present on a queue with no registered device";

pub(crate) const GPU_EMPTY_WARN: &str = "gpu selection matched no device, keeping every device";
pub(crate) const DEPTH_EMPTY_WARN: &str = "color depth selection matched no surface format, keeping every format";

pub(crate) const NULL_OK: [&str; 4] = [
    "vkCreateInstance",
    "vkEnumerateInstanceVersion",
    "vkEnumerateInstanceExtensionProperties",
    "vkEnumerateInstanceLayerProperties",
];

pub(crate) const USAGE: &str = "usage: volt [--probe] [PROFILE] -- COMMAND [ARGS...]\n  volt -- CMD               run CMD with the default profile (~/.config/volt-gui/default.toml)\n  volt NAME -- CMD          run CMD with profile ~/.config/volt-gui/NAME.toml\n  volt --probe NAME -- CMD  the same, and record what this device supports\n\nsettings are read once when the application starts and never change while it\nruns: edit the profile, then start the application again\n";

pub(crate) const FN_PRESENT_RECTANGLES: &str = "vkGetPhysicalDevicePresentRectanglesKHR";

pub(crate) const SECTION_GPU: &str = "gpu";
pub(crate) const SECTION_DISPLAY: &str = "display";
pub(crate) const SECTION_TEXTURES: &str = "textures";
pub(crate) const SECTION_RENDERING: &str = "rendering";
pub(crate) const SECTION_FRAMERATE: &str = "framerate";

#[derive(Clone, Copy, PartialEq, Eq)]
pub(crate) enum PacingChoice {
    Sleep,
    Sliced,
    Precise,
    Spin,
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub(crate) enum MethodChoice {
    Early,
    Late,
    Reactive,
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub(crate) enum LimitStage {
    Before,
    After,
}

pub(crate) const DEFAULT_CONFIG: &str = r#"# volt profile
# every value accepts "default" to keep the application's own choice
#
# each setting carries three values: the bare key forces a value, the _min and
# _max keys bound the value the application asked for without replacing it.
# a force wins over the bounds when both are set. a minimum above its maximum
# is a mistake: both are ignored and a warning is logged
#
# frame_limit, frame_limit_method and frame_pacing carry no bounds: a game
# never asks vulkan for a frame rate, so there is nothing to bound. they
# configure how the layer itself waits instead
#
# settings are read once when the application starts. changing this file has
# no effect on an application that is already running: start it again

[gpu]
device = "default"
device_min = "default"
device_max = "default"

[display]
present_mode = "default"
present_mode_min = "default"
present_mode_max = "default"
image_count = "default"
image_count_min = "default"
image_count_max = "default"
color_depth = "default"
color_depth_min = "default"
color_depth_max = "default"

[textures]
filtering = "default"
filtering_min = "default"
filtering_max = "default"
mipmap_mode = "default"
mipmap_mode_min = "default"
mipmap_mode_max = "default"
lod_bias = "default"
lod_bias_min = "default"
lod_bias_max = "default"
mip_floor = "default"
mip_floor_min = "default"
mip_floor_max = "default"
mip_ceiling = "default"
mip_ceiling_min = "default"
mip_ceiling_max = "default"

[rendering]
alpha_to_coverage = "default"
alpha_to_coverage_min = "default"
alpha_to_coverage_max = "default"

[framerate]
frame_limit = "default"
frame_limit_method = "default"
frame_pacing = "default"
"#;
