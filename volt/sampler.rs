use std::ffi::c_void;

use ash::vk;
use ash::vk::Handle;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::ANISO_OFF;
use crate::consts::FEATURE_ANISOTROPY;
use crate::consts::FILTER_LINEAR;
use crate::consts::MIPMAP_LINEAR;
use crate::consts::SETTING_ANISOTROPY;
use crate::consts::SETTING_LOD_BIAS;
use crate::consts::SETTING_MAG_FILTER;
use crate::consts::SETTING_MIN_FILTER;
use crate::consts::SETTING_MIP_CEILING;
use crate::consts::SETTING_MIP_FLOOR;
use crate::consts::SETTING_MIPMAP_MODE;
use crate::consts::TEXT_OFF;
use crate::device::DeviceCaps;
use crate::device::VkDevState;
use crate::instance::PfnWriteSamplers;
use crate::lists::forced;
use crate::logging::info_wanted;
use crate::report::call_report_value;
use crate::report::feature_note;
use crate::report::filter_text;
use crate::report::mipmap_text;
use crate::report::number_text;

fn filter_vk(value: u32) -> vk::Filter {
    match value {
        FILTER_LINEAR => vk::Filter::LINEAR,
        _ => vk::Filter::NEAREST,
    }
}

fn pick_filter(choice: Option<u32>, original: vk::Filter) -> vk::Filter {
    match choice {
        Some(value) => filter_vk(value),
        None => original,
    }
}

fn mipmap_vk(value: u32) -> vk::SamplerMipmapMode {
    match value {
        MIPMAP_LINEAR => vk::SamplerMipmapMode::LINEAR,
        _ => vk::SamplerMipmapMode::NEAREST,
    }
}

fn pick_mipmap(choice: Option<u32>, original: vk::SamplerMipmapMode) -> vk::SamplerMipmapMode {
    match choice {
        Some(value) => mipmap_vk(value),
        None => original,
    }
}

fn aniso_allowed(choice: Option<f32>, caps: &DeviceCaps) -> Option<f32> {
    match (choice, caps.sampler_anisotropy) {
        (None, _) => None,
        (Some(level), true) => Some(level.min(caps.max_anisotropy)),
        (Some(_), false) => None,
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
    original: (vk::Bool32, f32),
) -> (vk::Bool32, f32) {
    match aniso_allowed(choice, caps) {
        Some(level) => aniso_pair(level),
        None => original,
    }
}

fn pick_lod_bias(choice: Option<f32>, caps: &DeviceCaps, original: f32) -> f32 {
    forced(choice, original).clamp(-caps.max_lod_bias, caps.max_lod_bias)
}

fn pick_lod_range(s: &Settings, original: (f32, f32)) -> (f32, f32) {
    let low = forced(s.mip_floor, original.0);
    let high = forced(s.mip_ceiling, original.1);
    (low.min(high), high.max(low))
}

fn patched_ci<'a>(
    s: &Settings,
    caps: &DeviceCaps,
    original: &vk::SamplerCreateInfo<'a>,
) -> vk::SamplerCreateInfo<'a> {
    let (aniso_enable, aniso_max) = pick_aniso(
        s.anisotropy,
        caps,
        (original.anisotropy_enable, original.max_anisotropy),
    );
    let (lod_low, lod_high) = pick_lod_range(s, (original.min_lod, original.max_lod));
    vk::SamplerCreateInfo {
        mag_filter: pick_filter(s.mag_filter, original.mag_filter),
        min_filter: pick_filter(s.min_filter, original.min_filter),
        mipmap_mode: pick_mipmap(s.mipmap, original.mipmap_mode),
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
        s.mag_filter.is_some(),
        asked.mag_filter.as_raw() as u32,
        held.mag_filter.as_raw() as u32,
        filter_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_MIN_FILTER,
        s.min_filter.is_some(),
        asked.min_filter.as_raw() as u32,
        held.min_filter.as_raw() as u32,
        filter_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_MIPMAP_MODE,
        s.mipmap.is_some(),
        asked.mipmap_mode.as_raw() as u32,
        held.mipmap_mode.as_raw() as u32,
        mipmap_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_ANISOTROPY,
        s.anisotropy.is_some(),
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
        s.lod_bias.is_some(),
        asked.mip_lod_bias,
        held.mip_lod_bias,
        number_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_MIP_FLOOR,
        s.mip_floor.is_some(),
        asked.min_lod,
        held.min_lod,
        number_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_MIP_CEILING,
        s.mip_ceiling.is_some(),
        asked.max_lod,
        held.max_lod,
        number_text,
        None,
    );
}

fn call_report_one(
    dev: &VkDevState,
    asked: &vk::SamplerCreateInfo<'_>,
    held: &vk::SamplerCreateInfo<'_>,
) {
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
