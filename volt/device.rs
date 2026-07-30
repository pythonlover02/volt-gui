use std::collections::HashMap;
use std::ffi::c_char;
use std::ffi::c_void;
use std::ffi::CStr;
use std::ffi::CString;
use std::mem;
use std::ptr;
use std::sync::Arc;
use std::sync::RwLock;

use ash::vk;
use ash::vk::Handle;

use crate::consts::EXT_ANTI_LAG;
use crate::consts::EXT_DISPLAY_TIMING;
use crate::consts::EXT_HDR_METADATA;
use crate::consts::EXT_LOW_LATENCY;
use crate::consts::EXT_SWAP_MAINT;
use crate::consts::EXT_VIEW_MIN_LOD;
use crate::consts::FN_PRESENT_RECTANGLES;
use crate::ext::st;
use crate::ext::AntiLagFeaturesAmd;
use crate::ext::PfnAntiLagUpdateAmd;
use crate::ext::PfnSetHdrMetadataExt;
use crate::ext::PfnSetLatencySleepModeNv;
use crate::ext::SwapMaintFeaturesExt;
use crate::ext::ViewMinLodFeaturesExt;
use crate::ext::ST_ANTI_LAG_FEATURES;
use crate::ext::ST_SWAP_MAINT_FEATURES;
use crate::ext::ST_VIEW_MIN_LOD_FEATURES;
use crate::instance::call_next_gdpa;
use crate::instance::call_next_gipa;
use crate::instance::owning_instance;
use crate::instance::VkInstState;
use crate::instance::VkLayerLinkInfo;
use crate::logging::log_at;
use crate::logging::LogLevel;

#[derive(Clone, Copy, Default)]
pub(crate) struct DeviceCaps {
    pub(crate) sampler_anisotropy: bool,
    pub(crate) fill_mode_non_solid: bool,
    pub(crate) sample_rate_shading: bool,
    pub(crate) max_anisotropy: f32,
    pub(crate) max_lod_bias: f32,
    pub(crate) anti_lag: bool,
    pub(crate) low_latency: bool,
    pub(crate) swap_maint: bool,
    pub(crate) display_timing: bool,
    pub(crate) hdr_metadata: bool,
    pub(crate) view_min_lod: bool,
}

struct ExtPick {
    anti_lag: bool,
    low_latency: bool,
    swap_maint: bool,
    display_timing: bool,
    hdr_metadata: bool,
    view_min_lod: bool,
}

pub(crate) struct VkDevState {
    pub(crate) device: ash::Device,
    pub(crate) phys: vk::PhysicalDevice,
    pub(crate) gdpa: vk::PFN_vkGetDeviceProcAddr,
    pub(crate) swap_fp: vk::KhrSwapchainFn,
    pub(crate) caps: DeviceCaps,
    pub(crate) anti_lag_fp: Option<PfnAntiLagUpdateAmd>,
    pub(crate) latency_fp: Option<PfnSetLatencySleepModeNv>,
    pub(crate) hdr_fp: Option<PfnSetHdrMetadataExt>,
    pub(crate) instance_handle: u64,
}

struct MergedDeviceCi {
    ci: vk::DeviceCreateInfo,
    caps: DeviceCaps,
    _enabled_features: Box<vk::PhysicalDeviceFeatures>,
    _ext_cstrings: Vec<CString>,
    _ext_ptrs: Vec<*const c_char>,
    _anti_feat: Box<AntiLagFeaturesAmd>,
    _maint_feat: Box<SwapMaintFeaturesExt>,
    _lod_feat: Box<ViewMinLodFeaturesExt>,
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

pub(crate) fn queue_dev_get(q: u64) -> Option<u64> {
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
        fill_mode_non_solid: enable_flag(base.fill_mode_non_solid, supported.fill_mode_non_solid),
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

fn build_caps(
    supported: &vk::PhysicalDeviceFeatures,
    limits: &vk::PhysicalDeviceLimits,
    pick: &ExtPick,
) -> DeviceCaps {
    DeviceCaps {
        sampler_anisotropy: supported.sampler_anisotropy == vk::TRUE,
        fill_mode_non_solid: supported.fill_mode_non_solid == vk::TRUE,
        sample_rate_shading: supported.sample_rate_shading == vk::TRUE,
        max_anisotropy: limits.max_sampler_anisotropy,
        max_lod_bias: limits.max_sampler_lod_bias,
        anti_lag: pick.anti_lag,
        low_latency: pick.low_latency,
        swap_maint: pick.swap_maint,
        display_timing: pick.display_timing,
        hdr_metadata: pick.hdr_metadata,
        view_min_lod: pick.view_min_lod,
    }
}

fn supported_device_exts(inst: &VkInstState, phys: vk::PhysicalDevice) -> Vec<String> {
    unsafe { inst.instance.enumerate_device_extension_properties(phys) }
        .unwrap_or_default()
        .into_iter()
        .map(|p| unsafe { CStr::from_ptr(p.extension_name.as_ptr()) }
            .to_string_lossy()
            .into_owned())
        .collect()
}

fn ext_supported(list: &[String], name: &str) -> bool {
    list.iter().any(|s| s == name)
}

fn pick_exts(list: &[String]) -> ExtPick {
    ExtPick {
        anti_lag: ext_supported(list, EXT_ANTI_LAG),
        low_latency: ext_supported(list, EXT_LOW_LATENCY),
        swap_maint: ext_supported(list, EXT_SWAP_MAINT),
        display_timing: ext_supported(list, EXT_DISPLAY_TIMING),
        hdr_metadata: ext_supported(list, EXT_HDR_METADATA),
        view_min_lod: ext_supported(list, EXT_VIEW_MIN_LOD),
    }
}

fn chosen_names(pick: &ExtPick) -> Vec<&'static str> {
    [
        (pick.anti_lag, EXT_ANTI_LAG),
        (pick.low_latency, EXT_LOW_LATENCY),
        (pick.swap_maint, EXT_SWAP_MAINT),
        (pick.display_timing, EXT_DISPLAY_TIMING),
        (pick.hdr_metadata, EXT_HDR_METADATA),
        (pick.view_min_lod, EXT_VIEW_MIN_LOD),
    ]
    .into_iter()
    .filter(|(on, _)| *on)
    .map(|(_, name)| name)
    .collect()
}

fn log_chosen(names: &[&str]) {
    names
        .iter()
        .for_each(|n| log_at(LogLevel::Info, &format!("optional extension enabled: {}", n)));
}

fn original_ext_cstrings(ci: &vk::DeviceCreateInfo) -> Vec<CString> {
    (0..ci.enabled_extension_count as usize)
        .map(|i| unsafe { CStr::from_ptr(*ci.pp_enabled_extension_names.add(i)) }.to_owned())
        .collect()
}

fn ext_is_present(exts: &[CString], name: &str) -> bool {
    exts.contains(&CString::new(name).unwrap_or_default())
}

fn push_missing(mut acc: Vec<CString>, name: &str) -> Vec<CString> {
    match ext_is_present(&acc, name) {
        true => acc,
        false => {
            acc.push(CString::new(name).unwrap_or_default());
            acc
        }
    }
}

fn appended_exts(original: Vec<CString>, names: &[&str]) -> Vec<CString> {
    names.iter().fold(original, |acc, n| push_missing(acc, n))
}

fn maybe_chain<T, F>(use_it: bool, head: *const c_void, feat: &mut T, set_next: F) -> *const c_void
where
    F: FnOnce(&mut T, *mut c_void),
{
    match use_it {
        true => {
            set_next(feat, head as *mut c_void);
            feat as *mut T as *const c_void
        }
        false => head,
    }
}

fn build_merged(inst: &VkInstState, phys: vk::PhysicalDevice, ci: *const vk::DeviceCreateInfo) -> MergedDeviceCi {
    let original = unsafe { &*ci };
    let supported = unsafe { inst.instance.get_physical_device_features(phys) };
    let props = unsafe { inst.instance.get_physical_device_properties(phys) };
    let pick = pick_exts(&supported_device_exts(inst, phys));
    log_chosen(&chosen_names(&pick));
    let features2_node = chain_find(original.p_next, vk::StructureType::PHYSICAL_DEVICE_FEATURES_2);
    maybe_patch_features2(features2_node, &supported);
    let enabled_features = Box::new(merged_features(original_features_ptr(original), &supported));
    let exts = appended_exts(original_ext_cstrings(original), &chosen_names(&pick));
    let ext_ptrs: Vec<*const c_char> = exts.iter().map(|c| c.as_ptr()).collect();
    let mut anti_feat = Box::new(AntiLagFeaturesAmd {
        s_type: st(ST_ANTI_LAG_FEATURES),
        p_next: ptr::null_mut(),
        anti_lag: vk::TRUE,
    });
    let mut maint_feat = Box::new(SwapMaintFeaturesExt {
        s_type: st(ST_SWAP_MAINT_FEATURES),
        p_next: ptr::null_mut(),
        swapchain_maintenance1: vk::TRUE,
    });
    let mut lod_feat = Box::new(ViewMinLodFeaturesExt {
        s_type: st(ST_VIEW_MIN_LOD_FEATURES),
        p_next: ptr::null_mut(),
        min_lod: vk::TRUE,
    });
    let mut head = original.p_next;
    head = maybe_chain(pick.anti_lag, head, anti_feat.as_mut(), |f, n| f.p_next = n);
    head = maybe_chain(pick.swap_maint, head, maint_feat.as_mut(), |f, n| f.p_next = n);
    head = maybe_chain(pick.view_min_lod, head, lod_feat.as_mut(), |f, n| f.p_next = n);
    MergedDeviceCi {
        ci: vk::DeviceCreateInfo {
            p_next: head,
            enabled_extension_count: ext_ptrs.len() as u32,
            pp_enabled_extension_names: ext_ptrs.as_ptr(),
            p_enabled_features: pick_features_ptr(features2_node, enabled_features.as_ref()),
            ..*original
        },
        caps: build_caps(&supported, &props.limits, &pick),
        _enabled_features: enabled_features,
        _ext_cstrings: exts,
        _ext_ptrs: ext_ptrs,
        _anti_feat: anti_feat,
        _maint_feat: maint_feat,
        _lod_feat: lod_feat,
    }
}

fn load_named_fp(
    gdpa: vk::PFN_vkGetDeviceProcAddr,
    handle: vk::Device,
    enabled: bool,
    name: &str,
) -> Option<unsafe extern "system" fn()> {
    match enabled {
        true => call_next_gdpa(gdpa, handle, name),
        false => None,
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
    let anti_lag_fp = load_named_fp(gdpa, handle, caps.anti_lag, "vkAntiLagUpdateAMD")
        .map(|f| unsafe { mem::transmute::<unsafe extern "system" fn(), PfnAntiLagUpdateAmd>(f) });
    let latency_fp = load_named_fp(gdpa, handle, caps.low_latency, "vkSetLatencySleepModeNV")
        .map(|f| unsafe { mem::transmute::<unsafe extern "system" fn(), PfnSetLatencySleepModeNv>(f) });
    let hdr_fp = load_named_fp(gdpa, handle, caps.hdr_metadata, "vkSetHdrMetadataEXT")
        .map(|f| unsafe { mem::transmute::<unsafe extern "system" fn(), PfnSetHdrMetadataExt>(f) });
    devs_put(
        handle.as_raw(),
        VkDevState {
            device,
            phys,
            gdpa,
            swap_fp,
            caps,
            anti_lag_fp,
            latency_fp,
            hdr_fp,
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
    let r = unsafe {
        let cf: vk::PFN_vkCreateDevice = mem::transmute(create_fn);
        cf(phys, &merged.ci, alloc, out)
    };
    match r {
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
