use std::collections::HashMap;
use std::ffi::c_void;
use std::ffi::CString;
use std::mem;
use std::ptr;
use std::sync::RwLock;

use ash::vk;
use ash::vk::Handle;

use crate::bounds::accepts;
use crate::bounds::bounds_set;
use crate::bounds::kept;
use crate::bounds::Bounds;
use crate::config::ensure_settings;
use crate::consts::FN_DEVICE_GROUPS;
use crate::consts::FN_DEVICE_GROUPS_KHR;
use crate::consts::FN_SURFACE_CAPS_2;
use crate::consts::FN_SURFACE_FORMATS_2;
use crate::consts::FN_SURFACE_MODES_2;
use crate::consts::GPU_EMPTY_WARN;
use crate::consts::GROUP_EMPTY_WARN;
use crate::consts::LAYER_LINK_INFO;
use crate::logging::log_at;
use crate::logging::LogLevel;

pub(crate) const SURFACE_FORMAT_2: u32 = 1000119002;

pub(crate) type PfnSurfaceCaps2 = unsafe extern "system" fn(
    vk::PhysicalDevice,
    *const VkPhysicalDeviceSurfaceInfo2,
    *mut VkSurfaceCapabilities2,
) -> vk::Result;

pub(crate) type PfnSurfaceFormats2 = unsafe extern "system" fn(
    vk::PhysicalDevice,
    *const VkPhysicalDeviceSurfaceInfo2,
    *mut u32,
    *mut VkSurfaceFormat2,
) -> vk::Result;

pub(crate) type PfnSurfaceModes2 = unsafe extern "system" fn(
    vk::PhysicalDevice,
    *const VkPhysicalDeviceSurfaceInfo2,
    *mut u32,
    *mut vk::PresentModeKHR,
) -> vk::Result;

pub(crate) type PfnDeviceGroups = unsafe extern "system" fn(
    vk::Instance,
    *mut u32,
    *mut vk::PhysicalDeviceGroupProperties,
) -> vk::Result;

pub(crate) type PfnCreateSharedSwapchains = unsafe extern "system" fn(
    vk::Device,
    u32,
    *const vk::SwapchainCreateInfoKHR,
    *const vk::AllocationCallbacks,
    *mut vk::SwapchainKHR,
) -> vk::Result;

pub(crate) type PfnWriteSamplers = unsafe extern "system" fn(
    vk::Device,
    u32,
    *const vk::SamplerCreateInfo,
    *const c_void,
) -> vk::Result;

pub(crate) type PfnCmdSetAlphaToCoverage =
    unsafe extern "system" fn(vk::CommandBuffer, vk::Bool32);

#[repr(C)]
pub(crate) struct VkLayerLink {
    pub(crate) p_next: *mut VkLayerLink,
    pub(crate) pfn_next_get_instance_proc_addr: vk::PFN_vkGetInstanceProcAddr,
    pub(crate) pfn_next_get_device_proc_addr: vk::PFN_vkGetDeviceProcAddr,
}

pub(crate) struct VkLayerLinkInfo {
    pub(crate) pfn_next_get_instance_proc_addr: vk::PFN_vkGetInstanceProcAddr,
    pub(crate) pfn_next_get_device_proc_addr: vk::PFN_vkGetDeviceProcAddr,
}

#[repr(C)]
pub(crate) struct VkLayerCreateInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) function: i32,
    pub(crate) u_layer_info: *mut VkLayerLink,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkPhysicalDeviceSurfaceInfo2 {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) surface: vk::SurfaceKHR,
}

#[repr(C)]
pub(crate) struct VkSurfaceCapabilities2 {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) surface_capabilities: vk::SurfaceCapabilitiesKHR,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkSurfaceFormat2 {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) surface_format: vk::SurfaceFormatKHR,
}

#[derive(Clone)]
pub(crate) struct VkInstState {
    pub(crate) instance: ash::Instance,
    pub(crate) gipa: vk::PFN_vkGetInstanceProcAddr,
    pub(crate) surface_fp: vk::KhrSurfaceFn,
    pub(crate) caps2_fp: Option<PfnSurfaceCaps2>,
    pub(crate) formats2_fp: Option<PfnSurfaceFormats2>,
    pub(crate) modes2_fp: Option<PfnSurfaceModes2>,
    pub(crate) groups_fp: Option<PfnDeviceGroups>,
    pub(crate) groups_khr_fp: Option<PfnDeviceGroups>,
}

static INSTS: RwLock<Option<HashMap<u64, VkInstState>>> = RwLock::new(None);
static PHYS_OWNER: RwLock<Option<HashMap<u64, u64>>> = RwLock::new(None);

fn phys_owner_get(phys: u64) -> Option<u64> {
    PHYS_OWNER
        .read()
        .ok()
        .and_then(|g| g.as_ref().and_then(|m| m.get(&phys).copied()))
}

fn phys_owner_put(phys: u64, inst: u64) {
    match PHYS_OWNER.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).insert(phys, inst);
        }
        Err(_) => (),
    }
}

fn phys_owner_forget(inst: u64) {
    match PHYS_OWNER.write() {
        Ok(mut g) => g
            .iter_mut()
            .for_each(|m| m.retain(|_, owner| *owner != inst)),
        Err(_) => (),
    }
}

pub(crate) fn insts_get(h: u64) -> Option<VkInstState> {
    INSTS.read().ok().and_then(|g| g.as_ref().and_then(|m| m.get(&h).cloned()))
}

pub(crate) fn insts_put(h: u64, v: VkInstState) {
    match INSTS.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).insert(h, v);
        }
        Err(_) => (),
    }
}

pub(crate) fn insts_del(h: u64) {
    phys_owner_forget(h);
    match INSTS.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).remove(&h);
        }
        Err(_) => (),
    }
}

fn insts_all() -> Vec<(u64, VkInstState)> {
    INSTS
        .read()
        .ok()
        .and_then(|g| g.as_ref().map(|m| m.iter().map(|(k, v)| (*k, v.clone())).collect()))
        .unwrap_or_default()
}

fn instance_lists_phys(st: &VkInstState, phys: vk::PhysicalDevice) -> bool {
    unsafe { st.instance.enumerate_physical_devices() }
        .map(|v| v.contains(&phys))
        .unwrap_or(false)
}

fn scan_owning_instance(phys: vk::PhysicalDevice) -> Option<(u64, VkInstState)> {
    insts_all()
        .into_iter()
        .find(|(_, st)| instance_lists_phys(st, phys))
}

fn cached_owner(phys: vk::PhysicalDevice) -> Option<(u64, VkInstState)> {
    phys_owner_get(phys.as_raw()).and_then(|h| insts_get(h).map(|st| (h, st)))
}

fn scanned_owner(phys: vk::PhysicalDevice) -> Option<(u64, VkInstState)> {
    scan_owning_instance(phys).map(|(h, st)| {
        phys_owner_put(phys.as_raw(), h);
        (h, st)
    })
}

pub(crate) fn owning_instance(phys: vk::PhysicalDevice) -> Option<(u64, VkInstState)> {
    match cached_owner(phys) {
        Some(found) => Some(found),
        None => scanned_owner(phys),
    }
}

fn indexed(devices: Vec<vk::PhysicalDevice>) -> Vec<(usize, vk::PhysicalDevice)> {
    devices.into_iter().enumerate().collect()
}

fn plain(pairs: Vec<(usize, vk::PhysicalDevice)>) -> Vec<vk::PhysicalDevice> {
    pairs.into_iter().map(|(_, device)| device).collect()
}

fn device_position(pair: &(usize, vk::PhysicalDevice)) -> u32 {
    pair.0 as u32 + 1
}

fn gpu_filtered(devices: Vec<vk::PhysicalDevice>, b: Bounds<u32>) -> Vec<vk::PhysicalDevice> {
    match bounds_set(&b) {
        true => plain(kept(
            indexed(devices),
            |pair| accepts(b, device_position(pair)),
            GPU_EMPTY_WARN,
        )),
        false => devices,
    }
}

fn group_devices(group: &vk::PhysicalDeviceGroupProperties) -> Vec<vk::PhysicalDevice> {
    group.physical_devices[..group.physical_device_count as usize].to_vec()
}

fn group_wanted(
    group: &vk::PhysicalDeviceGroupProperties,
    allowed: &[vk::PhysicalDevice],
) -> bool {
    group_devices(group)
        .into_iter()
        .any(|device| allowed.contains(&device))
}

fn group_filtered(
    groups: Vec<vk::PhysicalDeviceGroupProperties>,
    allowed: Vec<vk::PhysicalDevice>,
    b: Bounds<u32>,
) -> Vec<vk::PhysicalDeviceGroupProperties> {
    match bounds_set(&b) {
        true => kept(groups, |group| group_wanted(group, &allowed), GROUP_EMPTY_WARN),
        false => groups,
    }
}

fn copy_count(requested: u32, available: usize) -> usize {
    (requested as usize).min(available)
}

fn completeness(written: usize, available: usize) -> vk::Result {
    match written == available {
        true => vk::Result::SUCCESS,
        false => vk::Result::INCOMPLETE,
    }
}

fn non_null_ci(p: *const VkLayerCreateInfo) -> Option<*const VkLayerCreateInfo> {
    match p.is_null() {
        true => None,
        false => Some(p),
    }
}

pub(crate) fn chain_link_info(p_next: *const c_void, want: vk::StructureType) -> *mut VkLayerCreateInfo {
    std::iter::successors(non_null_ci(p_next as *const VkLayerCreateInfo), |p| {
        non_null_ci(unsafe { (**p).p_next as *const VkLayerCreateInfo })
    })
    .find(|p| unsafe { (**p).s_type == want && (**p).function == LAYER_LINK_INFO })
    .map(|p| p as *mut VkLayerCreateInfo)
    .unwrap_or(ptr::null_mut())
}

pub(crate) fn call_advance_chain(link: *mut VkLayerCreateInfo) -> Option<VkLayerLinkInfo> {
    match link.is_null() || unsafe { (*link).u_layer_info.is_null() } {
        true => None,
        false => unsafe {
            let li = (*link).u_layer_info;
            let out = VkLayerLinkInfo {
                pfn_next_get_instance_proc_addr: (*li).pfn_next_get_instance_proc_addr,
                pfn_next_get_device_proc_addr: (*li).pfn_next_get_device_proc_addr,
            };
            (*link).u_layer_info = (*li).p_next;
            Some(out)
        },
    }
}

pub(crate) fn call_next_gipa(gipa: vk::PFN_vkGetInstanceProcAddr, inst: vk::Instance, name: &str) -> vk::PFN_vkVoidFunction {
    let c = CString::new(name).unwrap_or_default();
    unsafe { gipa(inst, c.as_ptr()) }
}

pub(crate) fn call_next_gdpa(gdpa: vk::PFN_vkGetDeviceProcAddr, dev: vk::Device, name: &str) -> vk::PFN_vkVoidFunction {
    let c = CString::new(name).unwrap_or_default();
    unsafe { gdpa(dev, c.as_ptr()) }
}

fn call_write_count<T>(list: &[T], count: *mut u32) -> vk::Result {
    unsafe { *count = list.len() as u32 };
    vk::Result::SUCCESS
}

fn call_write_items<T: Copy>(list: &[T], count: *mut u32, out: *mut T) -> vk::Result {
    let n = copy_count(unsafe { *count }, list.len());
    (0..n).for_each(|i| unsafe { *out.add(i) = list[i] });
    unsafe { *count = n as u32 };
    completeness(n, list.len())
}

pub(crate) fn call_write_list<T: Copy>(list: &[T], count: *mut u32, out: *mut T) -> vk::Result {
    match out.is_null() {
        true => call_write_count(list, count),
        false => call_write_items(list, count, out),
    }
}

fn call_enumerate_through(
    st: &VkInstState,
    count: *mut u32,
    devices: *mut vk::PhysicalDevice,
) -> vk::Result {
    match unsafe { st.instance.enumerate_physical_devices() } {
        Ok(all) => call_write_list(&gpu_filtered(all, ensure_settings().gpu), count, devices),
        Err(e) => e,
    }
}

pub(crate) fn call_filtered_enumerate(
    inst: vk::Instance,
    count: *mut u32,
    devices: *mut vk::PhysicalDevice,
) -> vk::Result {
    match insts_get(inst.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(st) => call_enumerate_through(&st, count, devices),
    }
}

fn call_query_groups(
    handle: vk::Instance,
    fp: PfnDeviceGroups,
) -> Vec<vk::PhysicalDeviceGroupProperties> {
    let mut n: u32 = 0;
    let r1 = unsafe { fp(handle, &mut n, ptr::null_mut()) };
    let mut v: Vec<vk::PhysicalDeviceGroupProperties> =
        (0..n).map(|_| Default::default()).collect();
    let r2 = unsafe { fp(handle, &mut n, v.as_mut_ptr()) };
    match (r1, r2) {
        (vk::Result::SUCCESS, vk::Result::SUCCESS) => v,
        (_, _) => Vec::new(),
    }
}

fn call_allowed_devices(st: &VkInstState) -> Vec<vk::PhysicalDevice> {
    gpu_filtered(
        unsafe { st.instance.enumerate_physical_devices() }.unwrap_or_default(),
        ensure_settings().gpu,
    )
}

fn call_groups_through(
    st: &VkInstState,
    handle: vk::Instance,
    fp: PfnDeviceGroups,
    count: *mut u32,
    groups: *mut vk::PhysicalDeviceGroupProperties,
) -> vk::Result {
    call_write_list(
        &group_filtered(
            call_query_groups(handle, fp),
            call_allowed_devices(st),
            ensure_settings().gpu,
        ),
        count,
        groups,
    )
}

fn call_groups_with(
    inst: vk::Instance,
    found: Option<(VkInstState, PfnDeviceGroups)>,
    count: *mut u32,
    groups: *mut vk::PhysicalDeviceGroupProperties,
) -> vk::Result {
    match found {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some((st, fp)) => call_groups_through(&st, inst, fp, count, groups),
    }
}

pub(crate) fn call_filtered_groups(
    inst: vk::Instance,
    count: *mut u32,
    groups: *mut vk::PhysicalDeviceGroupProperties,
) -> vk::Result {
    call_groups_with(
        inst,
        insts_get(inst.as_raw()).and_then(|st| st.groups_fp.map(|fp| (st, fp))),
        count,
        groups,
    )
}

pub(crate) fn call_filtered_groups_khr(
    inst: vk::Instance,
    count: *mut u32,
    groups: *mut vk::PhysicalDeviceGroupProperties,
) -> vk::Result {
    call_groups_with(
        inst,
        insts_get(inst.as_raw()).and_then(|st| st.groups_khr_fp.map(|fp| (st, fp))),
        count,
        groups,
    )
}

fn load_surface_fp(gipa: vk::PFN_vkGetInstanceProcAddr, handle: vk::Instance) -> vk::KhrSurfaceFn {
    vk::KhrSurfaceFn::load(|name| unsafe { mem::transmute(gipa(handle, name.as_ptr())) })
}

fn call_typed_instance_fp<T>(
    gipa: vk::PFN_vkGetInstanceProcAddr,
    handle: vk::Instance,
    name: &str,
) -> Option<T> {
    call_next_gipa(gipa, handle, name).map(|f| unsafe { mem::transmute_copy(&f) })
}

fn register_instance(gipa: vk::PFN_vkGetInstanceProcAddr, handle: vk::Instance) {
    let static_fn = vk::StaticFn { get_instance_proc_addr: gipa };
    let instance = unsafe { ash::Instance::load(&static_fn, handle) };
    insts_put(
        handle.as_raw(),
        VkInstState {
            instance,
            gipa,
            surface_fp: load_surface_fp(gipa, handle),
            caps2_fp: call_typed_instance_fp(gipa, handle, FN_SURFACE_CAPS_2),
            formats2_fp: call_typed_instance_fp(gipa, handle, FN_SURFACE_FORMATS_2),
            modes2_fp: call_typed_instance_fp(gipa, handle, FN_SURFACE_MODES_2),
            groups_fp: call_typed_instance_fp(gipa, handle, FN_DEVICE_GROUPS),
            groups_khr_fp: call_typed_instance_fp(gipa, handle, FN_DEVICE_GROUPS_KHR),
        },
    );
    log_at(LogLevel::Info, "vk instance registered");
}

fn invoke_create_instance(
    create_fn: unsafe extern "system" fn(),
    gipa: vk::PFN_vkGetInstanceProcAddr,
    ci: *const vk::InstanceCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Instance,
) -> vk::Result {
    match unsafe {
        let cf: vk::PFN_vkCreateInstance = mem::transmute(create_fn);
        cf(ci, alloc, out)
    } {
        vk::Result::SUCCESS => {
            register_instance(gipa, unsafe { *out });
            vk::Result::SUCCESS
        }
        e => e,
    }
}

pub(crate) fn call_real_create_instance(
    link: Option<VkLayerLinkInfo>,
    ci: *const vk::InstanceCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Instance,
) -> vk::Result {
    match link {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(l) => call_next_gipa(l.pfn_next_get_instance_proc_addr, vk::Instance::null(), "vkCreateInstance")
            .map(|f| invoke_create_instance(f, l.pfn_next_get_instance_proc_addr, ci, alloc, out))
            .unwrap_or(vk::Result::ERROR_INITIALIZATION_FAILED),
    }
}
