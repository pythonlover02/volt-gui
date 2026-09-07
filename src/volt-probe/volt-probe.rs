mod dl;
mod xcb;

use std::ffi::c_char;
use std::ffi::c_void;
use std::ffi::CStr;
use std::ffi::CString;
use std::process::exit;

use ash::vk;

const API_MAJOR: u32 = 1;
const API_MINOR: u32 = 0;
const API_PATCH: u32 = 0;
const API_VARIANT: u32 = 0;
const EXIT_OK: i32 = 0;
const EXIT_FAIL: i32 = 1;
const IMAGE_LAYERS: u32 = 1;
const QUEUE_COUNT: u32 = 1;
const QUEUE_PRIORITY: f32 = 1.0;

const EXT_SURFACE: &str = "VK_KHR_surface";
const EXT_SWAPCHAIN: &str = "VK_KHR_swapchain";
const FN_CREATE_SWAPCHAIN: &str = "vkCreateSwapchainKHR";
const FN_DESTROY_SWAPCHAIN: &str = "vkDestroySwapchainKHR";

pub(crate) const WINDOW_EDGE: u16 = 1;

pub(crate) struct Handles {
    pub(crate) display: *mut c_void,
    pub(crate) window: u64,
}

pub(crate) struct Backend {
    pub(crate) extension: &'static str,
    pub(crate) open: fn() -> Option<Handles>,
    pub(crate) create_surface:
        fn(&ash::Entry, &ash::Instance, &Handles) -> Option<vk::SurfaceKHR>,
    pub(crate) close: fn(&Handles),
}

const BACKENDS: [Backend; 1] = [xcb::BACKEND];

type PfnCreateSwapchain = unsafe extern "system" fn(
    vk::Device,
    *const vk::SwapchainCreateInfoKHR<'_>,
    *const vk::AllocationCallbacks<'_>,
    *mut vk::SwapchainKHR,
) -> vk::Result;

type PfnDestroySwapchain = unsafe extern "system" fn(
    vk::Device,
    vk::SwapchainKHR,
    *const vk::AllocationCallbacks<'_>,
);

fn wanted_extensions() -> Vec<&'static str> {
    std::iter::once(EXT_SURFACE)
        .chain(BACKENDS.iter().map(|backend| backend.extension))
        .collect()
}

fn available_name(one: &vk::ExtensionProperties) -> Option<String> {
    unsafe { CStr::from_ptr(one.extension_name.as_ptr()) }
        .to_str()
        .ok()
        .map(str::to_owned)
}

fn available_names(entry: &ash::Entry) -> Vec<String> {
    unsafe { entry.enumerate_instance_extension_properties(None) }
        .unwrap_or_default()
        .iter()
        .filter_map(available_name)
        .collect()
}

fn enabled_names(entry: &ash::Entry) -> Vec<CString> {
    let available = available_names(entry);
    wanted_extensions()
        .into_iter()
        .filter(|name| available.iter().any(|one| one.as_str() == *name))
        .filter_map(|name| CString::new(name).ok())
        .collect()
}

fn name_pointers(names: &[CString]) -> Vec<*const c_char> {
    names.iter().map(|name| name.as_ptr()).collect()
}

fn graphics_family(props: &[vk::QueueFamilyProperties]) -> Option<u32> {
    props
        .iter()
        .position(|one| one.queue_flags.contains(vk::QueueFlags::GRAPHICS))
        .map(|at| at as u32)
}

fn swapchain_extent(caps: &vk::SurfaceCapabilitiesKHR) -> vk::Extent2D {
    match caps.current_extent.width {
        u32::MAX => vk::Extent2D {
            width: WINDOW_EDGE as u32,
            height: WINDOW_EDGE as u32,
        },
        _ => caps.current_extent,
    }
}

fn supported_alpha(mask: vk::CompositeAlphaFlagsKHR) -> vk::CompositeAlphaFlagsKHR {
    match mask.contains(vk::CompositeAlphaFlagsKHR::OPAQUE) {
        true => vk::CompositeAlphaFlagsKHR::OPAQUE,
        false => vk::CompositeAlphaFlagsKHR::INHERIT,
    }
}

fn swapchain_info(
    surface: vk::SurfaceKHR,
    format: vk::SurfaceFormatKHR,
    caps: &vk::SurfaceCapabilitiesKHR,
) -> vk::SwapchainCreateInfoKHR<'static> {
    vk::SwapchainCreateInfoKHR {
        surface,
        min_image_count: caps.min_image_count,
        image_format: format.format,
        image_color_space: format.color_space,
        image_extent: swapchain_extent(caps),
        image_array_layers: IMAGE_LAYERS,
        image_usage: vk::ImageUsageFlags::COLOR_ATTACHMENT,
        image_sharing_mode: vk::SharingMode::EXCLUSIVE,
        pre_transform: caps.current_transform,
        composite_alpha: supported_alpha(caps.supported_composite_alpha),
        present_mode: vk::PresentModeKHR::FIFO,
        clipped: vk::TRUE,
        ..Default::default()
    }
}

fn sampler_info() -> vk::SamplerCreateInfo<'static> {
    vk::SamplerCreateInfo {
        mag_filter: vk::Filter::LINEAR,
        min_filter: vk::Filter::LINEAR,
        mipmap_mode: vk::SamplerMipmapMode::LINEAR,
        ..Default::default()
    }
}

fn call_entry() -> Option<ash::Entry> {
    unsafe { ash::Entry::load() }.ok()
}

fn call_create_instance(entry: &ash::Entry) -> Option<ash::Instance> {
    let names = enabled_names(entry);
    let pointers = name_pointers(&names);
    let application = vk::ApplicationInfo {
        api_version: vk::make_api_version(API_VARIANT, API_MAJOR, API_MINOR, API_PATCH),
        ..Default::default()
    };
    let info = vk::InstanceCreateInfo {
        p_application_info: &application,
        enabled_extension_count: pointers.len() as u32,
        pp_enabled_extension_names: pointers.as_ptr(),
        ..Default::default()
    };
    unsafe { entry.create_instance(&info, None) }.ok()
}

fn call_first_physical(instance: &ash::Instance) -> Option<vk::PhysicalDevice> {
    unsafe { instance.enumerate_physical_devices() }
        .ok()
        .and_then(|all| all.first().copied())
}

fn call_graphics_family(instance: &ash::Instance, phys: vk::PhysicalDevice) -> Option<u32> {
    graphics_family(&unsafe { instance.get_physical_device_queue_family_properties(phys) })
}

fn call_create_device(
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    family: u32,
) -> Option<ash::Device> {
    let priorities = [QUEUE_PRIORITY];
    let queue = vk::DeviceQueueCreateInfo {
        queue_family_index: family,
        queue_count: QUEUE_COUNT,
        p_queue_priorities: priorities.as_ptr(),
        ..Default::default()
    };
    let name = CString::new(EXT_SWAPCHAIN).ok()?;
    let pointers = [name.as_ptr()];
    let info = vk::DeviceCreateInfo {
        queue_create_info_count: QUEUE_COUNT,
        p_queue_create_infos: &queue,
        enabled_extension_count: pointers.len() as u32,
        pp_enabled_extension_names: pointers.as_ptr(),
        ..Default::default()
    };
    unsafe { instance.create_device(phys, &info, None) }.ok()
}

fn call_first_format(
    loader: &ash::khr::surface::Instance,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
) -> Option<vk::SurfaceFormatKHR> {
    unsafe { loader.get_physical_device_surface_formats(phys, surface) }
        .ok()
        .and_then(|all| all.first().copied())
}

fn call_surface_caps(
    loader: &ash::khr::surface::Instance,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
) -> Option<vk::SurfaceCapabilitiesKHR> {
    unsafe { loader.get_physical_device_surface_capabilities(phys, surface) }.ok()
}

fn call_device_fn<T>(instance: &ash::Instance, device: &ash::Device, name: &str) -> Option<T> {
    let cname = CString::new(name).ok()?;
    unsafe { (instance.fp_v1_0().get_device_proc_addr)(device.handle(), cname.as_ptr()) }
        .map(|found| unsafe { std::mem::transmute_copy(&found) })
}

fn call_swapchain_result(
    result: vk::Result,
    swapchain: vk::SwapchainKHR,
) -> Option<vk::SwapchainKHR> {
    match result {
        vk::Result::SUCCESS => Some(swapchain),
        _ => None,
    }
}

fn call_create_swapchain(
    fp: PfnCreateSwapchain,
    device: &ash::Device,
    surface: vk::SurfaceKHR,
    format: vk::SurfaceFormatKHR,
    caps: &vk::SurfaceCapabilitiesKHR,
) -> Option<vk::SwapchainKHR> {
    let info = swapchain_info(surface, format, caps);
    let mut swapchain = vk::SwapchainKHR::null();
    call_swapchain_result(
        unsafe { fp(device.handle(), &info, std::ptr::null(), &mut swapchain) },
        swapchain,
    )
}

fn call_create_sampler(device: &ash::Device) -> Option<vk::Sampler> {
    unsafe { device.create_sampler(&sampler_info(), None) }.ok()
}

fn call_exercise_sampler(device: &ash::Device) -> Option<()> {
    let sampler = call_create_sampler(device)?;
    unsafe { device.destroy_sampler(sampler, None) };
    Some(())
}

fn call_on_swapchain(
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    device: &ash::Device,
    surfaces: &ash::khr::surface::Instance,
    surface: vk::SurfaceKHR,
) -> Option<()> {
    let caps = call_surface_caps(surfaces, phys, surface)?;
    let format = call_first_format(surfaces, phys, surface)?;
    let create: PfnCreateSwapchain = call_device_fn(instance, device, FN_CREATE_SWAPCHAIN)?;
    let destroy: PfnDestroySwapchain = call_device_fn(instance, device, FN_DESTROY_SWAPCHAIN)?;
    let swapchain = call_create_swapchain(create, device, surface, format, &caps)?;
    unsafe { destroy(device.handle(), swapchain, std::ptr::null()) };
    Some(())
}

fn call_on_surface(
    entry: &ash::Entry,
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    device: &ash::Device,
    backend: &Backend,
    handles: &Handles,
) -> Option<()> {
    let surfaces = ash::khr::surface::Instance::new(entry, instance);
    let surface = (backend.create_surface)(entry, instance, handles)?;
    let done = call_on_swapchain(instance, phys, device, &surfaces, surface);
    unsafe { surfaces.destroy_surface(surface, None) };
    done
}

fn call_on_backend(
    entry: &ash::Entry,
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    device: &ash::Device,
    backend: &Backend,
) -> Option<()> {
    let handles = (backend.open)()?;
    let done = call_on_surface(entry, instance, phys, device, backend, &handles);
    (backend.close)(&handles);
    done
}

fn call_every_backend(
    entry: &ash::Entry,
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    device: &ash::Device,
) {
    BACKENDS.iter().for_each(|backend| {
        let _ = call_on_backend(entry, instance, phys, device, backend);
    });
}

fn call_on_device(
    entry: &ash::Entry,
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    device: &ash::Device,
) -> Option<()> {
    call_exercise_sampler(device)?;
    call_every_backend(entry, instance, phys, device);
    Some(())
}

fn call_with_device(
    entry: &ash::Entry,
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
) -> Option<()> {
    let device = call_create_device(instance, phys, call_graphics_family(instance, phys)?)?;
    let done = call_on_device(entry, instance, phys, &device);
    unsafe { device.destroy_device(None) };
    done
}

fn call_on_instance(entry: &ash::Entry, instance: &ash::Instance) -> Option<()> {
    call_with_device(entry, instance, call_first_physical(instance)?)
}

fn call_with_instance(entry: &ash::Entry) -> Option<()> {
    let instance = call_create_instance(entry)?;
    let done = call_on_instance(entry, &instance);
    unsafe { instance.destroy_instance(None) };
    done
}

fn call_probe() -> Option<()> {
    call_with_instance(&call_entry()?)
}

fn call_status() -> i32 {
    match call_probe() {
        Some(()) => EXIT_OK,
        None => EXIT_FAIL,
    }
}

fn main() {
    exit(call_status());
}
