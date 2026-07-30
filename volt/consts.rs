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

pub(crate) const FLATPAK_CMD: &str = "flatpak";
pub(crate) const FLATPAK_RUN: &str = "run";
pub(crate) const FLATPAK_INJECT: &str = "/usr/lib/extensions/vulkan/volt/bin/volt-flatpak";

pub(crate) const POLL_INTERVAL_MS: i32 = 250;
pub(crate) const INOTIFY_BUF: usize = 4096;
pub(crate) const DEBOUNCE_MS: u64 = 100;

pub(crate) const LOG_FD: i32 = 2;
pub(crate) const LOG_LEVEL_OFF: i32 = 0;
pub(crate) const LOG_LEVEL_ERROR: i32 = 1;
pub(crate) const LOG_LEVEL_WARN: i32 = 2;
pub(crate) const LOG_LEVEL_INFO: i32 = 3;
pub(crate) const DEFAULT_LOG_LEVEL: i32 = 2;

pub(crate) const US_PER_S: f32 = 1_000_000.0;
pub(crate) const FRAME_LIMIT_MIN: f32 = 1.0;
pub(crate) const ANISO_MIN: f32 = 1.0;
pub(crate) const SHADING_MAX: f32 = 1.0;
pub(crate) const LAYER_IFACE_VERSION: u32 = 2;
pub(crate) const LAYER_LINK_INFO: i32 = 0;

pub(crate) const NULL_OK: [&str; 4] = [
    "vkCreateInstance",
    "vkEnumerateInstanceVersion",
    "vkEnumerateInstanceExtensionProperties",
    "vkEnumerateInstanceLayerProperties",
];

pub(crate) const USAGE: &str = "usage: volt [PROFILE] -- COMMAND [ARGS...]\n  volt -- CMD             run CMD with the default profile (~/.config/volt-gui/default.toml)\n  volt NAME -- CMD        run CMD with profile ~/.config/volt-gui/NAME.toml\n";

pub(crate) const FN_PRESENT_RECTANGLES: &str = "vkGetPhysicalDevicePresentRectanglesKHR";

pub(crate) const SECTION_DISPLAY: &str = "display";
pub(crate) const SECTION_TEXTURES: &str = "textures";
pub(crate) const SECTION_ADVANCED: &str = "advanced";

#[derive(Clone, Copy, PartialEq, Eq)]
pub(crate) enum PresentChoice {
    Fifo,
    FifoRelaxed,
    Mailbox,
    Immediate,
}

#[derive(Clone, Copy, PartialEq)]
pub(crate) enum AnisoChoice {
    Off,
    Level(f32),
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub(crate) enum FilterChoice {
    Retro,
    Bilinear,
    Trilinear,
}

#[derive(Clone, Copy, PartialEq)]
pub(crate) enum ShadingChoice {
    Off,
    Rate(f32),
}

pub(crate) const DEFAULT_CONFIG: &str = r#"# volt profile
# every value accepts "default" to keep the application's own choice

[display]
present_mode = "default"
frame_limit = "default"
image_count = "default"
image_count_min = "default"
image_count_max = "default"

[textures]
filtering = "default"
anisotropy = "default"
lod_bias = "default"
lod_bias_min = "default"
lod_bias_max = "default"
lod_min = "default"
lod_max = "default"

[advanced]
wireframe = "default"
sample_shading = "default"
"#;
