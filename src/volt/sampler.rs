use std::ffi::c_void;

use ash::vk;
use ash::vk::Handle;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::ANISO_OFF;
use crate::consts::CHAIN_SAMPLER_LABEL;
use crate::consts::CUBIC_REASON;
use crate::consts::FEATURE_ANISOTROPY;
use crate::consts::FILTER_CUBIC;
use crate::consts::LINEAR_REASON;
use crate::consts::MIP_CROSS_REASON;
use crate::consts::PORTABILITY_REASON;
use crate::consts::SAMPLER_IMAGE_PROCESSING_BIT;
use crate::consts::SAMPLER_SHAPE_REASON;
use crate::consts::SAMPLER_SUBSAMPLED_BIT;
use crate::consts::SAMPLER_YCBCR_CONVERSION_INFO_TYPE;
use crate::consts::SETTING_ANISOTROPY;
use crate::consts::SETTING_LOD_BIAS;
use crate::consts::SETTING_MAG_FILTER;
use crate::consts::SETTING_MIN_FILTER;
use crate::consts::SETTING_MIP_CEILING;
use crate::consts::SETTING_MIP_FLOOR;
use crate::consts::SETTING_MIPMAP_MODE;
use crate::consts::SHADER_MAPPING_INFO_TYPE;
use crate::consts::SOURCE_CONSTANT_OFFSET;
use crate::consts::SOURCE_INDIRECT_INDEX;
use crate::consts::SOURCE_INDIRECT_INDEX_ARRAY;
use crate::consts::SOURCE_PUSH_INDEX;
use crate::consts::SOURCE_SHADER_RECORD_INDEX;
use crate::consts::TEXT_OFF;
use crate::device::DeviceCaps;
use crate::device::VkDevState;
use crate::instance::call_relinked_chain;
use crate::instance::chain_find;
use crate::instance::PfnWriteSamplers;
use crate::instance::Relinked;
use crate::instance::VkDescriptorMappingSourceDataEXT;
use crate::instance::VkDescriptorSetAndBindingMappingEXT;
use crate::instance::VkShaderDescriptorSetAndBindingMappingInfoEXT;
use crate::lists::forced;
use crate::logging::info_wanted;
use crate::report::call_report_reason;
use crate::report::call_report_value;
use crate::report::feature_note;
use crate::report::filter_text;
use crate::report::mipmap_text;
use crate::report::number_text;


fn uses_cubic(original: &vk::SamplerCreateInfo<'_>) -> bool {
    original.mag_filter.as_raw() == FILTER_CUBIC || original.min_filter.as_raw() == FILTER_CUBIC
}

fn aniso_allowed(choice: Option<f32>, caps: &DeviceCaps, cubic: bool) -> Option<f32> {
    match (choice, caps.sampler_anisotropy, cubic) {
        (None, _, _) => None,
        (Some(_), _, true) => None,
        (Some(level), true, false) => Some(level.min(caps.max_anisotropy)),
        (Some(_), false, false) => None,
    }
}

fn aniso_pair(level: f32) -> (vk::Bool32, f32) {
    match level > ANISO_OFF {
        true => (vk::TRUE, level),
        false => (vk::FALSE, ANISO_OFF),
    }
}

fn pick_aniso(
    choice: Option<f32>,
    caps: &DeviceCaps,
    original: &vk::SamplerCreateInfo<'_>,
) -> (vk::Bool32, f32) {
    match aniso_allowed(choice, caps, uses_cubic(original)) {
        Some(level) => aniso_pair(level),
        None => (original.anisotropy_enable, original.max_anisotropy),
    }
}

fn pick_lod_bias(choice: Option<f32>, caps: &DeviceCaps, original: f32) -> f32 {
    match (choice, caps.portability_subset) {
        (Some(value), false) => value.clamp(-caps.max_lod_bias, caps.max_lod_bias),
        (_, _) => original,
    }
}

fn landed(value: f32, held: bool) -> Option<f32> {
    match held {
        true => Some(value),
        false => None,
    }
}

fn landed_floor(choice: Option<f32>, against: f32) -> Option<f32> {
    choice.and_then(|value| landed(value, value <= against))
}

fn landed_ceiling(choice: Option<f32>, against: f32) -> Option<f32> {
    choice.and_then(|value| landed(value, value >= against))
}

fn pick_lod_range(s: &Settings, original: (f32, f32)) -> (f32, f32) {
    let low = forced(
        landed_floor(s.mip_floor, forced(s.mip_ceiling, original.1)),
        original.0,
    );
    let high = forced(landed_ceiling(s.mip_ceiling, low), original.1);
    (low, high)
}

fn already_linear(original: &vk::SamplerCreateInfo<'_>) -> bool {
    original.mag_filter == vk::Filter::LINEAR
        || original.min_filter == vk::Filter::LINEAR
        || original.mipmap_mode == vk::SamplerMipmapMode::LINEAR
}

fn linear_filter_choice(choice: Option<vk::Filter>, linear: bool) -> Option<vk::Filter> {
    match choice {
        Some(value) if value == vk::Filter::LINEAR && !linear => None,
        held => held,
    }
}

fn linear_mipmap_choice(
    choice: Option<vk::SamplerMipmapMode>,
    linear: bool,
) -> Option<vk::SamplerMipmapMode> {
    match choice {
        Some(value) if value == vk::SamplerMipmapMode::LINEAR && !linear => None,
        held => held,
    }
}

fn restricted_shape(original: &vk::SamplerCreateInfo<'_>) -> bool {
    original.flags.as_raw() & SAMPLER_SUBSAMPLED_BIT != 0
        || original.flags.as_raw() & SAMPLER_IMAGE_PROCESSING_BIT != 0
        || original.unnormalized_coordinates == vk::TRUE
}

fn converted_sampler(original: &vk::SamplerCreateInfo<'_>) -> bool {
    chain_find(original.p_next, SAMPLER_YCBCR_CONVERSION_INFO_TYPE).is_some()
}

fn shape_choice<T>(choice: Option<T>, restricted: bool) -> Option<T> {
    match restricted {
        true => None,
        false => choice,
    }
}

fn shaped_range(s: &Settings, restricted: bool, original: (f32, f32)) -> (f32, f32) {
    pick_lod_range(
        &Settings {
            mip_floor: shape_choice(s.mip_floor, restricted),
            mip_ceiling: shape_choice(s.mip_ceiling, restricted),
            ..Default::default()
        },
        original,
    )
}

fn patched_ci<'a>(
    s: &Settings,
    caps: &DeviceCaps,
    original: &vk::SamplerCreateInfo<'a>,
) -> vk::SamplerCreateInfo<'a> {
    let shape = restricted_shape(original);
    let filters = shape || converted_sampler(original);
    let linear = already_linear(original);
    let (aniso_enable, aniso_max) = pick_aniso(
        shape_choice(s.anisotropy, filters),
        caps,
        original,
    );
    let (lod_low, lod_high) = shaped_range(s, shape, (original.min_lod, original.max_lod));
    vk::SamplerCreateInfo {
        mag_filter: forced(
            linear_filter_choice(shape_choice(s.mag_filter, filters), linear),
            original.mag_filter,
        ),
        min_filter: forced(
            linear_filter_choice(shape_choice(s.min_filter, filters), linear),
            original.min_filter,
        ),
        mipmap_mode: forced(
            linear_mipmap_choice(shape_choice(s.mipmap, shape), linear),
            original.mipmap_mode,
        ),
        anisotropy_enable: aniso_enable,
        max_anisotropy: aniso_max,
        mip_lod_bias: pick_lod_bias(s.lod_bias, caps, original.mip_lod_bias),
        min_lod: lod_low,
        max_lod: lod_high,
        ..*original
    }
}

fn aniso_text(level: f32) -> String {
    match level > ANISO_OFF {
        true => number_text(level),
        false => TEXT_OFF.into(),
    }
}

fn aniso_of(enable: vk::Bool32, level: f32) -> f32 {
    match enable == vk::TRUE {
        true => level,
        false => ANISO_OFF,
    }
}

fn call_report_fields(
    owner: u64,
    s: &Settings,
    caps: &DeviceCaps,
    asked: &vk::SamplerCreateInfo<'_>,
    held: &vk::SamplerCreateInfo<'_>,
) {
    call_report_value(
        owner,
        SETTING_MAG_FILTER,
        asked.mag_filter,
        held.mag_filter,
        filter_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_MIN_FILTER,
        asked.min_filter,
        held.min_filter,
        filter_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_MIPMAP_MODE,
        asked.mipmap_mode,
        held.mipmap_mode,
        mipmap_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_ANISOTROPY,
        aniso_of(asked.anisotropy_enable, asked.max_anisotropy),
        aniso_of(held.anisotropy_enable, held.max_anisotropy),
        aniso_text,
        feature_note(
            s.anisotropy.is_some(),
            caps.sampler_anisotropy,
            FEATURE_ANISOTROPY,
        ),
    );
    call_report_value(
        owner,
        SETTING_LOD_BIAS,
        asked.mip_lod_bias,
        held.mip_lod_bias,
        number_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_MIP_FLOOR,
        asked.min_lod,
        held.min_lod,
        number_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_MIP_CEILING,
        asked.max_lod,
        held.max_lod,
        number_text,
        None,
    );
}

fn kept_reason(set: bool, reasons: &[(bool, &'static str)]) -> Option<&'static str> {
    match set {
        true => reasons.iter().find(|entry| entry.0).map(|entry| entry.1),
        false => None,
    }
}

fn filter_dropped(choice: Option<vk::Filter>, linear: bool) -> bool {
    linear_filter_choice(choice, linear) != choice
}

fn mipmap_dropped(choice: Option<vk::SamplerMipmapMode>, linear: bool) -> bool {
    linear_mipmap_choice(choice, linear) != choice
}

fn floor_crossed(s: &Settings, asked: &vk::SamplerCreateInfo<'_>) -> bool {
    landed_floor(s.mip_floor, forced(s.mip_ceiling, asked.max_lod)).is_none()
}

fn ceiling_crossed(s: &Settings, asked: &vk::SamplerCreateInfo<'_>) -> bool {
    landed_ceiling(
        s.mip_ceiling,
        forced(
            landed_floor(s.mip_floor, forced(s.mip_ceiling, asked.max_lod)),
            asked.min_lod,
        ),
    )
    .is_none()
}

fn filter_reason(
    choice: Option<vk::Filter>,
    filters: bool,
    linear: bool,
) -> Option<&'static str> {
    kept_reason(
        choice.is_some(),
        &[
            (filters, SAMPLER_SHAPE_REASON),
            (filter_dropped(choice, linear), LINEAR_REASON),
        ],
    )
}

fn call_report_filter_reasons(s: &Settings, asked: &vk::SamplerCreateInfo<'_>) {
    let shape = restricted_shape(asked);
    let filters = shape || converted_sampler(asked);
    let linear = already_linear(asked);
    call_report_reason(SETTING_MAG_FILTER, filter_reason(s.mag_filter, filters, linear));
    call_report_reason(SETTING_MIN_FILTER, filter_reason(s.min_filter, filters, linear));
    call_report_reason(
        SETTING_MIPMAP_MODE,
        kept_reason(
            s.mipmap.is_some(),
            &[
                (shape, SAMPLER_SHAPE_REASON),
                (mipmap_dropped(s.mipmap, linear), LINEAR_REASON),
            ],
        ),
    );
}

fn call_report_level_reasons(
    s: &Settings,
    caps: &DeviceCaps,
    asked: &vk::SamplerCreateInfo<'_>,
) {
    let shape = restricted_shape(asked);
    call_report_reason(
        SETTING_ANISOTROPY,
        kept_reason(
            s.anisotropy.is_some(),
            &[
                (shape || converted_sampler(asked), SAMPLER_SHAPE_REASON),
                (uses_cubic(asked), CUBIC_REASON),
            ],
        ),
    );
    call_report_reason(
        SETTING_LOD_BIAS,
        kept_reason(
            s.lod_bias.is_some(),
            &[(caps.portability_subset, PORTABILITY_REASON)],
        ),
    );
    call_report_reason(
        SETTING_MIP_FLOOR,
        kept_reason(
            s.mip_floor.is_some(),
            &[
                (shape, SAMPLER_SHAPE_REASON),
                (floor_crossed(s, asked), MIP_CROSS_REASON),
            ],
        ),
    );
    call_report_reason(
        SETTING_MIP_CEILING,
        kept_reason(
            s.mip_ceiling.is_some(),
            &[
                (shape, SAMPLER_SHAPE_REASON),
                (ceiling_crossed(s, asked), MIP_CROSS_REASON),
            ],
        ),
    );
}

fn call_report_one(
    dev: &VkDevState,
    asked: &vk::SamplerCreateInfo<'_>,
    held: &vk::SamplerCreateInfo<'_>,
) {
    call_report_filter_reasons(ensure_settings(), asked);
    call_report_level_reasons(ensure_settings(), &dev.caps, asked);
    call_report_fields(
        dev.device.handle().as_raw(),
        ensure_settings(),
        &dev.caps,
        asked,
        held,
    );
}

fn call_report_sampler(
    dev: &VkDevState,
    asked: &vk::SamplerCreateInfo<'_>,
    held: &vk::SamplerCreateInfo<'_>,
) {
    match info_wanted() {
        true => call_report_one(dev, asked, held),
        false => (),
    }
}

fn call_report_each(
    dev: &VkDevState,
    cis: *const vk::SamplerCreateInfo<'_>,
    count: u32,
    held: &[vk::SamplerCreateInfo<'_>],
) {
    unsafe { std::slice::from_raw_parts(cis, count as usize) }
        .iter()
        .zip(held.iter())
        .for_each(|(asked, one)| call_report_one(dev, asked, one));
}

fn call_report_samplers(
    dev: &VkDevState,
    cis: *const vk::SamplerCreateInfo<'_>,
    count: u32,
    held: &[vk::SamplerCreateInfo<'_>],
) {
    match info_wanted() {
        true => call_report_each(dev, cis, count, held),
        false => (),
    }
}

fn patched_list<'a>(
    s: &Settings,
    caps: &DeviceCaps,
    cis: *const vk::SamplerCreateInfo<'a>,
    count: u32,
) -> Vec<vk::SamplerCreateInfo<'a>> {
    unsafe { std::slice::from_raw_parts(cis, count as usize) }
        .iter()
        .map(|original| patched_ci(s, caps, original))
        .collect()
}

pub(crate) fn call_create_sampler(
    dev: &VkDevState,
    ci: *const vk::SamplerCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Sampler,
) -> vk::Result {
    let patched = patched_ci(ensure_settings(), &dev.caps, unsafe { &*ci });
    call_report_sampler(dev, unsafe { &*ci }, &patched);
    match unsafe { dev.device.create_sampler(&patched, alloc.as_ref()) } {
        Ok(sampler) => {
            unsafe { *out = sampler };
            vk::Result::SUCCESS
        }
        Err(e) => e,
    }
}

pub(crate) struct ChainRebuild {
    #[allow(dead_code)]
    samplers: Vec<Option<vk::SamplerCreateInfo<'static>>>,
    #[allow(dead_code)]
    mappings: Vec<VkDescriptorSetAndBindingMappingEXT>,
    #[allow(dead_code)]
    info: Vec<VkShaderDescriptorSetAndBindingMappingInfoEXT>,
    #[allow(dead_code)]
    relink: Relinked,
    pub(crate) head: *const c_void,
}

pub(crate) struct StageRebuild {
    #[allow(dead_code)]
    chain: ChainRebuild,
    pub(crate) stage: vk::PipelineShaderStageCreateInfo<'static>,
}

pub(crate) struct StagesRebuild {
    #[allow(dead_code)]
    each: Vec<Option<StageRebuild>>,
    pub(crate) stages: Vec<vk::PipelineShaderStageCreateInfo<'static>>,
}

fn named_sampler(
    mapping: &VkDescriptorSetAndBindingMappingEXT,
) -> Option<*const vk::SamplerCreateInfo<'static>> {
    match mapping.source {
        SOURCE_CONSTANT_OFFSET => {
            Some(unsafe { mapping.source_data.constant_offset.p_embedded_sampler })
        }
        SOURCE_PUSH_INDEX => Some(unsafe { mapping.source_data.push_index.p_embedded_sampler }),
        SOURCE_INDIRECT_INDEX => {
            Some(unsafe { mapping.source_data.indirect_index.p_embedded_sampler })
        }
        SOURCE_INDIRECT_INDEX_ARRAY => {
            Some(unsafe { mapping.source_data.indirect_index_array.p_embedded_sampler })
        }
        SOURCE_SHADER_RECORD_INDEX => {
            Some(unsafe { mapping.source_data.shader_record_index.p_embedded_sampler })
        }
        _ => None,
    }
}

pub(crate) fn embedded_sampler(
    mapping: &VkDescriptorSetAndBindingMappingEXT,
) -> Option<*const vk::SamplerCreateInfo<'static>> {
    named_sampler(mapping).filter(|held| !held.is_null())
}

fn rebuilt_data(
    mapping: &VkDescriptorSetAndBindingMappingEXT,
    sampler: *const vk::SamplerCreateInfo<'static>,
) -> VkDescriptorMappingSourceDataEXT {
    let mut data = mapping.source_data;
    match mapping.source {
        SOURCE_CONSTANT_OFFSET => data.constant_offset.p_embedded_sampler = sampler,
        SOURCE_PUSH_INDEX => data.push_index.p_embedded_sampler = sampler,
        SOURCE_INDIRECT_INDEX => data.indirect_index.p_embedded_sampler = sampler,
        SOURCE_INDIRECT_INDEX_ARRAY => data.indirect_index_array.p_embedded_sampler = sampler,
        SOURCE_SHADER_RECORD_INDEX => data.shader_record_index.p_embedded_sampler = sampler,
        _ => (),
    };
    data
}

fn mapping_list(
    info: *const VkShaderDescriptorSetAndBindingMappingInfoEXT,
) -> Vec<VkDescriptorSetAndBindingMappingEXT> {
    (0..unsafe { (*info).mapping_count } as usize)
        .map(|at| unsafe { *(*info).p_mappings.add(at) })
        .collect()
}

fn call_patched_embedded(
    dev: &VkDevState,
    original: *const vk::SamplerCreateInfo<'static>,
) -> vk::SamplerCreateInfo<'static> {
    let held = patched_ci(ensure_settings(), &dev.caps, unsafe { &*original });
    call_report_sampler(dev, unsafe { &*original }, &held);
    held
}

fn patched_embedded(
    dev: &VkDevState,
    mapping: &VkDescriptorSetAndBindingMappingEXT,
) -> Option<vk::SamplerCreateInfo<'static>> {
    embedded_sampler(mapping).map(|original| call_patched_embedded(dev, original))
}

fn patched_samplers(
    dev: &VkDevState,
    info: *const VkShaderDescriptorSetAndBindingMappingInfoEXT,
) -> Vec<Option<vk::SamplerCreateInfo<'static>>> {
    mapping_list(info)
        .iter()
        .map(|mapping| patched_embedded(dev, mapping))
        .collect()
}

fn rebuilt_mapping(
    mapping: &VkDescriptorSetAndBindingMappingEXT,
    sampler: &Option<vk::SamplerCreateInfo<'static>>,
) -> VkDescriptorSetAndBindingMappingEXT {
    match sampler {
        Some(held) => VkDescriptorSetAndBindingMappingEXT {
            source_data: rebuilt_data(mapping, held as *const vk::SamplerCreateInfo<'static>),
            ..*mapping
        },
        None => *mapping,
    }
}

fn rebuilt_mappings(
    info: *const VkShaderDescriptorSetAndBindingMappingInfoEXT,
    samplers: &[Option<vk::SamplerCreateInfo<'static>>],
) -> Vec<VkDescriptorSetAndBindingMappingEXT> {
    mapping_list(info)
        .iter()
        .zip(samplers.iter())
        .map(|(mapping, sampler)| rebuilt_mapping(mapping, sampler))
        .collect()
}

fn rebuilt_info(
    info: *const VkShaderDescriptorSetAndBindingMappingInfoEXT,
    mappings: &[VkDescriptorSetAndBindingMappingEXT],
) -> VkShaderDescriptorSetAndBindingMappingInfoEXT {
    VkShaderDescriptorSetAndBindingMappingInfoEXT {
        p_mappings: mappings.as_ptr(),
        ..unsafe { *info }
    }
}

fn built_chain(
    head: *const c_void,
    info: *const VkShaderDescriptorSetAndBindingMappingInfoEXT,
    samplers: Vec<Option<vk::SamplerCreateInfo<'static>>>,
) -> Option<ChainRebuild> {
    let mappings = rebuilt_mappings(info, &samplers);
    let node = vec![rebuilt_info(info, &mappings)];
    let relink = call_relinked_chain(
        head,
        SHADER_MAPPING_INFO_TYPE,
        node.as_ptr() as *const c_void,
        CHAIN_SAMPLER_LABEL,
    )?;
    Some(ChainRebuild {
        head: relink.head,
        samplers,
        mappings,
        info: node,
        relink,
    })
}

pub(crate) fn rebuilt_mapping_chain(dev: &VkDevState, head: *const c_void) -> Option<ChainRebuild> {
    let info = chain_find(head, SHADER_MAPPING_INFO_TYPE)?
        as *const VkShaderDescriptorSetAndBindingMappingInfoEXT;
    let samplers = patched_samplers(dev, info);
    match samplers.iter().any(|one| one.is_some()) {
        true => built_chain(head, info, samplers),
        false => None,
    }
}

pub(crate) fn rebuilt_stage(
    dev: &VkDevState,
    p: *const vk::PipelineShaderStageCreateInfo<'static>,
) -> Option<StageRebuild> {
    let chain = rebuilt_mapping_chain(dev, unsafe { (*p).p_next })?;
    Some(StageRebuild {
        stage: vk::PipelineShaderStageCreateInfo {
            p_next: chain.head,
            ..unsafe { *p }
        },
        chain,
    })
}

fn stage_values(
    each: &[Option<StageRebuild>],
    p: *const vk::PipelineShaderStageCreateInfo<'static>,
) -> Vec<vk::PipelineShaderStageCreateInfo<'static>> {
    each.iter()
        .enumerate()
        .map(|(at, built)| match built {
            Some(one) => one.stage,
            None => unsafe { *p.add(at) },
        })
        .collect()
}

fn built_stages(
    each: Vec<Option<StageRebuild>>,
    p: *const vk::PipelineShaderStageCreateInfo<'static>,
) -> Option<StagesRebuild> {
    match each.iter().any(|one| one.is_some()) {
        true => Some(StagesRebuild {
            stages: stage_values(&each, p),
            each,
        }),
        false => None,
    }
}

pub(crate) fn rebuilt_stages(
    dev: &VkDevState,
    p: *const vk::PipelineShaderStageCreateInfo<'static>,
    count: u32,
) -> Option<StagesRebuild> {
    match p.is_null() {
        true => None,
        false => built_stages(
            (0..count as usize)
                .map(|at| rebuilt_stage(dev, unsafe { p.add(at) }))
                .collect(),
            p,
        ),
    }
}

fn call_samplers_through(
    dev: &VkDevState,
    fp: PfnWriteSamplers,
    handle: vk::Device,
    count: u32,
    cis: *const vk::SamplerCreateInfo<'_>,
    descriptors: *const c_void,
) -> vk::Result {
    let patched = patched_list(ensure_settings(), &dev.caps, cis, count);
    call_report_samplers(dev, cis, count, &patched);
    unsafe { fp(handle, count, patched.as_ptr(), descriptors) }
}

pub(crate) fn call_write_sampler_descriptors(
    dev: &VkDevState,
    handle: vk::Device,
    count: u32,
    cis: *const vk::SamplerCreateInfo<'_>,
    descriptors: *const c_void,
) -> vk::Result {
    match dev.samplers_fp {
        Some(fp) => call_samplers_through(dev, fp, handle, count, cis, descriptors),
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
    }
}
