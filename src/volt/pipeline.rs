use std::ffi::c_void;
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
use crate::consts::SHADER_GROUPS_TYPE;
use crate::consts::SHADING_OFF;
use crate::consts::TEXT_OFF;
use crate::consts::TOGGLE_ON;
use crate::consts::UNOWNED_BUFFER_ERROR;
use crate::device::DeviceCaps;
use crate::device::VkDevState;
use crate::instance::call_relinked_chain;
use crate::instance::chain_find;
use crate::instance::PfnCreateRayTracingKHR;
use crate::instance::PfnCreateRayTracingNV;
use crate::instance::PfnCreateShaders;
use crate::instance::PfnPipelineIndirectMemory;
use crate::instance::Relinked;
use crate::instance::VkGraphicsPipelineShaderGroupsCreateInfoNV;
use crate::instance::VkGraphicsShaderGroupCreateInfoNV;
use crate::instance::VkHandle;
use crate::instance::VkRayTracingPipelineCreateInfoKHR;
use crate::instance::VkRayTracingPipelineCreateInfoNV;
use crate::instance::VkShaderCreateInfoEXT;
use crate::logging::info_wanted;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::report::call_report_value;
use crate::report::feature_note;
use crate::report::number_text;
use crate::report::toggle_text;
use crate::sampler::rebuilt_mapping_chain;
use crate::sampler::rebuilt_stage;
use crate::sampler::rebuilt_stages;
use crate::sampler::ChainRebuild;
use crate::sampler::StageRebuild;
use crate::sampler::StagesRebuild;

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
    asked: &vk::PipelineMultisampleStateCreateInfo<'_>,
    held: &vk::PipelineMultisampleStateCreateInfo<'_>,
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
    asked: &vk::PipelineMultisampleStateCreateInfo<'_>,
    held: &vk::PipelineMultisampleStateCreateInfo<'_>,
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
    original: *const vk::PipelineMultisampleStateCreateInfo<'_>,
    patched: &Option<vk::PipelineMultisampleStateCreateInfo<'_>>,
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
    original: *const vk::PipelineRasterizationStateCreateInfo<'_>,
    patched: &Option<vk::PipelineRasterizationStateCreateInfo<'_>>,
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
    original: &vk::GraphicsPipelineCreateInfo<'_>,
    multisample: &Option<vk::PipelineMultisampleStateCreateInfo<'_>>,
    rasterization: &Option<vk::PipelineRasterizationStateCreateInfo<'_>>,
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
    originals: &[vk::GraphicsPipelineCreateInfo<'_>],
    multisamples: &[Option<vk::PipelineMultisampleStateCreateInfo<'_>>],
    rasterizations: &[Option<vk::PipelineRasterizationStateCreateInfo<'_>>],
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
    originals: &[vk::GraphicsPipelineCreateInfo<'_>],
    multisamples: &[Option<vk::PipelineMultisampleStateCreateInfo<'_>>],
    rasterizations: &[Option<vk::PipelineRasterizationStateCreateInfo<'_>>],
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

fn rebuilt_multisample<'a>(
    s: &Settings,
    caps: &DeviceCaps,
    original: &vk::PipelineMultisampleStateCreateInfo<'a>,
) -> vk::PipelineMultisampleStateCreateInfo<'a> {
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

fn rebuilt_rasterization<'a>(
    s: &Settings,
    caps: &DeviceCaps,
    original: &vk::PipelineRasterizationStateCreateInfo<'a>,
) -> vk::PipelineRasterizationStateCreateInfo<'a> {
    vk::PipelineRasterizationStateCreateInfo {
        depth_clamp_enable: pick_coverage(
            clamp_allowed(s.depth_clamp, caps),
            original.depth_clamp_enable,
        ),
        ..*original
    }
}

fn patched_rasterization<'a>(
    s: &Settings,
    caps: &DeviceCaps,
    p: *const vk::PipelineRasterizationStateCreateInfo<'a>,
) -> Option<vk::PipelineRasterizationStateCreateInfo<'a>> {
    match p.is_null() {
        true => None,
        false => Some(rebuilt_rasterization(s, caps, unsafe { &*p })),
    }
}

fn patched_multisample<'a>(
    s: &Settings,
    caps: &DeviceCaps,
    p: *const vk::PipelineMultisampleStateCreateInfo<'a>,
) -> Option<vk::PipelineMultisampleStateCreateInfo<'a>> {
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

pub(crate) struct GroupsRebuild {
    #[allow(dead_code)]
    each: Vec<Option<StagesRebuild>>,
    #[allow(dead_code)]
    groups: Vec<VkGraphicsShaderGroupCreateInfoNV>,
    #[allow(dead_code)]
    node: Vec<VkGraphicsPipelineShaderGroupsCreateInfoNV>,
    #[allow(dead_code)]
    relink: Relinked,
    head: *const c_void,
}

fn group_list(
    node: *const VkGraphicsPipelineShaderGroupsCreateInfoNV,
) -> Vec<VkGraphicsShaderGroupCreateInfoNV> {
    (0..unsafe { (*node).group_count } as usize)
        .map(|at| unsafe { *(*node).p_groups.add(at) })
        .collect()
}

fn rebuilt_group(
    group: &VkGraphicsShaderGroupCreateInfoNV,
    built: &Option<StagesRebuild>,
) -> VkGraphicsShaderGroupCreateInfoNV {
    match built {
        Some(one) => VkGraphicsShaderGroupCreateInfoNV {
            p_stages: one.stages.as_ptr(),
            ..*group
        },
        None => *group,
    }
}

fn rebuilt_groups_node(
    node: *const VkGraphicsPipelineShaderGroupsCreateInfoNV,
    groups: &[VkGraphicsShaderGroupCreateInfoNV],
) -> VkGraphicsPipelineShaderGroupsCreateInfoNV {
    VkGraphicsPipelineShaderGroupsCreateInfoNV {
        p_groups: groups.as_ptr(),
        ..unsafe { *node }
    }
}

fn linked_groups(
    head: *const c_void,
    node: *const VkGraphicsPipelineShaderGroupsCreateInfoNV,
    each: Vec<Option<StagesRebuild>>,
) -> Option<GroupsRebuild> {
    let groups: Vec<VkGraphicsShaderGroupCreateInfoNV> = group_list(node)
        .iter()
        .zip(each.iter())
        .map(|(group, built)| rebuilt_group(group, built))
        .collect();
    let owned = vec![rebuilt_groups_node(node, &groups)];
    let relink = call_relinked_chain(head, SHADER_GROUPS_TYPE, owned.as_ptr() as *const c_void)?;
    Some(GroupsRebuild {
        head: relink.head,
        each,
        groups,
        node: owned,
        relink,
    })
}

fn built_groups(
    dev: &VkDevState,
    head: *const c_void,
    node: *const VkGraphicsPipelineShaderGroupsCreateInfoNV,
) -> Option<GroupsRebuild> {
    let each: Vec<Option<StagesRebuild>> = group_list(node)
        .iter()
        .map(|group| rebuilt_stages(dev, group.p_stages, group.stage_count))
        .collect();
    match each.iter().any(|one| one.is_some()) {
        true => linked_groups(head, node, each),
        false => None,
    }
}

fn rebuilt_groups(dev: &VkDevState, head: *const c_void) -> Option<GroupsRebuild> {
    built_groups(
        dev,
        head,
        chain_find(head, SHADER_GROUPS_TYPE)? as *const VkGraphicsPipelineShaderGroupsCreateInfoNV,
    )
}

fn stages_ptr<'a>(
    built: &'a Option<StagesRebuild>,
    original: *const vk::PipelineShaderStageCreateInfo<'a>,
) -> *const vk::PipelineShaderStageCreateInfo<'a> {
    match built {
        Some(one) => one.stages.as_ptr().cast(),
        None => original,
    }
}

fn groups_ptr(built: &Option<GroupsRebuild>, original: *const c_void) -> *const c_void {
    match built {
        Some(one) => one.head,
        None => original,
    }
}

fn chain_ptr(built: &Option<ChainRebuild>, original: *const c_void) -> *const c_void {
    match built {
        Some(one) => one.head,
        None => original,
    }
}

fn patched_ci<'a>(
    original: &vk::GraphicsPipelineCreateInfo<'a>,
    multisample: &'a Option<vk::PipelineMultisampleStateCreateInfo<'a>>,
    rasterization: &'a Option<vk::PipelineRasterizationStateCreateInfo<'a>>,
    stages: &'a Option<StagesRebuild>,
    groups: &'a Option<GroupsRebuild>,
) -> vk::GraphicsPipelineCreateInfo<'a> {
    vk::GraphicsPipelineCreateInfo {
        p_multisample_state: state_ptr(multisample, original.p_multisample_state),
        p_rasterization_state: state_ptr(rasterization, original.p_rasterization_state),
        p_stages: stages_ptr(stages, original.p_stages),
        p_next: groups_ptr(groups, original.p_next),
        ..*original
    }
}

fn patched_compute_ci<'a>(
    original: &vk::ComputePipelineCreateInfo<'a>,
    built: &'a Option<StageRebuild>,
) -> vk::ComputePipelineCreateInfo<'a> {
    match built {
        Some(one) => vk::ComputePipelineCreateInfo {
            stage: one.stage,
            ..*original
        },
        None => *original,
    }
}

fn patched_shader_ci(
    original: &VkShaderCreateInfoEXT,
    built: &Option<ChainRebuild>,
) -> VkShaderCreateInfoEXT {
    VkShaderCreateInfoEXT {
        p_next: chain_ptr(built, original.p_next),
        ..*original
    }
}

fn patched_ray_khr_ci(
    original: &VkRayTracingPipelineCreateInfoKHR,
    built: &Option<StagesRebuild>,
) -> VkRayTracingPipelineCreateInfoKHR {
    match built {
        Some(one) => VkRayTracingPipelineCreateInfoKHR {
            p_stages: one.stages.as_ptr(),
            ..*original
        },
        None => *original,
    }
}

fn patched_ray_nv_ci(
    original: &VkRayTracingPipelineCreateInfoNV,
    built: &Option<StagesRebuild>,
) -> VkRayTracingPipelineCreateInfoNV {
    match built {
        Some(one) => VkRayTracingPipelineCreateInfoNV {
            p_stages: one.stages.as_ptr(),
            ..*original
        },
        None => *original,
    }
}

fn stage_of<'a>(
    ci: &'a vk::ComputePipelineCreateInfo<'a>,
) -> *const vk::PipelineShaderStageCreateInfo<'static> {
    (&ci.stage as *const vk::PipelineShaderStageCreateInfo<'a>).cast()
}

pub(crate) fn call_create_compute_pipelines(
    dev: &VkDevState,
    cache: vk::PipelineCache,
    count: u32,
    cis: *const vk::ComputePipelineCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Pipeline,
) -> vk::Result {
    let originals: Vec<vk::ComputePipelineCreateInfo<'_>> =
        unsafe { std::slice::from_raw_parts(cis, count as usize) }.to_vec();
    let stages: Vec<Option<StageRebuild>> = originals
        .iter()
        .map(|ci| rebuilt_stage(dev, stage_of(ci)))
        .collect();
    let patched: Vec<vk::ComputePipelineCreateInfo<'_>> = originals
        .iter()
        .zip(stages.iter())
        .map(|(ci, built)| patched_compute_ci(ci, built))
        .collect();
    unsafe {
        (dev.device.fp_v1_0().create_compute_pipelines)(
            dev.device.handle(),
            cache,
            count,
            patched.as_ptr(),
            alloc,
            out,
        )
    }
}

pub(crate) fn call_create_shaders(
    dev: &VkDevState,
    fp: PfnCreateShaders,
    handle: vk::Device,
    count: u32,
    cis: *const VkShaderCreateInfoEXT,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut VkHandle,
) -> vk::Result {
    let originals: Vec<VkShaderCreateInfoEXT> =
        unsafe { std::slice::from_raw_parts(cis, count as usize) }.to_vec();
    let chains: Vec<Option<ChainRebuild>> = originals
        .iter()
        .map(|ci| rebuilt_mapping_chain(dev, ci.p_next))
        .collect();
    let patched: Vec<VkShaderCreateInfoEXT> = originals
        .iter()
        .zip(chains.iter())
        .map(|(ci, built)| patched_shader_ci(ci, built))
        .collect();
    unsafe { fp(handle, count, patched.as_ptr(), alloc, out) }
}

pub(crate) fn call_create_ray_tracing_khr(
    dev: &VkDevState,
    fp: PfnCreateRayTracingKHR,
    handle: vk::Device,
    deferred: VkHandle,
    cache: vk::PipelineCache,
    count: u32,
    cis: *const VkRayTracingPipelineCreateInfoKHR,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Pipeline,
) -> vk::Result {
    let originals: Vec<VkRayTracingPipelineCreateInfoKHR> =
        unsafe { std::slice::from_raw_parts(cis, count as usize) }.to_vec();
    let stages: Vec<Option<StagesRebuild>> = originals
        .iter()
        .map(|ci| rebuilt_stages(dev, ci.p_stages, ci.stage_count))
        .collect();
    let patched: Vec<VkRayTracingPipelineCreateInfoKHR> = originals
        .iter()
        .zip(stages.iter())
        .map(|(ci, built)| patched_ray_khr_ci(ci, built))
        .collect();
    unsafe { fp(handle, deferred, cache, count, patched.as_ptr(), alloc, out) }
}

pub(crate) fn call_create_ray_tracing_nv(
    dev: &VkDevState,
    fp: PfnCreateRayTracingNV,
    handle: vk::Device,
    cache: vk::PipelineCache,
    count: u32,
    cis: *const VkRayTracingPipelineCreateInfoNV,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Pipeline,
) -> vk::Result {
    let originals: Vec<VkRayTracingPipelineCreateInfoNV> =
        unsafe { std::slice::from_raw_parts(cis, count as usize) }.to_vec();
    let stages: Vec<Option<StagesRebuild>> = originals
        .iter()
        .map(|ci| rebuilt_stages(dev, ci.p_stages, ci.stage_count))
        .collect();
    let patched: Vec<VkRayTracingPipelineCreateInfoNV> = originals
        .iter()
        .zip(stages.iter())
        .map(|(ci, built)| patched_ray_nv_ci(ci, built))
        .collect();
    unsafe { fp(handle, cache, count, patched.as_ptr(), alloc, out) }
}

pub(crate) fn call_pipeline_indirect_memory(
    dev: &VkDevState,
    fp: PfnPipelineIndirectMemory,
    handle: vk::Device,
    ci: *const vk::ComputePipelineCreateInfo<'_>,
    out: *mut c_void,
) {
    let original = unsafe { *ci };
    let built = rebuilt_stage(dev, stage_of(&original));
    unsafe { fp(handle, &patched_compute_ci(&original, &built), out) };
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
    cis: *const vk::GraphicsPipelineCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Pipeline,
) -> vk::Result {
    let s = ensure_settings();
    let originals: Vec<vk::GraphicsPipelineCreateInfo<'_>> =
        unsafe { std::slice::from_raw_parts(cis, count as usize) }.to_vec();
    let multisamples: Vec<Option<vk::PipelineMultisampleStateCreateInfo<'_>>> = originals
        .iter()
        .map(|ci| patched_multisample(s, &dev.caps, ci.p_multisample_state))
        .collect();
    let rasterizations: Vec<Option<vk::PipelineRasterizationStateCreateInfo<'_>>> = originals
        .iter()
        .map(|ci| patched_rasterization(s, &dev.caps, ci.p_rasterization_state))
        .collect();
    call_report_pipelines(dev, s, &originals, &multisamples, &rasterizations);
    let stages: Vec<Option<StagesRebuild>> = originals
        .iter()
        .map(|ci| rebuilt_stages(dev, ci.p_stages.cast(), ci.stage_count))
        .collect();
    let groups: Vec<Option<GroupsRebuild>> = originals
        .iter()
        .map(|ci| rebuilt_groups(dev, ci.p_next))
        .collect();
    let patched: Vec<vk::GraphicsPipelineCreateInfo<'_>> = originals
        .iter()
        .zip(multisamples.iter())
        .zip(rasterizations.iter())
        .zip(stages.iter())
        .zip(groups.iter())
        .map(|((((ci, m), r), t), g)| patched_ci(ci, m, r, t, g))
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
