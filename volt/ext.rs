use std::ffi::c_void;

use ash::vk;

pub(crate) const ST_ANTI_LAG_FEATURES: i32 = 1000476000;
pub(crate) const ST_ANTI_LAG_DATA: i32 = 1000476001;
pub(crate) const ST_LATENCY_SLEEP_MODE_INFO: i32 = 1000505000;
pub(crate) const ST_SWAPCHAIN_LATENCY_CREATE_INFO: i32 = 1000505007;
pub(crate) const ST_SWAP_MAINT_FEATURES: i32 = 1000275000;
pub(crate) const ST_PRESENT_MODES_CREATE_INFO: i32 = 1000275002;
pub(crate) const ST_PRESENT_MODE_INFO: i32 = 1000275003;
pub(crate) const ST_VIEW_MIN_LOD_FEATURES: i32 = 1000391000;
pub(crate) const ST_VIEW_MIN_LOD_CREATE_INFO: i32 = 1000391001;

pub(crate) const ANTI_LAG_MODE_ON: u32 = 1;
pub(crate) const ANTI_LAG_MODE_OFF: u32 = 2;

#[repr(C)]
pub(crate) struct AntiLagFeaturesAmd {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) anti_lag: vk::Bool32,
}

#[repr(C)]
pub(crate) struct AntiLagDataAmd {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) mode: u32,
    pub(crate) max_fps: u32,
    pub(crate) p_presentation_info: *const c_void,
}

#[repr(C)]
pub(crate) struct LatencySleepModeInfoNv {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) low_latency_mode: vk::Bool32,
    pub(crate) low_latency_boost: vk::Bool32,
    pub(crate) minimum_interval_us: u32,
}

#[repr(C)]
pub(crate) struct SwapLatencyCreateInfoNv {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) latency_mode_enable: vk::Bool32,
}

#[repr(C)]
pub(crate) struct SwapMaintFeaturesExt {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) swapchain_maintenance1: vk::Bool32,
}

#[repr(C)]
pub(crate) struct SwapPresentModesCreateInfoExt {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) present_mode_count: u32,
    pub(crate) p_present_modes: *const vk::PresentModeKHR,
}

#[repr(C)]
pub(crate) struct SwapPresentModeInfoExt {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) swapchain_count: u32,
    pub(crate) p_present_modes: *const vk::PresentModeKHR,
}

#[repr(C)]
pub(crate) struct ViewMinLodFeaturesExt {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) min_lod: vk::Bool32,
}

#[repr(C)]
pub(crate) struct ViewMinLodCreateInfoExt {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) min_lod: f32,
}

pub(crate) type PfnAntiLagUpdateAmd = unsafe extern "system" fn(vk::Device, *const AntiLagDataAmd);
pub(crate) type PfnSetLatencySleepModeNv =
    unsafe extern "system" fn(vk::Device, vk::SwapchainKHR, *const LatencySleepModeInfoNv) -> vk::Result;
pub(crate) type PfnSetHdrMetadataExt =
    unsafe extern "system" fn(vk::Device, u32, *const vk::SwapchainKHR, *const vk::HdrMetadataEXT);

pub(crate) fn st(raw: i32) -> vk::StructureType {
    vk::StructureType::from_raw(raw)
}
