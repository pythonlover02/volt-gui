use std::collections::HashMap;
use std::collections::HashSet;
use std::ffi::c_void;
use std::ptr;
use std::sync::Mutex;

use ash::vk;
use ash::vk::Handle;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::ALPHA_MISS_WARN;
use crate::consts::ALPHA_OPAQUE_INFO;
use crate::consts::COUNT_SHARED_REASON;
use crate::consts::EXT_GET_SURFACE_CAPS_2;
use crate::consts::EXT_SURFACE_MAINTENANCE_1;
use crate::consts::EXT_SURFACE_MAINTENANCE_1_EXT;
use crate::consts::LOG_SWAPCHAIN_CREATED;
use crate::consts::MODE_COMPATIBILITY_TYPE;
use crate::consts::MODE_LIST_TYPES;
use crate::consts::NO_FLAGS;
use crate::consts::NO_IMAGE_LIMIT;
use crate::consts::PRESENT_EMPTY_WARN;
use crate::consts::PRESENT_ABOVE_FLOOR_REASON;
use crate::consts::PRESENT_LIST_REASON;
use crate::consts::PRESENT_MISS_WARN;
use crate::consts::PRESENT_TIE_REASON;
use crate::consts::SETTING_CLIPPED;
use crate::consts::SETTING_COMPOSITE_ALPHA;
use crate::consts::SETTING_FRAME_LIMIT;
use crate::consts::SETTING_FRAME_LIMIT_CADENCE;
use crate::consts::SETTING_FRAME_LIMIT_METHOD;
use crate::consts::SETTING_FRAME_LIMIT_OFFSET;
use crate::consts::SETTING_FRAME_PACING;
use crate::consts::SETTING_IMAGE_COUNT;
use crate::consts::SETTING_PRESENT_MODE;
use crate::consts::SURFACE_CAPABILITIES_2_TYPE;
use crate::consts::SURFACE_INFO_2_TYPE;
use crate::consts::SURFACE_PRESENT_MODE_TYPE;
use crate::consts::SWAPCHAIN_MODE_LIST_TYPE;
use crate::consts::SWAPCHAIN_PRESENT_MODE_INFO_TYPE;
use crate::consts::SWAPCHAIN_PRESENT_SCALING_TYPE;
use crate::device::VkDevState;
use crate::env::env_probe_active;
use crate::instance::call_relinked_chain;
use crate::instance::call_write_list;
use crate::instance::chain_find;
use crate::instance::filled_nodes;
use crate::instance::insts_get;
use crate::instance::owning_instance;
use crate::instance::surface_tag;
use crate::instance::PfnCreateSharedSwapchains;
use crate::instance::PfnSurfaceCaps2;
use crate::instance::VkChainNode;
use crate::instance::VkInstState;
use crate::instance::VkPhysicalDeviceSurfaceInfo2;
use crate::instance::Relinked;
use crate::instance::VkPresentModeList;
use crate::instance::VkSurfaceCapabilities2;
use crate::instance::VkSurfacePresentModeKHR;
use crate::instance::VkSwapchainPresentModeInfoKHR;
use crate::instance::VkSwapchainPresentModesCreateInfoKHR;
use crate::instance::VkSwapchainPresentScalingCreateInfoKHR;
use crate::lists::call_warned;
use crate::lists::forced;
use crate::lists::untouched;
use crate::lists::Narrowed;
use crate::logging::info_wanted;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::present::cadence_display;
use crate::present::method_display;
use crate::present::pacing_display;
use crate::probe::build_surface;
use crate::probe::call_record_surface;
use crate::ranks::alpha_display;
use crate::ranks::alpha_semantic;
use crate::ranks::present_display;
use crate::ranks::present_semantic;
use crate::report::call_report_choice;
use crate::report::call_report_reason;
use crate::report::call_report_value;
use crate::report::count_text;
use crate::report::number_text;
use crate::report::toggle_text;

fn on_floor(mode: vk::PresentModeKHR) -> bool {
    present_semantic(mode).is_some_and(|facts| facts.floor)
}

fn present_kept(mode: vk::PresentModeKHR, choice: vk::PresentModeKHR) -> bool {
    match on_floor(mode) {
        true => mode == choice,
        false => true,
    }
}

fn floor_survived(modes: &[vk::PresentModeKHR]) -> bool {
    modes.iter().copied().any(on_floor)
}

fn restored_modes(
    narrowed: Vec<vk::PresentModeKHR>,
    modes: Vec<vk::PresentModeKHR>,
) -> Narrowed<vk::PresentModeKHR> {
    match floor_survived(&narrowed) {
        true => untouched(narrowed),
        false => Narrowed {
            items: modes,
            restored: true,
        },
    }
}

pub(crate) fn present_narrowed(
    modes: Vec<vk::PresentModeKHR>,
    choice: Option<vk::PresentModeKHR>,
) -> Narrowed<vk::PresentModeKHR> {
    match choice {
        None => untouched(modes),
        Some(value) => restored_modes(
            modes
                .iter()
                .copied()
                .filter(|mode| present_kept(*mode, value))
                .collect(),
            modes,
        ),
    }
}

fn call_present_filtered(
    modes: Vec<vk::PresentModeKHR>,
    choice: Option<vk::PresentModeKHR>,
) -> Vec<vk::PresentModeKHR> {
    call_warned(present_narrowed(modes, choice), PRESENT_EMPTY_WARN)
}

fn supported_mode(
    supported: &[vk::PresentModeKHR],
    value: vk::PresentModeKHR,
) -> Option<vk::PresentModeKHR> {
    supported.iter().copied().find(|m| *m == value)
}

fn logged_mode_miss(original: vk::PresentModeKHR) -> vk::PresentModeKHR {
    log_at(LogLevel::Warn, PRESENT_MISS_WARN);
    original
}

fn chosen_mode(
    supported: &[vk::PresentModeKHR],
    value: vk::PresentModeKHR,
    original: vk::PresentModeKHR,
) -> vk::PresentModeKHR {
    match supported_mode(supported, value) {
        Some(mode) => mode,
        None => logged_mode_miss(original),
    }
}

fn scaling_set(node: *const VkSwapchainPresentScalingCreateInfoKHR) -> bool {
    unsafe {
        (*node).scaling_behavior != NO_FLAGS
            || (*node).present_gravity_x != NO_FLAGS
            || (*node).present_gravity_y != NO_FLAGS
    }
}

fn scaling_chained(p_next: *const c_void) -> bool {
    match chain_find(p_next, SWAPCHAIN_PRESENT_SCALING_TYPE) {
        Some(node) => scaling_set(node as *const VkSwapchainPresentScalingCreateInfoKHR),
        None => false,
    }
}

pub(crate) fn mode_tie_holds(
    flags: vk::SwapchainCreateFlagsKHR,
    p_next: *const c_void,
) -> bool {
    flags.as_raw() == NO_FLAGS && !scaling_chained(p_next)
}

fn pick_present_mode(
    choice: Option<vk::PresentModeKHR>,
    supported: &[vk::PresentModeKHR],
    tie_holds: bool,
    original: vk::PresentModeKHR,
) -> vk::PresentModeKHR {
    match (choice, tie_holds, on_floor(original)) {
        (Some(value), true, true) => chosen_mode(supported, value, original),
        (_, _, _) => original,
    }
}

fn logged_alpha_miss(original: vk::CompositeAlphaFlagsKHR) -> vk::CompositeAlphaFlagsKHR {
    log_at(LogLevel::Warn, ALPHA_MISS_WARN);
    original
}

fn chosen_alpha(
    mask: vk::CompositeAlphaFlagsKHR,
    value: vk::CompositeAlphaFlagsKHR,
    original: vk::CompositeAlphaFlagsKHR,
) -> vk::CompositeAlphaFlagsKHR {
    match value.as_raw() != NO_FLAGS && mask.as_raw() & value.as_raw() == value.as_raw() {
        true => value,
        false => logged_alpha_miss(original),
    }
}

fn narrowed_alpha_mask(
    mask: vk::CompositeAlphaFlagsKHR,
    choice: Option<vk::CompositeAlphaFlagsKHR>,
) -> vk::CompositeAlphaFlagsKHR {
    match choice {
        Some(value) if mask.as_raw() & value.as_raw() == value.as_raw() => value,
        _ => mask,
    }
}

fn narrowed_alpha(
    caps: vk::SurfaceCapabilitiesKHR,
    choice: Option<vk::CompositeAlphaFlagsKHR>,
) -> vk::SurfaceCapabilitiesKHR {
    vk::SurfaceCapabilitiesKHR {
        supported_composite_alpha: narrowed_alpha_mask(caps.supported_composite_alpha, choice),
        ..caps
    }
}

fn pick_alpha(
    choice: Option<vk::CompositeAlphaFlagsKHR>,
    mask: Option<vk::CompositeAlphaFlagsKHR>,
    original: vk::CompositeAlphaFlagsKHR,
) -> vk::CompositeAlphaFlagsKHR {
    match (choice, mask) {
        (Some(value), Some(held)) => chosen_alpha(held, value, original),
        (_, _) => original,
    }
}

fn pick_clipped(choice: Option<vk::Bool32>, original: vk::Bool32) -> vk::Bool32 {
    forced(choice, original)
}

fn caps_upper(caps_max: u32) -> u32 {
    match caps_max {
        NO_IMAGE_LIMIT => u32::MAX,
        n => n,
    }
}

fn clamped_count(choice: Option<u32>, caps: &vk::SurfaceCapabilitiesKHR, original: u32) -> u32 {
    match choice {
        Some(value) => value.clamp(caps.min_image_count, caps_upper(caps.max_image_count)),
        None => original,
    }
}

fn pick_image_count(
    choice: Option<u32>,
    caps: Option<&vk::SurfaceCapabilitiesKHR>,
    mode: vk::PresentModeKHR,
    original: u32,
) -> u32 {
    match (present_semantic(mode).is_some_and(|facts| facts.shared), caps) {
        (false, Some(held)) => clamped_count(choice, held, original),
        (_, _) => original,
    }
}

fn reported_high(high: u32) -> u32 {
    match high {
        u32::MAX => NO_IMAGE_LIMIT,
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

fn call_log_blending(blends: bool) {
    match blends {
        false => log_at(LogLevel::Info, ALPHA_OPAQUE_INFO),
        true => (),
    }
}

fn call_log_alpha(choice: Option<vk::CompositeAlphaFlagsKHR>) {
    match choice.and_then(alpha_semantic) {
        Some(facts) => call_log_blending(facts.blends),
        None => (),
    }
}

fn present_note(
    choice: Option<vk::PresentModeKHR>,
    tie_holds: bool,
    original: vk::PresentModeKHR,
) -> Option<&'static str> {
    match (choice, on_floor(original), tie_holds) {
        (None, _, _) => None,
        (Some(_), false, _) => Some(PRESENT_ABOVE_FLOOR_REASON),
        (Some(_), true, false) => Some(PRESENT_TIE_REASON),
        (Some(_), true, true) => None,
    }
}

fn count_note(choice: Option<u32>, mode: vk::PresentModeKHR) -> Option<&'static str> {
    match (choice, present_semantic(mode).is_some_and(|facts| facts.shared)) {
        (Some(_), true) => Some(COUNT_SHARED_REASON),
        (_, _) => None,
    }
}

fn call_report_display(
    owner: u64,
    asked: &vk::SwapchainCreateInfoKHR<'_>,
    held: &vk::SwapchainCreateInfoKHR<'_>,
) {
    call_report_value(
        owner,
        SETTING_PRESENT_MODE,
        asked.present_mode,
        held.present_mode,
        present_display,
        None,
    );
    call_report_value(
        owner,
        SETTING_IMAGE_COUNT,
        asked.min_image_count,
        held.min_image_count,
        count_text,
        None,
    );
    call_report_value(
        owner,
        SETTING_COMPOSITE_ALPHA,
        asked.composite_alpha,
        held.composite_alpha,
        alpha_display,
        None,
    );
    call_report_value(
        owner,
        SETTING_CLIPPED,
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
    call_report_display(owner, asked, held);
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
    caps: Option<&vk::SurfaceCapabilitiesKHR>,
    s: &Settings,
) -> vk::SwapchainCreateInfoKHR<'a> {
    vk::SwapchainCreateInfoKHR {
        present_mode: chosen,
        min_image_count: pick_image_count(s.image_count, caps, chosen, original.min_image_count),
        composite_alpha: pick_alpha(
            s.composite_alpha,
            caps.map(|held| held.supported_composite_alpha),
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
) -> Option<vk::SurfaceCapabilitiesKHR> {
    let mut caps = vk::SurfaceCapabilitiesKHR::default();
    match unsafe {
        (inst.surface_fp.get_physical_device_surface_capabilities_khr)(phys, surface, &mut caps)
    } {
        vk::Result::SUCCESS => Some(caps),
        _ => None,
    }
}

fn call_filtered_modes(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    choice: Option<vk::PresentModeKHR>,
) -> Vec<vk::PresentModeKHR> {
    call_present_filtered(call_query_present_modes(inst, phys, surface), choice)
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
    s: &Settings,
) -> vk::Result {
    match queried {
        vk::Result::SUCCESS => {
            unsafe { *out = narrowed_alpha(clamped_caps(*out, s.image_count), s.composite_alpha) };
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
            ensure_settings(),
        ),
    }
}

fn node_type(node: *mut VkChainNode) -> u32 {
    unsafe { (*node).s_type.as_raw() as u32 }
}

fn mode_lists(head: *mut c_void) -> Vec<*mut VkPresentModeList> {
    filled_nodes(head)
        .into_iter()
        .filter(|node| MODE_LIST_TYPES.contains(&node_type(*node)))
        .map(|node| node as *mut VkPresentModeList)
        .collect()
}

fn read_modes(list: *mut VkPresentModeList) -> Vec<vk::PresentModeKHR> {
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

fn call_filtered_mode_list(list: *mut VkPresentModeList, choice: Option<vk::PresentModeKHR>) {
    match unsafe { (*list).p_present_modes.is_null() } {
        true => (),
        false => call_write_modes(list, &call_present_filtered(read_modes(list), choice)),
    }
}

fn call_filtered_chain(head: *mut c_void, choice: Option<vk::PresentModeKHR>) {
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
                (*out).surface_capabilities = narrowed_alpha(
                    clamped_caps((*out).surface_capabilities, s.image_count),
                    s.composite_alpha,
                )
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

fn call_probe_surface(
    tag: Option<&'static str>,
    supported: &[vk::PresentModeKHR],
    caps: Option<&vk::SurfaceCapabilitiesKHR>,
) {
    match (env_probe_active(), tag, caps) {
        (true, Some(name), Some(held)) => {
            call_record_surface(name, build_surface(supported, held))
        }
        (_, _, _) => (),
    }
}

static FORCED_MODES: Mutex<Option<HashMap<(u64, u64), vk::PresentModeKHR>>> = Mutex::new(None);

fn call_remember_forced(dev: u64, swapchain: u64, mode: vk::PresentModeKHR) {
    match FORCED_MODES.lock() {
        Ok(mut guard) => {
            guard
                .get_or_insert_with(HashMap::new)
                .insert((dev, swapchain), mode);
        }
        Err(_) => (),
    }
}

pub(crate) fn call_forget_forced_mode(dev: u64, swapchain: vk::SwapchainKHR) {
    match FORCED_MODES.lock() {
        Ok(mut guard) => {
            guard
                .get_or_insert_with(HashMap::new)
                .remove(&(dev, swapchain.as_raw()));
        }
        Err(_) => (),
    }
}

pub(crate) fn call_forget_device_forced_modes(dev: u64) {
    match FORCED_MODES.lock() {
        Ok(mut guard) => guard
            .get_or_insert_with(HashMap::new)
            .retain(|(owner, _), _| *owner != dev),
        Err(_) => (),
    }
}

fn forced_mode_for(dev: u64, swapchain: u64) -> Option<vk::PresentModeKHR> {
    FORCED_MODES
        .lock()
        .ok()
        .and_then(|guard| guard.as_ref().and_then(|m| m.get(&(dev, swapchain)).copied()))
}

fn compatibility_allowed(extensions: &HashSet<String>) -> bool {
    extensions.contains(EXT_GET_SURFACE_CAPS_2)
        && (extensions.contains(EXT_SURFACE_MAINTENANCE_1)
            || extensions.contains(EXT_SURFACE_MAINTENANCE_1_EXT))
}

fn surface_mode_node(forced: vk::PresentModeKHR) -> VkSurfacePresentModeKHR {
    VkSurfacePresentModeKHR {
        s_type: vk::StructureType::from_raw(SURFACE_PRESENT_MODE_TYPE as i32),
        p_next: ptr::null_mut(),
        present_mode: forced,
    }
}

fn compatibility_node(modes: *mut vk::PresentModeKHR, count: u32) -> VkPresentModeList {
    VkPresentModeList {
        s_type: vk::StructureType::from_raw(MODE_COMPATIBILITY_TYPE as i32),
        p_next: ptr::null_mut(),
        present_mode_count: count,
        p_present_modes: modes,
    }
}

fn capabilities_2(chained: *mut c_void) -> VkSurfaceCapabilities2 {
    VkSurfaceCapabilities2 {
        s_type: vk::StructureType::from_raw(SURFACE_CAPABILITIES_2_TYPE as i32),
        p_next: chained,
        surface_capabilities: vk::SurfaceCapabilitiesKHR::default(),
    }
}

fn call_compatibility_list(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    forced: vk::PresentModeKHR,
) -> Option<Vec<vk::PresentModeKHR>> {
    let fp = inst.caps2_fp?;
    let mode_info = surface_mode_node(forced);
    let info = VkPhysicalDeviceSurfaceInfo2 {
        s_type: vk::StructureType::from_raw(SURFACE_INFO_2_TYPE as i32),
        p_next: &mode_info as *const VkSurfacePresentModeKHR as *const c_void,
        surface,
    };
    let mut counting = compatibility_node(ptr::null_mut(), 0);
    let mut caps = capabilities_2(&mut counting as *mut VkPresentModeList as *mut c_void);
    let counted = unsafe { fp(phys, &info, &mut caps) };
    let mut modes = vec![vk::PresentModeKHR::FIFO; counting.present_mode_count as usize];
    let mut filling = compatibility_node(modes.as_mut_ptr(), counting.present_mode_count);
    let mut out = capabilities_2(&mut filling as *mut VkPresentModeList as *mut c_void);
    let filled = unsafe { fp(phys, &info, &mut out) };
    match (counted, filled) {
        (vk::Result::SUCCESS, vk::Result::SUCCESS) => {
            Some(modes[..filling.present_mode_count as usize].to_vec())
        }
        (_, _) => None,
    }
}

fn call_compatible(
    inst: &VkInstState,
    dev: &VkDevState,
    surface: vk::SurfaceKHR,
    forced: vk::PresentModeKHR,
) -> bool {
    compatibility_allowed(&inst.extensions)
        && call_compatibility_list(inst, dev.phys, surface, forced)
            .map(|list| list.contains(&forced))
            .unwrap_or(false)
}

fn call_created_swapchain(created: vk::Result) -> vk::Result {
    match created {
        vk::Result::SUCCESS => {
            log_at(LogLevel::Info, LOG_SWAPCHAIN_CREATED);
            vk::Result::SUCCESS
        }
        e => e,
    }
}

pub(crate) struct SwapchainRebuild<'a> {
    #[allow(dead_code)]
    modes: Vec<vk::PresentModeKHR>,
    #[allow(dead_code)]
    node: Vec<VkSwapchainPresentModesCreateInfoKHR>,
    #[allow(dead_code)]
    relink: Option<Relinked>,
    pub(crate) forced: Option<vk::PresentModeKHR>,
    pub(crate) ci: vk::SwapchainCreateInfoKHR<'a>,
}

pub(crate) struct PresentRebuild<'a> {
    #[allow(dead_code)]
    modes: Vec<vk::PresentModeKHR>,
    #[allow(dead_code)]
    node: Vec<VkSwapchainPresentModeInfoKHR>,
    #[allow(dead_code)]
    relink: Relinked,
    pub(crate) info: vk::PresentInfoKHR<'a>,
}

fn spent_mode(dev: u64, swapchain: vk::SwapchainKHR, asked: vk::PresentModeKHR) -> vk::PresentModeKHR {
    match forced_mode_for(dev, swapchain.as_raw()) {
        Some(mode) => mode,
        None => asked,
    }
}

fn spent_modes(
    dev: u64,
    info: &vk::PresentInfoKHR<'_>,
    node: *const VkSwapchainPresentModeInfoKHR,
) -> Vec<vk::PresentModeKHR> {
    (0..unsafe { (*node).swapchain_count } as usize)
        .map(|at| {
            spent_mode(
                dev,
                unsafe { *info.p_swapchains.add(at) },
                unsafe { *(*node).p_present_modes.add(at) },
            )
        })
        .collect()
}

fn rebuilt_mode_info(
    node: *const VkSwapchainPresentModeInfoKHR,
    modes: &[vk::PresentModeKHR],
) -> VkSwapchainPresentModeInfoKHR {
    VkSwapchainPresentModeInfoKHR {
        p_present_modes: modes.as_ptr(),
        ..unsafe { *node }
    }
}

fn asked_modes(node: *const VkSwapchainPresentModeInfoKHR) -> Vec<vk::PresentModeKHR> {
    (0..unsafe { (*node).swapchain_count } as usize)
        .map(|at| unsafe { *(*node).p_present_modes.add(at) })
        .collect()
}

fn built_present<'a>(
    dev: u64,
    info: &vk::PresentInfoKHR<'a>,
    node: *const VkSwapchainPresentModeInfoKHR,
) -> Option<PresentRebuild<'a>> {
    let modes = spent_modes(dev, info, node);
    match modes == asked_modes(node) {
        true => None,
        false => call_linked_present(info, node, modes),
    }
}

fn call_linked_present<'a>(
    info: &vk::PresentInfoKHR<'a>,
    node: *const VkSwapchainPresentModeInfoKHR,
    modes: Vec<vk::PresentModeKHR>,
) -> Option<PresentRebuild<'a>> {
    let owned = vec![rebuilt_mode_info(node, &modes)];
    let relink = call_relinked_chain(
        info.p_next,
        SWAPCHAIN_PRESENT_MODE_INFO_TYPE,
        owned.as_ptr() as *const c_void,
        SETTING_PRESENT_MODE,
    )?;
    Some(PresentRebuild {
        info: vk::PresentInfoKHR {
            p_next: relink.head,
            ..*info
        },
        modes,
        node: owned,
        relink,
    })
}

pub(crate) fn rebuilt_present<'a>(
    dev: u64,
    info: &vk::PresentInfoKHR<'a>,
) -> Option<PresentRebuild<'a>> {
    built_present(
        dev,
        info,
        chain_find(info.p_next, SWAPCHAIN_PRESENT_MODE_INFO_TYPE)?
            as *const VkSwapchainPresentModeInfoKHR,
    )
}

fn rebuilt_mode_node(
    node: *const VkSwapchainPresentModesCreateInfoKHR,
    modes: &[vk::PresentModeKHR],
) -> VkSwapchainPresentModesCreateInfoKHR {
    VkSwapchainPresentModesCreateInfoKHR {
        present_mode_count: modes.len() as u32,
        p_present_modes: modes.as_ptr(),
        ..unsafe { *node }
    }
}

fn plain_swapchain(patched: vk::SwapchainCreateInfoKHR<'_>) -> SwapchainRebuild<'_> {
    SwapchainRebuild {
        modes: Vec::new(),
        node: Vec::new(),
        relink: None,
        forced: None,
        ci: patched,
    }
}

fn kept_swapchain<'a>(
    original: &vk::SwapchainCreateInfoKHR<'a>,
    patched: vk::SwapchainCreateInfoKHR<'a>,
) -> SwapchainRebuild<'a> {
    plain_swapchain(vk::SwapchainCreateInfoKHR {
        present_mode: original.present_mode,
        ..patched
    })
}

fn call_rebuilt_swapchain<'a>(
    original: &vk::SwapchainCreateInfoKHR<'a>,
    patched: vk::SwapchainCreateInfoKHR<'a>,
    node: *const VkSwapchainPresentModesCreateInfoKHR,
) -> SwapchainRebuild<'a> {
    let modes = vec![patched.present_mode];
    let owned = vec![rebuilt_mode_node(node, &modes)];
    match call_relinked_chain(
        patched.p_next,
        SWAPCHAIN_MODE_LIST_TYPE,
        owned.as_ptr() as *const c_void,
        SETTING_PRESENT_MODE,
    ) {
        Some(relink) => SwapchainRebuild {
            ci: vk::SwapchainCreateInfoKHR {
                p_next: relink.head,
                ..patched
            },
            forced: Some(patched.present_mode),
            modes,
            node: owned,
            relink: Some(relink),
        },
        None => kept_swapchain(original, patched),
    }
}

fn call_refused_swapchain<'a>(
    original: &vk::SwapchainCreateInfoKHR<'a>,
    patched: vk::SwapchainCreateInfoKHR<'a>,
) -> SwapchainRebuild<'a> {
    call_report_reason(SETTING_PRESENT_MODE, Some(PRESENT_LIST_REASON));
    kept_swapchain(original, patched)
}

fn call_listed_swapchain<'a>(
    inst: &VkInstState,
    dev: &VkDevState,
    original: &vk::SwapchainCreateInfoKHR<'a>,
    patched: vk::SwapchainCreateInfoKHR<'a>,
    node: *const VkSwapchainPresentModesCreateInfoKHR,
) -> SwapchainRebuild<'a> {
    match call_compatible(inst, dev, original.surface, patched.present_mode) {
        true => call_rebuilt_swapchain(original, patched, node),
        false => call_refused_swapchain(original, patched),
    }
}

fn call_narrowed_swapchain<'a>(
    inst: &VkInstState,
    dev: &VkDevState,
    original: &vk::SwapchainCreateInfoKHR<'a>,
    patched: vk::SwapchainCreateInfoKHR<'a>,
    landed: bool,
) -> SwapchainRebuild<'a> {
    match (landed, chain_find(patched.p_next, SWAPCHAIN_MODE_LIST_TYPE)) {
        (true, Some(node)) => call_listed_swapchain(
            inst,
            dev,
            original,
            patched,
            node as *const VkSwapchainPresentModesCreateInfoKHR,
        ),
        (_, _) => plain_swapchain(patched),
    }
}

fn call_prepared_ci<'a>(
    inst: &VkInstState,
    dev: &VkDevState,
    original: &vk::SwapchainCreateInfoKHR<'a>,
    s: &Settings,
) -> SwapchainRebuild<'a> {
    let supported = call_query_present_modes(inst, dev.phys, original.surface);
    let caps = call_query_surface_caps(inst, dev.phys, original.surface);
    call_probe_surface(
        surface_tag(vk::Instance::from_raw(dev.instance_handle), original.surface),
        &supported,
        caps.as_ref(),
    );
    call_log_alpha(s.composite_alpha);
    let tie_holds = mode_tie_holds(original.flags, original.p_next);
    let patched = patched_swapchain_ci(
        original,
        pick_present_mode(s.present_mode, &supported, tie_holds, original.present_mode),
        caps.as_ref(),
        s,
    );
    let built = call_narrowed_swapchain(
        inst,
        dev,
        original,
        patched,
        tie_holds && s.present_mode == Some(patched.present_mode),
    );
    call_report_reason(
        SETTING_PRESENT_MODE,
        present_note(s.present_mode, tie_holds, original.present_mode),
    );
    call_report_reason(
        SETTING_IMAGE_COUNT,
        count_note(s.image_count, original.present_mode),
    );
    call_report_swapchain(dev, s, original, &built.ci);
    built
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
    let built = call_prepared_ci(inst, dev, original, s);
    call_recorded_swapchain(
        call_created_swapchain(unsafe {
            (dev.swap_fp.create_swapchain_khr)(handle, &built.ci, alloc, out)
        }),
        handle.as_raw(),
        &[built.forced],
        out,
    )
}

fn call_recorded_swapchain(
    created: vk::Result,
    dev: u64,
    forced: &[Option<vk::PresentModeKHR>],
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    match created {
        vk::Result::SUCCESS => {
            forced.iter().enumerate().for_each(|(at, mode)| match mode {
                Some(held) => {
                    call_remember_forced(dev, unsafe { (*out.add(at)).as_raw() }, *held)
                }
                None => (),
            });
            vk::Result::SUCCESS
        }
        e => e,
    }
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
) -> Vec<SwapchainRebuild<'a>> {
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
    let built = call_shared_patched(dev, inst, cis, count, ensure_settings());
    let patched: Vec<vk::SwapchainCreateInfoKHR<'_>> = built.iter().map(|one| one.ci).collect();
    let forced: Vec<Option<vk::PresentModeKHR>> = built.iter().map(|one| one.forced).collect();
    call_recorded_swapchain(
        call_created_swapchain(unsafe { fp(handle, count, patched.as_ptr(), alloc, out) }),
        handle.as_raw(),
        &forced,
        out,
    )
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
