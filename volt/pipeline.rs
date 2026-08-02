use ash::vk;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::ShadingChoice;
use crate::device::DeviceCaps;
use crate::device::VkDevState;

fn pick_shading(
    wanted: Option<ShadingChoice>,
    caps: &DeviceCaps,
    original: (vk::Bool32, f32),
) -> (vk::Bool32, f32) {
    match (wanted, caps.sample_rate_shading) {
        (Some(ShadingChoice::Off), _) => (vk::FALSE, original.1),
        (Some(ShadingChoice::Rate(r)), true) => (vk::TRUE, r),
        (Some(ShadingChoice::Rate(_)), false) => original,
        (None, _) => original,
    }
}

fn patched_multisample(
    s: &Settings,
    caps: &DeviceCaps,
    p: *const vk::PipelineMultisampleStateCreateInfo,
) -> Option<vk::PipelineMultisampleStateCreateInfo> {
    match p.is_null() {
        true => None,
        false => {
            let (enable, rate) = pick_shading(
                s.sample_shading,
                caps,
                unsafe { ((*p).sample_shading_enable, (*p).min_sample_shading) },
            );
            Some(vk::PipelineMultisampleStateCreateInfo {
                sample_shading_enable: enable,
                min_sample_shading: rate,
                ..unsafe { *p }
            })
        }
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
