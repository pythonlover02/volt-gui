pub(crate) const LAYER_NAME: &str = "VK_LAYER_VOLT_settings";
pub(crate) const LAYER_DESC: &str = "Driver style Vulkan settings layer for Linux.";

pub(crate) const ENABLE_VALUE: &str = "1";
pub(crate) const DEFAULT_PROFILE: &str = "default";
pub(crate) const RESERVED_PROFILES: [&str; 2] = ["probe", "options"];
pub(crate) const EXIT_EXEC_FAILED: i32 = 127;
pub(crate) const EXIT_USAGE: i32 = 1;
pub(crate) const EXIT_OK: i32 = 0;

pub(crate) const ENV_CONFIG_NAME: &str = "VOLT_CONFIG_NAME";
pub(crate) const ENV_LOG: &str = "VOLT_LOG";
pub(crate) const ENV_ENABLE: &str = "VOLT_ENABLE";
pub(crate) const ENV_PROBE: &str = "VOLT_PROBE";
pub(crate) const ENV_HOME: &str = "HOME";
pub(crate) const ENV_LIB_PATH: &str = "LD_LIBRARY_PATH";

pub(crate) const HOME_FALLBACK: &str = "/tmp";
pub(crate) const HOME_UNSET_WARN: &str = "HOME is unset, reading profiles from /tmp instead";
pub(crate) const USER_LIB_REL: &str = ".local/lib/volt";
pub(crate) const LIB_DIR_64: &str = "x86_64-linux-gnu";
pub(crate) const LIB_DIR_32: &str = "i386-linux-gnu";
pub(crate) const PATH_SEP: &str = ":";

pub(crate) const PROBE_FLAG: &str = "--probe";
pub(crate) const PROBE_FILE: &str = "probe.toml";
pub(crate) const PROBE_SECTION: &str = "[probe]";
pub(crate) const PROBE_SEP: &str = ";";
pub(crate) const PROBE_ON: &str = "on";
pub(crate) const PROBE_OFF: &str = "off";
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
pub(crate) const ANISO_OFF: f32 = 1.0;
pub(crate) const SHADING_OFF: f32 = 0.0;
pub(crate) const SHADING_MAX: f32 = 1.0;
pub(crate) const LAYER_IFACE_VERSION: u32 = 2;
pub(crate) const LAYER_LINK_INFO: i32 = 0;
pub(crate) const LAYER_DATA_CALLBACK: i32 = 1;

pub(crate) const MODE_COMPATIBILITY_TYPE: u32 = 1000274002;
pub(crate) const LATENCY_CAPABILITIES_TYPE: u32 = 1000505008;
pub(crate) const MODE_LIST_TYPES: [u32; 2] = [
    MODE_COMPATIBILITY_TYPE,
    LATENCY_CAPABILITIES_TYPE,
];

pub(crate) const DEPTH_SUFFIX: &str = "bit";
pub(crate) const PRESENT_UNKNOWN_PREFIX: &str = "present mode ";
pub(crate) const SPACE_UNKNOWN_PREFIX: &str = "color space ";
pub(crate) const ALPHA_UNKNOWN_PREFIX: &str = "composite alpha ";
pub(crate) const FORMAT_UNKNOWN_PREFIX: &str = "format ";

pub(crate) const FILTER_RETRO: u32 = 0;
pub(crate) const FILTER_BILINEAR: u32 = 1;
pub(crate) const FILTER_TRILINEAR: u32 = 2;

pub(crate) const MIPMAP_NEAREST: u32 = 0;
pub(crate) const MIPMAP_LINEAR: u32 = 1;

pub(crate) const TOGGLE_OFF: u32 = 0;
pub(crate) const TOGGLE_ON: u32 = 1;

pub(crate) const SETTINGS_FROZEN_INFO: &str = "settings loaded and frozen for the life of the process";
pub(crate) const ANISO_ABSENT_INFO: &str = "the application did not enable samplerAnisotropy, leaving anisotropic filtering alone";
pub(crate) const SHADING_ABSENT_INFO: &str = "the application did not enable sampleRateShading, leaving sample shading alone";
pub(crate) const PRESENT_MISS_WARN: &str = "the surface does not support the present mode setting, keeping application choice";
pub(crate) const PRESENT_EMPTY_WARN: &str = "present mode selection matched no supported mode, keeping every mode";

pub(crate) const PRESENT_EXTENDED_INFO: &str = "this present mode comes from an extension and only exists where the application enabled it";
pub(crate) const ALPHA_MISS_WARN: &str = "the surface does not support the composite alpha setting, keeping application choice";
pub(crate) const UNOWNED_QUEUE_ERROR: &str = "present on a queue with no registered device";
pub(crate) const UNOWNED_BUFFER_ERROR: &str = "alpha to coverage on a command buffer with no registered device";

pub(crate) const GPU_EMPTY_WARN: &str = "gpu selection matched no device, keeping every device";
pub(crate) const GROUP_EMPTY_WARN: &str = "gpu selection matched no device group, keeping every group";
pub(crate) const DEPTH_EMPTY_WARN: &str = "color depth selection matched no surface format, keeping every format";
pub(crate) const SPACE_EMPTY_WARN: &str = "color space selection matched no surface format, keeping every format";
pub(crate) const TRANSFER_EMPTY_WARN: &str = "transfer function selection matched no surface format, keeping every format";
pub(crate) const SPACE_EXTENDED_INFO: &str = "this color space comes from a swapchain colorspace extension and only exists where the stack enabled it";
pub(crate) const ALPHA_OPAQUE_INFO: &str = "opaque composite alpha skips compositor blending";
pub(crate) const TRANSFER_ENCODED_INFO: &str = "this transfer function leaves the encoding curve to the display hardware";
pub(crate) const TRANSFER_SHADER_INFO: &str = "this transfer function leaves the encoding curve to whatever the application does in its own shaders";
pub(crate) const FORMAT_FORCED_WARN: &str = "the application asked for a color depth the settings exclude, leaving it alone: it may have allocated resources to match";
pub(crate) const SPACE_FORCED_WARN: &str = "the application asked for a color space the settings exclude, leaving it alone: it may have allocated resources to match";
pub(crate) const TRANSFER_FORCED_WARN: &str = "the application asked for a transfer function the settings exclude, leaving it alone: it may have allocated resources to match";

pub(crate) const NULL_OK: [&str; 4] = [
    "vkCreateInstance",
    "vkEnumerateInstanceVersion",
    "vkEnumerateInstanceExtensionProperties",
    "vkEnumerateInstanceLayerProperties",
];

pub(crate) const USAGE: &str = "usage: volt [--probe] [PROFILE] -- COMMAND [ARGS...]\n  volt -- CMD               run CMD with the default profile (~/.config/volt-gui/default.toml)\n  volt NAME -- CMD          run CMD with profile ~/.config/volt-gui/NAME.toml\n  volt --probe NAME -- CMD  the same, and record what this device supports\n\nsettings are read once when the application starts and never change while it\nruns: edit the profile, then start the application again\n";

pub(crate) const FN_PRESENT_RECTANGLES: &str = "vkGetPhysicalDevicePresentRectanglesKHR";

pub(crate) const FN_CREATE_SWAPCHAIN: &str = "vkCreateSwapchainKHR";
pub(crate) const FN_DESTROY_SWAPCHAIN: &str = "vkDestroySwapchainKHR";
pub(crate) const FN_QUEUE_PRESENT: &str = "vkQueuePresentKHR";
pub(crate) const FN_DEVICE_QUEUE_2: &str = "vkGetDeviceQueue2";

pub(crate) const FN_SURFACE_CAPS_2: &str = "vkGetPhysicalDeviceSurfaceCapabilities2KHR";
pub(crate) const FN_SURFACE_FORMATS_2: &str = "vkGetPhysicalDeviceSurfaceFormats2KHR";
pub(crate) const FN_SURFACE_MODES_2: &str = "vkGetPhysicalDeviceSurfacePresentModes2EXT";
pub(crate) const FN_DEVICE_GROUPS: &str = "vkEnumeratePhysicalDeviceGroups";
pub(crate) const FN_DEVICE_GROUPS_KHR: &str = "vkEnumeratePhysicalDeviceGroupsKHR";
pub(crate) const FN_SHARED_SWAPCHAINS: &str = "vkCreateSharedSwapchainsKHR";
pub(crate) const FN_WRITE_SAMPLERS: &str = "vkWriteSamplerDescriptorsEXT";
pub(crate) const FN_SET_ALPHA_COVERAGE: &str = "vkCmdSetAlphaToCoverageEnableEXT";

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
# every setting is one value: the value volt forces, or "default", which
# keeps whatever the application asked for. there is no range and no order
#
# a value volt has no name for is written the way the interface shows it,
# and forces exactly like a named one
#
# anisotropy and sample_shading need a device feature the application itself
# enabled. volt never enables one: where the application left the feature
# clear the setting is ignored and a line is logged
#
# a forced value the device did not report is not forced: volt keeps the
# application's own value and logs a warning
#
# settings are read once when the application starts. changing this file has
# no effect on an application that is already running: start it again

[gpu]
device = "default"

[display]
present_mode = "default"
image_count = "default"
color_depth = "default"
color_space = "default"
transfer_function = "default"
composite_alpha = "default"
clipped = "default"

[textures]
filtering = "default"
mipmap_mode = "default"
anisotropy = "default"
lod_bias = "default"
mip_floor = "default"
mip_ceiling = "default"

[rendering]
sample_shading = "default"
alpha_to_coverage = "default"

[framerate]
frame_limit = "default"
frame_limit_method = "default"
frame_pacing = "default"
"#;
