use std::ffi::c_char;
use std::ffi::c_void;
use std::ffi::CStr;
use std::mem;
use std::ptr;
use std::sync::Arc;

use ash::vk;
use ash::vk::Handle;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::FN_ALLOCATE_COMMAND_BUFFERS;
use crate::consts::FN_CREATE_COMPUTE_PIPELINES;
use crate::consts::FN_CREATE_DEVICE;
use crate::consts::FN_CREATE_GRAPHICS_PIPELINES;
use crate::consts::FN_CREATE_INSTANCE;
use crate::consts::FN_CREATE_PIPELINE_BINARIES;
use crate::consts::FN_CREATE_SAMPLER;
use crate::consts::FN_DESTROY_COMMAND_POOL;
use crate::consts::FN_DESTROY_DEVICE;
use crate::consts::FN_DESTROY_INSTANCE;
use crate::consts::FN_DEVICE_QUEUE;
use crate::consts::FN_ENUMERATE_DEVICES;
use crate::consts::FN_FREE_COMMAND_BUFFERS;
use crate::consts::FN_GET_DEVICE_PROC_ADDR;
use crate::consts::FN_GET_INSTANCE_PROC_ADDR;
use crate::consts::LOG_QUEUE_2_UNREGISTERED;
use crate::consts::LOG_QUEUE_UNREGISTERED;
use crate::consts::FN_GET_PIPELINE_KEY;
use crate::consts::FN_CREATE_RAY_TRACING_KHR;
use crate::consts::FN_CREATE_RAY_TRACING_NV;
use crate::consts::FN_CREATE_SHADERS;
use crate::consts::FN_CREATE_SWAPCHAIN;
use crate::consts::FN_CREATE_WAYLAND_SURFACE;
use crate::consts::FN_PIPELINE_INDIRECT_MEMORY;
use crate::consts::FN_CREATE_XCB_SURFACE;
use crate::consts::FN_CREATE_XLIB_SURFACE;
use crate::consts::FN_DESTROY_SURFACE;
use crate::consts::FN_DESTROY_SWAPCHAIN;
use crate::consts::FN_DEVICE_GROUPS;
use crate::consts::FN_DEVICE_GROUPS_KHR;
use crate::consts::FN_DEVICE_QUEUE_2;
use crate::consts::FN_QUEUE_PRESENT;
use crate::consts::FN_SET_ALPHA_COVERAGE;
use crate::consts::FN_SET_ALPHA_ONE;
use crate::consts::FN_SET_DEPTH_CLAMP;
use crate::consts::FN_SHARED_SWAPCHAINS;
use crate::consts::FN_SURFACE_CAPS;
use crate::consts::FN_SURFACE_CAPS_2;
use crate::consts::FN_SURFACE_PRESENT_MODES;
use crate::consts::FN_WRITE_SAMPLERS;
use crate::consts::CORE_10_DEVICE_HOOKS;
use crate::consts::LAYER_DATA_CALLBACK;
use crate::consts::LAYER_IFACE_VERSION;
use crate::consts::LAYER_LINK_INFO;
use crate::consts::LAYER_NEGOTIATE_INTERFACE_STRUCT;
use crate::consts::LimitStage;
use crate::consts::NULL_OK;
use crate::consts::TAG_WAYLAND;
use crate::consts::TAG_XCB;
use crate::consts::UNOWNED_QUEUE_ERROR;
use crate::device::call_allocate_command_buffers;
use crate::device::call_destroy_command_pool;
use crate::device::call_free_command_buffers;
use crate::device::call_real_create_device;
use crate::device::call_register_queue;
use crate::device::cmdbuf_owner;
use crate::device::device_hook_on;
use crate::device::devs_del;
use crate::device::devs_gdpa;
use crate::device::devs_get;
use crate::device::queue_dev_put;
use crate::device::queue_owner;
use crate::device::VkDevState;
use crate::instance::call_advance_chain;
use crate::instance::call_create_tagged_surface;
use crate::instance::call_destroy_tagged_surface;
use crate::instance::call_filtered_enumerate;
use crate::instance::call_filtered_groups;
use crate::instance::call_filtered_groups_khr;
use crate::instance::call_loader_data_fn;
use crate::instance::call_next_gdpa;
use crate::instance::call_next_gipa;
use crate::instance::call_real_create_instance;
use crate::instance::chain_layer_info;
use crate::instance::insts_del;
use crate::instance::insts_get;
use crate::instance::provider_on;
use crate::instance::VkHandle;
use crate::instance::VkPhysicalDeviceGroupProperties;
use crate::instance::VkPhysicalDeviceSurfaceInfo2;
use crate::instance::VkPipelineBinaryCreateInfoKHR;
use crate::instance::VkPipelineCreateInfoKHR;
use crate::instance::VkRayTracingPipelineCreateInfoKHR;
use crate::instance::VkRayTracingPipelineCreateInfoNV;
use crate::instance::VkShaderCreateInfoEXT;
use crate::instance::VkSurfaceCapabilities2;
use crate::logging::init_log_level;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::pipeline::call_create_compute_pipelines;
use crate::pipeline::call_create_pipeline_binaries;
use crate::pipeline::call_create_graphics_pipelines;
use crate::pipeline::call_create_ray_tracing_khr;
use crate::pipeline::call_create_ray_tracing_nv;
use crate::pipeline::call_create_shaders;
use crate::pipeline::call_get_pipeline_key;
use crate::pipeline::call_pipeline_indirect_memory;
use crate::pipeline::call_set_alpha_coverage;
use crate::pipeline::call_set_alpha_one;
use crate::pipeline::call_set_depth_clamp;
use crate::present::call_forget_timeline;
use crate::present::call_present_frame;
use crate::present::maybe_limit_frame;
use crate::sampler::call_create_sampler;
use crate::sampler::call_write_sampler_descriptors;
use crate::swapchain::call_create_shared_swapchains;
use crate::swapchain::call_forget_forced_mode;
use crate::swapchain::call_create_swapchain;
use crate::swapchain::call_surface_capabilities;
use crate::swapchain::call_surface_capabilities2;
use crate::swapchain::call_surface_present_modes;

pub(crate) fn negotiated_version(offered: u32, wanted: u32) -> Option<u32> {
    match offered < wanted {
        true => None,
        false => Some(wanted),
    }
}

#[repr(C)]
struct VkNegotiateLayerInterface {
    s_type: i32,
    p_next: *mut c_void,
    loader_layer_interface_version: u32,
    pfn_get_instance_proc_addr: Option<vk::PFN_vkGetInstanceProcAddr>,
    pfn_get_device_proc_addr: Option<vk::PFN_vkGetDeviceProcAddr>,
    pfn_get_physical_device_proc_addr: Option<vk::PFN_vkVoidFunction>,
}

fn cstr_to_str<'a>(p: *const c_char) -> &'a str {
    match p.is_null() {
        true => "",
        false => unsafe { CStr::from_ptr(p).to_str().unwrap_or("") },
    }
}

fn null_ok_name(name: &str) -> bool {
    NULL_OK.contains(&name)
}

fn instance_symbol(name: &str) -> Option<*mut c_void> {
    match name {
        FN_GET_INSTANCE_PROC_ADDR => Some(vkGetInstanceProcAddr as *mut c_void),
        FN_GET_DEVICE_PROC_ADDR => Some(vkGetDeviceProcAddr as *mut c_void),
        FN_CREATE_INSTANCE => Some(vkCreateInstance as *mut c_void),
        FN_DESTROY_INSTANCE => Some(vkDestroyInstance as *mut c_void),
        FN_CREATE_DEVICE => Some(vkCreateDevice as *mut c_void),
        FN_ENUMERATE_DEVICES => Some(vkEnumeratePhysicalDevices as *mut c_void),
        _ => None,
    }
}

fn instance_surface_symbol(name: &str) -> Option<*mut c_void> {
    match name {
        FN_SURFACE_PRESENT_MODES => Some(vkGetPhysicalDeviceSurfacePresentModesKHR as *mut c_void),
        FN_SURFACE_CAPS => Some(vkGetPhysicalDeviceSurfaceCapabilitiesKHR as *mut c_void),
        _ => None,
    }
}

fn instance_gated_surface(inst: vk::Instance, name: &str) -> Option<*mut c_void> {
    instance_surface_symbol(name).filter(|_| {
        insts_get(inst.as_raw())
            .map(|st| provider_on(st.api_version, &st.extensions, name))
            .unwrap_or(false)
    })
}

fn device_symbol(name: &str) -> Option<*mut c_void> {
    match name {
        FN_GET_DEVICE_PROC_ADDR => Some(vkGetDeviceProcAddr as *mut c_void),
        FN_DESTROY_DEVICE => Some(vkDestroyDevice as *mut c_void),
        FN_CREATE_GRAPHICS_PIPELINES => Some(vkCreateGraphicsPipelines as *mut c_void),
        FN_CREATE_COMPUTE_PIPELINES => Some(vkCreateComputePipelines as *mut c_void),
        FN_CREATE_SAMPLER => Some(vkCreateSampler as *mut c_void),
        FN_ALLOCATE_COMMAND_BUFFERS => Some(vkAllocateCommandBuffers as *mut c_void),
        FN_FREE_COMMAND_BUFFERS => Some(vkFreeCommandBuffers as *mut c_void),
        FN_DESTROY_COMMAND_POOL => Some(vkDestroyCommandPool as *mut c_void),
        FN_DEVICE_QUEUE => Some(volt_GetDeviceQueue as *mut c_void),
        _ => None,
    }
}

fn device_provided_symbol(name: &str) -> Option<*mut c_void> {
    match name {
        FN_DEVICE_QUEUE_2 => Some(volt_GetDeviceQueue2 as *mut c_void),
        FN_CREATE_SWAPCHAIN => Some(vkCreateSwapchainKHR as *mut c_void),
        FN_DESTROY_SWAPCHAIN => Some(vkDestroySwapchainKHR as *mut c_void),
        FN_QUEUE_PRESENT => Some(vkQueuePresentKHR as *mut c_void),
        _ => None,
    }
}

fn device_provided_hooked(dev: vk::Device, name: &str) -> Option<*mut c_void> {
    device_provided_symbol(name).filter(|_| {
        devs_get(dev.as_raw())
            .map(|d| device_hook_on(&d, name))
            .unwrap_or(false)
    })
}

fn instance_extension_hook(name: &str) -> Option<*mut c_void> {
    match name {
        FN_SURFACE_CAPS_2 => Some(vkGetPhysicalDeviceSurfaceCapabilities2KHR as *mut c_void),
        FN_DEVICE_GROUPS => Some(vkEnumeratePhysicalDeviceGroups as *mut c_void),
        FN_DEVICE_GROUPS_KHR => Some(vkEnumeratePhysicalDeviceGroupsKHR as *mut c_void),
        FN_CREATE_XCB_SURFACE => Some(vkCreateXcbSurfaceKHR as *mut c_void),
        FN_CREATE_XLIB_SURFACE => Some(vkCreateXlibSurfaceKHR as *mut c_void),
        FN_CREATE_WAYLAND_SURFACE => Some(vkCreateWaylandSurfaceKHR as *mut c_void),
        FN_DESTROY_SURFACE => Some(vkDestroySurfaceKHR as *mut c_void),
        _ => None,
    }
}

fn instance_pointer_present(st: &crate::instance::VkInstState, name: &str) -> bool {
    match name {
        FN_SURFACE_CAPS_2 => st.caps2_fp.is_some(),
        FN_DEVICE_GROUPS => st.groups_fp.is_some(),
        FN_DEVICE_GROUPS_KHR => st.groups_khr_fp.is_some(),
        FN_DESTROY_SURFACE => st.destroy_surface_fp.is_some(),
        other => st.surface_fps.contains_key(other),
    }
}

fn instance_fp_present(inst: vk::Instance, name: &str) -> bool {
    match insts_get(inst.as_raw()) {
        Some(st) => {
            provider_on(st.api_version, &st.extensions, name)
                && instance_pointer_present(&st, name)
        }
        None => false,
    }
}

fn instance_hooked_symbol(inst: vk::Instance, name: &str) -> Option<*mut c_void> {
    instance_extension_hook(name).filter(|_| instance_fp_present(inst, name))
}

fn device_extension_hook(name: &str) -> Option<*mut c_void> {
    match name {
        FN_GET_PIPELINE_KEY => Some(vkGetPipelineKeyKHR as *mut c_void),
        FN_CREATE_PIPELINE_BINARIES => Some(vkCreatePipelineBinariesKHR as *mut c_void),
        FN_SHARED_SWAPCHAINS => Some(vkCreateSharedSwapchainsKHR as *mut c_void),
        FN_WRITE_SAMPLERS => Some(vkWriteSamplerDescriptorsEXT as *mut c_void),
        FN_CREATE_SHADERS => Some(vkCreateShadersEXT as *mut c_void),
        FN_CREATE_RAY_TRACING_KHR => Some(vkCreateRayTracingPipelinesKHR as *mut c_void),
        FN_CREATE_RAY_TRACING_NV => Some(vkCreateRayTracingPipelinesNV as *mut c_void),
        FN_PIPELINE_INDIRECT_MEMORY => Some(vkGetPipelineIndirectMemoryRequirementsNV as *mut c_void),
        FN_SET_ALPHA_COVERAGE => Some(vkCmdSetAlphaToCoverageEnableEXT as *mut c_void),
        FN_SET_ALPHA_ONE => Some(vkCmdSetAlphaToOneEnableEXT as *mut c_void),
        FN_SET_DEPTH_CLAMP => Some(vkCmdSetDepthClampEnableEXT as *mut c_void),
        _ => None,
    }
}

fn device_pointer_present(d: &VkDevState, name: &str) -> bool {
    match name {
        FN_GET_PIPELINE_KEY => d.pipeline_key_fp.is_some(),
        FN_CREATE_PIPELINE_BINARIES => d.pipeline_binaries_fp.is_some(),
        FN_SHARED_SWAPCHAINS => d.shared_fp.is_some(),
        FN_WRITE_SAMPLERS => d.samplers_fp.is_some(),
        FN_CREATE_SHADERS => d.shaders_fp.is_some(),
        FN_CREATE_RAY_TRACING_KHR => d.ray_khr_fp.is_some(),
        FN_CREATE_RAY_TRACING_NV => d.ray_nv_fp.is_some(),
        FN_PIPELINE_INDIRECT_MEMORY => d.indirect_memory_fp.is_some(),
        FN_SET_ALPHA_COVERAGE => d.alpha_fp.is_some(),
        FN_SET_ALPHA_ONE => d.alpha_one_fp.is_some(),
        FN_SET_DEPTH_CLAMP => d.clamp_fp.is_some(),
        _ => false,
    }
}

fn device_fp_present(dev: vk::Device, name: &str) -> bool {
    match devs_get(dev.as_raw()) {
        Some(d) => device_hook_on(&d, name) && device_pointer_present(&d, name),
        None => false,
    }
}

fn device_hooked_symbol(dev: vk::Device, name: &str) -> Option<*mut c_void> {
    device_extension_hook(name).filter(|_| device_fp_present(dev, name))
}

fn device_core_symbol(name: &str) -> Option<*mut c_void> {
    device_symbol(name).filter(|_| CORE_10_DEVICE_HOOKS.contains(&name))
}

fn null_ok_ptr(name: &str) -> *mut c_void {
    match name {
        FN_GET_INSTANCE_PROC_ADDR => vkGetInstanceProcAddr as *mut c_void,
        FN_CREATE_INSTANCE => vkCreateInstance as *mut c_void,
        _ => ptr::null_mut(),
    }
}

fn forward_device_proc(dev: vk::Device, name: &str) -> vk::PFN_vkVoidFunction {
    match devs_gdpa(dev.as_raw()) {
        Some(gdpa) => call_next_gdpa(gdpa, dev, name),
        None => None,
    }
}

fn forward_instance_proc(inst: vk::Instance, name: &str) -> vk::PFN_vkVoidFunction {
    match insts_get(inst.as_raw()) {
        Some(st) => call_next_gipa(st.gipa, inst, name),
        None => None,
    }
}

fn instance_path_symbol(inst: vk::Instance, name: &str) -> Option<*mut c_void> {
    match (
        instance_symbol(name),
        device_core_symbol_by_name(name),
        instance_gated_surface(inst, name),
        instance_hooked_symbol(inst, name),
    ) {
        (Some(p), _, _, _) => Some(p),
        (None, Some(p), _, _) => Some(p),
        (None, None, Some(p), _) => Some(p),
        (None, None, None, found) => found,
    }
}

fn device_core_symbol_by_name(name: &str) -> Option<*mut c_void> {
    device_core_symbol(name)
}

fn resolve_instance_proc(inst: vk::Instance, name: &str) -> vk::PFN_vkVoidFunction {
    match instance_path_symbol(inst, name) {
        Some(p) => unsafe { mem::transmute(p) },
        None => forward_instance_proc(inst, name),
    }
}

fn resolve_null_instance_proc(name: &str) -> vk::PFN_vkVoidFunction {
    match null_ok_name(name) {
        true => unsafe { mem::transmute(null_ok_ptr(name)) },
        false => None,
    }
}

fn call_chain_destroy_instance(gipa: vk::PFN_vkGetInstanceProcAddr, inst: vk::Instance, alloc: *const vk::AllocationCallbacks<'_>) {
    match call_next_gipa(gipa, inst, FN_DESTROY_INSTANCE) {
        Some(d) => unsafe {
            let df: vk::PFN_vkDestroyInstance = mem::transmute(d);
            df(inst, alloc);
        },
        None => (),
    }
}

fn call_unowned_present() -> vk::Result {
    log_at(LogLevel::Error, UNOWNED_QUEUE_ERROR);
    vk::Result::ERROR_INITIALIZATION_FAILED
}

fn call_forward_present(
    owner: Option<Arc<VkDevState>>,
    queue: vk::Queue,
    info: *const vk::PresentInfoKHR<'_>,
) -> vk::Result {
    match owner {
        Some(d) => call_present_frame(&d, queue, info),
        None => call_unowned_present(),
    }
}

fn call_staged_limit(
    stage: LimitStage,
    s: &Settings,
    dev: Option<u64>,
    info: *const vk::PresentInfoKHR<'_>,
) {
    match dev {
        Some(handle) => maybe_limit_frame(stage, s, handle, info),
        None => (),
    }
}

fn call_after_present(
    presented: vk::Result,
    s: &Settings,
    dev: Option<u64>,
    info: *const vk::PresentInfoKHR<'_>,
) -> vk::Result {
    call_staged_limit(LimitStage::After, s, dev, info);
    presented
}

fn call_limited_present(
    owner: Option<Arc<VkDevState>>,
    queue: vk::Queue,
    info: *const vk::PresentInfoKHR<'_>,
) -> vk::Result {
    let s = ensure_settings();
    let dev = owner.as_ref().map(|d| d.device.handle().as_raw());
    call_staged_limit(LimitStage::Before, s, dev, info);
    call_after_present(call_forward_present(owner, queue, info), s, dev, info)
}

extern "system" fn volt_GetDeviceQueue(dev: vk::Device, qfam: u32, qidx: u32, out: *mut vk::Queue) {
    match devs_get(dev.as_raw()) {
        Some(d) => {
            let q = unsafe { d.device.get_device_queue(qfam, qidx) };
            call_register_queue(&d, dev, q);
            queue_dev_put(q.as_raw(), dev.as_raw());
            unsafe { *out = q };
        }
        None => log_at(LogLevel::Warn, LOG_QUEUE_UNREGISTERED),
    }
}

extern "system" fn volt_GetDeviceQueue2(dev: vk::Device, info: *const c_void, out: *mut vk::Queue) {
    match devs_get(dev.as_raw()).and_then(|d| d.queue2_fp.map(|fp| (d, fp))) {
        Some((d, fp)) => {
            unsafe { fp(dev, info, out) };
            let q = unsafe { *out };
            call_register_queue(&d, dev, q);
            queue_dev_put(q.as_raw(), dev.as_raw());
        }
        None => log_at(LogLevel::Warn, LOG_QUEUE_2_UNREGISTERED),
    }
}

extern "system" fn vkGetInstanceProcAddr(inst: vk::Instance, name: *const c_char) -> vk::PFN_vkVoidFunction {
    let n = cstr_to_str(name);
    match inst == vk::Instance::null() {
        true => resolve_null_instance_proc(n),
        false => resolve_instance_proc(inst, n),
    }
}

extern "system" fn vkGetDeviceProcAddr(dev: vk::Device, name: *const c_char) -> vk::PFN_vkVoidFunction {
    let n = cstr_to_str(name);
    match (
        device_core_symbol(n),
        device_provided_hooked(dev, n),
        device_hooked_symbol(dev, n),
    ) {
        (Some(p), _, _) => unsafe { mem::transmute(p) },
        (None, Some(p), _) => unsafe { mem::transmute(p) },
        (None, None, Some(p)) => unsafe { mem::transmute(p) },
        (None, None, None) => forward_device_proc(dev, n),
    }
}

extern "system" fn vkCreateInstance(
    ci: *const vk::InstanceCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Instance,
) -> vk::Result {
    init_log_level();
    call_real_create_instance(
        call_advance_chain(chain_layer_info(
            unsafe { (*ci).p_next },
            vk::StructureType::LOADER_INSTANCE_CREATE_INFO,
            LAYER_LINK_INFO,
        )),
        ci,
        alloc,
        out,
    )
}

extern "system" fn vkDestroyInstance(inst: vk::Instance, alloc: *const vk::AllocationCallbacks<'_>) {
    let st = insts_get(inst.as_raw());
    insts_del(inst.as_raw());
    match st {
        Some(s) => call_chain_destroy_instance(s.gipa, inst, alloc),
        None => (),
    }
}

extern "system" fn vkEnumeratePhysicalDevices(
    inst: vk::Instance,
    count: *mut u32,
    devices: *mut vk::PhysicalDevice,
) -> vk::Result {
    call_filtered_enumerate(inst, count, devices)
}

extern "system" fn vkEnumeratePhysicalDeviceGroups(
    inst: vk::Instance,
    count: *mut u32,
    groups: *mut VkPhysicalDeviceGroupProperties,
) -> vk::Result {
    call_filtered_groups(inst, count, groups)
}

extern "system" fn vkEnumeratePhysicalDeviceGroupsKHR(
    inst: vk::Instance,
    count: *mut u32,
    groups: *mut VkPhysicalDeviceGroupProperties,
) -> vk::Result {
    call_filtered_groups_khr(inst, count, groups)
}

extern "system" fn vkCreateDevice(
    phys: vk::PhysicalDevice,
    ci: *const vk::DeviceCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Device,
) -> vk::Result {
    call_real_create_device(
        call_advance_chain(chain_layer_info(
            unsafe { (*ci).p_next },
            vk::StructureType::LOADER_DEVICE_CREATE_INFO,
            LAYER_LINK_INFO,
        )),
        call_loader_data_fn(chain_layer_info(
            unsafe { (*ci).p_next },
            vk::StructureType::LOADER_DEVICE_CREATE_INFO,
            LAYER_DATA_CALLBACK,
        )),
        phys,
        ci,
        alloc,
        out,
    )
}

extern "system" fn vkDestroyDevice(dev: vk::Device, alloc: *const vk::AllocationCallbacks<'_>) {
    match devs_del(dev.as_raw()) {
        Some(d) => unsafe { d.device.destroy_device(alloc.as_ref()) },
        None => (),
    }
}

extern "system" fn vkCreateGraphicsPipelines(
    dev: vk::Device,
    cache: vk::PipelineCache,
    count: u32,
    cis: *const vk::GraphicsPipelineCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Pipeline,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_create_graphics_pipelines(&d, cache, count, cis, alloc, out),
    }
}

extern "system" fn vkCreateComputePipelines(
    dev: vk::Device,
    cache: vk::PipelineCache,
    count: u32,
    cis: *const vk::ComputePipelineCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Pipeline,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_create_compute_pipelines(&d, cache, count, cis, alloc, out),
    }
}

extern "system" fn vkCreateShadersEXT(
    dev: vk::Device,
    count: u32,
    cis: *const VkShaderCreateInfoEXT,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut VkHandle,
) -> vk::Result {
    match devs_get(dev.as_raw()).and_then(|d| d.shaders_fp.map(|fp| (d, fp))) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some((d, fp)) => call_create_shaders(&d, fp, dev, count, cis, alloc, out),
    }
}

extern "system" fn vkCreateRayTracingPipelinesKHR(
    dev: vk::Device,
    deferred: VkHandle,
    cache: vk::PipelineCache,
    count: u32,
    cis: *const VkRayTracingPipelineCreateInfoKHR,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Pipeline,
) -> vk::Result {
    match devs_get(dev.as_raw()).and_then(|d| d.ray_khr_fp.map(|fp| (d, fp))) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some((d, fp)) => {
            call_create_ray_tracing_khr(&d, fp, dev, deferred, cache, count, cis, alloc, out)
        }
    }
}

extern "system" fn vkCreateRayTracingPipelinesNV(
    dev: vk::Device,
    cache: vk::PipelineCache,
    count: u32,
    cis: *const VkRayTracingPipelineCreateInfoNV,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Pipeline,
) -> vk::Result {
    match devs_get(dev.as_raw()).and_then(|d| d.ray_nv_fp.map(|fp| (d, fp))) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some((d, fp)) => call_create_ray_tracing_nv(&d, fp, dev, cache, count, cis, alloc, out),
    }
}

extern "system" fn vkGetPipelineIndirectMemoryRequirementsNV(
    dev: vk::Device,
    ci: *const vk::ComputePipelineCreateInfo<'_>,
    out: *mut c_void,
) {
    match devs_get(dev.as_raw()).and_then(|d| d.indirect_memory_fp.map(|fp| (d, fp))) {
        None => (),
        Some((d, fp)) => call_pipeline_indirect_memory(&d, fp, dev, ci, out),
    }
}

extern "system" fn vkGetPipelineKeyKHR(
    dev: vk::Device,
    ci: *const VkPipelineCreateInfoKHR,
    out: *mut c_void,
) -> vk::Result {
    match devs_get(dev.as_raw()).and_then(|d| d.pipeline_key_fp.map(|fp| (d, fp))) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some((d, fp)) => call_get_pipeline_key(&d, fp, dev, ci, out),
    }
}

extern "system" fn vkCreatePipelineBinariesKHR(
    dev: vk::Device,
    ci: *const VkPipelineBinaryCreateInfoKHR,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut c_void,
) -> vk::Result {
    match devs_get(dev.as_raw()).and_then(|d| d.pipeline_binaries_fp.map(|fp| (d, fp))) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some((d, fp)) => call_create_pipeline_binaries(&d, fp, dev, ci, alloc, out),
    }
}

extern "system" fn vkCmdSetAlphaToCoverageEnableEXT(
    buffer: vk::CommandBuffer,
    enable: vk::Bool32,
) {
    call_set_alpha_coverage(cmdbuf_owner(buffer), buffer, enable)
}

extern "system" fn vkCmdSetAlphaToOneEnableEXT(
    buffer: vk::CommandBuffer,
    enable: vk::Bool32,
) {
    call_set_alpha_one(cmdbuf_owner(buffer), buffer, enable)
}

extern "system" fn vkCmdSetDepthClampEnableEXT(
    buffer: vk::CommandBuffer,
    enable: vk::Bool32,
) {
    call_set_depth_clamp(cmdbuf_owner(buffer), buffer, enable)
}

extern "system" fn vkAllocateCommandBuffers(
    dev: vk::Device,
    info: *const vk::CommandBufferAllocateInfo<'_>,
    out: *mut vk::CommandBuffer,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_allocate_command_buffers(&d, dev, info, out),
    }
}

extern "system" fn vkFreeCommandBuffers(
    dev: vk::Device,
    pool: vk::CommandPool,
    count: u32,
    buffers: *const vk::CommandBuffer,
) {
    match devs_get(dev.as_raw()) {
        Some(d) => call_free_command_buffers(&d, dev, pool, count, buffers),
        None => (),
    }
}

extern "system" fn vkDestroyCommandPool(
    dev: vk::Device,
    pool: vk::CommandPool,
    alloc: *const vk::AllocationCallbacks<'_>,
) {
    match devs_get(dev.as_raw()) {
        Some(d) => call_destroy_command_pool(&d, dev, pool, alloc),
        None => (),
    }
}

extern "system" fn vkCreateSampler(
    dev: vk::Device,
    ci: *const vk::SamplerCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Sampler,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_create_sampler(&d, ci, alloc, out),
    }
}

extern "system" fn vkWriteSamplerDescriptorsEXT(
    dev: vk::Device,
    count: u32,
    cis: *const vk::SamplerCreateInfo<'_>,
    descriptors: *const c_void,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_write_sampler_descriptors(&d, dev, count, cis, descriptors),
    }
}

extern "system" fn vkCreateSwapchainKHR(
    dev: vk::Device,
    ci: *const vk::SwapchainCreateInfoKHR<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_create_swapchain(&d, dev, ci, alloc, out),
    }
}

extern "system" fn vkCreateSharedSwapchainsKHR(
    dev: vk::Device,
    count: u32,
    cis: *const vk::SwapchainCreateInfoKHR<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_create_shared_swapchains(&d, dev, count, cis, alloc, out),
    }
}

extern "system" fn vkDestroySwapchainKHR(
    dev: vk::Device,
    sc: vk::SwapchainKHR,
    alloc: *const vk::AllocationCallbacks<'_>,
) {
    match devs_get(dev.as_raw()) {
        Some(d) => {
            call_forget_timeline(dev.as_raw(), sc);
            call_forget_forced_mode(dev.as_raw(), sc);
            unsafe { (d.swap_fp.destroy_swapchain_khr)(dev, sc, alloc) };
        }
        None => (),
    }
}

extern "system" fn vkCreateXcbSurfaceKHR(
    inst: vk::Instance,
    ci: *const c_void,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::SurfaceKHR,
) -> vk::Result {
    call_create_tagged_surface(FN_CREATE_XCB_SURFACE, TAG_XCB, inst, ci, alloc, out)
}

extern "system" fn vkCreateXlibSurfaceKHR(
    inst: vk::Instance,
    ci: *const c_void,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::SurfaceKHR,
) -> vk::Result {
    call_create_tagged_surface(FN_CREATE_XLIB_SURFACE, TAG_XCB, inst, ci, alloc, out)
}

extern "system" fn vkCreateWaylandSurfaceKHR(
    inst: vk::Instance,
    ci: *const c_void,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::SurfaceKHR,
) -> vk::Result {
    call_create_tagged_surface(FN_CREATE_WAYLAND_SURFACE, TAG_WAYLAND, inst, ci, alloc, out)
}

extern "system" fn vkDestroySurfaceKHR(
    inst: vk::Instance,
    surface: vk::SurfaceKHR,
    alloc: *const vk::AllocationCallbacks<'_>,
) {
    call_destroy_tagged_surface(inst, surface, alloc)
}

extern "system" fn vkGetPhysicalDeviceSurfacePresentModesKHR(
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    count: *mut u32,
    modes: *mut vk::PresentModeKHR,
) -> vk::Result {
    call_surface_present_modes(phys, surface, count, modes)
}

extern "system" fn vkGetPhysicalDeviceSurfaceCapabilitiesKHR(
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    caps: *mut vk::SurfaceCapabilitiesKHR,
) -> vk::Result {
    call_surface_capabilities(phys, surface, caps)
}

extern "system" fn vkGetPhysicalDeviceSurfaceCapabilities2KHR(
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
    caps: *mut VkSurfaceCapabilities2,
) -> vk::Result {
    call_surface_capabilities2(phys, info, caps)
}

extern "system" fn vkQueuePresentKHR(queue: vk::Queue, info: *const vk::PresentInfoKHR<'_>) -> vk::Result {
    call_limited_present(queue_owner(queue), queue, info)
}

fn call_agreed(iface: *mut VkNegotiateLayerInterface, agreed: u32) -> vk::Result {
    unsafe { (*iface).loader_layer_interface_version = agreed };
    unsafe { (*iface).pfn_get_instance_proc_addr = Some(vkGetInstanceProcAddr) };
    unsafe { (*iface).pfn_get_device_proc_addr = Some(vkGetDeviceProcAddr) };
    unsafe { (*iface).pfn_get_physical_device_proc_addr = None };
    vk::Result::SUCCESS
}

fn call_negotiated(iface: *mut VkNegotiateLayerInterface) -> vk::Result {
    let offered = unsafe { (*iface).loader_layer_interface_version };
    match negotiated_version(offered, LAYER_IFACE_VERSION) {
        Some(agreed) => call_agreed(iface, agreed),
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
    }
}

#[no_mangle]
pub extern "system" fn vkNegotiateLoaderLayerInterfaceVersion(p: *mut c_void) -> vk::Result {
    let iface = p as *mut VkNegotiateLayerInterface;
    match unsafe { (*iface).s_type } == LAYER_NEGOTIATE_INTERFACE_STRUCT {
        true => call_negotiated(iface),
        false => vk::Result::ERROR_INITIALIZATION_FAILED,
    }
}
