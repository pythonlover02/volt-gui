use std::collections::HashMap;
use std::ffi::c_void;
use std::mem;
use std::ptr;
use std::sync::Arc;
use std::sync::RwLock;

use ash::vk;
use ash::vk::Handle;

use crate::consts::FN_PRESENT_RECTANGLES;
use crate::instance::call_next_gipa;
use crate::instance::owning_instance;
use crate::instance::VkInstState;
use crate::instance::VkLayerLinkInfo;
use crate::logging::log_at;
use crate::logging::LogLevel;

#[derive(Clone, Copy, Default)]
pub(crate) struct DeviceCaps {
    pub(crate) sampler_anisotropy: bool,
    pub(crate) sample_rate_shading: bool,
    pub(crate) max_anisotropy: f32,
    pub(crate) max_lod_bias: f32,
    pub(crate) max_lod_level: f32,
}

pub(crate) struct VkDevState {
    pub(crate) device: ash::Device,
    pub(crate) phys: vk::PhysicalDevice,
    pub(crate) gdpa: vk::PFN_vkGetDeviceProcAddr,
    pub(crate) swap_fp: vk::KhrSwapchainFn,
    pub(crate) caps: DeviceCaps,
    pub(crate) instance_handle: u64,
}

struct MergedDeviceCi {
    ci: vk::DeviceCreateInfo,
    caps: DeviceCaps,
    _enabled_features: Box<vk::PhysicalDeviceFeatures>,
}

static DEVS: RwLock<Option<HashMap<u64, Arc<VkDevState>>>> = RwLock::new(None);
static QUEUE_TO_DEV: RwLock<Option<HashMap<u64, u64>>> = RwLock::new(None);

pub(crate) fn devs_get(h: u64) -> Option<Arc<VkDevState>> {
    DEVS.read()
        .ok()
        .and_then(|g| g.as_ref().and_then(|m| m.get(&h).cloned()))
}

pub(crate) fn devs_any() -> Option<Arc<VkDevState>> {
    DEVS.read()
        .ok()
        .and_then(|g| g.as_ref().and_then(|m| m.values().next().cloned()))
}

pub(crate) fn devs_gdpa(h: u64) -> Option<vk::PFN_vkGetDeviceProcAddr> {
    DEVS.read()
        .ok()
        .and_then(|g| g.as_ref().and_then(|m| m.get(&h).map(|d| d.gdpa)))
}

pub(crate) fn devs_put(h: u64, v: VkDevState) {
    match DEVS.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).insert(h, Arc::new(v));
        }
        Err(_) => (),
    }
}

pub(crate) fn devs_del(h: u64) -> Option<Arc<VkDevState>> {
    DEVS.write()
        .ok()
        .and_then(|mut g| g.as_mut().and_then(|m| m.remove(&h)))
}

fn queue_dev_get(q: u64) -> Option<u64> {
    QUEUE_TO_DEV
        .read()
        .ok()
        .and_then(|g| g.as_ref().and_then(|m| m.get(&q).copied()))
}

pub(crate) fn queue_dev_put(q: u64, d: u64) {
    match QUEUE_TO_DEV.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).insert(q, d);
        }
        Err(_) => (),
    }
}

pub(crate) fn queue_owner(queue: vk::Queue) -> Option<Arc<VkDevState>> {
    queue_dev_get(queue.as_raw()).and_then(devs_get)
}

fn enable_flag(base: vk::Bool32, supported: vk::Bool32) -> vk::Bool32 {
    match supported {
        vk::TRUE => vk::TRUE,
        _ => base,
    }
}

fn merged_features(
    original: Option<&vk::PhysicalDeviceFeatures>,
    supported: &vk::PhysicalDeviceFeatures,
) -> vk::PhysicalDeviceFeatures {
    let base = original.copied().unwrap_or_default();
    vk::PhysicalDeviceFeatures {
        sampler_anisotropy: enable_flag(base.sampler_anisotropy, supported.sampler_anisotropy),
        sample_rate_shading: enable_flag(base.sample_rate_shading, supported.sample_rate_shading),
        ..base
    }
}

fn original_features_ptr(ci: &vk::DeviceCreateInfo) -> Option<&vk::PhysicalDeviceFeatures> {
    match ci.p_enabled_features.is_null() {
        true => None,
        false => Some(unsafe { &*ci.p_enabled_features }),
    }
}

fn non_null_base(p: *const c_void) -> Option<*mut vk::BaseOutStructure> {
    match p.is_null() {
        true => None,
        false => Some(p as *mut vk::BaseOutStructure),
    }
}

fn chain_find(p_next: *const c_void, want: vk::StructureType) -> Option<*mut vk::BaseOutStructure> {
    std::iter::successors(non_null_base(p_next), |p| {
        non_null_base(unsafe { (**p).p_next as *const c_void })
    })
    .find(|p| unsafe { (**p).s_type == want })
}

fn patch_features2_node(node: *mut vk::BaseOutStructure, supported: &vk::PhysicalDeviceFeatures) {
    let f = node as *mut vk::PhysicalDeviceFeatures2;
    unsafe { (*f).features = merged_features(Some(&(*f).features), supported) };
}

fn maybe_patch_features2(
    node: Option<*mut vk::BaseOutStructure>,
    supported: &vk::PhysicalDeviceFeatures,
) {
    match node {
        Some(n) => patch_features2_node(n, supported),
        None => (),
    }
}

fn pick_features_ptr(
    features2_node: Option<*mut vk::BaseOutStructure>,
    merged: &vk::PhysicalDeviceFeatures,
) -> *const vk::PhysicalDeviceFeatures {
    match features2_node {
        Some(_) => ptr::null(),
        None => merged,
    }
}

fn lod_levels_for(max_dimension: u32) -> f32 {
    (max_dimension.max(1) as f32).log2().floor()
}

fn build_caps(
    supported: &vk::PhysicalDeviceFeatures,
    limits: &vk::PhysicalDeviceLimits,
) -> DeviceCaps {
    DeviceCaps {
        sampler_anisotropy: supported.sampler_anisotropy == vk::TRUE,
        sample_rate_shading: supported.sample_rate_shading == vk::TRUE,
        max_anisotropy: limits.max_sampler_anisotropy,
        max_lod_bias: limits.max_sampler_lod_bias,
        max_lod_level: lod_levels_for(limits.max_image_dimension2_d),
    }
}

fn build_merged(inst: &VkInstState, phys: vk::PhysicalDevice, ci: *const vk::DeviceCreateInfo) -> MergedDeviceCi {
    let original = unsafe { &*ci };
    let supported = unsafe { inst.instance.get_physical_device_features(phys) };
    let props = unsafe { inst.instance.get_physical_device_properties(phys) };
    let features2_node = chain_find(original.p_next, vk::StructureType::PHYSICAL_DEVICE_FEATURES_2);
    maybe_patch_features2(features2_node, &supported);
    let enabled_features = Box::new(merged_features(original_features_ptr(original), &supported));
    MergedDeviceCi {
        ci: vk::DeviceCreateInfo {
            p_enabled_features: pick_features_ptr(features2_node, enabled_features.as_ref()),
            ..*original
        },
        caps: build_caps(&supported, &props.limits),
        _enabled_features: enabled_features,
    }
}

fn name_is_device_level(name: &std::ffi::CStr) -> bool {
    name.to_str().map(|s| s != FN_PRESENT_RECTANGLES).unwrap_or(true)
}

fn load_swap_fp(gdpa: vk::PFN_vkGetDeviceProcAddr, handle: vk::Device) -> vk::KhrSwapchainFn {
    vk::KhrSwapchainFn::load(|name| match name_is_device_level(name) {
        true => unsafe { mem::transmute(gdpa(handle, name.as_ptr())) },
        false => ptr::null(),
    })
}

pub(crate) fn inherit_device_dispatch(device_handle: vk::Device, queue: vk::Queue) {
    let src = device_handle.as_raw() as *const *const c_void;
    let dst = queue.as_raw() as *mut *const c_void;
    unsafe { *dst = *src };
}

fn register_device(
    gdpa: vk::PFN_vkGetDeviceProcAddr,
    handle: vk::Device,
    inst: &VkInstState,
    inst_handle: u64,
    phys: vk::PhysicalDevice,
    caps: DeviceCaps,
) {
    let mut inst_fp = inst.instance.fp_v1_0().clone();
    inst_fp.get_device_proc_addr = gdpa;
    let device = unsafe { ash::Device::load(&inst_fp, handle) };
    let swap_fp = load_swap_fp(gdpa, handle);
    devs_put(
        handle.as_raw(),
        VkDevState {
            device,
            phys,
            gdpa,
            swap_fp,
            caps,
            instance_handle: inst_handle,
        },
    );
    log_at(LogLevel::Info, "vk device registered");
}

fn invoke_create_device(
    create_fn: unsafe extern "system" fn(),
    link: &VkLayerLinkInfo,
    inst: &VkInstState,
    inst_handle: u64,
    phys: vk::PhysicalDevice,
    merged: &MergedDeviceCi,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Device,
) -> vk::Result {
    match unsafe {
        let cf: vk::PFN_vkCreateDevice = mem::transmute(create_fn);
        cf(phys, &merged.ci, alloc, out)
    } {
        vk::Result::SUCCESS => {
            register_device(
                link.pfn_next_get_device_proc_addr,
                unsafe { *out },
                inst,
                inst_handle,
                phys,
                merged.caps,
            );
            vk::Result::SUCCESS
        }
        e => e,
    }
}

pub(crate) fn call_real_create_device(
    link: Option<VkLayerLinkInfo>,
    phys: vk::PhysicalDevice,
    ci: *const vk::DeviceCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Device,
) -> vk::Result {
    match (link, owning_instance(phys)) {
        (Some(l), Some((ih, inst))) => {
            let merged = build_merged(&inst, phys, ci);
            call_next_gipa(
                l.pfn_next_get_instance_proc_addr,
                vk::Instance::from_raw(ih),
                "vkCreateDevice",
            )
            .map(|f| invoke_create_device(f, &l, &inst, ih, phys, &merged, alloc, out))
            .unwrap_or(vk::Result::ERROR_INITIALIZATION_FAILED)
        }
        (_, _) => vk::Result::ERROR_INITIALIZATION_FAILED,
    }
}
