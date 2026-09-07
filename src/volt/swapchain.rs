use std::ffi::c_void;
use std::ptr;

use ash::vk;
use ash::vk::Handle;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::ALPHA_MISS_WARN;
use crate::consts::ALPHA_OPAQUE_INFO;
use crate::consts::MODE_LIST_TYPES;
use crate::consts::PRESENT_EMPTY_WARN;
use crate::consts::PRESENT_EXTENDED_INFO;
use crate::consts::PRESENT_MISS_WARN;
use crate::consts::SETTING_CLIPPED;
use crate::consts::SETTING_COMPOSITE_ALPHA;
use crate::consts::SETTING_FRAME_LIMIT;
use crate::consts::SETTING_FRAME_LIMIT_CADENCE;
use crate::consts::SETTING_FRAME_LIMIT_METHOD;
use crate::consts::SETTING_FRAME_LIMIT_OFFSET;
use crate::consts::SETTING_FRAME_PACING;
use crate::consts::SETTING_IMAGE_COUNT;
use crate::consts::SETTING_PRESENT_MODE;
use crate::consts::TOGGLE_ON;
use crate::device::VkDevState;
use crate::env::env_probe_active;
use crate::instance::call_write_list;
use crate::instance::insts_get;
use crate::instance::owning_instance;
use crate::instance::PfnCreateSharedSwapchains;
use crate::instance::PfnSurfaceCaps2;
use crate::instance::PfnSurfaceModes2;
use crate::instance::VkChainNode;
use crate::instance::VkInstState;
use crate::instance::VkPhysicalDeviceSurfaceInfo2;
use crate::instance::VkPresentModeList;
use crate::instance::VkSurfaceCapabilities2;
use crate::lists::filtered;
use crate::lists::forced;
use crate::logging::info_wanted;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::present::cadence_display;
use crate::present::method_display;
use crate::present::pacing_display;
use crate::probe::build_probe;
use crate::probe::call_write_probe;
use crate::ranks::alpha_display;
use crate::ranks::alpha_semantic;
use crate::ranks::present_display;
use crate::ranks::present_semantic;
use crate::report::call_report_choice;
use crate::report::call_report_value;
use crate::report::count_text;
use crate::report::number_text;
use crate::report::toggle_text;

fn mode_value(mode: &vk::PresentModeKHR) -> Option<u32> {
    Some(mode.as_raw() as u32)
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

fn call_report_display(
    owner: u64,
    s: &Settings,
    asked: &vk::SwapchainCreateInfoKHR<'_>,
    held: &vk::SwapchainCreateInfoKHR<'_>,
) {
    call_report_value(
        owner,
        SETTING_PRESENT_MODE,
        s.present_mode.is_some(),
        asked.present_mode.as_raw() as u32,
        held.present_mode.as_raw() as u32,
        present_display,
        None,
    );
    call_report_value(
        owner,
        SETTING_IMAGE_COUNT,
        s.image_count.is_some(),
        asked.min_image_count,
        held.min_image_count,
        count_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_COMPOSITE_ALPHA,
        s.composite_alpha.is_some(),
        asked.composite_alpha.as_raw(),
        held.composite_alpha.as_raw(),
        alpha_display,
        None,
    );
    call_report_value(
        owner,
        SETTING_CLIPPED,
        s.clipped.is_some(),
        asked.clipped,
        held.clipped,
        toggle_text,
        None,
    );
}

fn call_report_framerate(owner: u64, s: &Settings) {
    call_report_choice(owner, SETTING_FRAME_LIMIT, s.frame_limit.map(number_text));
    call_report_choice(
        owner,
        SETTING_FRAME_LIMIT_OFFSET,
        s.frame_limit_offset.map(number_text),
    );
    call_report_choice(
        owner,
        SETTING_FRAME_LIMIT_CADENCE,
        s.cadence.map(cadence_display),
    );
    call_report_choice(
        owner,
        SETTING_FRAME_LIMIT_METHOD,
        s.limit_method.map(method_display),
    );
    call_report_choice(owner, SETTING_FRAME_PACING, s.pacing.map(pacing_display));
}

fn call_report_fields(
    owner: u64,
    s: &Settings,
    asked: &vk::SwapchainCreateInfoKHR<'_>,
    held: &vk::SwapchainCreateInfoKHR<'_>,
) {
    call_report_display(owner, s, asked, held);
    call_report_framerate(owner, s);
}

fn call_report_swapchain(
    dev: &VkDevState,
    s: &Settings,
    asked: &vk::SwapchainCreateInfoKHR<'_>,
    held: &vk::SwapchainCreateInfoKHR<'_>,
) {
    match info_wanted() {
        true => call_report_fields(dev.device.handle().as_raw(), s, asked, held),
        false => (),
    }
}

fn patched_swapchain_ci<'a>(
    original: &vk::SwapchainCreateInfoKHR<'a>,
    chosen: vk::PresentModeKHR,
    caps: &vk::SurfaceCapabilitiesKHR,
    s: &Settings,
) -> vk::SwapchainCreateInfoKHR<'a> {
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

fn non_null_node(p: *mut c_void) -> Option<*mut VkChainNode> {
    match p.is_null() {
        true => None,
        false => Some(p as *mut VkChainNode),
    }
}

fn chain_nodes(head: *mut c_void) -> Vec<*mut VkChainNode> {
    std::iter::successors(non_null_node(head), |node| {
        non_null_node(unsafe { (**node).p_next })
    })
    .collect()
}

fn node_type(node: *mut VkChainNode) -> u32 {
    unsafe { (*node).s_type.as_raw() as u32 }
}

fn mode_lists(head: *mut c_void) -> Vec<*mut VkPresentModeList> {
    chain_nodes(head)
        .into_iter()
        .filter(|node| MODE_LIST_TYPES.contains(&node_type(*node)))
        .map(|node| node as *mut VkPresentModeList)
        .collect()
}

fn call_read_modes(list: *mut VkPresentModeList) -> Vec<vk::PresentModeKHR> {
    (0..unsafe { (*list).present_mode_count } as usize)
        .map(|at| unsafe { *(*list).p_present_modes.add(at) })
        .collect()
}

fn call_write_modes(list: *mut VkPresentModeList, kept_modes: &[vk::PresentModeKHR]) {
    kept_modes
        .iter()
        .enumerate()
        .for_each(|(at, mode)| unsafe { *(*list).p_present_modes.add(at) = *mode });
    unsafe { (*list).present_mode_count = kept_modes.len() as u32 };
}

fn call_filtered_mode_list(list: *mut VkPresentModeList, choice: Option<u32>) {
    match unsafe { (*list).p_present_modes.is_null() } {
        true => (),
        false => call_write_modes(list, &present_filtered(call_read_modes(list), choice)),
    }
}

fn call_filtered_chain(head: *mut c_void, choice: Option<u32>) {
    mode_lists(head)
        .into_iter()
        .for_each(|list| call_filtered_mode_list(list, choice));
}

fn call_caps2_through(
    fp: PfnSurfaceCaps2,
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
    out: *mut VkSurfaceCapabilities2,
    s: &Settings,
) -> vk::Result {
    match unsafe { fp(phys, info, out) } {
        vk::Result::SUCCESS => {
            unsafe {
                (*out).surface_capabilities =
                    clamped_caps((*out).surface_capabilities, s.image_count)
            };
            call_filtered_chain(unsafe { (*out).p_next }, s.present_mode);
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
        Some(fp) => call_caps2_through(fp, phys, info, out, ensure_settings()),
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
    supported: &[vk::PresentModeKHR],
    caps: &vk::SurfaceCapabilitiesKHR,
) {
    match env_probe_active() {
        true => call_write_probe(build_probe(inst, dev, supported, caps)),
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

fn call_prepared_ci<'a>(
    inst: &VkInstState,
    dev: &VkDevState,
    original: &vk::SwapchainCreateInfoKHR<'a>,
    s: &Settings,
) -> vk::SwapchainCreateInfoKHR<'a> {
    let supported = call_query_present_modes(inst, dev.phys, original.surface);
    let caps = call_query_surface_caps(inst, dev.phys, original.surface);
    maybe_probe(inst, dev, &supported, &caps);
    maybe_log_alpha(s.composite_alpha);
    let patched = patched_swapchain_ci(
        original,
        pick_present_mode(s.present_mode, &supported, original.present_mode),
        &caps,
        s,
    );
    call_report_swapchain(dev, s, original, &patched);
    patched
}

fn call_create_registered(
    dev: &VkDevState,
    handle: vk::Device,
    inst: &VkInstState,
    original: &vk::SwapchainCreateInfoKHR<'_>,
    s: &Settings,
    alloc: *const vk::AllocationCallbacks<'_>,
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
    ci: *const vk::SwapchainCreateInfoKHR<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    let s = ensure_settings();
    match insts_get(dev.instance_handle) {
        Some(inst) => call_create_registered(dev, handle, &inst, unsafe { &*ci }, s, alloc, out),
        None => unsafe { (dev.swap_fp.create_swapchain_khr)(handle, ci, alloc, out) },
    }
}

fn call_shared_patched<'a>(
    dev: &VkDevState,
    inst: &VkInstState,
    cis: *const vk::SwapchainCreateInfoKHR<'a>,
    count: u32,
    s: &Settings,
) -> Vec<vk::SwapchainCreateInfoKHR<'a>> {
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
    cis: *const vk::SwapchainCreateInfoKHR<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
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
    cis: *const vk::SwapchainCreateInfoKHR<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    match (dev.shared_fp, insts_get(dev.instance_handle)) {
        (Some(fp), Some(inst)) => {
            call_shared_through(dev, &inst, fp, handle, count, cis, alloc, out)
        }
        (_, _) => vk::Result::ERROR_INITIALIZATION_FAILED,
    }
}
