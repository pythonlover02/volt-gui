use std::ffi::c_void;

use ash::vk;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::ANISO_ABSENT_INFO;
use crate::consts::ANISO_OFF;
use crate::consts::FILTER_LINEAR;
use crate::consts::MIPMAP_LINEAR;
use crate::device::DeviceCaps;
use crate::device::VkDevState;
use crate::instance::PfnWriteSamplers;
use crate::lists::forced;
use crate::logging::log_at;
use crate::logging::LogLevel;

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

fn aniso_absent() -> Option<f32> {
    log_at(LogLevel::Info, ANISO_ABSENT_INFO);
    None
}

fn aniso_allowed(choice: Option<f32>, caps: &DeviceCaps) -> Option<f32> {
    match (choice, caps.sampler_anisotropy) {
        (None, _) => None,
        (Some(level), true) => Some(level.min(caps.max_anisotropy)),
        (Some(_), false) => aniso_absent(),
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

fn patched_ci(
    s: &Settings,
    caps: &DeviceCaps,
    original: &vk::SamplerCreateInfo,
) -> vk::SamplerCreateInfo {
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

fn patched_list(
    s: &Settings,
    caps: &DeviceCaps,
    cis: *const vk::SamplerCreateInfo,
    count: u32,
) -> Vec<vk::SamplerCreateInfo> {
    unsafe { std::slice::from_raw_parts(cis, count as usize) }
        .iter()
        .map(|original| patched_ci(s, caps, original))
        .collect()
}

pub(crate) fn call_create_sampler(
    dev: &VkDevState,
    ci: *const vk::SamplerCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Sampler,
) -> vk::Result {
    let patched = patched_ci(ensure_settings(), &dev.caps, unsafe { &*ci });
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
    cis: *const vk::SamplerCreateInfo,
    descriptors: *const c_void,
) -> vk::Result {
    let patched = patched_list(ensure_settings(), &dev.caps, cis, count);
    unsafe { fp(handle, count, patched.as_ptr(), descriptors) }
}

pub(crate) fn call_write_sampler_descriptors(
    dev: &VkDevState,
    handle: vk::Device,
    count: u32,
    cis: *const vk::SamplerCreateInfo,
    descriptors: *const c_void,
) -> vk::Result {
    match dev.samplers_fp {
        Some(fp) => call_samplers_through(dev, fp, handle, count, cis, descriptors),
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
    }
}
