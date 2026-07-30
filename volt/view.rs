use std::ffi::c_void;

use ash::vk;

use crate::config::ensure_settings;
use crate::device::VkDevState;
use crate::ext::st;
use crate::ext::ViewMinLodCreateInfoExt;
use crate::ext::ST_VIEW_MIN_LOD_CREATE_INFO;

fn is_sampled_color_view(ci: &vk::ImageViewCreateInfo) -> bool {
    ci.subresource_range.aspect_mask == vk::ImageAspectFlags::COLOR
        && ci.subresource_range.level_count > 1
}

fn wanted_min_lod(dev: &VkDevState, ci: &vk::ImageViewCreateInfo) -> Option<f32> {
    ensure_settings()
        .lod_min
        .filter(|_| dev.caps.view_min_lod)
        .filter(|_| is_sampled_color_view(ci))
}

fn call_create_through(
    dev: &VkDevState,
    ci: *const vk::ImageViewCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::ImageView,
) -> vk::Result {
    match unsafe { dev.device.create_image_view(&*ci, alloc.as_ref()) } {
        Ok(view) => {
            unsafe { *out = view };
            vk::Result::SUCCESS
        }
        Err(e) => e,
    }
}

pub(crate) fn call_create_image_view(
    dev: &VkDevState,
    ci: *const vk::ImageViewCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::ImageView,
) -> vk::Result {
    let original = unsafe { &*ci };
    match wanted_min_lod(dev, original) {
        None => call_create_through(dev, ci, alloc, out),
        Some(lod) => {
            let lod_info = ViewMinLodCreateInfoExt {
                s_type: st(ST_VIEW_MIN_LOD_CREATE_INFO),
                p_next: original.p_next,
                min_lod: lod.min(original.subresource_range.level_count as f32 - 1.0),
            };
            let patched = vk::ImageViewCreateInfo {
                p_next: &lod_info as *const ViewMinLodCreateInfoExt as *const c_void,
                ..*original
            };
            call_create_through(dev, &patched, alloc, out)
        }
    }
}
