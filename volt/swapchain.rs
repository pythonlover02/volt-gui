use std::ptr;

use ash::vk;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::ALPHA_MISS_WARN;
use crate::consts::ALPHA_OPAQUE_INFO;
use crate::consts::DEPTH_EMPTY_WARN;
use crate::consts::FORMAT_FORCED_WARN;
use crate::consts::PRESENT_EMPTY_WARN;
use crate::consts::PRESENT_EXTENDED_INFO;
use crate::consts::PRESENT_MISS_WARN;
use crate::consts::SPACE_EMPTY_WARN;
use crate::consts::SPACE_EXTENDED_INFO;
use crate::consts::SPACE_FORCED_WARN;
use crate::consts::TOGGLE_ON;
use crate::consts::TRANSFER_EMPTY_WARN;
use crate::consts::TRANSFER_ENCODED_INFO;
use crate::consts::TRANSFER_FORCED_WARN;
use crate::consts::TRANSFER_SHADER_INFO;
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
use crate::lists::filtered;
use crate::lists::forced;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::probe::build_probe;
use crate::probe::call_write_probe;
use crate::ranks::alpha_semantic;
use crate::ranks::format_display;
use crate::ranks::format_semantic;
use crate::ranks::numeric_semantic;
use crate::ranks::present_semantic;
use crate::ranks::space_semantic;
use crate::ranks::Numeric;

fn mode_value(mode: &vk::PresentModeKHR) -> Option<u32> {
    Some(mode.as_raw() as u32)
}

fn depth_of(f: &vk::SurfaceFormatKHR) -> Option<u32> {
    format_semantic(f.format.as_raw() as u32).map(|facts| facts.depth)
}

fn numeric_of(f: &vk::SurfaceFormatKHR) -> Option<Numeric> {
    format_semantic(f.format.as_raw() as u32).map(|facts| facts.numeric)
}

fn space_of(f: &vk::SurfaceFormatKHR) -> Option<u32> {
    Some(f.color_space.as_raw() as u32)
}

fn surface_filtered(
    formats: Vec<vk::SurfaceFormatKHR>,
    s: &Settings,
) -> Vec<vk::SurfaceFormatKHR> {
    filtered(
        filtered(
            filtered(formats, s.depth, depth_of, DEPTH_EMPTY_WARN),
            s.color_space,
            space_of,
            SPACE_EMPTY_WARN,
        ),
        s.transfer,
        numeric_of,
        TRANSFER_EMPTY_WARN,
    )
}

fn present_filtered(
    modes: Vec<vk::PresentModeKHR>,
    choice: Option<u32>,
) -> Vec<vk::PresentModeKHR> {
    filtered(modes, choice, mode_value, PRESENT_EMPTY_WARN)
}

fn supported_mode(supported: &[vk::PresentModeKHR], value: u32) -> Option<vk::PresentModeKHR> {
    supported.iter().copied().find(|m| m.as_raw() as u32 == value)
}

fn logged_mode_miss(original: vk::PresentModeKHR) -> vk::PresentModeKHR {
    log_at(LogLevel::Warn, PRESENT_MISS_WARN);
    original
}

fn chosen_mode(
    supported: &[vk::PresentModeKHR],
    value: u32,
    original: vk::PresentModeKHR,
) -> vk::PresentModeKHR {
    match supported_mode(supported, value) {
        Some(mode) => mode,
        None => logged_mode_miss(original),
    }
}

fn pick_present_mode(
    choice: Option<u32>,
    supported: &[vk::PresentModeKHR],
    original: vk::PresentModeKHR,
) -> vk::PresentModeKHR {
    match choice {
        Some(value) => chosen_mode(supported, value, original),
        None => original,
    }
}

fn logged_alpha_miss(original: vk::CompositeAlphaFlagsKHR) -> vk::CompositeAlphaFlagsKHR {
    log_at(LogLevel::Warn, ALPHA_MISS_WARN);
    original
}

fn chosen_alpha(
    mask: vk::CompositeAlphaFlagsKHR,
    value: u32,
    original: vk::CompositeAlphaFlagsKHR,
) -> vk::CompositeAlphaFlagsKHR {
    match mask.as_raw() & value != 0 {
        true => vk::CompositeAlphaFlagsKHR::from_raw(value),
        false => logged_alpha_miss(original),
    }
}

fn pick_alpha(
    choice: Option<u32>,
    mask: vk::CompositeAlphaFlagsKHR,
    original: vk::CompositeAlphaFlagsKHR,
) -> vk::CompositeAlphaFlagsKHR {
    match choice {
        Some(value) => chosen_alpha(mask, value, original),
        None => original,
    }
}

fn toggle_vk(value: u32) -> vk::Bool32 {
    match value {
        TOGGLE_ON => vk::TRUE,
        _ => vk::FALSE,
    }
}

fn pick_clipped(choice: Option<u32>, original: vk::Bool32) -> vk::Bool32 {
    match choice {
        Some(value) => toggle_vk(value),
        None => original,
    }
}

fn caps_upper(caps_max: u32) -> u32 {
    match caps_max {
        0 => u32::MAX,
        n => n,
    }
}

fn pick_image_count(
    choice: Option<u32>,
    caps: &vk::SurfaceCapabilitiesKHR,
    original: u32,
) -> u32 {
    forced(choice, original).clamp(caps.min_image_count, caps_upper(caps.max_image_count))
}

fn reported_high(high: u32) -> u32 {
    match high {
        u32::MAX => 0,
        n => n,
    }
}

fn narrowed_caps(caps: vk::SurfaceCapabilitiesKHR, value: u32) -> vk::SurfaceCapabilitiesKHR {
    let held = value.clamp(caps.min_image_count, caps_upper(caps.max_image_count));
    vk::SurfaceCapabilitiesKHR {
        min_image_count: held,
        max_image_count: reported_high(held),
        ..caps
    }
}

fn clamped_caps(
    caps: vk::SurfaceCapabilitiesKHR,
    choice: Option<u32>,
) -> vk::SurfaceCapabilitiesKHR {
    match choice {
        Some(value) => narrowed_caps(caps, value),
        None => caps,
    }
}

fn log_extended(extended: bool, message: &str) {
    match extended {
        true => log_at(LogLevel::Info, message),
        false => (),
    }
}

fn maybe_log_space(choice: Option<u32>) {
    match choice.and_then(space_semantic) {
        Some(facts) => log_extended(facts.extended, SPACE_EXTENDED_INFO),
        None => (),
    }
}

fn maybe_log_present(choice: Option<u32>) {
    match choice.and_then(present_semantic) {
        Some(facts) => log_extended(facts.extended, PRESENT_EXTENDED_INFO),
        None => (),
    }
}

fn log_blending(blends: bool) {
    match blends {
        false => log_at(LogLevel::Info, ALPHA_OPAQUE_INFO),
        true => (),
    }
}

fn maybe_log_alpha(choice: Option<u32>) {
    match choice.and_then(alpha_semantic) {
        Some(facts) => log_blending(facts.blends),
        None => (),
    }
}

fn log_encoding(encoded: bool) {
    match encoded {
        true => log_at(LogLevel::Info, TRANSFER_ENCODED_INFO),
        false => log_at(LogLevel::Info, TRANSFER_SHADER_INFO),
    }
}

fn maybe_log_transfer(choice: Option<Numeric>) {
    match choice.and_then(numeric_semantic) {
        Some(facts) => log_encoding(facts.encoded),
        None => (),
    }
}

fn excluded<V: PartialEq>(choice: Option<V>, value: Option<V>) -> bool {
    match choice {
        Some(wanted) => value != Some(wanted),
        None => false,
    }
}

fn maybe_warn(kept_out: bool, warn: &str) {
    match kept_out {
        true => log_at(LogLevel::Warn, warn),
        false => (),
    }
}

fn warn_excluded_format(kept_out: bool, format: u32) {
    match kept_out {
        true => log_at(
            LogLevel::Warn,
            &format!("{}: {}", FORMAT_FORCED_WARN, format_display(format)),
        ),
        false => (),
    }
}

fn warn_excluded_choice(asked: vk::SurfaceFormatKHR, s: &Settings) {
    warn_excluded_format(
        excluded(s.depth, depth_of(&asked)),
        asked.format.as_raw() as u32,
    );
    maybe_warn(excluded(s.color_space, space_of(&asked)), SPACE_FORCED_WARN);
    maybe_warn(excluded(s.transfer, numeric_of(&asked)), TRANSFER_FORCED_WARN);
}

fn asked_format(original: &vk::SwapchainCreateInfoKHR) -> vk::SurfaceFormatKHR {
    vk::SurfaceFormatKHR {
        format: original.image_format,
        color_space: original.image_color_space,
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
        composite_alpha: pick_alpha(
            s.composite_alpha,
            caps.supported_composite_alpha,
            original.composite_alpha,
        ),
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
    maybe_log_transfer(s.transfer);
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

fn call_filtered_modes(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    choice: Option<u32>,
) -> Vec<vk::PresentModeKHR> {
    maybe_log_present(choice);
    present_filtered(call_query_present_modes(inst, phys, surface), choice)
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
            &call_filtered_modes(&inst, phys, surface, ensure_settings().present_mode),
            count,
            modes,
        ),
    }
}

fn call_narrowed_result(
    queried: vk::Result,
    out: *mut vk::SurfaceCapabilitiesKHR,
    choice: Option<u32>,
) -> vk::Result {
    match queried {
        vk::Result::SUCCESS => {
            unsafe { *out = clamped_caps(*out, choice) };
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
    choice: Option<u32>,
) -> vk::Result {
    match unsafe { fp(phys, info, out) } {
        vk::Result::SUCCESS => {
            unsafe {
                (*out).surface_capabilities = clamped_caps((*out).surface_capabilities, choice)
            };
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
    offsets.iter().enumerate().for_each(|(at, from)| unsafe {
        (*out.add(at)).surface_format = (*out.add(*from)).surface_format
    });
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
    maybe_log_transfer(s.transfer);
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
