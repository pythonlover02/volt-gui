use std::collections::HashMap;
use std::ffi::c_char;
use std::ffi::c_void;
use std::ffi::CStr;
use std::ffi::CString;
use std::mem;
use std::ptr;
use std::sync::RwLock;

use ash::vk;
use ash::vk::Handle;

use crate::config::ensure_settings;
use crate::consts::INSTANCE_OPT_EXTS;
use crate::consts::LAYER_LINK_INFO;
use crate::logging::log_at;
use crate::logging::LogLevel;

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

#[derive(Clone)]
pub(crate) struct VkInstState {
    pub(crate) instance: ash::Instance,
    pub(crate) gipa: vk::PFN_vkGetInstanceProcAddr,
    pub(crate) surface_fp: vk::KhrSurfaceFn,
}

static INSTS: RwLock<Option<HashMap<u64, VkInstState>>> = RwLock::new(None);

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

pub(crate) fn insts_del(h: u64) -> bool {
    INSTS
        .write()
        .ok()
        .and_then(|mut g| {
            g.as_mut().map(|m| {
                m.remove(&h);
                m.is_empty()
            })
        })
        .unwrap_or(true)
}

pub(crate) fn insts_all() -> Vec<(u64, VkInstState)> {
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

pub(crate) fn owning_instance(phys: vk::PhysicalDevice) -> Option<(u64, VkInstState)> {
    insts_all()
        .into_iter()
        .find(|(_, st)| instance_lists_phys(st, phys))
}

fn gpu_slice(devices: Vec<vk::PhysicalDevice>, index: u32) -> Vec<vk::PhysicalDevice> {
    match devices.get(index as usize - 1) {
        Some(d) => vec![*d],
        None => {
            log_at(LogLevel::Warn, "gpu index out of range, keeping all devices");
            devices
        }
    }
}

fn gpu_filtered(devices: Vec<vk::PhysicalDevice>, index: Option<u32>) -> Vec<vk::PhysicalDevice> {
    match index {
        None => devices,
        Some(i) => gpu_slice(devices, i),
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

pub(crate) fn call_write_count<T>(list: &[T], count: *mut u32) -> vk::Result {
    unsafe { *count = list.len() as u32 };
    vk::Result::SUCCESS
}

pub(crate) fn call_write_items<T: Copy>(list: &[T], count: *mut u32, out: *mut T) -> vk::Result {
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

fn load_surface_fp(gipa: vk::PFN_vkGetInstanceProcAddr, handle: vk::Instance) -> vk::KhrSurfaceFn {
    vk::KhrSurfaceFn::load(|name| unsafe { mem::transmute(gipa(handle, name.as_ptr())) })
}

fn register_instance(gipa: vk::PFN_vkGetInstanceProcAddr, handle: vk::Instance) {
    let static_fn = vk::StaticFn { get_instance_proc_addr: gipa };
    let instance = unsafe { ash::Instance::load(&static_fn, handle) };
    let surface_fp = load_surface_fp(gipa, handle);
    insts_put(handle.as_raw(), VkInstState { instance, gipa, surface_fp });
    log_at(LogLevel::Info, "vk instance registered");
}

fn invoke_create_instance(
    create_fn: unsafe extern "system" fn(),
    gipa: vk::PFN_vkGetInstanceProcAddr,
    ci: *const vk::InstanceCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Instance,
) -> vk::Result {
    let r = unsafe {
        let cf: vk::PFN_vkCreateInstance = mem::transmute(create_fn);
        cf(ci, alloc, out)
    };
    match r {
        vk::Result::SUCCESS => {
            register_instance(gipa, unsafe { *out });
            vk::Result::SUCCESS
        }
        e => e,
    }
}

struct MergedInstanceCi {
    ci: vk::InstanceCreateInfo,
    _ext_cstrings: Vec<CString>,
    _ext_ptrs: Vec<*const c_char>,
}

type PfnEnumInstExts =
    unsafe extern "system" fn(*const c_char, *mut u32, *mut vk::ExtensionProperties) -> vk::Result;

fn call_enum_instance_exts(f: PfnEnumInstExts) -> Vec<String> {
    let mut n: u32 = 0;
    let _ = unsafe { f(ptr::null(), &mut n, ptr::null_mut()) };
    let mut v = vec![vk::ExtensionProperties::default(); n as usize];
    let _ = unsafe { f(ptr::null(), &mut n, v.as_mut_ptr()) };
    v.into_iter()
        .map(|p| unsafe { CStr::from_ptr(p.extension_name.as_ptr()) }
            .to_string_lossy()
            .into_owned())
        .collect()
}

fn call_supported_instance_exts(gipa: vk::PFN_vkGetInstanceProcAddr) -> Vec<String> {
    match call_next_gipa(gipa, vk::Instance::null(), "vkEnumerateInstanceExtensionProperties") {
        None => Vec::new(),
        Some(f) => call_enum_instance_exts(unsafe { mem::transmute::<_, PfnEnumInstExts>(f) }),
    }
}

fn instance_ext_cstrings(ci: &vk::InstanceCreateInfo) -> Vec<CString> {
    (0..ci.enabled_extension_count as usize)
        .map(|i| unsafe { CStr::from_ptr(*ci.pp_enabled_extension_names.add(i)) }.to_owned())
        .collect()
}

fn instance_ext_present(exts: &[CString], name: &str) -> bool {
    exts.contains(&CString::new(name).unwrap_or_default())
}

fn instance_push_missing(mut acc: Vec<CString>, name: &str) -> Vec<CString> {
    match instance_ext_present(&acc, name) {
        true => acc,
        false => {
            acc.push(CString::new(name).unwrap_or_default());
            acc
        }
    }
}

fn appended_instance_exts(original: Vec<CString>, supported: &[String]) -> Vec<CString> {
    INSTANCE_OPT_EXTS
        .iter()
        .filter(|n| supported.iter().any(|s| s == *n))
        .fold(original, |acc, n| instance_push_missing(acc, n))
}

fn build_instance_merged(
    gipa: vk::PFN_vkGetInstanceProcAddr,
    ci: *const vk::InstanceCreateInfo,
) -> MergedInstanceCi {
    let original = unsafe { &*ci };
    let exts = appended_instance_exts(
        instance_ext_cstrings(original),
        &call_supported_instance_exts(gipa),
    );
    let ext_ptrs: Vec<*const c_char> = exts.iter().map(|c| c.as_ptr()).collect();
    MergedInstanceCi {
        ci: vk::InstanceCreateInfo {
            enabled_extension_count: ext_ptrs.len() as u32,
            pp_enabled_extension_names: ext_ptrs.as_ptr(),
            ..*original
        },
        _ext_cstrings: exts,
        _ext_ptrs: ext_ptrs,
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
        Some(l) => {
            let merged = build_instance_merged(l.pfn_next_get_instance_proc_addr, ci);
            call_next_gipa(l.pfn_next_get_instance_proc_addr, vk::Instance::null(), "vkCreateInstance")
                .map(|f| invoke_create_instance(f, l.pfn_next_get_instance_proc_addr, &merged.ci, alloc, out))
                .unwrap_or(vk::Result::ERROR_INITIALIZATION_FAILED)
        }
    }
}
