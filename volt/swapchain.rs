use std::ptr;

use ash::vk;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::PresentChoice;
use crate::device::VkDevState;
use crate::instance::call_write_list;
use crate::instance::insts_get;
use crate::instance::owning_instance;
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

fn is_ten_bit(format: vk::Format) -> bool {
    format == vk::Format::A2B10G10R10_UNORM_PACK32
        || format == vk::Format::A2R10G10B10_UNORM_PACK32
}

fn reordered_ten_bit(formats: Vec<vk::SurfaceFormatKHR>) -> Vec<vk::SurfaceFormatKHR> {
    let (ten, rest): (Vec<vk::SurfaceFormatKHR>, Vec<vk::SurfaceFormatKHR>) =
        formats.into_iter().partition(|f| is_ten_bit(f.format));
    [ten, rest].concat()
}

fn ten_bit_first(formats: Vec<vk::SurfaceFormatKHR>, prefer: Option<bool>) -> Vec<vk::SurfaceFormatKHR> {
    match prefer.unwrap_or(false) {
        true => reordered_ten_bit(formats),
        false => formats,
    }
}

fn maybe_log_ten_bit(prefer: Option<bool>) {
    match prefer.unwrap_or(false) {
        true => log_at(LogLevel::Info, "surface formats reordered to prefer 10-bit"),
        false => (),
    }
}

fn call_query_surface_formats_all(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
) -> Vec<vk::SurfaceFormatKHR> {
    let mut n: u32 = 0;
    let r1 = unsafe {
        (inst.surface_fp.get_physical_device_surface_formats_khr)(phys, surface, &mut n, ptr::null_mut())
    };
    let mut v = vec![vk::SurfaceFormatKHR::default(); n as usize];
    let r2 = unsafe {
        (inst.surface_fp.get_physical_device_surface_formats_khr)(phys, surface, &mut n, v.as_mut_ptr())
    };
    match (r1, r2) {
        (vk::Result::SUCCESS, vk::Result::SUCCESS) => v,
        (_, _) => Vec::new(),
    }
}

pub(crate) fn call_surface_formats(
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    count: *mut u32,
    formats: *mut vk::SurfaceFormatKHR,
) -> vk::Result {
    let s = ensure_settings();
    match owning_instance(phys) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some((_, inst)) => {
            maybe_log_ten_bit(s.ten_bit);
            call_write_list(
                &ten_bit_first(call_query_surface_formats_all(&inst, phys, surface), s.ten_bit),
                count,
                formats,
            )
        }
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
