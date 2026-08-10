use std::sync::Arc;

use ash::vk;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::TOGGLE_ON;
use crate::consts::UNOWNED_BUFFER_ERROR;
use crate::device::VkDevState;
use crate::logging::log_at;
use crate::logging::LogLevel;

fn toggle_vk(value: u32) -> vk::Bool32 {
    match value {
        TOGGLE_ON => vk::TRUE,
        _ => vk::FALSE,
    }
}

fn pick_coverage(choice: Option<u32>, original: vk::Bool32) -> vk::Bool32 {
    match choice {
        Some(value) => toggle_vk(value),
        None => original,
    }
}

fn rebuilt_multisample(
    s: &Settings,
    original: &vk::PipelineMultisampleStateCreateInfo,
) -> vk::PipelineMultisampleStateCreateInfo {
    vk::PipelineMultisampleStateCreateInfo {
        alpha_to_coverage_enable: pick_coverage(s.alpha_coverage, original.alpha_to_coverage_enable),
        ..*original
    }
}

fn patched_multisample(
    s: &Settings,
    p: *const vk::PipelineMultisampleStateCreateInfo,
) -> Option<vk::PipelineMultisampleStateCreateInfo> {
    match p.is_null() {
        true => None,
        false => Some(rebuilt_multisample(s, unsafe { &*p })),
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

fn call_forward_coverage(dev: &VkDevState, buffer: vk::CommandBuffer, enable: vk::Bool32) {
    match dev.alpha_fp {
        Some(fp) => unsafe {
            fp(buffer, pick_coverage(ensure_settings().alpha_coverage, enable))
        },
        None => (),
    }
}

pub(crate) fn call_set_alpha_coverage(
    owner: Option<Arc<VkDevState>>,
    buffer: vk::CommandBuffer,
    enable: vk::Bool32,
) {
    match owner {
        Some(d) => call_forward_coverage(&d, buffer, enable),
        None => log_at(LogLevel::Error, UNOWNED_BUFFER_ERROR),
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
        .map(|ci| patched_multisample(s, ci.p_multisample_state))
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
