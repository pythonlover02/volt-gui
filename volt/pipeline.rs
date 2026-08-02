use ash::vk;

use crate::bounds::bounds_set;
use crate::bounds::resolved;
use crate::bounds::Bounds;
use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::SHADING_OFF;
use crate::consts::TOGGLE_OFF;
use crate::consts::TOGGLE_ON;
use crate::device::DeviceCaps;
use crate::device::VkDevState;

fn toggle_rank(flag: vk::Bool32) -> u32 {
    match flag {
        vk::TRUE => TOGGLE_ON,
        _ => TOGGLE_OFF,
    }
}

fn toggle_vk(rank: u32) -> vk::Bool32 {
    match rank {
        TOGGLE_ON => vk::TRUE,
        _ => vk::FALSE,
    }
}

fn shading_level(enable: vk::Bool32, rate: f32) -> f32 {
    match enable {
        vk::TRUE => rate,
        _ => SHADING_OFF,
    }
}

fn shading_pair(level: f32, caps: &DeviceCaps) -> (vk::Bool32, f32) {
    match level > SHADING_OFF && caps.sample_rate_shading {
        true => (vk::TRUE, level),
        false => (vk::FALSE, level),
    }
}

fn pick_shading(
    b: Bounds<f32>,
    caps: &DeviceCaps,
    original: (vk::Bool32, f32),
) -> (vk::Bool32, f32) {
    match bounds_set(&b) {
        true => shading_pair(resolved(b, shading_level(original.0, original.1)), caps),
        false => original,
    }
}

fn pick_coverage(b: Bounds<u32>, original: vk::Bool32) -> vk::Bool32 {
    match bounds_set(&b) {
        true => toggle_vk(resolved(b, toggle_rank(original))),
        false => original,
    }
}

fn rebuilt_multisample(
    s: &Settings,
    caps: &DeviceCaps,
    original: &vk::PipelineMultisampleStateCreateInfo,
) -> vk::PipelineMultisampleStateCreateInfo {
    let (enable, rate) = pick_shading(
        s.sample_shading,
        caps,
        (original.sample_shading_enable, original.min_sample_shading),
    );
    vk::PipelineMultisampleStateCreateInfo {
        sample_shading_enable: enable,
        min_sample_shading: rate,
        alpha_to_coverage_enable: pick_coverage(s.alpha_coverage, original.alpha_to_coverage_enable),
        ..*original
    }
}

fn patched_multisample(
    s: &Settings,
    caps: &DeviceCaps,
    p: *const vk::PipelineMultisampleStateCreateInfo,
) -> Option<vk::PipelineMultisampleStateCreateInfo> {
    match p.is_null() {
        true => None,
        false => Some(rebuilt_multisample(s, caps, unsafe { &*p })),
    }
}

fn state_ptr<T>(owned: &Option<T>, original: *const T) -> *const T {
    match owned {
        Some(v) => v as *const T,
        None => original,
    }
}

fn patched_ci(
    original: &vk::GraphicsPipelineCreateInfo,
    multisample: &Option<vk::PipelineMultisampleStateCreateInfo>,
) -> vk::GraphicsPipelineCreateInfo {
    vk::GraphicsPipelineCreateInfo {
        p_multisample_state: state_ptr(multisample, original.p_multisample_state),
        ..*original
    }
}

pub(crate) fn call_create_graphics_pipelines(
    dev: &VkDevState,
    cache: vk::PipelineCache,
    count: u32,
    cis: *const vk::GraphicsPipelineCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Pipeline,
) -> vk::Result {
    let s = ensure_settings();
    let originals: Vec<vk::GraphicsPipelineCreateInfo> =
        unsafe { std::slice::from_raw_parts(cis, count as usize) }.to_vec();
    let multisamples: Vec<Option<vk::PipelineMultisampleStateCreateInfo>> = originals
        .iter()
        .map(|ci| patched_multisample(&s, &dev.caps, ci.p_multisample_state))
        .collect();
    let patched: Vec<vk::GraphicsPipelineCreateInfo> = originals
        .iter()
        .zip(multisamples.iter())
        .map(|(ci, m)| patched_ci(ci, m))
        .collect();
    unsafe {
        (dev.device.fp_v1_0().create_graphics_pipelines)(
            dev.device.handle(),
            cache,
            count,
            patched.as_ptr(),
            alloc,
            out,
        )
    }
}
