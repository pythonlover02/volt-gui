use std::ffi::c_char;
use std::ffi::c_void;
use std::ffi::CStr;
use std::mem;
use std::ptr;

use ash::vk;
use ash::vk::Handle;

use crate::consts::LAYER_DESC;
use crate::consts::LAYER_IFACE_VERSION;
use crate::consts::LAYER_NAME;
use crate::consts::NULL_OK;
use crate::device::call_real_create_device;
use crate::device::devs_any;
use crate::device::devs_del;
use crate::device::devs_gdpa;
use crate::device::devs_get;
use crate::device::inherit_device_dispatch;
use crate::device::queue_dev_put;
use crate::device::queue_owner;
use crate::instance::call_advance_chain;
use crate::instance::call_next_gdpa;
use crate::instance::call_next_gipa;
use crate::instance::chain_link_info;
use crate::instance::call_real_create_instance;
use crate::instance::insts_del;
use crate::instance::insts_get;
use crate::logging::init_log_level;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::pipeline::call_create_graphics_pipelines;
use crate::present::maybe_limit_frame;
use crate::sampler::call_create_sampler;
use crate::swapchain::call_create_swapchain;
use crate::watch::maybe_reload;
use crate::watch::maybe_shutdown_watch;

#[repr(C)]
struct VkNegotiateLayerInterface {
    s_type: i32,
    p_next: *mut c_void,
    loader_layer_interface_version: u32,
    pfn_get_instance_proc_addr: Option<vk::PFN_vkGetInstanceProcAddr>,
    pfn_get_device_proc_addr: Option<vk::PFN_vkGetDeviceProcAddr>,
    pfn_get_physical_device_proc_addr: Option<vk::PFN_vkVoidFunction>,
}

pub(crate) fn cstr_to_str<'a>(p: *const c_char) -> &'a str {
    match p.is_null() {
        true => "",
        false => unsafe { CStr::from_ptr(p).to_str().unwrap_or("") },
    }
}

fn null_ok_name(name: &str) -> bool {
    NULL_OK.contains(&name)
}

fn vk_hooked_symbol(name: &str) -> Option<*mut c_void> {
    match name {
        "vkGetInstanceProcAddr" => Some(vkGetInstanceProcAddr as *mut c_void),
        "vkGetDeviceProcAddr" => Some(vkGetDeviceProcAddr as *mut c_void),
        "vkCreateInstance" => Some(vkCreateInstance as *mut c_void),
        "vkDestroyInstance" => Some(vkDestroyInstance as *mut c_void),
        "vkCreateDevice" => Some(vkCreateDevice as *mut c_void),
        "vkDestroyDevice" => Some(vkDestroyDevice as *mut c_void),
        "vkCreateGraphicsPipelines" => Some(vkCreateGraphicsPipelines as *mut c_void),
        "vkCreateSampler" => Some(vkCreateSampler as *mut c_void),
        "vkCreateSwapchainKHR" => Some(vkCreateSwapchainKHR as *mut c_void),
        "vkQueuePresentKHR" => Some(vkQueuePresentKHR as *mut c_void),
        "vkGetDeviceQueue" => Some(volt_GetDeviceQueue as *mut c_void),
        "vkGetDeviceQueue2" => Some(volt_GetDeviceQueue2 as *mut c_void),
        _ => None,
    }
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

fn resolve_instance_proc(inst: vk::Instance, name: &str) -> vk::PFN_vkVoidFunction {
    match (vk_hooked_symbol(name), insts_get(inst.as_raw())) {
        (Some(p), _) => unsafe { mem::transmute(p) },
        (None, Some(st)) => call_next_gipa(st.gipa, inst, name),
        (None, None) => None,
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

fn call_forward_present(queue: vk::Queue, info: *const vk::PresentInfoKHR) -> vk::Result {
    match queue_owner(queue) {
        Some(d) => unsafe { (d.swap_fp.queue_present_khr)(queue, info) },
        None => call_fallback_present(queue, info),
    }
}

fn call_fallback_present(queue: vk::Queue, info: *const vk::PresentInfoKHR) -> vk::Result {
    match devs_any() {
        Some(d) => {
            log_at(LogLevel::Warn, "present on untracked queue, forwarding directly");
            unsafe { (d.swap_fp.queue_present_khr)(queue, info) }
        }
        None => {
            log_at(LogLevel::Error, "present with no registered device, dropping frame");
            vk::Result::SUCCESS
        }
    }
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
            inherit_device_dispatch(dev, q);
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
            inherit_device_dispatch(dev, q);
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
    match vk_hooked_symbol(n) {
        Some(p) => mem::transmute(p),
        None => forward_device_proc(dev, n),
    }
}

unsafe extern "system" fn vkCreateInstance(
    ci: *const vk::InstanceCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Instance,
) -> vk::Result {
    init_log_level();
    let link = call_advance_chain(chain_link_info((*ci).p_next, vk::StructureType::LOADER_INSTANCE_CREATE_INFO));
    call_real_create_instance(link, ci, alloc, out)
}

unsafe extern "system" fn vkDestroyInstance(inst: vk::Instance, alloc: *const vk::AllocationCallbacks) {
    let st = insts_get(inst.as_raw());
    let last = insts_del(inst.as_raw());
    maybe_shutdown_watch(last);
    match st {
        Some(s) => call_chain_destroy_instance(s.gipa, inst, alloc),
        None => (),
    }
}

unsafe extern "system" fn vkCreateDevice(
    phys: vk::PhysicalDevice,
    ci: *const vk::DeviceCreateInfo,
    alloc: *const vk::AllocationCallbacks,
    out: *mut vk::Device,
) -> vk::Result {
    let link = call_advance_chain(chain_link_info((*ci).p_next, vk::StructureType::LOADER_DEVICE_CREATE_INFO));
    call_real_create_device(link, phys, ci, alloc, out)
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

unsafe extern "system" fn vkQueuePresentKHR(queue: vk::Queue, info: *const vk::PresentInfoKHR) -> vk::Result {
    maybe_reload();
    maybe_limit_frame();
    call_forward_present(queue, info)
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
