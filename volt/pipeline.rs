use std::sync::Arc;

use ash::vk;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::ALPHA_ONE_ABSENT_INFO;
use crate::consts::CLAMP_ABSENT_INFO;
use crate::consts::SHADING_ABSENT_INFO;
use crate::consts::SHADING_OFF;
use crate::consts::TOGGLE_ON;
use crate::consts::UNOWNED_BUFFER_ERROR;
use crate::device::DeviceCaps;
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

fn shading_absent() -> Option<f32> {
    log_at(LogLevel::Info, SHADING_ABSENT_INFO);
    None
}

fn alpha_one_absent() -> Option<u32> {
    log_at(LogLevel::Info, ALPHA_ONE_ABSENT_INFO);
    None
}

fn alpha_one_allowed(choice: Option<u32>, caps: &DeviceCaps) -> Option<u32> {
    match (choice, caps.alpha_to_one) {
        (None, _) => None,
        (Some(value), true) => Some(value),
        (Some(_), false) => alpha_one_absent(),
    }
}

fn clamp_absent() -> Option<u32> {
    log_at(LogLevel::Info, CLAMP_ABSENT_INFO);
    None
}

fn clamp_allowed(choice: Option<u32>, caps: &DeviceCaps) -> Option<u32> {
    match (choice, caps.depth_clamp) {
        (None, _) => None,
        (Some(value), true) => Some(value),
        (Some(_), false) => clamp_absent(),
    }
}

fn shading_allowed(choice: Option<f32>, caps: &DeviceCaps) -> Option<f32> {
    match (choice, caps.sample_rate_shading) {
        (None, _) => None,
        (Some(rate), true) => Some(rate),
        (Some(_), false) => shading_absent(),
    }
}

fn shading_pair(rate: f32) -> (vk::Bool32, f32) {
    match rate > SHADING_OFF {
        true => (vk::TRUE, rate),
        false => (vk::FALSE, SHADING_OFF),
    }
}

fn pick_shading(
    choice: Option<f32>,
    caps: &DeviceCaps,
    original: (vk::Bool32, f32),
) -> (vk::Bool32, f32) {
    match shading_allowed(choice, caps) {
        Some(rate) => shading_pair(rate),
        None => original,
    }
}

fn rebuilt_multisample(
    s: &Settings,
    caps: &DeviceCaps,
    original: &vk::PipelineMultisampleStateCreateInfo,
) -> vk::PipelineMultisampleStateCreateInfo {
    let (shading_enable, shading_rate) = pick_shading(
        s.sample_shading,
        caps,
        (original.sample_shading_enable, original.min_sample_shading),
    );
    vk::PipelineMultisampleStateCreateInfo {
        sample_shading_enable: shading_enable,
        min_sample_shading: shading_rate,
        alpha_to_coverage_enable: pick_coverage(s.alpha_coverage, original.alpha_to_coverage_enable),
        alpha_to_one_enable: pick_coverage(
            alpha_one_allowed(s.alpha_to_one, caps),
            original.alpha_to_one_enable,
        ),
        ..*original
    }
}

fn rebuilt_rasterization(
    s: &Settings,
    caps: &DeviceCaps,
    original: &vk::PipelineRasterizationStateCreateInfo,
) -> vk::PipelineRasterizationStateCreateInfo {
    vk::PipelineRasterizationStateCreateInfo {
        depth_clamp_enable: pick_coverage(
            clamp_allowed(s.depth_clamp, caps),
            original.depth_clamp_enable,
        ),
        ..*original
    }
}

fn patched_rasterization(
    s: &Settings,
    caps: &DeviceCaps,
    p: *const vk::PipelineRasterizationStateCreateInfo,
) -> Option<vk::PipelineRasterizationStateCreateInfo> {
    match p.is_null() {
        true => None,
        false => Some(rebuilt_rasterization(s, caps, unsafe { &*p })),
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
    rasterization: &Option<vk::PipelineRasterizationStateCreateInfo>,
) -> vk::GraphicsPipelineCreateInfo {
    vk::GraphicsPipelineCreateInfo {
        p_multisample_state: state_ptr(multisample, original.p_multisample_state),
        p_rasterization_state: state_ptr(rasterization, original.p_rasterization_state),
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

fn call_forward_alpha_one(dev: &VkDevState, buffer: vk::CommandBuffer, enable: vk::Bool32) {
    match dev.alpha_one_fp {
        Some(fp) => unsafe {
            fp(
                buffer,
                pick_coverage(
                    alpha_one_allowed(ensure_settings().alpha_to_one, &dev.caps),
                    enable,
                ),
            )
        },
        None => (),
    }
}

pub(crate) fn call_set_alpha_one(
    owner: Option<Arc<VkDevState>>,
    buffer: vk::CommandBuffer,
    enable: vk::Bool32,
) {
    match owner {
        Some(d) => call_forward_alpha_one(&d, buffer, enable),
        None => log_at(LogLevel::Error, UNOWNED_BUFFER_ERROR),
    }
}

fn call_forward_clamp(dev: &VkDevState, buffer: vk::CommandBuffer, enable: vk::Bool32) {
    match dev.clamp_fp {
        Some(fp) => unsafe {
            fp(
                buffer,
                pick_coverage(
                    clamp_allowed(ensure_settings().depth_clamp, &dev.caps),
                    enable,
                ),
            )
        },
        None => (),
    }
}

pub(crate) fn call_set_depth_clamp(
    owner: Option<Arc<VkDevState>>,
    buffer: vk::CommandBuffer,
    enable: vk::Bool32,
) {
    match owner {
        Some(d) => call_forward_clamp(&d, buffer, enable),
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
        .map(|ci| patched_multisample(s, &dev.caps, ci.p_multisample_state))
        .collect();
    let rasterizations: Vec<Option<vk::PipelineRasterizationStateCreateInfo>> = originals
        .iter()
        .map(|ci| patched_rasterization(s, &dev.caps, ci.p_rasterization_state))
        .collect();
    let patched: Vec<vk::GraphicsPipelineCreateInfo> = originals
        .iter()
        .zip(multisamples.iter())
        .zip(rasterizations.iter())
        .map(|((ci, m), r)| patched_ci(ci, m, r))
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
