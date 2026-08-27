use std::sync::Arc;

use ash::vk;
use ash::vk::Handle;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::FEATURE_ALPHA_ONE;
use crate::consts::FEATURE_DEPTH_CLAMP;
use crate::consts::FEATURE_SHADING;
use crate::consts::SETTING_ALPHA_COVERAGE;
use crate::consts::SETTING_ALPHA_ONE;
use crate::consts::SETTING_DEPTH_CLAMP;
use crate::consts::SETTING_SAMPLE_SHADING;
use crate::consts::SHADING_OFF;
use crate::consts::TEXT_OFF;
use crate::consts::TOGGLE_ON;
use crate::consts::UNOWNED_BUFFER_ERROR;
use crate::device::DeviceCaps;
use crate::device::VkDevState;
use crate::logging::info_wanted;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::report::call_report_value;
use crate::report::feature_note;
use crate::report::number_text;
use crate::report::toggle_text;

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

fn alpha_one_allowed(choice: Option<u32>, caps: &DeviceCaps) -> Option<u32> {
    match (choice, caps.alpha_to_one) {
        (None, _) => None,
        (Some(value), true) => Some(value),
        (Some(_), false) => None,
    }
}

fn clamp_allowed(choice: Option<u32>, caps: &DeviceCaps) -> Option<u32> {
    match (choice, caps.depth_clamp) {
        (None, _) => None,
        (Some(value), true) => Some(value),
        (Some(_), false) => None,
    }
}

fn shading_allowed(choice: Option<f32>, caps: &DeviceCaps) -> Option<f32> {
    match (choice, caps.sample_rate_shading) {
        (None, _) => None,
        (Some(rate), true) => Some(rate),
        (Some(_), false) => None,
    }
}

fn shading_text(rate: f32) -> String {
    match rate > SHADING_OFF {
        true => number_text(rate),
        false => TEXT_OFF.into(),
    }
}

fn shading_of(enable: vk::Bool32, rate: f32) -> f32 {
    match enable == vk::TRUE {
        true => rate,
        false => SHADING_OFF,
    }
}

fn call_coverage_line(owner: u64, s: &Settings, asked: vk::Bool32, held: vk::Bool32) {
    call_report_value(
        owner,
        SETTING_ALPHA_COVERAGE,
        s.alpha_coverage.is_some(),
        asked,
        held,
        toggle_text,
        None,
    );
}

fn call_alpha_one_line(
    owner: u64,
    s: &Settings,
    caps: &DeviceCaps,
    asked: vk::Bool32,
    held: vk::Bool32,
) {
    call_report_value(
        owner,
        SETTING_ALPHA_ONE,
        s.alpha_to_one.is_some(),
        asked,
        held,
        toggle_text,
        feature_note(s.alpha_to_one.is_some(), caps.alpha_to_one, FEATURE_ALPHA_ONE),
    );
}

fn call_clamp_line(
    owner: u64,
    s: &Settings,
    caps: &DeviceCaps,
    asked: vk::Bool32,
    held: vk::Bool32,
) {
    call_report_value(
        owner,
        SETTING_DEPTH_CLAMP,
        s.depth_clamp.is_some(),
        asked,
        held,
        toggle_text,
        feature_note(
            s.depth_clamp.is_some(),
            caps.depth_clamp,
            FEATURE_DEPTH_CLAMP,
        ),
    );
}

fn call_shading_line(
    owner: u64,
    s: &Settings,
    caps: &DeviceCaps,
    asked: &vk::PipelineMultisampleStateCreateInfo,
    held: &vk::PipelineMultisampleStateCreateInfo,
) {
    call_report_value(
        owner,
        SETTING_SAMPLE_SHADING,
        s.sample_shading.is_some(),
        shading_of(asked.sample_shading_enable, asked.min_sample_shading),
        shading_of(held.sample_shading_enable, held.min_sample_shading),
        shading_text,
        feature_note(
            s.sample_shading.is_some(),
            caps.sample_rate_shading,
            FEATURE_SHADING,
        ),
    );
}

fn call_multisample_lines(
    owner: u64,
    s: &Settings,
    caps: &DeviceCaps,
    asked: &vk::PipelineMultisampleStateCreateInfo,
    held: &vk::PipelineMultisampleStateCreateInfo,
) {
    call_shading_line(owner, s, caps, asked, held);
    call_coverage_line(
        owner,
        s,
        asked.alpha_to_coverage_enable,
        held.alpha_to_coverage_enable,
    );
    call_alpha_one_line(
        owner,
        s,
        caps,
        asked.alpha_to_one_enable,
        held.alpha_to_one_enable,
    );
}

fn call_report_multisample(
    owner: u64,
    s: &Settings,
    caps: &DeviceCaps,
    original: *const vk::PipelineMultisampleStateCreateInfo,
    patched: &Option<vk::PipelineMultisampleStateCreateInfo>,
) {
    match (unsafe { original.as_ref() }, patched) {
        (Some(asked), Some(held)) => call_multisample_lines(owner, s, caps, asked, held),
        (_, _) => (),
    }
}

fn call_report_rasterization(
    owner: u64,
    s: &Settings,
    caps: &DeviceCaps,
    original: *const vk::PipelineRasterizationStateCreateInfo,
    patched: &Option<vk::PipelineRasterizationStateCreateInfo>,
) {
    match (unsafe { original.as_ref() }, patched) {
        (Some(asked), Some(held)) => call_clamp_line(
            owner,
            s,
            caps,
            asked.depth_clamp_enable,
            held.depth_clamp_enable,
        ),
        (_, _) => (),
    }
}

fn call_report_one(
    owner: u64,
    s: &Settings,
    caps: &DeviceCaps,
    original: &vk::GraphicsPipelineCreateInfo,
    multisample: &Option<vk::PipelineMultisampleStateCreateInfo>,
    rasterization: &Option<vk::PipelineRasterizationStateCreateInfo>,
) {
    call_report_multisample(owner, s, caps, original.p_multisample_state, multisample);
    call_report_rasterization(
        owner,
        s,
        caps,
        original.p_rasterization_state,
        rasterization,
    );
}

fn call_report_each(
    dev: &VkDevState,
    s: &Settings,
    originals: &[vk::GraphicsPipelineCreateInfo],
    multisamples: &[Option<vk::PipelineMultisampleStateCreateInfo>],
    rasterizations: &[Option<vk::PipelineRasterizationStateCreateInfo>],
) {
    originals
        .iter()
        .zip(multisamples.iter())
        .zip(rasterizations.iter())
        .for_each(|((ci, m), r)| {
            call_report_one(dev.device.handle().as_raw(), s, &dev.caps, ci, m, r)
        });
}

fn call_report_pipelines(
    dev: &VkDevState,
    s: &Settings,
    originals: &[vk::GraphicsPipelineCreateInfo],
    multisamples: &[Option<vk::PipelineMultisampleStateCreateInfo>],
    rasterizations: &[Option<vk::PipelineRasterizationStateCreateInfo>],
) {
    match info_wanted() {
        true => call_report_each(dev, s, originals, multisamples, rasterizations),
        false => (),
    }
}

fn call_report_coverage(dev: &VkDevState, asked: vk::Bool32, held: vk::Bool32) {
    match info_wanted() {
        true => call_coverage_line(
            dev.device.handle().as_raw(),
            ensure_settings(),
            asked,
            held,
        ),
        false => (),
    }
}

fn call_report_alpha_one(dev: &VkDevState, asked: vk::Bool32, held: vk::Bool32) {
    match info_wanted() {
        true => call_alpha_one_line(
            dev.device.handle().as_raw(),
            ensure_settings(),
            &dev.caps,
            asked,
            held,
        ),
        false => (),
    }
}

fn call_report_clamp(dev: &VkDevState, asked: vk::Bool32, held: vk::Bool32) {
    match info_wanted() {
        true => call_clamp_line(
            dev.device.handle().as_raw(),
            ensure_settings(),
            &dev.caps,
            asked,
            held,
        ),
        false => (),
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
    let held = pick_coverage(ensure_settings().alpha_coverage, enable);
    call_report_coverage(dev, enable, held);
    match dev.alpha_fp {
        Some(fp) => unsafe { fp(buffer, held) },
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
    let held = pick_coverage(
        alpha_one_allowed(ensure_settings().alpha_to_one, &dev.caps),
        enable,
    );
    call_report_alpha_one(dev, enable, held);
    match dev.alpha_one_fp {
        Some(fp) => unsafe { fp(buffer, held) },
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
    let held = pick_coverage(
        clamp_allowed(ensure_settings().depth_clamp, &dev.caps),
        enable,
    );
    call_report_clamp(dev, enable, held);
    match dev.clamp_fp {
        Some(fp) => unsafe { fp(buffer, held) },
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
    call_report_pipelines(dev, s, &originals, &multisamples, &rasterizations);
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
