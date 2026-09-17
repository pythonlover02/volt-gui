use ash::vk;

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
pub(crate) const PROBE_TEMP: &str = "probe.toml.new";
pub(crate) const PROBE_SECTION_OPEN: &str = "[";
pub(crate) const PROBE_SECTION_CLOSE: &str = "]";
pub(crate) const PROBE_SEP: &str = ";";
pub(crate) const PROBE_ON: &str = "on";
pub(crate) const PROBE_OFF: &str = "off";
pub(crate) const PROBE_UNSET: &str = "";
pub(crate) const PROBE_WRITE_INFO: &str = "probe written to the config directory";
pub(crate) const PROBE_FAIL_WARN: &str = "probe write failed, the interface keeps its built in lists";

pub(crate) const FLATPAK_CMD: &str = "flatpak";
pub(crate) const FLATPAK_RUN: &str = "run";
pub(crate) const FLATPAK_INJECT: &str = "/usr/lib/extensions/vulkan/volt/bin/volt-flatpak";
pub(crate) const FLATPAK_CONFIG_RO: &str = "--filesystem=xdg-config/volt-gui:ro";
pub(crate) const FLATPAK_CONFIG_RW: &str = "--filesystem=xdg-config/volt-gui";

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
pub(crate) const PACE_WINDOW: u64 = 4;
pub(crate) const PACE_SPIKE_LIMIT: u64 = 4;
pub(crate) const PACE_STEPS: u64 = 4;
pub(crate) const FRAME_LIMIT_MIN: f32 = 1.0;
pub(crate) const FRAME_LIMIT_OFFSET_NONE: f32 = 0.0;
pub(crate) const FRAME_LIMIT_OFFSET_MAX: f32 = 20.0;
pub(crate) const ANISO_OFF: f32 = 1.0;
pub(crate) const SHADING_OFF: f32 = 0.0;
pub(crate) const SHADING_MAX: f32 = 1.0;
pub(crate) const LAYER_IFACE_VERSION: u32 = 2;
pub(crate) const LAYER_LINK_INFO: i32 = 0;
pub(crate) const LAYER_DATA_CALLBACK: i32 = 1;

pub(crate) const DEVICE_GROUP_SIZE: usize = 32;
pub(crate) const DEVICE_GROUP_PROPERTIES_TYPE: u32 = 1000070000;
pub(crate) const DEVICE_GROUP_DEVICE_CREATE_INFO_TYPE: u32 = 1000070001;
pub(crate) const DEVICE_FEATURES_2_TYPE: u32 = 1000059000;
pub(crate) const MODE_COMPATIBILITY_TYPE: u32 = 1000274002;
pub(crate) const LATENCY_CAPABILITIES_TYPE: u32 = 1000505008;
pub(crate) const MODE_LIST_TYPES: [u32; 2] = [
    MODE_COMPATIBILITY_TYPE,
    LATENCY_CAPABILITIES_TYPE,
];

pub(crate) const SHADER_MAPPING_INFO_TYPE: u32 = 1000135006;
pub(crate) const SHADER_GROUPS_TYPE: u32 = 1000277002;

pub(crate) const SOURCE_CONSTANT_OFFSET: i32 = 0;
pub(crate) const SOURCE_PUSH_INDEX: i32 = 1;
pub(crate) const SOURCE_INDIRECT_INDEX: i32 = 2;
pub(crate) const SOURCE_INDIRECT_INDEX_ARRAY: i32 = 3;
pub(crate) const SOURCE_SHADER_RECORD_INDEX: i32 = 8;

pub(crate) const DEVICE_GROUP_SWAPCHAIN_TYPE: u32 = 1000060012;
pub(crate) const IMAGE_COMPRESSION_CONTROL_TYPE: u32 = 1000338001;
pub(crate) const IMAGE_FORMAT_LIST_TYPE: u32 = 1000147000;
pub(crate) const IMAGE_USAGE_FLAGS_2_TYPE: u32 = 1000668002;
pub(crate) const SWAPCHAIN_COUNTER_TYPE: u32 = 1000091003;
pub(crate) const SWAPCHAIN_NATIVE_HDR_TYPE: u32 = 1000213001;
pub(crate) const SWAPCHAIN_LATENCY_TYPE: u32 = 1000505007;
pub(crate) const SWAPCHAIN_PRESENT_BARRIER_TYPE: u32 = 1000292002;
pub(crate) const SWAPCHAIN_PRESENT_SCALING_TYPE: u32 = 1000275004;
pub(crate) const CUSTOM_RESOLVE_TYPE: u32 = 1000628002;
pub(crate) const DEBUG_UTILS_OBJECT_NAME_TYPE: u32 = 1000128000;
pub(crate) const PIPELINE_ROBUSTNESS_TYPE: u32 = 1000068000;
pub(crate) const STAGE_MODULE_IDENTIFIER_TYPE: u32 = 1000462002;
pub(crate) const STAGE_SUBGROUP_SIZE_TYPE: u32 = 1000225001;
pub(crate) const SHADER_MODULE_TYPE: u32 = 16;
pub(crate) const SHADER_MODULE_CACHE_TYPE: u32 = 1000160001;
pub(crate) const VALIDATION_FEATURES_TYPE: u32 = 1000247000;
pub(crate) const ATTACHMENT_SAMPLE_COUNT_TYPE: u32 = 1000044008;
pub(crate) const GRAPHICS_PIPELINE_LIBRARY_TYPE: u32 = 1000320002;
pub(crate) const MULTIVIEW_PER_VIEW_TYPE: u32 = 1000044009;
pub(crate) const PIPELINE_BINARY_INFO_TYPE: u32 = 1000483002;
pub(crate) const PIPELINE_COMPILER_CONTROL_TYPE: u32 = 1000183000;
pub(crate) const PIPELINE_CREATE_FLAGS_2_TYPE: u32 = 1000470005;
pub(crate) const PIPELINE_CREATION_FEEDBACK_TYPE: u32 = 1000192000;
pub(crate) const PIPELINE_DISCARD_RECTANGLE_TYPE: u32 = 1000099001;
pub(crate) const PIPELINE_DENSITY_LAYERED_TYPE: u32 = 1000611002;
pub(crate) const PIPELINE_SHADING_RATE_ENUM_TYPE: u32 = 1000326002;
pub(crate) const PIPELINE_SHADING_RATE_STATE_TYPE: u32 = 1000226001;
pub(crate) const PIPELINE_LIBRARY_TYPE: u32 = 1000290000;
pub(crate) const PIPELINE_RENDERING_TYPE: u32 = 1000044002;
pub(crate) const PIPELINE_REPRESENTATIVE_TYPE: u32 = 1000166001;
pub(crate) const RENDERING_ATTACHMENT_LOCATION_TYPE: u32 = 1000232001;
pub(crate) const RENDERING_INPUT_ATTACHMENT_TYPE: u32 = 1000232002;

pub(crate) const CHAIN_NODE_WARN: &str = "a node in the chain is one this build does not declare, leaving the setting alone";
pub(crate) const SWAPCHAIN_MODE_LIST_TYPE: u32 = 1000275002;
pub(crate) const SURFACE_PRESENT_MODE_TYPE: u32 = 1000274000;
pub(crate) const SURFACE_INFO_2_TYPE: u32 = 1000119000;
pub(crate) const SURFACE_CAPABILITIES_2_TYPE: u32 = 1000119001;
pub(crate) const SWAPCHAIN_PRESENT_MODE_INFO_TYPE: u32 = 1000275003;
pub(crate) const DEVICE_GROUP_PRESENT_INFO_TYPE: u32 = 1000060011;
pub(crate) const DISPLAY_PRESENT_INFO_TYPE: u32 = 1000003000;
pub(crate) const FRAME_BOUNDARY_TYPE: u32 = 1000375001;
pub(crate) const FRAME_BOUNDARY_TENSORS_TYPE: u32 = 1000460023;
pub(crate) const PRESENT_ID_2_TYPE: u32 = 1000479001;
pub(crate) const PRESENT_ID_TYPE: u32 = 1000294000;
pub(crate) const PRESENT_REGIONS_TYPE: u32 = 1000084000;
pub(crate) const PRESENT_TIMES_GOOGLE_TYPE: u32 = 1000092000;
pub(crate) const PRESENT_TIMINGS_TYPE: u32 = 1000208003;
pub(crate) const SET_PRESENT_CONFIG_TYPE: u32 = 1000613000;
pub(crate) const SWAPCHAIN_PRESENT_FENCE_TYPE: u32 = 1000275001;
pub(crate) const EXT_SURFACE_MAINTENANCE_1: &str = "VK_KHR_surface_maintenance1";
pub(crate) const EXT_SURFACE_MAINTENANCE_1_EXT: &str = "VK_EXT_surface_maintenance1";

pub(crate) const PRESENT_UNKNOWN_PREFIX: &str = "present mode ";
pub(crate) const ALPHA_UNKNOWN_PREFIX: &str = "composite alpha ";

pub(crate) const FILTER_NEAREST: i32 = 0;
pub(crate) const FILTER_LINEAR: i32 = 1;

pub(crate) const MIPMAP_NEAREST: i32 = 0;
pub(crate) const MIPMAP_LINEAR: i32 = 1;

pub(crate) const TOGGLE_OFF: vk::Bool32 = vk::FALSE;
pub(crate) const TOGGLE_ON: vk::Bool32 = vk::TRUE;

pub(crate) const TEXT_NEAREST: &str = "nearest";
pub(crate) const TEXT_LINEAR: &str = "linear";
pub(crate) const TEXT_OFF: &str = "off";
pub(crate) const TEXT_ON: &str = "on";
pub(crate) const FILTER_UNKNOWN_PREFIX: &str = "filter ";
pub(crate) const MIPMAP_UNKNOWN_PREFIX: &str = "mipmap mode ";

pub(crate) const CADENCE_FIXED: &str = "fixed";
pub(crate) const CADENCE_SMOOTH: &str = "smooth";
pub(crate) const CADENCE_DYNAMIC: &str = "dynamic";
pub(crate) const METHOD_EARLY: &str = "early";
pub(crate) const METHOD_LATE: &str = "late";
pub(crate) const METHOD_REACTIVE: &str = "reactive";
pub(crate) const PACING_SLEEP: &str = "sleep";
pub(crate) const PACING_SLICED: &str = "sliced";
pub(crate) const PACING_PRECISE: &str = "precise";
pub(crate) const PACING_SPIN: &str = "spin";

pub(crate) const SETTINGS_FROZEN_INFO: &str = "settings loaded and frozen for the life of the process";
pub(crate) const PRESENT_MISS_WARN: &str = "the surface does not support the present mode setting, keeping application choice";
pub(crate) const PRESENT_EMPTY_WARN: &str = "present mode selection matched no supported mode, keeping every mode";

pub(crate) const ALPHA_MISS_WARN: &str = "the surface does not support the composite alpha setting, keeping application choice";
pub(crate) const UNOWNED_QUEUE_ERROR: &str = "present on a queue with no registered device";
pub(crate) const UNOWNED_BUFFER_ERROR: &str = "dynamic state on a command buffer with no registered device";

pub(crate) const GPU_EMPTY_WARN: &str = "gpu selection matched no device, keeping every device";
pub(crate) const GROUP_EMPTY_WARN: &str = "gpu selection matched no device group, keeping every group";
pub(crate) const GPU_MISS_WARN: &str = "gpu selection did not take, the application kept the device it picked";
pub(crate) const ALPHA_OPAQUE_INFO: &str = "opaque composite alpha skips compositor blending";

pub(crate) const REPORT_MARK: &str = ": ";
pub(crate) const REPORT_SEP: &str = ", ";
pub(crate) const REPORT_NOTE: &str = "; ";
pub(crate) const REPORT_ASKED: &str = "asked ";
pub(crate) const REPORT_FORCED: &str = "forced ";
pub(crate) const NOTE_NOT_ENABLED: &str = "the application did not enable ";
pub(crate) const NOTE_NOT_SET: &str = "the profile did not set it";

pub(crate) const FEATURE_ANISOTROPY: &str = "samplerAnisotropy";
pub(crate) const FEATURE_SHADING: &str = "sampleRateShading";
pub(crate) const FEATURE_ALPHA_ONE: &str = "alphaToOne";
pub(crate) const FEATURE_DEPTH_CLAMP: &str = "depthClamp";

pub(crate) const SETTING_GPU: &str = "gpu device";
pub(crate) const SETTING_PRESENT_MODE: &str = "present_mode";
pub(crate) const SETTING_IMAGE_COUNT: &str = "image_count";
pub(crate) const SETTING_COMPOSITE_ALPHA: &str = "composite_alpha";
pub(crate) const SETTING_CLIPPED: &str = "clipped";
pub(crate) const SETTING_MAG_FILTER: &str = "mag_filter";
pub(crate) const SETTING_MIN_FILTER: &str = "min_filter";
pub(crate) const SETTING_MIPMAP_MODE: &str = "mipmap_mode";
pub(crate) const SETTING_ANISOTROPY: &str = "anisotropy";
pub(crate) const SETTING_LOD_BIAS: &str = "lod_bias";
pub(crate) const SETTING_MIP_FLOOR: &str = "mip_floor";
pub(crate) const SETTING_MIP_CEILING: &str = "mip_ceiling";
pub(crate) const SETTING_SAMPLE_SHADING: &str = "sample_shading";
pub(crate) const SETTING_ALPHA_COVERAGE: &str = "alpha_to_coverage";
pub(crate) const SETTING_ALPHA_ONE: &str = "alpha_to_one";
pub(crate) const SETTING_DEPTH_CLAMP: &str = "depth_clamp";
pub(crate) const SETTING_FRAME_LIMIT: &str = "frame_limit";
pub(crate) const SETTING_FRAME_LIMIT_OFFSET: &str = "frame_limit_offset";
pub(crate) const SETTING_FRAME_LIMIT_CADENCE: &str = "frame_limit_cadence";
pub(crate) const SETTING_FRAME_LIMIT_METHOD: &str = "frame_limit_method";
pub(crate) const SETTING_FRAME_PACING: &str = "frame_pacing";

pub(crate) const NULL_OK: [&str; 2] = ["vkGetInstanceProcAddr", "vkCreateInstance"];

pub(crate) const USAGE: &str = "usage: volt [--probe] [PROFILE] -- COMMAND [ARGS...]\n  volt -- CMD               run CMD with the default profile (~/.config/volt-gui/default.toml)\n  volt NAME -- CMD          run CMD with profile ~/.config/volt-gui/NAME.toml\n  volt --probe NAME -- CMD  the same, and record what this device supports\n\nsettings are read once when the application starts and never change while it\nruns: edit the profile, then start the application again\n";

pub(crate) const FN_CREATE_SWAPCHAIN: &str = "vkCreateSwapchainKHR";
pub(crate) const FN_DESTROY_SWAPCHAIN: &str = "vkDestroySwapchainKHR";
pub(crate) const FN_QUEUE_PRESENT: &str = "vkQueuePresentKHR";
pub(crate) const FN_DEVICE_QUEUE_2: &str = "vkGetDeviceQueue2";

pub(crate) const FN_SURFACE_CAPS_2: &str = "vkGetPhysicalDeviceSurfaceCapabilities2KHR";
pub(crate) const FN_DEVICE_GROUPS: &str = "vkEnumeratePhysicalDeviceGroups";
pub(crate) const FN_DEVICE_GROUPS_KHR: &str = "vkEnumeratePhysicalDeviceGroupsKHR";
pub(crate) const FN_SHARED_SWAPCHAINS: &str = "vkCreateSharedSwapchainsKHR";
pub(crate) const FN_WRITE_SAMPLERS: &str = "vkWriteSamplerDescriptorsEXT";
pub(crate) const FN_SET_ALPHA_COVERAGE: &str = "vkCmdSetAlphaToCoverageEnableEXT";
pub(crate) const FN_SET_ALPHA_ONE: &str = "vkCmdSetAlphaToOneEnableEXT";
pub(crate) const FN_SET_DEPTH_CLAMP: &str = "vkCmdSetDepthClampEnableEXT";
pub(crate) const FN_CREATE_XCB_SURFACE: &str = "vkCreateXcbSurfaceKHR";
pub(crate) const FN_CREATE_XLIB_SURFACE: &str = "vkCreateXlibSurfaceKHR";
pub(crate) const FN_CREATE_WAYLAND_SURFACE: &str = "vkCreateWaylandSurfaceKHR";
pub(crate) const FN_DESTROY_SURFACE: &str = "vkDestroySurfaceKHR";
pub(crate) const FN_CREATE_COMPUTE_PIPELINES: &str = "vkCreateComputePipelines";
pub(crate) const FN_CREATE_SHADERS: &str = "vkCreateShadersEXT";
pub(crate) const FN_CREATE_RAY_TRACING_KHR: &str = "vkCreateRayTracingPipelinesKHR";
pub(crate) const FN_CREATE_RAY_TRACING_NV: &str = "vkCreateRayTracingPipelinesNV";
pub(crate) const FN_PIPELINE_INDIRECT_MEMORY: &str = "vkGetPipelineIndirectMemoryRequirementsNV";

pub(crate) const TAG_XCB: &str = "xcb";
pub(crate) const TAG_WAYLAND: &str = "wayland";

pub(crate) const FN_GET_INSTANCE_PROC_ADDR: &str = "vkGetInstanceProcAddr";
pub(crate) const FN_GET_DEVICE_PROC_ADDR: &str = "vkGetDeviceProcAddr";
pub(crate) const FN_CREATE_INSTANCE: &str = "vkCreateInstance";
pub(crate) const FN_DESTROY_INSTANCE: &str = "vkDestroyInstance";
pub(crate) const FN_CREATE_DEVICE: &str = "vkCreateDevice";
pub(crate) const FN_DESTROY_DEVICE: &str = "vkDestroyDevice";
pub(crate) const FN_ENUMERATE_DEVICES: &str = "vkEnumeratePhysicalDevices";
pub(crate) const FN_CREATE_GRAPHICS_PIPELINES: &str = "vkCreateGraphicsPipelines";
pub(crate) const FN_CREATE_SAMPLER: &str = "vkCreateSampler";
pub(crate) const FN_ALLOCATE_COMMAND_BUFFERS: &str = "vkAllocateCommandBuffers";
pub(crate) const FN_FREE_COMMAND_BUFFERS: &str = "vkFreeCommandBuffers";
pub(crate) const FN_DESTROY_COMMAND_POOL: &str = "vkDestroyCommandPool";
pub(crate) const FN_DEVICE_QUEUE: &str = "vkGetDeviceQueue";
pub(crate) const FN_SURFACE_PRESENT_MODES: &str = "vkGetPhysicalDeviceSurfacePresentModesKHR";
pub(crate) const FN_SURFACE_CAPS: &str = "vkGetPhysicalDeviceSurfaceCapabilitiesKHR";

pub(crate) const EXT_SURFACE: &str = "VK_KHR_surface";
pub(crate) const EXT_SWAPCHAIN: &str = "VK_KHR_swapchain";
pub(crate) const EXT_DISPLAY_SWAPCHAIN: &str = "VK_KHR_display_swapchain";
pub(crate) const EXT_DESCRIPTOR_HEAP: &str = "VK_EXT_descriptor_heap";
pub(crate) const EXT_SHADER_OBJECT: &str = "VK_EXT_shader_object";
pub(crate) const EXT_RAY_TRACING_PIPELINE: &str = "VK_KHR_ray_tracing_pipeline";
pub(crate) const EXT_NV_RAY_TRACING: &str = "VK_NV_ray_tracing";
pub(crate) const EXT_NV_GENERATED_COMPUTE: &str = "VK_NV_device_generated_commands_compute";
pub(crate) const EXT_DYNAMIC_STATE_3: &str = "VK_EXT_extended_dynamic_state3";
pub(crate) const EXT_DEVICE_GROUP_CREATION: &str = "VK_KHR_device_group_creation";
pub(crate) const EXT_GET_SURFACE_CAPS_2: &str = "VK_KHR_get_surface_capabilities2";
pub(crate) const EXT_XCB_SURFACE: &str = "VK_KHR_xcb_surface";
pub(crate) const EXT_XLIB_SURFACE: &str = "VK_KHR_xlib_surface";
pub(crate) const EXT_WAYLAND_SURFACE: &str = "VK_KHR_wayland_surface";

pub(crate) enum Provider {
    Version(u32),
    Ext(&'static str),
}

pub(crate) const HOOK_PROVIDERS: &[(&str, Provider)] = &[
    (FN_SURFACE_PRESENT_MODES, Provider::Ext(EXT_SURFACE)),
    (FN_SURFACE_CAPS, Provider::Ext(EXT_SURFACE)),
    (FN_DESTROY_SURFACE, Provider::Ext(EXT_SURFACE)),
    (FN_SURFACE_CAPS_2, Provider::Ext(EXT_GET_SURFACE_CAPS_2)),
    (FN_DEVICE_GROUPS, Provider::Version(vk::API_VERSION_1_1)),
    (FN_DEVICE_GROUPS_KHR, Provider::Ext(EXT_DEVICE_GROUP_CREATION)),
    (FN_CREATE_XCB_SURFACE, Provider::Ext(EXT_XCB_SURFACE)),
    (FN_CREATE_XLIB_SURFACE, Provider::Ext(EXT_XLIB_SURFACE)),
    (FN_CREATE_WAYLAND_SURFACE, Provider::Ext(EXT_WAYLAND_SURFACE)),
    (FN_CREATE_SWAPCHAIN, Provider::Ext(EXT_SWAPCHAIN)),
    (FN_DESTROY_SWAPCHAIN, Provider::Ext(EXT_SWAPCHAIN)),
    (FN_QUEUE_PRESENT, Provider::Ext(EXT_SWAPCHAIN)),
    (FN_DEVICE_QUEUE_2, Provider::Version(vk::API_VERSION_1_1)),
    (FN_SHARED_SWAPCHAINS, Provider::Ext(EXT_DISPLAY_SWAPCHAIN)),
    (FN_WRITE_SAMPLERS, Provider::Ext(EXT_DESCRIPTOR_HEAP)),
    (FN_CREATE_SHADERS, Provider::Ext(EXT_SHADER_OBJECT)),
    (FN_CREATE_RAY_TRACING_KHR, Provider::Ext(EXT_RAY_TRACING_PIPELINE)),
    (FN_CREATE_RAY_TRACING_NV, Provider::Ext(EXT_NV_RAY_TRACING)),
    (FN_PIPELINE_INDIRECT_MEMORY, Provider::Ext(EXT_NV_GENERATED_COMPUTE)),
    (FN_SET_ALPHA_COVERAGE, Provider::Ext(EXT_DYNAMIC_STATE_3)),
    (FN_SET_ALPHA_COVERAGE, Provider::Ext(EXT_SHADER_OBJECT)),
    (FN_SET_ALPHA_ONE, Provider::Ext(EXT_DYNAMIC_STATE_3)),
    (FN_SET_ALPHA_ONE, Provider::Ext(EXT_SHADER_OBJECT)),
    (FN_SET_DEPTH_CLAMP, Provider::Ext(EXT_DYNAMIC_STATE_3)),
    (FN_SET_DEPTH_CLAMP, Provider::Ext(EXT_SHADER_OBJECT)),
];

pub(crate) const CORE_10_DEVICE_HOOKS: [&str; 9] = [
    FN_GET_DEVICE_PROC_ADDR,
    FN_DESTROY_DEVICE,
    FN_CREATE_GRAPHICS_PIPELINES,
    FN_CREATE_COMPUTE_PIPELINES,
    FN_CREATE_SAMPLER,
    FN_ALLOCATE_COMMAND_BUFFERS,
    FN_FREE_COMMAND_BUFFERS,
    FN_DESTROY_COMMAND_POOL,
    FN_DEVICE_QUEUE,
];

pub(crate) const SURFACE_CREATORS: [(&str, &str); 3] = [
    (FN_CREATE_XCB_SURFACE, TAG_XCB),
    (FN_CREATE_XLIB_SURFACE, TAG_XCB),
    (FN_CREATE_WAYLAND_SURFACE, TAG_WAYLAND),
];

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

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum CadenceChoice {
    Fixed,
    Smooth,
    Dynamic,
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
composite_alpha = "default"
clipped = "default"

[textures]
mag_filter = "default"
min_filter = "default"
mipmap_mode = "default"
anisotropy = "default"
lod_bias = "default"
mip_floor = "default"
mip_ceiling = "default"

[rendering]
sample_shading = "default"
alpha_to_coverage = "default"
alpha_to_one = "default"
depth_clamp = "default"

[framerate]
frame_limit = "default"
frame_limit_offset = "default"
frame_limit_cadence = "default"
frame_limit_method = "default"
frame_pacing = "default"
"#;
