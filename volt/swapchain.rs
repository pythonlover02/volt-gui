use std::collections::HashMap;
use std::ffi::c_void;
use std::ptr;
use std::sync::RwLock;

use ash::vk;
use ash::vk::Handle;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::DepthChoice;
use crate::consts::LatencyChoice;
use crate::consts::PresentChoice;
use crate::device::VkDevState;
use crate::ext::st;
use crate::ext::SwapLatencyCreateInfoNv;
use crate::ext::SwapPresentModesCreateInfoExt;
use crate::ext::ST_PRESENT_MODES_CREATE_INFO;
use crate::ext::ST_SWAPCHAIN_LATENCY_CREATE_INFO;
use crate::instance::call_write_list;
use crate::instance::insts_get;
use crate::instance::owning_instance;
use crate::instance::VkInstState;
use crate::logging::log_at;
use crate::logging::LogLevel;

#[derive(Clone)]
pub(crate) struct SwapModes {
    pub(crate) created: vk::PresentModeKHR,
    pub(crate) supported: Vec<vk::PresentModeKHR>,
    pub(crate) switchable: bool,
}

static SWAPS: RwLock<Option<HashMap<u64, SwapModes>>> = RwLock::new(None);

pub(crate) fn swaps_get(h: u64) -> Option<SwapModes> {
    SWAPS
        .read()
        .ok()
        .and_then(|g| g.as_ref().and_then(|m| m.get(&h).cloned()))
}

pub(crate) fn swaps_put(h: u64, v: SwapModes) {
    match SWAPS.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).insert(h, v);
        }
        Err(_) => (),
    }
}

pub(crate) fn swaps_del(h: u64) {
    match SWAPS.write() {
        Ok(mut g) => {
            g.as_mut().map(|m| m.remove(&h));
        }
        Err(_) => (),
    }
}

pub(crate) fn present_vk(choice: PresentChoice) -> vk::PresentModeKHR {
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

fn is_preferred_format(f: &vk::SurfaceFormatKHR, depth: DepthChoice) -> bool {
    match depth {
        DepthChoice::TenBit => (f.format == vk::Format::A2B10G10R10_UNORM_PACK32
            || f.format == vk::Format::A2R10G10B10_UNORM_PACK32)
            && f.color_space == vk::ColorSpaceKHR::SRGB_NONLINEAR,
        DepthChoice::Hdr10 => f.color_space == vk::ColorSpaceKHR::HDR10_ST2084_EXT,
        DepthChoice::Scrgb => f.color_space == vk::ColorSpaceKHR::EXTENDED_SRGB_LINEAR_EXT,
    }
}

fn reordered_formats(formats: Vec<vk::SurfaceFormatKHR>, depth: DepthChoice) -> Vec<vk::SurfaceFormatKHR> {
    let (preferred, rest): (Vec<vk::SurfaceFormatKHR>, Vec<vk::SurfaceFormatKHR>) =
        formats.into_iter().partition(|f| is_preferred_format(f, depth));
    [preferred, rest].concat()
}

fn depth_first(formats: Vec<vk::SurfaceFormatKHR>, depth: Option<DepthChoice>) -> Vec<vk::SurfaceFormatKHR> {
    match depth {
        Some(d) => reordered_formats(formats, d),
        None => formats,
    }
}

fn maybe_log_depth(depth: Option<DepthChoice>) {
    match depth {
        Some(_) => log_at(LogLevel::Info, "surface formats reordered for the color depth preference"),
        None => (),
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
            maybe_log_depth(s.depth);
            call_write_list(
                &depth_first(call_query_surface_formats_all(&inst, phys, surface), s.depth),
                count,
                formats,
            )
        }
    }
}

fn hdr10_metadata() -> vk::HdrMetadataEXT {
    vk::HdrMetadataEXT {
        display_primary_red: vk::XYColorEXT { x: 0.708, y: 0.292 },
        display_primary_green: vk::XYColorEXT { x: 0.170, y: 0.797 },
        display_primary_blue: vk::XYColorEXT { x: 0.131, y: 0.046 },
        white_point: vk::XYColorEXT { x: 0.3127, y: 0.3290 },
        max_luminance: 1000.0,
        min_luminance: 0.001,
        max_content_light_level: 1000.0,
        max_frame_average_light_level: 400.0,
        ..Default::default()
    }
}

fn call_set_hdr_metadata(dev: &VkDevState, sc: vk::SwapchainKHR) {
    match dev.hdr_fp {
        Some(f) => unsafe { f(dev.device.handle(), 1, &sc, &hdr10_metadata()) },
        None => (),
    }
}

fn maybe_apply_hdr(dev: &VkDevState, sc: vk::SwapchainKHR, ci: &vk::SwapchainCreateInfoKHR, s: &Settings) {
    match (s.depth, ci.image_color_space == vk::ColorSpaceKHR::HDR10_ST2084_EXT) {
        (Some(DepthChoice::Hdr10), true) => call_set_hdr_metadata(dev, sc),
        (_, _) => (),
    }
}

fn latency_wanted(s: &Settings) -> bool {
    match s.low_latency {
        Some(LatencyChoice::On) | Some(LatencyChoice::Boost) => true,
        None => false,
    }
}

fn register_swapchain(
    dev: &VkDevState,
    sc: vk::SwapchainKHR,
    created: vk::PresentModeKHR,
    supported: Vec<vk::PresentModeKHR>,
) {
    swaps_put(
        sc.as_raw(),
        SwapModes {
            created,
            supported: supported.clone(),
            switchable: dev.caps.swap_maint,
        },
    );
    log_at(LogLevel::Info, "swapchain registered");
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
            let original = unsafe { &*ci };
            let supported = call_query_present_modes(&inst, dev.phys, original.surface);
            let caps = call_query_surface_caps(&inst, dev.phys, original.surface);
            let chosen = pick_present_mode(s.present_mode, &supported, original.present_mode);
            let modes_info = SwapPresentModesCreateInfoExt {
                s_type: st(ST_PRESENT_MODES_CREATE_INFO),
                p_next: original.p_next,
                present_mode_count: supported.len() as u32,
                p_present_modes: supported.as_ptr(),
            };
            let latency_info = SwapLatencyCreateInfoNv {
                s_type: st(ST_SWAPCHAIN_LATENCY_CREATE_INFO),
                p_next: &modes_info as *const SwapPresentModesCreateInfoExt as *const c_void,
                latency_mode_enable: vk::TRUE,
            };
            let head = match (dev.caps.swap_maint && !supported.is_empty(),
                              dev.caps.low_latency && latency_wanted(&s)) {
                (true, true) => &latency_info as *const SwapLatencyCreateInfoNv as *const c_void,
                (true, false) => &modes_info as *const SwapPresentModesCreateInfoExt as *const c_void,
                (false, true) => {
                    let solo = SwapLatencyCreateInfoNv {
                        p_next: original.p_next,
                        ..latency_info
                    };
                    let r = call_create_with(dev, handle, original, chosen, &caps, &s,
                        &solo as *const SwapLatencyCreateInfoNv as *const c_void, alloc, out);
                    match r {
                        vk::Result::SUCCESS => {
                            register_swapchain(dev, unsafe { *out }, chosen, supported);
                            maybe_apply_hdr(dev, unsafe { *out }, original, &s);
                        }
                        _ => (),
                    }
                    return r;
                }
                (false, false) => original.p_next,
            };
            let r = call_create_with(dev, handle, original, chosen, &caps, &s, head, alloc, out);
            match r {
                vk::Result::SUCCESS => {
                    register_swapchain(dev, unsafe { *out }, chosen, supported);
                    maybe_apply_hdr(dev, unsafe { *out }, original, &s);
                }
                _ => (),
            }
            r
        }
        None => unsafe { (dev.swap_fp.create_swapchain_khr)(handle, ci, alloc, out) },
    }
}

fn call_create_with(
    dev: &VkDevState,
    handle: vk::Device,
    original: &vk::SwapchainCreateInfoKHR,
    chosen: vk::PresentModeKHR,
    caps: &vk::SurfaceCapabilitiesKHR,
    s: &Settings,
    head: *const c_void,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    let patched = vk::SwapchainCreateInfoKHR {
        p_next: head,
        present_mode: chosen,
        min_image_count: pick_image_count(s, caps, original.min_image_count),
        ..*original
    };
    unsafe { (dev.swap_fp.create_swapchain_khr)(handle, &patched, alloc, out) }
}
