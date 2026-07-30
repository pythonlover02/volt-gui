use std::ptr;

use ash::vk;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::PresentChoice;
use crate::device::VkDevState;
use crate::instance::insts_get;
use crate::instance::VkInstState;
use crate::logging::log_at;
use crate::logging::LogLevel;

fn present_vk(choice: PresentChoice) -> vk::PresentModeKHR {
    match choice {
        PresentChoice::Fifo => vk::PresentModeKHR::FIFO,
        PresentChoice::FifoRelaxed => vk::PresentModeKHR::FIFO_RELAXED,
        PresentChoice::Mailbox => vk::PresentModeKHR::MAILBOX,
        PresentChoice::Immediate => vk::PresentModeKHR::IMMEDIATE,
    }
}

fn present_label(mode: vk::PresentModeKHR) -> &'static str {
    match mode {
        vk::PresentModeKHR::FIFO => "fifo",
        vk::PresentModeKHR::FIFO_RELAXED => "fifo_relaxed",
        vk::PresentModeKHR::MAILBOX => "mailbox",
        vk::PresentModeKHR::IMMEDIATE => "immediate",
        _ => "other",
    }
}

fn pick_present_mode(
    wanted: Option<PresentChoice>,
    supported: &[vk::PresentModeKHR],
    original: vk::PresentModeKHR,
) -> vk::PresentModeKHR {
    match wanted.map(present_vk) {
        None => original,
        Some(mode) => match supported.contains(&mode) {
            true => mode,
            false => {
                log_at(
                    LogLevel::Warn,
                    &format!("present mode {} unsupported by surface, keeping application choice", present_label(mode)),
                );
                original
            }
        },
    }
}

fn caps_upper(caps_max: u32) -> u32 {
    match caps_max {
        0 => u32::MAX,
        n => n,
    }
}

fn pick_image_count(s: &Settings, caps: &vk::SurfaceCapabilitiesKHR, original: u32) -> u32 {
    let lower = s.image_count_min.unwrap_or(0).max(caps.min_image_count);
    let upper = s.image_count_max.unwrap_or(u32::MAX).min(caps_upper(caps.max_image_count));
    s.image_count
        .unwrap_or(original)
        .clamp(lower.min(upper), upper.max(lower))
}

fn call_query_present_modes(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
) -> Vec<vk::PresentModeKHR> {
    let mut n: u32 = 0;
    let r1 = unsafe {
        (inst.surface_fp.get_physical_device_surface_present_modes_khr)(phys, surface, &mut n, ptr::null_mut())
    };
    let mut v = vec![vk::PresentModeKHR::FIFO; n as usize];
    let r2 = unsafe {
        (inst.surface_fp.get_physical_device_surface_present_modes_khr)(phys, surface, &mut n, v.as_mut_ptr())
    };
    match (r1, r2) {
        (vk::Result::SUCCESS, vk::Result::SUCCESS) => v,
        (_, _) => Vec::new(),
    }
}

fn call_query_surface_caps(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
) -> vk::SurfaceCapabilitiesKHR {
    let mut caps = vk::SurfaceCapabilitiesKHR::default();
    let r = unsafe {
        (inst.surface_fp.get_physical_device_surface_capabilities_khr)(phys, surface, &mut caps)
    };
    match r {
        vk::Result::SUCCESS => caps,
        _ => vk::SurfaceCapabilitiesKHR {
            min_image_count: 1,
            max_image_count: 0,
            ..caps
        },
    }
}

fn patched_ci(
    s: &Settings,
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    original: &vk::SwapchainCreateInfoKHR,
) -> vk::SwapchainCreateInfoKHR {
    let supported = call_query_present_modes(inst, phys, original.surface);
    let caps = call_query_surface_caps(inst, phys, original.surface);
    vk::SwapchainCreateInfoKHR {
        present_mode: pick_present_mode(s.present_mode, &supported, original.present_mode),
        min_image_count: pick_image_count(s, &caps, original.min_image_count),
        ..*original
    }
}

pub(crate) fn call_create_swapchain(
    dev: &VkDevState,
    handle: vk::Device,
    ci: *const vk::SwapchainCreateInfoKHR,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    let s = ensure_settings();
    match insts_get(dev.instance_handle) {
        Some(inst) => {
            let patched = patched_ci(&s, &inst, dev.phys, unsafe { &*ci });
            unsafe { (dev.swap_fp.create_swapchain_khr)(handle, &patched, alloc, out) }
        }
        None => unsafe { (dev.swap_fp.create_swapchain_khr)(handle, ci, alloc, out) },
    }
}
