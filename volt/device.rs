use std::collections::HashMap;
use std::ffi::c_void;
use std::mem;
use std::ptr;
use std::sync::Arc;
use std::sync::RwLock;

use ash::vk;
use ash::vk::Handle;

use crate::consts::FN_CREATE_SWAPCHAIN;
use crate::consts::FN_DEVICE_QUEUE_2;
use crate::consts::FN_PRESENT_RECTANGLES;
use crate::consts::FN_SET_ALPHA_COVERAGE;
use crate::consts::FN_SHARED_SWAPCHAINS;
use crate::consts::FN_WRITE_SAMPLERS;
use crate::instance::call_next_gdpa;
use crate::instance::call_next_gipa;
use crate::instance::owning_instance;
use crate::instance::PfnCmdSetAlphaToCoverage;
use crate::instance::PfnCreateSharedSwapchains;
use crate::instance::PfnSetDeviceLoaderData;
use crate::instance::PfnWriteSamplers;
use crate::instance::VkChainNode;
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
    pub(crate) loader_data: Option<PfnSetDeviceLoaderData>,
    pub(crate) swap_fp: vk::KhrSwapchainFn,
    pub(crate) shared_fp: Option<PfnCreateSharedSwapchains>,
    pub(crate) samplers_fp: Option<PfnWriteSamplers>,
    pub(crate) alpha_fp: Option<PfnCmdSetAlphaToCoverage>,
    pub(crate) swapchain_held: bool,
    pub(crate) queue2_held: bool,
    pub(crate) caps: DeviceCaps,
    pub(crate) instance_handle: u64,
}

static DEVS: RwLock<Option<HashMap<u64, Arc<VkDevState>>>> = RwLock::new(None);
static QUEUE_TO_DEV: RwLock<Option<HashMap<u64, u64>>> = RwLock::new(None);
static CMDBUF_TO_DEV: RwLock<Option<HashMap<u64, (u64, u64)>>> = RwLock::new(None);

pub(crate) fn devs_get(h: u64) -> Option<Arc<VkDevState>> {
    DEVS.read()
        .ok()
        .and_then(|g| g.as_ref().and_then(|m| m.get(&h).cloned()))
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

fn queue_dev_forget(dev: u64) {
    match QUEUE_TO_DEV.write() {
        Ok(mut g) => g
            .iter_mut()
            .for_each(|m| m.retain(|_, owner| *owner != dev)),
        Err(_) => (),
    }
}

fn cmdbuf_dev_forget(dev: u64) {
    match CMDBUF_TO_DEV.write() {
        Ok(mut g) => g
            .iter_mut()
            .for_each(|m| m.retain(|_, owner| owner.0 != dev)),
        Err(_) => (),
    }
}

pub(crate) fn devs_del(h: u64) -> Option<Arc<VkDevState>> {
    queue_dev_forget(h);
    cmdbuf_dev_forget(h);
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

fn cmdbuf_dev_get(c: u64) -> Option<u64> {
    CMDBUF_TO_DEV
        .read()
        .ok()
        .and_then(|g| g.as_ref().and_then(|m| m.get(&c).map(|owner| owner.0)))
}

fn cmdbuf_dev_put(c: u64, owner: (u64, u64)) {
    match CMDBUF_TO_DEV.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).insert(c, owner);
        }
        Err(_) => (),
    }
}

fn cmdbuf_dev_del(c: u64) {
    match CMDBUF_TO_DEV.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).remove(&c);
        }
        Err(_) => (),
    }
}

fn cmdbuf_pool_forget(pool: u64) {
    match CMDBUF_TO_DEV.write() {
        Ok(mut g) => g
            .iter_mut()
            .for_each(|m| m.retain(|_, owner| owner.1 != pool)),
        Err(_) => (),
    }
}

pub(crate) fn cmdbuf_owner(buffer: vk::CommandBuffer) -> Option<Arc<VkDevState>> {
    cmdbuf_dev_get(buffer.as_raw()).and_then(devs_get)
}

fn lod_levels_for(max_dimension: u32) -> f32 {
    (max_dimension.max(1) as f32).log2().floor()
}

fn build_caps(
    props: &vk::PhysicalDeviceProperties,
    asked: &vk::PhysicalDeviceFeatures,
) -> DeviceCaps {
    DeviceCaps {
        sampler_anisotropy: asked.sampler_anisotropy == vk::TRUE,
        sample_rate_shading: asked.sample_rate_shading == vk::TRUE,
        max_anisotropy: props.limits.max_sampler_anisotropy,
        max_lod_bias: props.limits.max_sampler_lod_bias,
        max_lod_level: lod_levels_for(props.limits.max_image_dimension2_d),
    }
}

fn non_null_node(p: *const c_void) -> Option<*const VkChainNode> {
    match p.is_null() {
        true => None,
        false => Some(p as *const VkChainNode),
    }
}

fn chained_features(p_next: *const c_void) -> Option<vk::PhysicalDeviceFeatures> {
    std::iter::successors(non_null_node(p_next), |node| {
        non_null_node(unsafe { (**node).p_next as *const c_void })
    })
    .find(|node| unsafe { (**node).s_type } == vk::StructureType::PHYSICAL_DEVICE_FEATURES_2)
    .map(|node| unsafe { (*(node as *const vk::PhysicalDeviceFeatures2)).features })
}

fn plain_features(ci: &vk::DeviceCreateInfo) -> Option<vk::PhysicalDeviceFeatures> {
    match ci.p_enabled_features.is_null() {
        true => None,
        false => Some(unsafe { *ci.p_enabled_features }),
    }
}

fn asked_features(ci: *const vk::DeviceCreateInfo) -> vk::PhysicalDeviceFeatures {
    match chained_features(unsafe { (*ci).p_next }) {
        Some(features) => features,
        None => plain_features(unsafe { &*ci }).unwrap_or_default(),
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

fn call_typed_device_fp<T>(
    gdpa: vk::PFN_vkGetDeviceProcAddr,
    handle: vk::Device,
    name: &str,
) -> Option<T> {
    call_next_gdpa(gdpa, handle, name).map(|f| unsafe { mem::transmute_copy(&f) })
}

fn call_resolved(
    gdpa: vk::PFN_vkGetDeviceProcAddr,
    handle: vk::Device,
    name: &str,
) -> bool {
    call_next_gdpa(gdpa, handle, name).is_some()
}

fn call_loader_data(fp: PfnSetDeviceLoaderData, handle: vk::Device, queue: vk::Queue) {
    let _ = unsafe { fp(handle, queue.as_raw() as usize as *mut c_void) };
}

pub(crate) fn call_register_queue(dev: &VkDevState, handle: vk::Device, queue: vk::Queue) {
    match dev.loader_data {
        Some(fp) => call_loader_data(fp, handle, queue),
        None => (),
    }
}

fn device_caps(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    ci: *const vk::DeviceCreateInfo,
) -> DeviceCaps {
    build_caps(
        unsafe { &inst.instance.get_physical_device_properties(phys) },
        &asked_features(ci),
    )
}

fn call_record_command_buffers(
    dev: vk::Device,
    info: *const vk::CommandBufferAllocateInfo,
    out: *mut vk::CommandBuffer,
) {
    (0..unsafe { (*info).command_buffer_count } as usize).for_each(|at| {
        cmdbuf_dev_put(
            unsafe { (*out.add(at)).as_raw() },
            (dev.as_raw(), unsafe { (*info).command_pool.as_raw() }),
        )
    });
}

fn call_forget_command_buffers(count: u32, buffers: *const vk::CommandBuffer) {
    (0..count as usize).for_each(|at| cmdbuf_dev_del(unsafe { (*buffers.add(at)).as_raw() }));
}

pub(crate) fn call_allocate_command_buffers(
    d: &VkDevState,
    dev: vk::Device,
    info: *const vk::CommandBufferAllocateInfo,
    out: *mut vk::CommandBuffer,
) -> vk::Result {
    match unsafe { (d.device.fp_v1_0().allocate_command_buffers)(dev, info, out) } {
        vk::Result::SUCCESS => {
            call_record_command_buffers(dev, info, out);
            vk::Result::SUCCESS
        }
        e => e,
    }
}

pub(crate) fn call_free_command_buffers(
    d: &VkDevState,
    dev: vk::Device,
    pool: vk::CommandPool,
    count: u32,
    buffers: *const vk::CommandBuffer,
) {
    call_forget_command_buffers(count, buffers);
    unsafe { (d.device.fp_v1_0().free_command_buffers)(dev, pool, count, buffers) };
}

pub(crate) fn call_destroy_command_pool(
    d: &VkDevState,
    dev: vk::Device,
    pool: vk::CommandPool,
    alloc: *const vk::AllocationCallbacks,
) {
    cmdbuf_pool_forget(pool.as_raw());
    unsafe { (d.device.fp_v1_0().destroy_command_pool)(dev, pool, alloc) };
}

fn register_device(
    gdpa: vk::PFN_vkGetDeviceProcAddr,
    loader_data: Option<PfnSetDeviceLoaderData>,
    handle: vk::Device,
    inst: &VkInstState,
    inst_handle: u64,
    phys: vk::PhysicalDevice,
    caps: DeviceCaps,
) {
    let mut inst_fp = inst.instance.fp_v1_0().clone();
    inst_fp.get_device_proc_addr = gdpa;
    let device = unsafe { ash::Device::load(&inst_fp, handle) };
    devs_put(
        handle.as_raw(),
        VkDevState {
            device,
            phys,
            gdpa,
            loader_data,
            swap_fp: load_swap_fp(gdpa, handle),
            shared_fp: call_typed_device_fp(gdpa, handle, FN_SHARED_SWAPCHAINS),
            samplers_fp: call_typed_device_fp(gdpa, handle, FN_WRITE_SAMPLERS),
            alpha_fp: call_typed_device_fp(gdpa, handle, FN_SET_ALPHA_COVERAGE),
            swapchain_held: call_resolved(gdpa, handle, FN_CREATE_SWAPCHAIN),
            queue2_held: call_resolved(gdpa, handle, FN_DEVICE_QUEUE_2),
            caps,
            instance_handle: inst_handle,
        },
    );
    log_at(LogLevel::Info, "vk device registered");
}

fn invoke_create_device(
    create_fn: unsafe extern "system" fn(),
    link: &VkLayerLinkInfo,
    loader_data: Option<PfnSetDeviceLoaderData>,
    inst: &VkInstState,
    inst_handle: u64,
    phys: vk::PhysicalDevice,
    ci: *const vk::DeviceCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Device,
) -> vk::Result {
    match unsafe {
        let cf: vk::PFN_vkCreateDevice = mem::transmute(create_fn);
        cf(phys, ci, alloc, out)
    } {
        vk::Result::SUCCESS => {
            register_device(
                link.pfn_next_get_device_proc_addr,
                loader_data,
                unsafe { *out },
                inst,
                inst_handle,
                phys,
                device_caps(inst, phys, ci),
            );
            vk::Result::SUCCESS
        }
        e => e,
    }
}

pub(crate) fn call_real_create_device(
    link: Option<VkLayerLinkInfo>,
    loader_data: Option<PfnSetDeviceLoaderData>,
    phys: vk::PhysicalDevice,
    ci: *const vk::DeviceCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Device,
) -> vk::Result {
    match (link, owning_instance(phys)) {
        (Some(l), Some((ih, inst))) => call_next_gipa(
            l.pfn_next_get_instance_proc_addr,
            vk::Instance::from_raw(ih),
            "vkCreateDevice",
        )
        .map(|f| invoke_create_device(f, &l, loader_data, &inst, ih, phys, ci, alloc, out))
        .unwrap_or(vk::Result::ERROR_INITIALIZATION_FAILED),
        (_, _) => vk::Result::ERROR_INITIALIZATION_FAILED,
    }
}
