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
use crate::consts::FN_CREATE_SWAPCHAIN;
use crate::consts::FN_DESTROY_SWAPCHAIN;
use crate::consts::FN_DEVICE_GROUPS;
use crate::consts::FN_DEVICE_GROUPS_KHR;
use crate::consts::FN_DEVICE_QUEUE_2;
use crate::consts::FN_QUEUE_PRESENT;
use crate::consts::FN_SET_ALPHA_COVERAGE;
use crate::consts::FN_SHARED_SWAPCHAINS;
use crate::consts::FN_SURFACE_CAPS_2;
use crate::consts::FN_SURFACE_MODES_2;
use crate::consts::FN_WRITE_SAMPLERS;
use crate::consts::LAYER_DATA_CALLBACK;
use crate::consts::LAYER_DESC;
use crate::consts::LAYER_IFACE_VERSION;
use crate::consts::LAYER_LINK_INFO;
use crate::consts::LAYER_NAME;
use crate::consts::LimitStage;
use crate::consts::NULL_OK;
use crate::consts::UNOWNED_QUEUE_ERROR;
use crate::device::call_allocate_command_buffers;
use crate::device::call_destroy_command_pool;
use crate::device::call_free_command_buffers;
use crate::device::call_real_create_device;
use crate::device::call_register_queue;
use crate::device::cmdbuf_owner;
use crate::device::devs_del;
use crate::device::devs_gdpa;
use crate::device::devs_get;
use crate::device::queue_dev_put;
use crate::device::queue_owner;
use crate::device::VkDevState;
use crate::instance::call_advance_chain;
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
use crate::instance::VkPhysicalDeviceSurfaceInfo2;
use crate::instance::VkSurfaceCapabilities2;
use crate::logging::init_log_level;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::pipeline::call_create_graphics_pipelines;
use crate::pipeline::call_set_alpha_coverage;
use crate::present::call_forget_timeline;
use crate::present::call_present_frame;
use crate::present::maybe_limit_frame;
use crate::sampler::call_create_sampler;
use crate::sampler::call_write_sampler_descriptors;
use crate::swapchain::call_create_shared_swapchains;
use crate::swapchain::call_create_swapchain;
use crate::swapchain::call_surface_capabilities;
use crate::swapchain::call_surface_capabilities2;
use crate::swapchain::call_surface_present_modes;
use crate::swapchain::call_surface_present_modes2;

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
        "vkGetInstanceProcAddr" => Some(vkGetInstanceProcAddr as *mut c_void),
        "vkGetDeviceProcAddr" => Some(vkGetDeviceProcAddr as *mut c_void),
        "vkCreateInstance" => Some(vkCreateInstance as *mut c_void),
        "vkDestroyInstance" => Some(vkDestroyInstance as *mut c_void),
        "vkCreateDevice" => Some(vkCreateDevice as *mut c_void),
        "vkEnumeratePhysicalDevices" => Some(vkEnumeratePhysicalDevices as *mut c_void),
        "vkGetPhysicalDeviceSurfacePresentModesKHR" => Some(vkGetPhysicalDeviceSurfacePresentModesKHR as *mut c_void),
        "vkGetPhysicalDeviceSurfaceCapabilitiesKHR" => Some(vkGetPhysicalDeviceSurfaceCapabilitiesKHR as *mut c_void),
        _ => None,
    }
}

fn device_symbol(name: &str) -> Option<*mut c_void> {
    match name {
        "vkGetDeviceProcAddr" => Some(vkGetDeviceProcAddr as *mut c_void),
        "vkDestroyDevice" => Some(vkDestroyDevice as *mut c_void),
        "vkCreateGraphicsPipelines" => Some(vkCreateGraphicsPipelines as *mut c_void),
        "vkCreateSampler" => Some(vkCreateSampler as *mut c_void),
        "vkAllocateCommandBuffers" => Some(vkAllocateCommandBuffers as *mut c_void),
        "vkFreeCommandBuffers" => Some(vkFreeCommandBuffers as *mut c_void),
        "vkDestroyCommandPool" => Some(vkDestroyCommandPool as *mut c_void),
        "vkGetDeviceQueue" => Some(volt_GetDeviceQueue as *mut c_void),
        FN_DEVICE_QUEUE_2 => Some(volt_GetDeviceQueue2 as *mut c_void),
        FN_CREATE_SWAPCHAIN => Some(vkCreateSwapchainKHR as *mut c_void),
        FN_DESTROY_SWAPCHAIN => Some(vkDestroySwapchainKHR as *mut c_void),
        FN_QUEUE_PRESENT => Some(vkQueuePresentKHR as *mut c_void),
        _ => None,
    }
}

fn instance_extension_hook(name: &str) -> Option<*mut c_void> {
    match name {
        FN_SURFACE_CAPS_2 => Some(vkGetPhysicalDeviceSurfaceCapabilities2KHR as *mut c_void),
        FN_SURFACE_MODES_2 => Some(vkGetPhysicalDeviceSurfacePresentModes2EXT as *mut c_void),
        FN_DEVICE_GROUPS => Some(vkEnumeratePhysicalDeviceGroups as *mut c_void),
        FN_DEVICE_GROUPS_KHR => Some(vkEnumeratePhysicalDeviceGroupsKHR as *mut c_void),
        _ => None,
    }
}

fn instance_fp_present(inst: vk::Instance, name: &str) -> bool {
    match (insts_get(inst.as_raw()), name) {
        (Some(st), FN_SURFACE_CAPS_2) => st.caps2_fp.is_some(),
        (Some(st), FN_SURFACE_MODES_2) => st.modes2_fp.is_some(),
        (Some(st), FN_DEVICE_GROUPS) => st.groups_fp.is_some(),
        (Some(st), FN_DEVICE_GROUPS_KHR) => st.groups_khr_fp.is_some(),
        (_, _) => false,
    }
}

fn instance_hooked_symbol(inst: vk::Instance, name: &str) -> Option<*mut c_void> {
    instance_extension_hook(name).filter(|_| instance_fp_present(inst, name))
}

fn device_extension_hook(name: &str) -> Option<*mut c_void> {
    match name {
        FN_SHARED_SWAPCHAINS => Some(vkCreateSharedSwapchainsKHR as *mut c_void),
        FN_WRITE_SAMPLERS => Some(vkWriteSamplerDescriptorsEXT as *mut c_void),
        FN_SET_ALPHA_COVERAGE => Some(vkCmdSetAlphaToCoverageEnableEXT as *mut c_void),
        _ => None,
    }
}

fn device_fp_present(dev: vk::Device, name: &str) -> bool {
    match (devs_get(dev.as_raw()), name) {
        (Some(d), FN_SHARED_SWAPCHAINS) => d.shared_fp.is_some(),
        (Some(d), FN_WRITE_SAMPLERS) => d.samplers_fp.is_some(),
        (Some(d), FN_SET_ALPHA_COVERAGE) => d.alpha_fp.is_some(),
        (_, _) => false,
    }
}

fn device_hooked_symbol(dev: vk::Device, name: &str) -> Option<*mut c_void> {
    device_extension_hook(name).filter(|_| device_fp_present(dev, name))
}

fn device_gate(dev: vk::Device, name: &str) -> bool {
    match (devs_get(dev.as_raw()), name) {
        (Some(d), FN_CREATE_SWAPCHAIN) => d.swapchain_held,
        (Some(d), FN_DESTROY_SWAPCHAIN) => d.swapchain_held,
        (Some(d), FN_QUEUE_PRESENT) => d.swapchain_held,
        (Some(d), FN_DEVICE_QUEUE_2) => d.queue2_held,
        (_, _) => true,
    }
}

fn device_gated_symbol(dev: vk::Device, name: &str) -> Option<*mut c_void> {
    device_symbol(name).filter(|_| device_gate(dev, name))
}

fn null_ok_ptr(name: &str) -> *mut c_void {
    match name {
        "vkCreateInstance" => vkCreateInstance as *mut c_void,
        "vkEnumerateInstanceExtensionProperties" => volt_EnumerateInstanceExtensionProperties as *mut c_void,
        "vkEnumerateInstanceLayerProperties" => volt_EnumerateInstanceLayerProperties as *mut c_void,
        "vkEnumerateInstanceVersion" => volt_EnumerateInstanceVersion as *mut c_void,
        _ => ptr::null_mut(),
    }
}

fn copy_cstr(dst: &mut [c_char], s: &str) {
    s.bytes().take(dst.len() - 1).enumerate().for_each(|(i, b)| dst[i] = b as c_char);
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

fn resolve_instance_proc(inst: vk::Instance, name: &str) -> vk::PFN_vkVoidFunction {
    match (
        instance_symbol(name),
        device_symbol(name),
        instance_hooked_symbol(inst, name),
    ) {
        (Some(p), _, _) => unsafe { mem::transmute(p) },
        (None, Some(p), _) => unsafe { mem::transmute(p) },
        (None, None, Some(p)) => unsafe { mem::transmute(p) },
        (None, None, None) => forward_instance_proc(inst, name),
    }
}

fn resolve_null_instance_proc(name: &str) -> vk::PFN_vkVoidFunction {
    match null_ok_name(name) {
        true => unsafe { mem::transmute(null_ok_ptr(name)) },
        false => None,
    }
}

fn call_chain_destroy_instance(gipa: vk::PFN_vkGetInstanceProcAddr, inst: vk::Instance, alloc: *const vk::AllocationCallbacks) {
    match call_next_gipa(gipa, inst, "vkDestroyInstance") {
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
    info: *const vk::PresentInfoKHR,
) -> vk::Result {
    match owner {
        Some(d) => call_present_frame(&d, queue, info),
        None => call_unowned_present(),
    }
}

fn call_after_present(
    presented: vk::Result,
    s: &Settings,
    info: *const vk::PresentInfoKHR,
) -> vk::Result {
    maybe_limit_frame(LimitStage::After, s, info);
    presented
}

fn call_limited_present(
    owner: Option<Arc<VkDevState>>,
    queue: vk::Queue,
    info: *const vk::PresentInfoKHR,
) -> vk::Result {
    let s = ensure_settings();
    maybe_limit_frame(LimitStage::Before, s, info);
    call_after_present(call_forward_present(owner, queue, info), s, info)
}

unsafe extern "system" fn volt_EnumerateInstanceExtensionProperties(
    layer: *const c_char,
    count: *mut u32,
    _props: *mut vk::ExtensionProperties,
) -> vk::Result {
    match cstr_to_str(layer) == LAYER_NAME {
        true => {
            *count = 0;
            vk::Result::SUCCESS
        }
        false => vk::Result::ERROR_LAYER_NOT_PRESENT,
    }
}

unsafe extern "system" fn volt_EnumerateInstanceLayerProperties(
    count: *mut u32,
    props: *mut vk::LayerProperties,
) -> vk::Result {
    match props.is_null() {
        true => {
            *count = 1;
            vk::Result::SUCCESS
        }
        false => {
            let mut p = vk::LayerProperties {
                spec_version: vk::make_api_version(0, 1, 0, 0),
                implementation_version: 1,
                ..Default::default()
            };
            copy_cstr(&mut p.layer_name, LAYER_NAME);
            copy_cstr(&mut p.description, LAYER_DESC);
            *count = 1;
            *props = p;
            vk::Result::SUCCESS
        }
    }
}

unsafe extern "system" fn volt_EnumerateInstanceVersion(v: *mut u32) -> vk::Result {
    *v = vk::make_api_version(0, 1, 0, 0);
    vk::Result::SUCCESS
}

unsafe extern "system" fn volt_GetDeviceQueue(dev: vk::Device, qfam: u32, qidx: u32, out: *mut vk::Queue) {
    match devs_get(dev.as_raw()) {
        Some(d) => {
            let q = d.device.get_device_queue(qfam, qidx);
            call_register_queue(&d, dev, q);
            queue_dev_put(q.as_raw(), dev.as_raw());
            *out = q;
        }
        None => log_at(LogLevel::Warn, "GetDeviceQueue on unregistered device"),
    }
}

unsafe extern "system" fn volt_GetDeviceQueue2(dev: vk::Device, info: *const vk::DeviceQueueInfo2, out: *mut vk::Queue) {
    match devs_get(dev.as_raw()) {
        Some(d) => {
            let q = d.device.get_device_queue2(&*info);
            call_register_queue(&d, dev, q);
            queue_dev_put(q.as_raw(), dev.as_raw());
            *out = q;
        }
        None => log_at(LogLevel::Warn, "GetDeviceQueue2 on unregistered device"),
    }
}

unsafe extern "system" fn vkGetInstanceProcAddr(inst: vk::Instance, name: *const c_char) -> vk::PFN_vkVoidFunction {
    let n = cstr_to_str(name);
    match inst == vk::Instance::null() {
        true => resolve_null_instance_proc(n),
        false => resolve_instance_proc(inst, n),
    }
}

unsafe extern "system" fn vkGetDeviceProcAddr(dev: vk::Device, name: *const c_char) -> vk::PFN_vkVoidFunction {
    let n = cstr_to_str(name);
    match (device_gated_symbol(dev, n), device_hooked_symbol(dev, n)) {
        (Some(p), _) => mem::transmute(p),
        (None, Some(p)) => mem::transmute(p),
        (None, None) => forward_device_proc(dev, n),
    }
}

unsafe extern "system" fn vkCreateInstance(
    ci: *const vk::InstanceCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Instance,
) -> vk::Result {
    init_log_level();
    call_real_create_instance(
        call_advance_chain(chain_layer_info(
            (*ci).p_next,
            vk::StructureType::LOADER_INSTANCE_CREATE_INFO,
            LAYER_LINK_INFO,
        )),
        ci,
        alloc,
        out,
    )
}

unsafe extern "system" fn vkDestroyInstance(inst: vk::Instance, alloc: *const vk::AllocationCallbacks) {
    let st = insts_get(inst.as_raw());
    insts_del(inst.as_raw());
    match st {
        Some(s) => call_chain_destroy_instance(s.gipa, inst, alloc),
        None => (),
    }
}

unsafe extern "system" fn vkEnumeratePhysicalDevices(
    inst: vk::Instance,
    count: *mut u32,
    devices: *mut vk::PhysicalDevice,
) -> vk::Result {
    call_filtered_enumerate(inst, count, devices)
}

unsafe extern "system" fn vkEnumeratePhysicalDeviceGroups(
    inst: vk::Instance,
    count: *mut u32,
    groups: *mut vk::PhysicalDeviceGroupProperties,
) -> vk::Result {
    call_filtered_groups(inst, count, groups)
}

unsafe extern "system" fn vkEnumeratePhysicalDeviceGroupsKHR(
    inst: vk::Instance,
    count: *mut u32,
    groups: *mut vk::PhysicalDeviceGroupProperties,
) -> vk::Result {
    call_filtered_groups_khr(inst, count, groups)
}

unsafe extern "system" fn vkCreateDevice(
    phys: vk::PhysicalDevice,
    ci: *const vk::DeviceCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Device,
) -> vk::Result {
    call_real_create_device(
        call_advance_chain(chain_layer_info(
            (*ci).p_next,
            vk::StructureType::LOADER_DEVICE_CREATE_INFO,
            LAYER_LINK_INFO,
        )),
        call_loader_data_fn(chain_layer_info(
            (*ci).p_next,
            vk::StructureType::LOADER_DEVICE_CREATE_INFO,
            LAYER_DATA_CALLBACK,
        )),
        phys,
        ci,
        alloc,
        out,
    )
}

unsafe extern "system" fn vkDestroyDevice(dev: vk::Device, alloc: *const vk::AllocationCallbacks) {
    match devs_del(dev.as_raw()) {
        Some(d) => d.device.destroy_device(alloc.as_ref()),
        None => (),
    }
}

unsafe extern "system" fn vkCreateGraphicsPipelines(
    dev: vk::Device,
    cache: vk::PipelineCache,
    count: u32,
    cis: *const vk::GraphicsPipelineCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Pipeline,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_create_graphics_pipelines(&d, cache, count, cis, alloc, out),
    }
}

unsafe extern "system" fn vkCmdSetAlphaToCoverageEnableEXT(
    buffer: vk::CommandBuffer,
    enable: vk::Bool32,
) {
    call_set_alpha_coverage(cmdbuf_owner(buffer), buffer, enable)
}

unsafe extern "system" fn vkAllocateCommandBuffers(
    dev: vk::Device,
    info: *const vk::CommandBufferAllocateInfo,
    out: *mut vk::CommandBuffer,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_allocate_command_buffers(&d, dev, info, out),
    }
}

unsafe extern "system" fn vkFreeCommandBuffers(
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

unsafe extern "system" fn vkDestroyCommandPool(
    dev: vk::Device,
    pool: vk::CommandPool,
    alloc: *const vk::AllocationCallbacks,
) {
    match devs_get(dev.as_raw()) {
        Some(d) => call_destroy_command_pool(&d, dev, pool, alloc),
        None => (),
    }
}

unsafe extern "system" fn vkCreateSampler(
    dev: vk::Device,
    ci: *const vk::SamplerCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Sampler,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_create_sampler(&d, ci, alloc, out),
    }
}

unsafe extern "system" fn vkWriteSamplerDescriptorsEXT(
    dev: vk::Device,
    count: u32,
    cis: *const vk::SamplerCreateInfo,
    descriptors: *const c_void,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_write_sampler_descriptors(&d, dev, count, cis, descriptors),
    }
}

unsafe extern "system" fn vkCreateSwapchainKHR(
    dev: vk::Device,
    ci: *const vk::SwapchainCreateInfoKHR,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_create_swapchain(&d, dev, ci, alloc, out),
    }
}

unsafe extern "system" fn vkCreateSharedSwapchainsKHR(
    dev: vk::Device,
    count: u32,
    cis: *const vk::SwapchainCreateInfoKHR,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::SwapchainKHR,
) -> vk::Result {
    match devs_get(dev.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(d) => call_create_shared_swapchains(&d, dev, count, cis, alloc, out),
    }
}

unsafe extern "system" fn vkDestroySwapchainKHR(
    dev: vk::Device,
    sc: vk::SwapchainKHR,
    alloc: *const vk::AllocationCallbacks,
) {
    match devs_get(dev.as_raw()) {
        Some(d) => {
            call_forget_timeline(sc);
            (d.swap_fp.destroy_swapchain_khr)(dev, sc, alloc);
        }
        None => (),
    }
}

unsafe extern "system" fn vkGetPhysicalDeviceSurfacePresentModesKHR(
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    count: *mut u32,
    modes: *mut vk::PresentModeKHR,
) -> vk::Result {
    call_surface_present_modes(phys, surface, count, modes)
}

unsafe extern "system" fn vkGetPhysicalDeviceSurfacePresentModes2EXT(
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
    count: *mut u32,
    modes: *mut vk::PresentModeKHR,
) -> vk::Result {
    call_surface_present_modes2(phys, info, count, modes)
}

unsafe extern "system" fn vkGetPhysicalDeviceSurfaceCapabilitiesKHR(
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    caps: *mut vk::SurfaceCapabilitiesKHR,
) -> vk::Result {
    call_surface_capabilities(phys, surface, caps)
}

unsafe extern "system" fn vkGetPhysicalDeviceSurfaceCapabilities2KHR(
    phys: vk::PhysicalDevice,
    info: *const VkPhysicalDeviceSurfaceInfo2,
    caps: *mut VkSurfaceCapabilities2,
) -> vk::Result {
    call_surface_capabilities2(phys, info, caps)
}

unsafe extern "system" fn vkQueuePresentKHR(queue: vk::Queue, info: *const vk::PresentInfoKHR) -> vk::Result {
    call_limited_present(queue_owner(queue), queue, info)
}

#[no_mangle]
pub unsafe extern "system" fn vkNegotiateLoaderLayerInterfaceVersion(p: *mut c_void) -> vk::Result {
    let iface = p as *mut VkNegotiateLayerInterface;
    (*iface).loader_layer_interface_version = LAYER_IFACE_VERSION;
    (*iface).pfn_get_instance_proc_addr = Some(vkGetInstanceProcAddr);
    (*iface).pfn_get_device_proc_addr = Some(vkGetDeviceProcAddr);
    (*iface).pfn_get_physical_device_proc_addr = None;
    vk::Result::SUCCESS
}
