use std::ffi::CStr;
use std::fs;
use std::sync::Once;

use ash::vk;

use crate::config::config_dir;
use crate::consts::PROBE_FAIL_WARN;
use crate::consts::PROBE_FILE;
use crate::consts::PROBE_SECTION;
use crate::consts::PROBE_SEP;
use crate::consts::PROBE_WRITE_INFO;
use crate::device::VkDevState;
use crate::instance::VkInstState;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::ranks::alpha_display;
use crate::ranks::depth_label;
use crate::ranks::format_semantic;
use crate::ranks::present_display;
use crate::ranks::present_semantic;
use crate::ranks::space_display;
use crate::ranks::space_semantic;
use crate::ranks::transfer_display;
use crate::ranks::transfer_semantic;

static WRITTEN: Once = Once::new();

pub(crate) struct ProbeData {
    pub(crate) index: u32,
    pub(crate) names: Vec<String>,
    pub(crate) present: Vec<String>,
    pub(crate) depths: Vec<String>,
    pub(crate) spaces: Vec<String>,
    pub(crate) transfers: Vec<String>,
    pub(crate) alphas: Vec<String>,
    pub(crate) min_images: u32,
    pub(crate) max_images: u32,
    pub(crate) max_lod_bias: f32,
    pub(crate) max_lod_level: f32,
}

fn sorted_names(mut pairs: Vec<(u32, String)>) -> Vec<String> {
    pairs.sort_by_key(|(rank, _)| *rank);
    pairs.into_iter().map(|(_, name)| name).collect()
}

fn unique_names(names: Vec<String>) -> Vec<String> {
    names.into_iter().fold(Vec::new(), |mut kept, name| {
        match kept.contains(&name) {
            true => kept,
            false => {
                kept.push(name);
                kept
            }
        }
    })
}

fn unique_sorted(mut values: Vec<u32>) -> Vec<u32> {
    values.sort();
    values.dedup();
    values
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
    sorted_names(
        unique_sorted(supported.iter().map(|m| m.as_raw() as u32).collect())
            .into_iter()
            .filter_map(|value| {
                present_semantic(value).map(|facts| (facts.rank, present_display(value)))
            })
            .collect(),
    )
}

fn space_names(formats: &[vk::SurfaceFormatKHR]) -> Vec<String> {
    sorted_names(
        unique_sorted(formats.iter().map(|f| f.color_space.as_raw() as u32).collect())
            .into_iter()
            .filter_map(|value| {
                space_semantic(value).map(|facts| (facts.rank, space_display(value)))
            })
            .collect(),
    )
}

fn depth_names(formats: &[vk::SurfaceFormatKHR]) -> Vec<String> {
    unique_sorted(
        formats
            .iter()
            .filter_map(|f| format_semantic(f.format.as_raw() as u32))
            .map(|facts| facts.depth)
            .collect(),
    )
    .into_iter()
    .map(depth_label)
    .collect()
}

fn transfer_names(formats: &[vk::SurfaceFormatKHR]) -> Vec<String> {
    unique_names(sorted_names(
        formats
            .iter()
            .filter_map(|f| format_semantic(f.format.as_raw() as u32))
            .map(|facts| {
                (transfer_semantic(facts.numeric).rank, transfer_display(facts.numeric))
            })
            .collect(),
    ))
}

fn set_bits(mask: u32) -> Vec<u32> {
    (0..u32::BITS)
        .map(|shift| 1u32 << shift)
        .filter(|bit| mask & *bit != 0)
        .collect()
}

fn alpha_names(mask: u32) -> Vec<String> {
    set_bits(mask).into_iter().map(alpha_display).collect()
}

fn joined(items: &[String]) -> String {
    items.join(PROBE_SEP)
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
        spaces: space_names(formats),
        transfers: transfer_names(formats),
        alphas: alpha_names(caps.supported_composite_alpha.as_raw()),
        min_images: caps.min_image_count,
        max_images: caps.max_image_count,
        max_lod_bias: dev.caps.max_lod_bias,
        max_lod_level: dev.caps.max_lod_level,
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
        pair("color_spaces", &joined(&d.spaces)),
        pair("transfer_functions", &joined(&d.transfers)),
        pair("composite_alphas", &joined(&d.alphas)),
        pair("min_image_count", &d.min_images.to_string()),
        pair("max_image_count", &d.max_images.to_string()),
        pair("max_lod_bias", &d.max_lod_bias.to_string()),
        pair("max_lod_level", &d.max_lod_level.to_string()),
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
