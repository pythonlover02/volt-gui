use ash::vk;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::AnisoChoice;
use crate::consts::FilterChoice;
use crate::device::DeviceCaps;
use crate::device::VkDevState;

fn filter_triple(choice: FilterChoice) -> (vk::Filter, vk::Filter, vk::SamplerMipmapMode) {
    match choice {
        FilterChoice::Retro => (vk::Filter::NEAREST, vk::Filter::NEAREST, vk::SamplerMipmapMode::NEAREST),
        FilterChoice::Bilinear => (vk::Filter::LINEAR, vk::Filter::LINEAR, vk::SamplerMipmapMode::NEAREST),
        FilterChoice::Trilinear => (vk::Filter::LINEAR, vk::Filter::LINEAR, vk::SamplerMipmapMode::LINEAR),
    }
}

fn pick_filters(
    wanted: Option<FilterChoice>,
    original: (vk::Filter, vk::Filter, vk::SamplerMipmapMode),
) -> (vk::Filter, vk::Filter, vk::SamplerMipmapMode) {
    match wanted {
        Some(choice) => filter_triple(choice),
        None => original,
    }
}

fn pick_aniso(
    wanted: Option<AnisoChoice>,
    caps: &DeviceCaps,
    original: (vk::Bool32, f32),
) -> (vk::Bool32, f32) {
    match (wanted, caps.sampler_anisotropy) {
        (Some(AnisoChoice::Off), _) => (vk::FALSE, original.1),
        (Some(AnisoChoice::Level(v)), true) => (vk::TRUE, v.min(caps.max_anisotropy)),
        (Some(AnisoChoice::Level(_)), false) => original,
        (None, _) => original,
    }
}

fn clamp_between(value: f32, lower: Option<f32>, upper: Option<f32>) -> f32 {
    value
        .max(lower.unwrap_or(f32::MIN))
        .min(upper.unwrap_or(f32::MAX))
}

fn pick_lod_bias(s: &Settings, caps: &DeviceCaps, original: f32) -> f32 {
    clamp_between(s.lod_bias.unwrap_or(original), s.lod_bias_min, s.lod_bias_max)
        .clamp(-caps.max_lod_bias, caps.max_lod_bias)
}

fn pick_lod_range(s: &Settings, original: (f32, f32)) -> (f32, f32) {
    let low = s.lod_min.unwrap_or(original.0);
    let high = s.lod_max.unwrap_or(original.1);
    (low.min(high), high.max(low))
}

fn patched_ci(s: &Settings, caps: &DeviceCaps, original: &vk::SamplerCreateInfo) -> vk::SamplerCreateInfo {
    let (mag, min, mip) = pick_filters(s.filtering, (original.mag_filter, original.min_filter, original.mipmap_mode));
    let (aniso_enable, aniso_max) = pick_aniso(s.anisotropy, caps, (original.anisotropy_enable, original.max_anisotropy));
    let (lod_low, lod_high) = pick_lod_range(s, (original.min_lod, original.max_lod));
    vk::SamplerCreateInfo {
        mag_filter: mag,
        min_filter: min,
        mipmap_mode: mip,
        anisotropy_enable: aniso_enable,
        max_anisotropy: aniso_max,
        mip_lod_bias: pick_lod_bias(s, caps, original.mip_lod_bias),
        min_lod: lod_low,
        max_lod: lod_high,
        ..*original
    }
}

pub(crate) fn call_create_sampler(
    dev: &VkDevState,
    ci: *const vk::SamplerCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Sampler,
) -> vk::Result {
    let s = ensure_settings();
    let patched = patched_ci(&s, &dev.caps, unsafe { &*ci });
    match unsafe { dev.device.create_sampler(&patched, alloc.as_ref()) } {
        Ok(sampler) => {
            unsafe { *out = sampler };
            vk::Result::SUCCESS
        }
        Err(e) => e,
    }
}
