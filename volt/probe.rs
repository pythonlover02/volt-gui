use std::ffi::CStr;
use std::fs;
use std::sync::Once;

use ash::vk;

use crate::config::config_dir;
use crate::consts::PROBE_FAIL_WARN;
use crate::consts::PROBE_FILE;
use crate::consts::PROBE_OFF;
use crate::consts::PROBE_ON;
use crate::consts::PROBE_SECTION;
use crate::consts::PROBE_SEP;
use crate::consts::PROBE_WRITE_INFO;
use crate::device::VkDevState;
use crate::instance::VkInstState;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::ranks::depth_label;
use crate::ranks::depth_rank;
use crate::ranks::present_name;
use crate::ranks::present_rank;

static WRITTEN: Once = Once::new();

pub(crate) struct ProbeData {
    pub(crate) index: u32,
    pub(crate) names: Vec<String>,
    pub(crate) present: Vec<String>,
    pub(crate) depths: Vec<String>,
    pub(crate) min_images: u32,
    pub(crate) max_images: u32,
    pub(crate) max_anisotropy: f32,
    pub(crate) max_lod_bias: f32,
    pub(crate) max_lod_level: f32,
    pub(crate) anisotropy: bool,
    pub(crate) shading: bool,
}

fn sorted_pairs(mut pairs: Vec<(u32, String)>) -> Vec<(u32, String)> {
    pairs.sort_by_key(|(rank, _)| *rank);
    pairs
}

fn unique_sorted(mut bits: Vec<u32>) -> Vec<u32> {
    bits.sort();
    bits.dedup();
    bits
}

fn all_devices(inst: &VkInstState) -> Vec<vk::PhysicalDevice> {
    unsafe { inst.instance.enumerate_physical_devices() }.unwrap_or_default()
}

fn device_name(inst: &VkInstState, phys: vk::PhysicalDevice) -> String {
    let props = unsafe { inst.instance.get_physical_device_properties(phys) };
    unsafe { CStr::from_ptr(props.device_name.as_ptr()) }
        .to_string_lossy()
        .to_lowercase()
}

fn device_names(inst: &VkInstState, all: &[vk::PhysicalDevice]) -> Vec<String> {
    all.iter().map(|p| device_name(inst, *p)).collect()
}

fn device_index(all: &[vk::PhysicalDevice], phys: vk::PhysicalDevice) -> u32 {
    all.iter()
        .position(|p| *p == phys)
        .map(|at| at as u32 + 1)
        .unwrap_or(1)
}

fn present_names(supported: &[vk::PresentModeKHR]) -> Vec<String> {
    sorted_pairs(
        supported
            .iter()
            .map(|m| (present_rank(*m), present_name(*m)))
            .collect(),
    )
    .into_iter()
    .map(|(_, name)| name)
    .collect()
}

fn depth_names(formats: &[vk::SurfaceFormatKHR]) -> Vec<String> {
    unique_sorted(
        formats
            .iter()
            .map(depth_rank)
            .filter(|bits| *bits > 0)
            .collect(),
    )
    .into_iter()
    .map(depth_label)
    .collect()
}

fn joined(items: &[String]) -> String {
    items.join(PROBE_SEP)
}

fn flag_text(value: bool) -> &'static str {
    match value {
        true => PROBE_ON,
        false => PROBE_OFF,
    }
}

fn pair(key: &str, value: &str) -> String {
    format!("{} = \"{}\"\n", key, value)
}

pub(crate) fn build_probe(
    inst: &VkInstState,
    dev: &VkDevState,
    supported: &[vk::PresentModeKHR],
    caps: &vk::SurfaceCapabilitiesKHR,
    formats: &[vk::SurfaceFormatKHR],
) -> ProbeData {
    let all = all_devices(inst);
    ProbeData {
        index: device_index(&all, dev.phys),
        names: device_names(inst, &all),
        present: present_names(supported),
        depths: depth_names(formats),
        min_images: caps.min_image_count,
        max_images: caps.max_image_count,
        max_anisotropy: dev.caps.max_anisotropy,
        max_lod_bias: dev.caps.max_lod_bias,
        max_lod_level: dev.caps.max_lod_level,
        anisotropy: dev.caps.sampler_anisotropy,
        shading: dev.caps.sample_rate_shading,
    }
}

fn render(d: &ProbeData) -> String {
    [
        PROBE_SECTION.to_string(),
        "\n".to_string(),
        pair("device_index", &d.index.to_string()),
        pair("device_names", &joined(&d.names)),
        pair("present_modes", &joined(&d.present)),
        pair("color_depths", &joined(&d.depths)),
        pair("min_image_count", &d.min_images.to_string()),
        pair("max_image_count", &d.max_images.to_string()),
        pair("max_anisotropy", &d.max_anisotropy.to_string()),
        pair("max_lod_bias", &d.max_lod_bias.to_string()),
        pair("max_lod_level", &d.max_lod_level.to_string()),
        pair("sampler_anisotropy", flag_text(d.anisotropy)),
        pair("sample_rate_shading", flag_text(d.shading)),
    ]
    .concat()
}

fn call_write_file(text: &str) {
    let _ = fs::create_dir_all(config_dir());
    match fs::write(config_dir().join(PROBE_FILE), text) {
        Ok(()) => log_at(LogLevel::Info, PROBE_WRITE_INFO),
        Err(_) => log_at(LogLevel::Warn, PROBE_FAIL_WARN),
    }
}

pub(crate) fn call_write_probe(d: ProbeData) {
    WRITTEN.call_once(|| call_write_file(&render(&d)));
}
