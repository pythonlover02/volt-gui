use std::ffi::CStr;
use std::fs;
use std::path::PathBuf;
use std::sync::Mutex;

use ash::vk;

use crate::config::config_dir;
use crate::consts::PROBE_FAIL_WARN;
use crate::consts::PROBE_FILE;
use crate::consts::PROBE_OFF;
use crate::consts::PROBE_ON;
use crate::consts::PROBE_SECTION;
use crate::consts::PROBE_SECTION_CLOSE;
use crate::consts::PROBE_SECTION_OPEN;
use crate::consts::PROBE_SEP;
use crate::consts::PROBE_TEMP;
use crate::consts::PROBE_WRITE_INFO;
use crate::device::DeviceCaps;
use crate::instance::all_devices;
use crate::instance::device_index;
use crate::instance::VkInstState;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::ranks::alpha_display;
use crate::ranks::present_display;

pub(crate) struct DeviceFacts {
    pub(crate) index: u32,
    pub(crate) names: Vec<String>,
    pub(crate) max_anisotropy: f32,
    pub(crate) max_lod_bias: f32,
    pub(crate) max_lod_level: f32,
    pub(crate) anisotropy: bool,
    pub(crate) shading: bool,
    pub(crate) alpha_one: bool,
    pub(crate) clamp: bool,
}

pub(crate) struct SurfaceFacts {
    pub(crate) present: Vec<String>,
    pub(crate) alphas: Vec<String>,
    pub(crate) min_images: u32,
    pub(crate) max_images: u32,
}

struct ProbeState {
    device: Option<DeviceFacts>,
    surfaces: Vec<(&'static str, SurfaceFacts)>,
}

static STATE: Mutex<Option<ProbeState>> = Mutex::new(None);

fn empty_state() -> ProbeState {
    ProbeState {
        device: None,
        surfaces: Vec::new(),
    }
}

fn unique_sorted(mut values: Vec<u32>) -> Vec<u32> {
    values.sort();
    values.dedup();
    values
}

fn device_features(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
) -> vk::PhysicalDeviceFeatures {
    unsafe { inst.instance.get_physical_device_features(phys) }
}

fn feature_held(flag: vk::Bool32) -> bool {
    flag == vk::TRUE
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

fn present_names(supported: &[vk::PresentModeKHR]) -> Vec<String> {
    unique_sorted(supported.iter().map(|m| m.as_raw() as u32).collect())
        .into_iter()
        .map(present_display)
        .collect()
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

fn flag_text(value: bool) -> &'static str {
    match value {
        true => PROBE_ON,
        false => PROBE_OFF,
    }
}

fn pair(key: &str, value: &str) -> String {
    format!("{} = \"{}\"\n", key, value)
}

fn section_head(tag: &str) -> String {
    format!("{}{}{}\n", PROBE_SECTION_OPEN, tag, PROBE_SECTION_CLOSE)
}

pub(crate) fn build_device(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    caps: &DeviceCaps,
) -> DeviceFacts {
    let all = all_devices(inst);
    let features = device_features(inst, phys);
    DeviceFacts {
        index: device_index(&all, phys),
        names: device_names(inst, &all),
        max_anisotropy: caps.max_anisotropy,
        max_lod_bias: caps.max_lod_bias,
        max_lod_level: caps.max_lod_level,
        anisotropy: feature_held(features.sampler_anisotropy),
        shading: feature_held(features.sample_rate_shading),
        alpha_one: feature_held(features.alpha_to_one),
        clamp: feature_held(features.depth_clamp),
    }
}

pub(crate) fn build_surface(
    supported: &[vk::PresentModeKHR],
    caps: &vk::SurfaceCapabilitiesKHR,
) -> SurfaceFacts {
    SurfaceFacts {
        present: present_names(supported),
        alphas: alpha_names(caps.supported_composite_alpha.as_raw()),
        min_images: caps.min_image_count,
        max_images: caps.max_image_count,
    }
}

fn render_device(d: &DeviceFacts) -> String {
    [
        PROBE_SECTION.to_string(),
        "\n".to_string(),
        pair("device_index", &d.index.to_string()),
        pair("device_names", &joined(&d.names)),
        pair("max_anisotropy", &d.max_anisotropy.to_string()),
        pair("max_lod_bias", &d.max_lod_bias.to_string()),
        pair("max_lod_level", &d.max_lod_level.to_string()),
        pair("sampler_anisotropy", flag_text(d.anisotropy)),
        pair("sample_rate_shading", flag_text(d.shading)),
        pair("alpha_to_one", flag_text(d.alpha_one)),
        pair("depth_clamp", flag_text(d.clamp)),
    ]
    .concat()
}

pub(crate) fn render_surface(tag: &str, s: &SurfaceFacts) -> String {
    [
        section_head(tag),
        pair("present_modes", &joined(&s.present)),
        pair("composite_alphas", &joined(&s.alphas)),
        pair("min_image_count", &s.min_images.to_string()),
        pair("max_image_count", &s.max_images.to_string()),
    ]
    .concat()
}

fn render_sections(state: &ProbeState) -> Vec<String> {
    state
        .device
        .iter()
        .map(render_device)
        .chain(
            state
                .surfaces
                .iter()
                .map(|(tag, facts)| render_surface(tag, facts)),
        )
        .collect()
}

fn render(state: &ProbeState) -> String {
    render_sections(state).join("\n")
}

fn call_unchanged(path: &PathBuf, text: &str) -> bool {
    fs::read_to_string(path)
        .map(|old| old == text)
        .unwrap_or(false)
}

fn call_replace_file(text: &str) {
    let temp = config_dir().join(PROBE_TEMP);
    match fs::write(&temp, text).and_then(|()| fs::rename(&temp, config_dir().join(PROBE_FILE))) {
        Ok(()) => log_at(LogLevel::Info, PROBE_WRITE_INFO),
        Err(_) => log_at(LogLevel::Warn, PROBE_FAIL_WARN),
    }
}

fn call_write_file(text: &str) {
    let _ = fs::create_dir_all(config_dir());
    match call_unchanged(&config_dir().join(PROBE_FILE), text) {
        true => (),
        false => call_replace_file(text),
    }
}

fn placed(
    surfaces: Vec<(&'static str, SurfaceFacts)>,
    tag: &'static str,
    facts: SurfaceFacts,
) -> Vec<(&'static str, SurfaceFacts)> {
    surfaces
        .into_iter()
        .filter(|(name, _)| *name != tag)
        .chain(std::iter::once((tag, facts)))
        .collect()
}

fn call_stored<F>(update: F)
where
    F: FnOnce(ProbeState) -> ProbeState,
{
    match STATE.lock() {
        Ok(mut guard) => {
            let next = update(guard.take().unwrap_or_else(empty_state));
            call_write_file(&render(&next));
            *guard = Some(next);
        }
        Err(_) => (),
    }
}

pub(crate) fn call_record_device(facts: DeviceFacts) {
    call_stored(|state| ProbeState {
        device: Some(facts),
        surfaces: state.surfaces,
    });
}

pub(crate) fn call_record_surface(tag: &'static str, facts: SurfaceFacts) {
    call_stored(|state| ProbeState {
        device: state.device,
        surfaces: placed(state.surfaces, tag, facts),
    });
}
