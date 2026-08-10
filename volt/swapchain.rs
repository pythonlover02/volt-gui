use std::ptr;

use ash::vk;

use crate::bounds::accepts;
use crate::bounds::bounds_set;
use crate::bounds::kept;
use crate::bounds::resolved;
use crate::bounds::Bounds;
use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::ALPHA_OPAQUE_INFO;
use crate::consts::DEPTH_EMPTY_WARN;
use crate::consts::FORMAT_FORCED_WARN;
use crate::consts::PRESENT_EMPTY_WARN;
use crate::consts::PRESENT_MISS_WARN;
use crate::consts::SPACE_EMPTY_WARN;
use crate::consts::SPACE_EXTENDED_INFO;
use crate::consts::SPACE_FORCED_WARN;
use crate::consts::TOGGLE_OFF;
use crate::consts::TOGGLE_ON;
use crate::consts::TRANSFER_EMPTY_WARN;
use crate::consts::TRANSFER_FORCED_WARN;
use crate::device::VkDevState;
use crate::env::env_probe_active;
use crate::instance::call_write_list;
use crate::instance::insts_get;
use crate::instance::owning_instance;
use crate::instance::PfnCreateSharedSwapchains;
use crate::instance::PfnSurfaceCaps2;
use crate::instance::PfnSurfaceFormats2;
use crate::instance::PfnSurfaceModes2;
use crate::instance::VkInstState;
use crate::instance::VkPhysicalDeviceSurfaceInfo2;
use crate::instance::VkSurfaceCapabilities2;
use crate::instance::VkSurfaceFormat2;
use crate::instance::SURFACE_FORMAT_2;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::probe::build_probe;
use crate::probe::call_write_probe;
use crate::ranks::alpha_semantic;
use crate::ranks::format_semantic;
use crate::ranks::present_semantic;
use crate::ranks::space_semantic;
use crate::ranks::transfer_semantic;

fn mode_rank(mode: vk::PresentModeKHR) -> Option<u32> {
    present_semantic(mode.as_raw() as u32).map(|facts| facts.rank)
}

fn depth_of(f: &vk::SurfaceFormatKHR) -> Option<u32> {
    format_semantic(f.format.as_raw() as u32).map(|facts| facts.depth)
}

fn transfer_of(f: &vk::SurfaceFormatKHR) -> Option<u32> {
    format_semantic(f.format.as_raw() as u32)
        .map(|facts| transfer_semantic(facts.numeric).rank)
}

fn space_of(f: &vk::SurfaceFormatKHR) -> Option<u32> {
    space_semantic(f.color_space.as_raw() as u32).map(|facts| facts.rank)
}

fn ranked_accepted(b: Bounds<u32>, rank: Option<u32>) -> bool {
    match rank {
        Some(value) => accepts(b, value),
        None => false,
    }
}

fn ranked_modes(supported: &[vk::PresentModeKHR]) -> Vec<(u32, vk::PresentModeKHR)> {
    supported
        .iter()
        .filter_map(|m| mode_rank(*m).map(|rank| (rank, *m)))
        .collect()
}

fn mode_of_rank(list: &[(u32, vk::PresentModeKHR)], rank: u32) -> Option<vk::PresentModeKHR> {
    list.iter().find(|(r, _)| *r == rank).map(|(_, m)| *m)
}

fn logged_miss(original: vk::PresentModeKHR) -> vk::PresentModeKHR {
    log_at(LogLevel::Warn, PRESENT_MISS_WARN);
    original
}

fn resolved_mode(
    b: Bounds<u32>,
    list: &[(u32, vk::PresentModeKHR)],
    original: vk::PresentModeKHR,
) -> vk::PresentModeKHR {
    match mode_rank(original).and_then(|rank| mode_of_rank(list, resolved(b, rank))) {
        Some(mode) => mode,
        None => logged_miss(original),
    }
}

fn pick_present_mode(
    b: Bounds<u32>,
    supported: &[vk::PresentModeKHR],
    original: vk::PresentModeKHR,
) -> vk::PresentModeKHR {
    match bounds_set(&b) {
        true => resolved_mode(b, &ranked_modes(supported), original),
        false => original,
    }
}

fn present_filtered(
    modes: Vec<vk::PresentModeKHR>,
    b: Bounds<u32>,
) -> Vec<vk::PresentModeKHR> {
    match bounds_set(&b) {
        true => kept(modes, |m| ranked_accepted(b, mode_rank(*m)), PRESENT_EMPTY_WARN),
        false => modes,
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

fn reported_high(high: u32) -> u32 {
    match high {
        u32::MAX => 0,
        n => n,
    }
}

fn narrowed_caps(caps: vk::SurfaceCapabilitiesKHR, b: Bounds<u32>) -> vk::SurfaceCapabilitiesKHR {
    let high = caps_upper(caps.max_image_count);
    vk::SurfaceCapabilitiesKHR {
        min_image_count: resolved(b, caps.min_image_count).clamp(caps.min_image_count, high),
        max_image_count: reported_high(resolved(b, high).clamp(caps.min_image_count, high)),
        ..caps
    }
}

fn clamped_caps(caps: vk::SurfaceCapabilitiesKHR, b: Bounds<u32>) -> vk::SurfaceCapabilitiesKHR {
    match bounds_set(&b) {
        true => narrowed_caps(caps, b),
        false => caps,
    }
}

fn depth_filtered(
    formats: Vec<vk::SurfaceFormatKHR>,
    b: Bounds<u32>,
) -> Vec<vk::SurfaceFormatKHR> {
    match bounds_set(&b) {
        true => kept(formats, |f| ranked_accepted(b, depth_of(f)), DEPTH_EMPTY_WARN),
        false => formats,
    }
}

fn space_filtered(
    formats: Vec<vk::SurfaceFormatKHR>,
    b: Bounds<u32>,
) -> Vec<vk::SurfaceFormatKHR> {
    match bounds_set(&b) {
        true => kept(formats, |f| ranked_accepted(b, space_of(f)), SPACE_EMPTY_WARN),
        false => formats,
    }
}

fn transfer_filtered(
    formats: Vec<vk::SurfaceFormatKHR>,
    b: Bounds<u32>,
) -> Vec<vk::SurfaceFormatKHR> {
    match bounds_set(&b) {
        true => kept(formats, |f| ranked_accepted(b, transfer_of(f)), TRANSFER_EMPTY_WARN),
        false => formats,
    }
}

fn surface_filtered(
    formats: Vec<vk::SurfaceFormatKHR>,
    s: &Settings,
) -> Vec<vk::SurfaceFormatKHR> {
    transfer_filtered(
        space_filtered(depth_filtered(formats, s.depth), s.color_space),
        s.transfer,
    )
}

fn log_extended(extended: bool) {
    match extended {
        true => log_at(LogLevel::Info, SPACE_EXTENDED_INFO),
        false => (),
    }
}

fn maybe_log_space(b: Bounds<u32>) {
    match b.force.and_then(space_semantic) {
        Some(facts) => log_extended(facts.extended),
        None => (),
    }
}

fn log_blending(blends: bool) {
    match blends {
        false => log_at(LogLevel::Info, ALPHA_OPAQUE_INFO),
        true => (),
    }
}

fn maybe_log_alpha(b: Bounds<u32>) {
    match b.force.and_then(alpha_semantic) {
        Some(facts) => log_blending(facts.blends),
        None => (),
    }
}

fn excluded(b: Bounds<u32>, rank: Option<u32>) -> bool {
    bounds_set(&b) && !ranked_accepted(b, rank)
}

fn maybe_warn(kept_out: bool, warn: &str) {
    match kept_out {
        true => log_at(LogLevel::Warn, warn),
        false => (),
    }
}

fn warn_excluded_choice(asked: vk::SurfaceFormatKHR, s: &Settings) {
    maybe_warn(excluded(s.depth, depth_of(&asked)), FORMAT_FORCED_WARN);
    maybe_warn(excluded(s.color_space, space_of(&asked)), SPACE_FORCED_WARN);
    maybe_warn(excluded(s.transfer, transfer_of(&asked)), TRANSFER_FORCED_WARN);
}

fn asked_format(original: &vk::SwapchainCreateInfoKHR) -> vk::SurfaceFormatKHR {
    vk::SurfaceFormatKHR {
        format: original.image_format,
        color_space: original.image_color_space,
    }
}

fn pick_alpha(b: Bounds<u32>, original: vk::CompositeAlphaFlagsKHR) -> vk::CompositeAlphaFlagsKHR {
    match bounds_set(&b) {
        true => vk::CompositeAlphaFlagsKHR::from_raw(resolved(b, original.as_raw())),
        false => original,
    }
}

fn toggle_rank(flag: vk::Bool32) -> u32 {
    match flag {
        vk::TRUE => TOGGLE_ON,
        _ => TOGGLE_OFF,
    }
}

fn toggle_vk(rank: u32) -> vk::Bool32 {
    match rank {
        TOGGLE_ON => vk::TRUE,
        _ => vk::FALSE,
    }
}

fn pick_clipped(b: Bounds<u32>, original: vk::Bool32) -> vk::Bool32 {
    match bounds_set(&b) {
        true => toggle_vk(resolved(b, toggle_rank(original))),
        false => original,
    }
}

fn patched_swapchain_ci(
    original: &vk::SwapchainCreateInfoKHR,
    chosen: vk::PresentModeKHR,
    caps: &vk::SurfaceCapabilitiesKHR,
    s: &Settings,
) -> vk::SwapchainCreateInfoKHR {
    vk::SwapchainCreateInfoKHR {
        present_mode: chosen,
        min_image_count: pick_image_count(s.image_count, caps, original.min_image_count),
        composite_alpha: pick_alpha(s.composite_alpha, original.composite_alpha),
        clipped: pick_clipped(s.clipped, original.clipped),
        ..*original
    }
}

pub(crate) fn call_query_present_modes(
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

pub(crate) fn call_query_surface_formats_all(
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

fn call_filtered_formats(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    s: &Settings,
) -> Vec<vk::SurfaceFormatKHR> {
    maybe_log_space(s.color_space);
    surface_filtered(call_query_surface_formats_all(inst, phys, surface), s)
}

pub(crate) fn call_surface_formats(
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    count: *mut u32,
    formats: *mut vk::SurfaceFormatKHR,
) -> vk::Result {
    match owning_instance(phys) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some((_, inst)) => call_write_list(
            &call_filtered_formats(&inst, phys, surface, ensure_settings()),
            count,
            formats,
        ),
    }
}

pub(crate) fn call_surface_present_modes(
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    count: *mut u32,
    modes: *mut vk::PresentModeKHR,
) -> vk::Result {
    match owning_instance(phys) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some((_, inst)) => call_write_list(
            &present_filtered(
                call_query_present_modes(&inst, phys, surface),
                ensure_settings().present_mode,
            ),
            count,
            modes,
        ),
    }
}

fn call_narrowed_result(
    queried: vk::Result,
    out: *mut vk::SurfaceCapabilitiesKHR,
    b: Bounds<u32>,
) -> vk::Result {
    match queried {
        vk::Result::SUCCESS => {
            unsafe { *out = clamped_caps(*out, b) };
            vk::Result::SUCCESS
        }
        e => e,
    }
}

pub(crate) fn call_surface_capabilities(
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    out: *mut vk::SurfaceCapabilitiesKHR,
) -> vk::Result {
    match owning_instance(phys) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some((_, inst)) => call_narrowed_result(
            unsafe {
                (inst.surface_fp.get_physical_device_surface_capabilities_khr)(phys, surface, out)
            },
            out,
            ensure_settings().image_count,
        ),
    }
}

fn call_caps2_through(
    fp: PfnSurfaceCaps2,
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
    out: *mut VkSurfaceCapabilities2,
    b: Bounds<u32>,
) -> vk::Result {
    match unsafe { fp(phys, info, out) } {
        vk::Result::SUCCESS => {
            unsafe { (*out).surface_capabilities = clamped_caps((*out).surface_capabilities, b) };
            vk::Result::SUCCESS
        }
        e => e,
    }
}

pub(crate) fn call_surface_capabilities2(
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
    out: *mut VkSurfaceCapabilities2,
) -> vk::Result {
    match owning_instance(phys).and_then(|(_, inst)| inst.caps2_fp) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(fp) => call_caps2_through(fp, phys, info, out, ensure_settings().image_count),
    }
}

fn empty_format2() -> VkSurfaceFormat2 {
    VkSurfaceFormat2 {
        s_type: vk::StructureType::from_raw(SURFACE_FORMAT_2 as i32),
        p_next: ptr::null_mut(),
        surface_format: vk::SurfaceFormatKHR::default(),
    }
}

fn unwrapped_formats(wrapped: Vec<VkSurfaceFormat2>) -> Vec<vk::SurfaceFormatKHR> {
    wrapped.into_iter().map(|one| one.surface_format).collect()
}

fn kept_offsets(
    filled: &[VkSurfaceFormat2],
    kept_formats: &[vk::SurfaceFormatKHR],
) -> Vec<usize> {
    filled
        .iter()
        .enumerate()
        .filter(|(_, one)| kept_formats.contains(&one.surface_format))
        .map(|(at, _)| at)
        .collect()
}

fn call_read_filled(count: *mut u32, out: *mut VkSurfaceFormat2) -> Vec<VkSurfaceFormat2> {
    (0..unsafe { *count } as usize)
        .map(|at| unsafe { *out.add(at) })
        .collect()
}

fn call_compact_to(out: *mut VkSurfaceFormat2, offsets: &[usize]) {
    offsets
        .iter()
        .enumerate()
        .for_each(|(at, from)| unsafe { ptr::swap(out.add(at), out.add(*from)) });
}

fn call_query_formats2_all(
    fp: PfnSurfaceFormats2,
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
) -> Vec<vk::SurfaceFormatKHR> {
    let mut n: u32 = 0;
    let r1 = unsafe { fp(phys, info, &mut n, ptr::null_mut()) };
    let mut v = vec![empty_format2(); n as usize];
    let r2 = unsafe { fp(phys, info, &mut n, v.as_mut_ptr()) };
    match (r1, r2) {
        (vk::Result::SUCCESS, vk::Result::SUCCESS) => unwrapped_formats(v),
        (_, _) => Vec::new(),
    }
}

fn completed(written: usize, available: usize) -> vk::Result {
    match written == available {
        true => vk::Result::SUCCESS,
        false => vk::Result::INCOMPLETE,
    }
}

fn call_filtered_in_place(
    queried: vk::Result,
    kept_formats: &[vk::SurfaceFormatKHR],
    count: *mut u32,
    out: *mut VkSurfaceFormat2,
) -> vk::Result {
    match queried {
        vk::Result::SUCCESS | vk::Result::INCOMPLETE => {
            let offsets = kept_offsets(&call_read_filled(count, out), kept_formats);
            call_compact_to(out, &offsets);
            unsafe { *count = offsets.len() as u32 };
            completed(offsets.len(), kept_formats.len())
        }
        e => e,
    }
}

fn call_formats2_into(
    fp: PfnSurfaceFormats2,
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
    kept_formats: &[vk::SurfaceFormatKHR],
    count: *mut u32,
    out: *mut VkSurfaceFormat2,
) -> vk::Result {
    call_filtered_in_place(
        unsafe { fp(phys, info, count, out) },
        kept_formats,
        count,
        out,
    )
}

fn call_formats2_count(kept_formats: &[vk::SurfaceFormatKHR], count: *mut u32) -> vk::Result {
    unsafe { *count = kept_formats.len() as u32 };
    vk::Result::SUCCESS
}

fn call_formats2_answer(
    fp: PfnSurfaceFormats2,
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
    kept_formats: &[vk::SurfaceFormatKHR],
    count: *mut u32,
    out: *mut VkSurfaceFormat2,
) -> vk::Result {
    match out.is_null() {
        true => call_formats2_count(kept_formats, count),
        false => call_formats2_into(fp, phys, info, kept_formats, count, out),
    }
}

fn call_formats2_through(
    fp: PfnSurfaceFormats2,
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
    count: *mut u32,
    out: *mut VkSurfaceFormat2,
    s: &Settings,
) -> vk::Result {
    maybe_log_space(s.color_space);
    call_formats2_answer(
        fp,
        phys,
        info,
        &surface_filtered(call_query_formats2_all(fp, phys, info), s),
        count,
        out,
    )
}

pub(crate) fn call_surface_formats2(
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
    count: *mut u32,
    out: *mut VkSurfaceFormat2,
) -> vk::Result {
    match owning_instance(phys).and_then(|(_, inst)| inst.formats2_fp) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(fp) => call_formats2_through(fp, phys, info, count, out, ensure_settings()),
    }
}

fn call_query_modes2_all(
    fp: PfnSurfaceModes2,
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
) -> Vec<vk::PresentModeKHR> {
    let mut n: u32 = 0;
    let r1 = unsafe { fp(phys, info, &mut n, ptr::null_mut()) };
    let mut v = vec![vk::PresentModeKHR::FIFO; n as usize];
    let r2 = unsafe { fp(phys, info, &mut n, v.as_mut_ptr()) };
    match (r1, r2) {
        (vk::Result::SUCCESS, vk::Result::SUCCESS) => v,
        (_, _) => Vec::new(),
    }
}

pub(crate) fn call_surface_present_modes2(
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
    count: *mut u32,
    out: *mut vk::PresentModeKHR,
) -> vk::Result {
    match owning_instance(phys).and_then(|(_, inst)| inst.modes2_fp) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(fp) => call_write_list(
            &present_filtered(
                call_query_modes2_all(fp, phys, info),
                ensure_settings().present_mode,
            ),
            count,
            out,
        ),
    }
}

fn maybe_probe(
    inst: &VkInstState,
    dev: &VkDevState,
    surface: vk::SurfaceKHR,
    supported: &[vk::PresentModeKHR],
    caps: &vk::SurfaceCapabilitiesKHR,
) {
    match env_probe_active() {
        true => call_write_probe(build_probe(
            inst,
            dev,
            supported,
            caps,
            &call_query_surface_formats_all(inst, dev.phys, surface),
        )),
        false => (),
    }
}

fn call_created_swapchain(created: vk::Result) -> vk::Result {
    match created {
        vk::Result::SUCCESS => {
            log_at(LogLevel::Info, "swapchain created");
            vk::Result::SUCCESS
        }
        e => e,
    }
}

fn call_prepared_ci(
    inst: &VkInstState,
    dev: &VkDevState,
    original: &vk::SwapchainCreateInfoKHR,
    s: &Settings,
) -> vk::SwapchainCreateInfoKHR {
    let supported = call_query_present_modes(inst, dev.phys, original.surface);
    let caps = call_query_surface_caps(inst, dev.phys, original.surface);
    maybe_probe(inst, dev, original.surface, &supported, &caps);
    maybe_log_alpha(s.composite_alpha);
    warn_excluded_choice(asked_format(original), s);
    patched_swapchain_ci(
        original,
        pick_present_mode(s.present_mode, &supported, original.present_mode),
        &caps,
        s,
    )
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
    call_created_swapchain(unsafe {
        (dev.swap_fp.create_swapchain_khr)(
            handle,
            &call_prepared_ci(inst, dev, original, s),
            alloc,
            out,
        )
    })
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
        Some(inst) => call_create_registered(dev, handle, &inst, unsafe { &*ci }, s, alloc, out),
        None => unsafe { (dev.swap_fp.create_swapchain_khr)(handle, ci, alloc, out) },
    }
}

fn call_shared_patched(
    dev: &VkDevState,
    inst: &VkInstState,
    cis: *const vk::SwapchainCreateInfoKHR,
    count: u32,
    s: &Settings,
) -> Vec<vk::SwapchainCreateInfoKHR> {
    unsafe { std::slice::from_raw_parts(cis, count as usize) }
        .iter()
        .map(|original| call_prepared_ci(inst, dev, original, s))
        .collect()
}

fn call_shared_through(
    dev: &VkDevState,
    inst: &VkInstState,
    fp: PfnCreateSharedSwapchains,
    handle: vk::Device,
    count: u32,
    cis: *const vk::SwapchainCreateInfoKHR,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    call_created_swapchain(unsafe {
        fp(
            handle,
            count,
            call_shared_patched(dev, inst, cis, count, ensure_settings()).as_ptr(),
            alloc,
            out,
        )
    })
}

pub(crate) fn call_create_shared_swapchains(
    dev: &VkDevState,
    handle: vk::Device,
    count: u32,
    cis: *const vk::SwapchainCreateInfoKHR,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    match (dev.shared_fp, insts_get(dev.instance_handle)) {
        (Some(fp), Some(inst)) => {
            call_shared_through(dev, &inst, fp, handle, count, cis, alloc, out)
        }
        (_, _) => vk::Result::ERROR_INITIALIZATION_FAILED,
    }
}
