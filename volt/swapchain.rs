use std::ptr;

use ash::vk;

use crate::bounds::accepts;
use crate::bounds::bounds_set;
use crate::bounds::kept;
use crate::bounds::resolved;
use crate::bounds::Bounds;
use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::DEPTH_EIGHT_BIT;
use crate::consts::DEPTH_EMPTY_WARN;
use crate::consts::DEPTH_TEN_BIT;
use crate::consts::PRESENT_FIFO_RELAXED;
use crate::consts::PRESENT_IMMEDIATE;
use crate::consts::PRESENT_MAILBOX;
use crate::device::VkDevState;
use crate::instance::call_write_list;
use crate::instance::insts_get;
use crate::instance::owning_instance;
use crate::instance::VkInstState;
use crate::logging::log_at;
use crate::logging::LogLevel;

fn present_rank(mode: vk::PresentModeKHR) -> Option<u32> {
    match mode {
        vk::PresentModeKHR::FIFO => Some(crate::consts::PRESENT_FIFO),
        vk::PresentModeKHR::FIFO_RELAXED => Some(PRESENT_FIFO_RELAXED),
        vk::PresentModeKHR::MAILBOX => Some(PRESENT_MAILBOX),
        vk::PresentModeKHR::IMMEDIATE => Some(PRESENT_IMMEDIATE),
        _ => None,
    }
}

fn present_vk(rank: u32) -> vk::PresentModeKHR {
    match rank {
        PRESENT_FIFO_RELAXED => vk::PresentModeKHR::FIFO_RELAXED,
        PRESENT_MAILBOX => vk::PresentModeKHR::MAILBOX,
        PRESENT_IMMEDIATE => vk::PresentModeKHR::IMMEDIATE,
        _ => vk::PresentModeKHR::FIFO,
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

fn wanted_rank(b: Bounds<u32>, original: vk::PresentModeKHR) -> Option<u32> {
    match present_rank(original) {
        Some(rank) => Some(resolved(b, rank)),
        None => b.force,
    }
}

fn target_mode(b: Bounds<u32>, original: vk::PresentModeKHR) -> Option<vk::PresentModeKHR> {
    match bounds_set(&b) {
        true => wanted_rank(b, original).map(present_vk),
        false => None,
    }
}

fn supported_mode(
    mode: vk::PresentModeKHR,
    supported: &[vk::PresentModeKHR],
    original: vk::PresentModeKHR,
) -> vk::PresentModeKHR {
    match supported.contains(&mode) {
        true => mode,
        false => {
            log_at(
                LogLevel::Warn,
                &format!("present mode {} unsupported by surface, keeping application choice", present_label(mode)),
            );
            original
        }
    }
}

fn pick_present_mode(
    b: Bounds<u32>,
    supported: &[vk::PresentModeKHR],
    original: vk::PresentModeKHR,
) -> vk::PresentModeKHR {
    match target_mode(b, original) {
        Some(mode) => supported_mode(mode, supported, original),
        None => original,
    }
}

fn caps_upper(caps_max: u32) -> u32 {
    match caps_max {
        0 => u32::MAX,
        n => n,
    }
}

fn pick_image_count(b: Bounds<u32>, caps: &vk::SurfaceCapabilitiesKHR, original: u32) -> u32 {
    resolved(b, original).clamp(caps.min_image_count, caps_upper(caps.max_image_count))
}

fn is_ten_bit(f: &vk::SurfaceFormatKHR) -> bool {
    (f.format == vk::Format::A2B10G10R10_UNORM_PACK32
        || f.format == vk::Format::A2R10G10B10_UNORM_PACK32)
        && f.color_space == vk::ColorSpaceKHR::SRGB_NONLINEAR
}

fn depth_rank(f: &vk::SurfaceFormatKHR) -> u32 {
    match is_ten_bit(f) {
        true => DEPTH_TEN_BIT,
        false => DEPTH_EIGHT_BIT,
    }
}

fn depth_filtered(
    formats: Vec<vk::SurfaceFormatKHR>,
    b: Bounds<u32>,
) -> Vec<vk::SurfaceFormatKHR> {
    match bounds_set(&b) {
        true => kept(formats, |f| accepts(b, depth_rank(f)), DEPTH_EMPTY_WARN),
        false => formats,
    }
}

fn maybe_log_depth(b: &Bounds<u32>) {
    match bounds_set(b) {
        true => log_at(LogLevel::Info, "surface formats filtered for the color depth setting"),
        false => (),
    }
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
    match unsafe {
        (inst.surface_fp.get_physical_device_surface_capabilities_khr)(phys, surface, &mut caps)
    } {
        vk::Result::SUCCESS => caps,
        _ => vk::SurfaceCapabilitiesKHR {
            min_image_count: 1,
            max_image_count: 0,
            ..caps
        },
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
            maybe_log_depth(&s.depth);
            call_write_list(
                &depth_filtered(call_query_surface_formats_all(&inst, phys, surface), s.depth),
                count,
                formats,
            )
        }
    }
}

fn call_create_with(
    dev: &VkDevState,
    handle: vk::Device,
    original: &vk::SwapchainCreateInfoKHR,
    chosen: vk::PresentModeKHR,
    caps: &vk::SurfaceCapabilitiesKHR,
    s: &Settings,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    let patched = vk::SwapchainCreateInfoKHR {
        present_mode: chosen,
        min_image_count: pick_image_count(s.image_count, caps, original.min_image_count),
        ..*original
    };
    unsafe { (dev.swap_fp.create_swapchain_khr)(handle, &patched, alloc, out) }
}

fn call_chosen_present_mode(
    inst: &VkInstState,
    dev: &VkDevState,
    original: &vk::SwapchainCreateInfoKHR,
    s: &Settings,
) -> vk::PresentModeKHR {
    pick_present_mode(
        s.present_mode,
        &call_query_present_modes(inst, dev.phys, original.surface),
        original.present_mode,
    )
}

fn call_logged_create(created: vk::Result) -> vk::Result {
    match created {
        vk::Result::SUCCESS => {
            log_at(LogLevel::Info, "swapchain created");
            vk::Result::SUCCESS
        }
        e => e,
    }
}

fn call_create_registered(
    dev: &VkDevState,
    handle: vk::Device,
    inst: &VkInstState,
    original: &vk::SwapchainCreateInfoKHR,
    s: &Settings,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    call_logged_create(call_create_with(
        dev,
        handle,
        original,
        call_chosen_present_mode(inst, dev, original, s),
        &call_query_surface_caps(inst, dev.phys, original.surface),
        s,
        alloc,
        out,
    ))
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
        Some(inst) => call_create_registered(dev, handle, &inst, unsafe { &*ci }, &s, alloc, out),
        None => unsafe { (dev.swap_fp.create_swapchain_khr)(handle, ci, alloc, out) },
    }
}
