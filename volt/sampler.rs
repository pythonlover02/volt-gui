use ash::vk;

use crate::bounds::bounds_set;
use crate::bounds::resolved;
use crate::bounds::Bounds;
use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::FILTER_BILINEAR;
use crate::consts::FILTER_RETRO;
use crate::consts::FILTER_TRILINEAR;
use crate::consts::MIPMAP_LINEAR;
use crate::consts::MIPMAP_NEAREST;
use crate::device::DeviceCaps;
use crate::device::VkDevState;

fn filter_rank(mag: vk::Filter, min: vk::Filter, mip: vk::SamplerMipmapMode) -> u32 {
    match (
        mag == vk::Filter::NEAREST && min == vk::Filter::NEAREST,
        mip == vk::SamplerMipmapMode::NEAREST,
    ) {
        (true, _) => FILTER_RETRO,
        (false, true) => FILTER_BILINEAR,
        (false, false) => FILTER_TRILINEAR,
    }
}

fn filter_triple(rank: u32) -> (vk::Filter, vk::Filter, vk::SamplerMipmapMode) {
    match rank {
        FILTER_RETRO => (vk::Filter::NEAREST, vk::Filter::NEAREST, vk::SamplerMipmapMode::NEAREST),
        FILTER_BILINEAR => (vk::Filter::LINEAR, vk::Filter::LINEAR, vk::SamplerMipmapMode::NEAREST),
        _ => (vk::Filter::LINEAR, vk::Filter::LINEAR, vk::SamplerMipmapMode::LINEAR),
    }
}

fn pick_filters(
    b: Bounds<u32>,
    original: (vk::Filter, vk::Filter, vk::SamplerMipmapMode),
) -> (vk::Filter, vk::Filter, vk::SamplerMipmapMode) {
    match bounds_set(&b) {
        true => filter_triple(resolved(b, filter_rank(original.0, original.1, original.2))),
        false => original,
    }
}

fn mipmap_rank(mode: vk::SamplerMipmapMode) -> u32 {
    match mode {
        vk::SamplerMipmapMode::LINEAR => MIPMAP_LINEAR,
        _ => MIPMAP_NEAREST,
    }
}

fn mipmap_vk(rank: u32) -> vk::SamplerMipmapMode {
    match rank {
        MIPMAP_LINEAR => vk::SamplerMipmapMode::LINEAR,
        _ => vk::SamplerMipmapMode::NEAREST,
    }
}

fn pick_mipmap(b: Bounds<u32>, original: vk::SamplerMipmapMode) -> vk::SamplerMipmapMode {
    match bounds_set(&b) {
        true => mipmap_vk(resolved(b, mipmap_rank(original))),
        false => original,
    }
}

fn pick_lod_bias(b: Bounds<f32>, caps: &DeviceCaps, original: f32) -> f32 {
    resolved(b, original).clamp(-caps.max_lod_bias, caps.max_lod_bias)
}

fn pick_lod_range(s: &Settings, original: (f32, f32)) -> (f32, f32) {
    let low = resolved(s.mip_floor, original.0);
    let high = resolved(s.mip_ceiling, original.1);
    (low.min(high), high.max(low))
}

fn patched_ci(s: &Settings, caps: &DeviceCaps, original: &vk::SamplerCreateInfo) -> vk::SamplerCreateInfo {
    let (mag, min, mip) = pick_filters(
        s.filtering,
        (original.mag_filter, original.min_filter, original.mipmap_mode),
    );
    let (lod_low, lod_high) = pick_lod_range(s, (original.min_lod, original.max_lod));
    vk::SamplerCreateInfo {
        mag_filter: mag,
        min_filter: min,
        mipmap_mode: pick_mipmap(s.mipmap, mip),
        mip_lod_bias: pick_lod_bias(s.lod_bias, caps, original.mip_lod_bias),
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
    let patched = patched_ci(ensure_settings(), &dev.caps, unsafe { &*ci });
    match unsafe { dev.device.create_sampler(&patched, alloc.as_ref()) } {
        Ok(sampler) => {
            unsafe { *out = sampler };
            vk::Result::SUCCESS
        }
        Err(e) => e,
    }
}
