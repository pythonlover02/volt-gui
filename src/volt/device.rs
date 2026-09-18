use std::collections::HashMap;
use std::collections::HashSet;
use std::ffi::c_void;
use std::mem;
use std::sync::Arc;
use std::sync::RwLock;

use ash::vk;
use ash::vk::Handle;

use crate::config::ensure_settings;
use crate::consts::FN_CREATE_RAY_TRACING_KHR;
use crate::consts::FN_CREATE_RAY_TRACING_NV;
use crate::consts::FN_CREATE_PIPELINE_BINARIES;
use crate::consts::FN_CREATE_SHADERS;
use crate::consts::FN_GET_PIPELINE_KEY;
use crate::consts::FN_PIPELINE_INDIRECT_MEMORY;
use crate::consts::FN_SET_ALPHA_COVERAGE;
use crate::consts::FN_SET_ALPHA_ONE;
use crate::consts::FN_SET_DEPTH_CLAMP;
use crate::consts::FN_SHARED_SWAPCHAINS;
use crate::consts::FN_WRITE_SAMPLERS;
use crate::consts::DEVICE_FEATURES_2_TYPE;
use crate::consts::EXT_MIXED_SAMPLES;
use crate::consts::FN_CREATE_DEVICE;
use crate::consts::FN_DEVICE_QUEUE_2;
use crate::consts::LOG_DEVICE_REGISTERED;
use crate::consts::EXT_PORTABILITY_SUBSET;
use crate::consts::DEVICE_GROUP_DEVICE_CREATE_INFO_TYPE;
use crate::consts::GPU_MISS_WARN;
use crate::consts::SETTING_GPU;
use crate::env::env_probe_active;
use crate::instance::call_all_devices;
use crate::instance::call_next_gdpa;
use crate::instance::call_next_gipa;
use crate::instance::cstr_names;
use crate::instance::device_index;
use crate::instance::owning_instance;
use crate::instance::provider_on;
use crate::instance::PfnCmdSetAlphaToCoverage;
use crate::instance::PfnCmdSetAlphaToOne;
use crate::instance::PfnCmdSetDepthClamp;
use crate::instance::PfnCreateRayTracingKHR;
use crate::instance::PfnCreateRayTracingNV;
use crate::instance::PfnCreateShaders;
use crate::instance::PfnCreatePipelineBinaries;
use crate::instance::PfnCreateSharedSwapchains;
use crate::instance::PfnGetDeviceQueue2;
use crate::instance::PfnGetPipelineKey;
use crate::instance::PfnPipelineIndirectMemory;
use crate::instance::PfnSetDeviceLoaderData;
use crate::instance::PfnWriteSamplers;
use crate::instance::walked_nodes;
use crate::instance::VkDeviceGroupDeviceCreateInfo;
use crate::instance::VkInstState;
use crate::instance::VkPhysicalDeviceFeatures2;
use crate::instance::VkLayerLinkInfo;
use crate::logging::info_wanted;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::present::call_forget_device_timelines;
use crate::probe::call_build_device;
use crate::probe::call_record_device;
use crate::report::call_forget_reports;
use crate::report::call_report_reading;
use crate::report::call_report_value;
use crate::report::count_text;
use crate::swapchain::call_forget_device_forced_modes;

#[derive(Clone, Copy, Default)]
pub(crate) struct DeviceCaps {
    pub(crate) sampler_anisotropy: bool,
    pub(crate) sample_rate_shading: bool,
    pub(crate) alpha_to_one: bool,
    pub(crate) depth_clamp: bool,
    pub(crate) max_anisotropy: f32,
    pub(crate) max_lod_bias: f32,
    pub(crate) max_lod_level: f32,
    pub(crate) portability_subset: bool,
    pub(crate) mixed_samples: bool,
}

pub(crate) struct VkDevState {
    pub(crate) device: ash::Device,
    pub(crate) phys: vk::PhysicalDevice,
    pub(crate) gdpa: vk::PFN_vkGetDeviceProcAddr,
    pub(crate) loader_data: Option<PfnSetDeviceLoaderData>,
    pub(crate) swap_fp: ash::khr::swapchain::DeviceFn,
    pub(crate) queue2_fp: Option<PfnGetDeviceQueue2>,
    pub(crate) shared_fp: Option<PfnCreateSharedSwapchains>,
    pub(crate) samplers_fp: Option<PfnWriteSamplers>,
    pub(crate) shaders_fp: Option<PfnCreateShaders>,
    pub(crate) ray_khr_fp: Option<PfnCreateRayTracingKHR>,
    pub(crate) ray_nv_fp: Option<PfnCreateRayTracingNV>,
    pub(crate) indirect_memory_fp: Option<PfnPipelineIndirectMemory>,
    pub(crate) alpha_fp: Option<PfnCmdSetAlphaToCoverage>,
    pub(crate) alpha_one_fp: Option<PfnCmdSetAlphaToOne>,
    pub(crate) clamp_fp: Option<PfnCmdSetDepthClamp>,
    pub(crate) caps: DeviceCaps,
    pub(crate) instance_handle: u64,
    pub(crate) api_version: u32,
    pub(crate) extensions: HashSet<String>,
    pub(crate) pipeline_key_fp: Option<PfnGetPipelineKey>,
    pub(crate) pipeline_binaries_fp: Option<PfnCreatePipelineBinaries>,
}

pub(crate) fn device_hook_on(dev: &VkDevState, command: &str) -> bool {
    provider_on(dev.api_version, &dev.extensions, command)
}

pub(crate) fn requested_device_extensions(ci: *const vk::DeviceCreateInfo<'_>) -> HashSet<String> {
    cstr_names(unsafe { (*ci).pp_enabled_extension_names }, unsafe {
        (*ci).enabled_extension_count
    })
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

pub(crate) fn call_devs_put(h: u64, v: VkDevState) {
    match DEVS.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).insert(h, Arc::new(v));
        }
        Err(_) => (),
    }
}

fn call_queue_dev_forget(dev: u64) {
    match QUEUE_TO_DEV.write() {
        Ok(mut g) => g
            .iter_mut()
            .for_each(|m| m.retain(|_, owner| *owner != dev)),
        Err(_) => (),
    }
}

fn call_cmdbuf_dev_forget(dev: u64) {
    match CMDBUF_TO_DEV.write() {
        Ok(mut g) => g
            .iter_mut()
            .for_each(|m| m.retain(|_, owner| owner.0 != dev)),
        Err(_) => (),
    }
}

pub(crate) fn call_devs_del(h: u64) -> Option<Arc<VkDevState>> {
    call_queue_dev_forget(h);
    call_cmdbuf_dev_forget(h);
    call_forget_reports(h);
    call_forget_device_timelines(h);
    call_forget_device_forced_modes(h);
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

pub(crate) fn call_queue_dev_put(q: u64, d: u64) {
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

fn call_cmdbuf_dev_put(c: u64, owner: (u64, u64)) {
    match CMDBUF_TO_DEV.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).insert(c, owner);
        }
        Err(_) => (),
    }
}

fn call_cmdbuf_dev_del(c: u64) {
    match CMDBUF_TO_DEV.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).remove(&c);
        }
        Err(_) => (),
    }
}

fn call_cmdbuf_pool_forget(dev: u64, pool: u64) {
    match CMDBUF_TO_DEV.write() {
        Ok(mut g) => g
            .iter_mut()
            .for_each(|m| m.retain(|_, owner| *owner != (dev, pool))),
        Err(_) => (),
    }
}

pub(crate) fn cmdbuf_owner(buffer: vk::CommandBuffer) -> Option<Arc<VkDevState>> {
    cmdbuf_dev_get(buffer.as_raw()).and_then(devs_get)
}

fn lod_levels_for(max_dimension: u32) -> f32 {
    (max_dimension.max(1) as f32).log2().floor()
}

pub(crate) fn limit_caps(props: &vk::PhysicalDeviceProperties) -> DeviceCaps {
    DeviceCaps {
        max_anisotropy: props.limits.max_sampler_anisotropy,
        max_lod_bias: props.limits.max_sampler_lod_bias,
        max_lod_level: lod_levels_for(props.limits.max_image_dimension2_d),
        ..DeviceCaps::default()
    }
}

fn build_caps(
    props: &vk::PhysicalDeviceProperties,
    asked: &vk::PhysicalDeviceFeatures,
    extensions: &HashSet<String>,
) -> DeviceCaps {
    DeviceCaps {
        sampler_anisotropy: asked.sampler_anisotropy == vk::TRUE,
        sample_rate_shading: asked.sample_rate_shading == vk::TRUE,
        alpha_to_one: asked.alpha_to_one == vk::TRUE,
        depth_clamp: asked.depth_clamp == vk::TRUE,
        max_anisotropy: props.limits.max_sampler_anisotropy,
        max_lod_bias: props.limits.max_sampler_lod_bias,
        max_lod_level: lod_levels_for(props.limits.max_image_dimension2_d),
        portability_subset: extensions.contains(EXT_PORTABILITY_SUBSET),
        mixed_samples: extensions.contains(EXT_MIXED_SAMPLES),
    }
}

fn chained_features(p_next: *const c_void) -> Option<vk::PhysicalDeviceFeatures> {
    walked_nodes(p_next)
        .into_iter()
        .find(|node| unsafe { (**node).s_type.as_raw() } as u32 == DEVICE_FEATURES_2_TYPE)
        .map(|node| unsafe { (*(node as *const VkPhysicalDeviceFeatures2)).features })
}

fn plain_features(ci: &vk::DeviceCreateInfo<'_>) -> Option<vk::PhysicalDeviceFeatures> {
    match ci.p_enabled_features.is_null() {
        true => None,
        false => Some(unsafe { *ci.p_enabled_features }),
    }
}

fn asked_features(ci: *const vk::DeviceCreateInfo<'_>) -> vk::PhysicalDeviceFeatures {
    match chained_features(unsafe { (*ci).p_next }) {
        Some(features) => features,
        None => plain_features(unsafe { &*ci }).unwrap_or_default(),
    }
}

fn load_swap_fp(
    gdpa: vk::PFN_vkGetDeviceProcAddr,
    handle: vk::Device,
) -> ash::khr::swapchain::DeviceFn {
    ash::khr::swapchain::DeviceFn::load(|name| unsafe {
        mem::transmute(gdpa(handle, name.as_ptr()))
    })
}

fn call_typed_device_fp<T>(
    gdpa: vk::PFN_vkGetDeviceProcAddr,
    handle: vk::Device,
    name: &str,
) -> Option<T> {
    call_next_gdpa(gdpa, handle, name).map(|f| unsafe { mem::transmute_copy(&f) })
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
    ci: *const vk::DeviceCreateInfo<'_>,
) -> DeviceCaps {
    build_caps(
        unsafe { &inst.instance.get_physical_device_properties(phys) },
        &asked_features(ci),
        &requested_device_extensions(ci),
    )
}

fn call_record_command_buffers(
    dev: vk::Device,
    info: *const vk::CommandBufferAllocateInfo<'_>,
    out: *mut vk::CommandBuffer,
) {
    (0..unsafe { (*info).command_buffer_count } as usize).for_each(|at| {
        call_cmdbuf_dev_put(
            unsafe { (*out.add(at)).as_raw() },
            (dev.as_raw(), unsafe { (*info).command_pool.as_raw() }),
        )
    });
}

fn call_forget_command_buffers(count: u32, buffers: *const vk::CommandBuffer) {
    (0..count as usize).for_each(|at| call_cmdbuf_dev_del(unsafe { (*buffers.add(at)).as_raw() }));
}

pub(crate) fn call_allocate_command_buffers(
    d: &VkDevState,
    dev: vk::Device,
    info: *const vk::CommandBufferAllocateInfo<'_>,
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
    alloc: *const vk::AllocationCallbacks<'_>,
) {
    call_cmdbuf_pool_forget(dev.as_raw(), pool.as_raw());
    unsafe { (d.device.fp_v1_0().destroy_command_pool)(dev, pool, alloc) };
}

fn group_create_node(p_next: *const c_void) -> Option<*const VkDeviceGroupDeviceCreateInfo> {
    walked_nodes(p_next)
        .into_iter()
        .find(|node| unsafe { (**node).s_type.as_raw() } as u32 == DEVICE_GROUP_DEVICE_CREATE_INFO_TYPE)
        .map(|node| node as *const VkDeviceGroupDeviceCreateInfo)
}

fn group_device_ids(
    all: &[vk::PhysicalDevice],
    node: *const VkDeviceGroupDeviceCreateInfo,
) -> Vec<u32> {
    (0..unsafe { (*node).physical_device_count } as usize)
        .map(|at| device_index(all, unsafe { *(*node).p_physical_devices.add(at) }))
        .collect()
}

fn asked_group(ci: *const vk::DeviceCreateInfo<'_>, all: &[vk::PhysicalDevice]) -> Option<Vec<u32>> {
    group_create_node(unsafe { (*ci).p_next }).map(|node| group_device_ids(all, node))
}

fn call_gpu_missed(ids: &[u32], chosen: u32) {
    match ids.contains(&chosen) {
        true => (),
        false => log_at(LogLevel::Warn, GPU_MISS_WARN),
    }
}

fn call_gpu_warned(id: u32, chosen: Option<u32>, group: Option<Vec<u32>>) {
    match chosen {
        Some(value) => call_gpu_missed(&group.unwrap_or_else(|| vec![id]), value),
        None => (),
    }
}

fn call_gpu_reported(id: u32, owner: u64, chosen: Option<u32>) {
    match info_wanted() {
        true => match chosen {
            Some(forced) => call_report_value(owner, SETTING_GPU, id, forced, count_text, None),
            None => call_report_reading(owner, SETTING_GPU, count_text(id)),
        },
        false => (),
    }
}

fn call_gpu_lines(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    ci: *const vk::DeviceCreateInfo<'_>,
    owner: u64,
    chosen: Option<u32>,
) {
    let all = call_all_devices(inst);
    let id = device_index(&all, phys);
    call_gpu_warned(id, chosen, asked_group(ci, &all));
    call_gpu_reported(id, owner, chosen);
}

fn gpu_line_wanted(chosen: Option<u32>) -> bool {
    match chosen {
        Some(_) => true,
        None => info_wanted(),
    }
}

fn call_probe_device(inst: &VkInstState, phys: vk::PhysicalDevice, caps: &DeviceCaps) {
    match env_probe_active() {
        true => call_record_device(call_build_device(inst, phys, caps)),
        false => (),
    }
}

fn call_report_gpu(
    inst: &VkInstState,
    phys: vk::PhysicalDevice,
    ci: *const vk::DeviceCreateInfo<'_>,
    handle: vk::Device,
) {
    let chosen = ensure_settings().gpu;
    match gpu_line_wanted(chosen) {
        true => call_gpu_lines(inst, phys, ci, handle.as_raw(), chosen),
        false => (),
    }
}

fn call_register_device(
    gdpa: vk::PFN_vkGetDeviceProcAddr,
    loader_data: Option<PfnSetDeviceLoaderData>,
    handle: vk::Device,
    inst: &VkInstState,
    inst_handle: u64,
    phys: vk::PhysicalDevice,
    caps: DeviceCaps,
    ci: *const vk::DeviceCreateInfo<'_>,
) {
    let device = unsafe {
        ash::Device::load_with(|name| mem::transmute(gdpa(handle, name.as_ptr())), handle)
    };
    call_devs_put(
        handle.as_raw(),
        VkDevState {
            device,
            phys,
            gdpa,
            loader_data,
            swap_fp: load_swap_fp(gdpa, handle),
            queue2_fp: call_typed_device_fp(gdpa, handle, FN_DEVICE_QUEUE_2),
            shared_fp: call_typed_device_fp(gdpa, handle, FN_SHARED_SWAPCHAINS),
            samplers_fp: call_typed_device_fp(gdpa, handle, FN_WRITE_SAMPLERS),
            shaders_fp: call_typed_device_fp(gdpa, handle, FN_CREATE_SHADERS),
            ray_khr_fp: call_typed_device_fp(gdpa, handle, FN_CREATE_RAY_TRACING_KHR),
            ray_nv_fp: call_typed_device_fp(gdpa, handle, FN_CREATE_RAY_TRACING_NV),
            indirect_memory_fp: call_typed_device_fp(gdpa, handle, FN_PIPELINE_INDIRECT_MEMORY),
            alpha_fp: call_typed_device_fp(gdpa, handle, FN_SET_ALPHA_COVERAGE),
            alpha_one_fp: call_typed_device_fp(gdpa, handle, FN_SET_ALPHA_ONE),
            clamp_fp: call_typed_device_fp(gdpa, handle, FN_SET_DEPTH_CLAMP),
            caps,
            instance_handle: inst_handle,
            api_version: inst.api_version,
            extensions: requested_device_extensions(ci),
            pipeline_key_fp: call_typed_device_fp(gdpa, handle, FN_GET_PIPELINE_KEY),
            pipeline_binaries_fp: call_typed_device_fp(gdpa, handle, FN_CREATE_PIPELINE_BINARIES),
        },
    );
    call_probe_device(inst, phys, &caps);
    call_report_gpu(inst, phys, ci, handle);
    log_at(LogLevel::Info, LOG_DEVICE_REGISTERED);
}

fn call_invoke_create_device(
    create_fn: unsafe extern "system" fn(),
    link: &VkLayerLinkInfo,
    loader_data: Option<PfnSetDeviceLoaderData>,
    inst: &VkInstState,
    inst_handle: u64,
    phys: vk::PhysicalDevice,
    ci: *const vk::DeviceCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Device,
) -> vk::Result {
    match unsafe {
        let cf: vk::PFN_vkCreateDevice = mem::transmute(create_fn);
        cf(phys, ci, alloc, out)
    } {
        vk::Result::SUCCESS => {
            call_register_device(
                link.pfn_next_get_device_proc_addr,
                loader_data,
                unsafe { *out },
                inst,
                inst_handle,
                phys,
                device_caps(inst, phys, ci),
                ci,
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
    ci: *const vk::DeviceCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Device,
) -> vk::Result {
    match (link, owning_instance(phys)) {
        (Some(l), Some((ih, inst))) => call_next_gipa(
            l.pfn_next_get_instance_proc_addr,
            vk::Instance::from_raw(ih),
            FN_CREATE_DEVICE,
        )
        .map(|f| call_invoke_create_device(f, &l, loader_data, &inst, ih, phys, ci, alloc, out))
        .unwrap_or(vk::Result::ERROR_INITIALIZATION_FAILED),
        (_, _) => vk::Result::ERROR_INITIALIZATION_FAILED,
    }
}
