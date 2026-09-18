mod dl;
mod wayland;
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
const EXIT_UNSUPPORTED: i32 = 2;
const EXT_PORTABILITY_SUBSET: &str = "VK_KHR_portability_subset";
const EXT_PORTABILITY_ENUMERATION: &str = "VK_KHR_portability_enumeration";
const EXT_PROPERTIES_2: &str = "VK_KHR_get_physical_device_properties2";
const NO_ARRAY_LAYERS: u32 = 0;
const ZERO_EXTENT: u32 = 0;
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

const BACKENDS: [Backend; 2] = [xcb::BACKEND, wayland::BACKEND];

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

fn wanted_extensions(has_surface: bool) -> Vec<&'static str> {
    let surface: Vec<&'static str> = match has_surface {
        true => vec![EXT_SURFACE],
        false => Vec::new(),
    };
    let backends: Vec<&'static str> = match has_surface {
        true => BACKENDS.iter().map(|backend| backend.extension).collect(),
        false => Vec::new(),
    };
    surface
        .into_iter()
        .chain(std::iter::once(EXT_PROPERTIES_2))
        .chain(std::iter::once(EXT_PORTABILITY_ENUMERATION))
        .chain(backends)
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

fn enabled_name_list(entry: &ash::Entry) -> Vec<String> {
    let available = available_names(entry);
    let has_surface = available.iter().any(|one| one.as_str() == EXT_SURFACE);
    wanted_extensions(has_surface)
        .into_iter()
        .filter(|name| available.iter().any(|one| one.as_str() == *name))
        .map(str::to_owned)
        .collect()
}

fn enabled_names(enabled: &[String]) -> Vec<CString> {
    enabled
        .iter()
        .filter_map(|name| CString::new(name.as_str()).ok())
        .collect()
}

fn name_pointers(names: &[CString]) -> Vec<*const c_char> {
    names.iter().map(|name| name.as_ptr()).collect()
}

fn family_draws(one: &vk::QueueFamilyProperties) -> bool {
    one.queue_flags.contains(vk::QueueFlags::GRAPHICS)
        || one.queue_flags.contains(vk::QueueFlags::COMPUTE)
}

fn drawing_family(props: &[vk::QueueFamilyProperties]) -> Option<u32> {
    props.iter().position(family_draws).map(|at| at as u32)
}

fn asked_extent(caps: &vk::SurfaceCapabilitiesKHR) -> (u32, u32) {
    match caps.current_extent.width {
        u32::MAX => (WINDOW_EDGE as u32, WINDOW_EDGE as u32),
        _ => (caps.current_extent.width, caps.current_extent.height),
    }
}

fn swapchain_extent(caps: &vk::SurfaceCapabilitiesKHR) -> vk::Extent2D {
    let (width, height) = asked_extent(caps);
    vk::Extent2D {
        width: width.clamp(caps.min_image_extent.width, caps.max_image_extent.width),
        height: height.clamp(caps.min_image_extent.height, caps.max_image_extent.height),
    }
}

fn surface_usable(caps: &vk::SurfaceCapabilitiesKHR) -> bool {
    caps.current_extent.width != ZERO_EXTENT
        && caps.current_extent.height != ZERO_EXTENT
        && caps.max_image_array_layers > NO_ARRAY_LAYERS
        && caps
            .supported_usage_flags
            .contains(vk::ImageUsageFlags::COLOR_ATTACHMENT)
        && caps.supported_composite_alpha.as_raw() != 0
}

fn supported_alpha(mask: vk::CompositeAlphaFlagsKHR) -> vk::CompositeAlphaFlagsKHR {
    vk::CompositeAlphaFlagsKHR::from_raw(mask.as_raw() & mask.as_raw().wrapping_neg())
}

fn supported_transform(caps: &vk::SurfaceCapabilitiesKHR) -> vk::SurfaceTransformFlagsKHR {
    match caps.supported_transforms.contains(caps.current_transform) {
        true => caps.current_transform,
        false => vk::SurfaceTransformFlagsKHR::from_raw(
            caps.supported_transforms.as_raw() & caps.supported_transforms.as_raw().wrapping_neg(),
        ),
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
        pre_transform: supported_transform(caps),
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

fn call_create_instance(entry: &ash::Entry, enabled: &[String]) -> Option<ash::Instance> {
    let names = enabled_names(enabled);
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

enum DeviceOutcome {
    Ready(vk::PhysicalDevice),
    Unsupported,
    Missing,
}

fn device_extension_names(instance: &ash::Instance, phys: vk::PhysicalDevice) -> Vec<String> {
    unsafe { instance.enumerate_device_extension_properties(phys) }
        .unwrap_or_default()
        .iter()
        .filter_map(available_name)
        .collect()
}

fn portability_listed(names: &[String]) -> bool {
    names.iter().any(|one| one == EXT_PORTABILITY_SUBSET)
}

fn outcome_for(
    phys: vk::PhysicalDevice,
    listed: bool,
    support: bool,
) -> DeviceOutcome {
    match (listed, support) {
        (true, false) => DeviceOutcome::Unsupported,
        (_, _) => DeviceOutcome::Ready(phys),
    }
}

fn call_first_physical(
    instance: &ash::Instance,
    support: bool,
) -> DeviceOutcome {
    match unsafe { instance.enumerate_physical_devices() }
        .ok()
        .and_then(|all| all.first().copied())
    {
        None => DeviceOutcome::Missing,
        Some(phys) => outcome_for(
            phys,
            portability_listed(&device_extension_names(instance, phys)),
            support,
        ),
    }
}

fn portability_support(enabled: &[String]) -> bool {
    enabled.iter().any(|one| one.as_str() == EXT_PROPERTIES_2)
}

fn call_surface_supported(
    loader: &ash::khr::surface::Instance,
    phys: vk::PhysicalDevice,
    family: u32,
    surface: vk::SurfaceKHR,
) -> bool {
    unsafe { loader.get_physical_device_surface_support(phys, family, surface) }.unwrap_or(false)
}

fn call_format_supported(
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    format: vk::Format,
) -> bool {
    unsafe {
        instance.get_physical_device_image_format_properties(
            phys,
            format,
            vk::ImageType::TYPE_2D,
            vk::ImageTiling::OPTIMAL,
            vk::ImageUsageFlags::COLOR_ATTACHMENT,
            vk::ImageCreateFlags::empty(),
        )
    }
    .is_ok()
}

fn call_drawing_family(instance: &ash::Instance, phys: vk::PhysicalDevice) -> Option<u32> {
    drawing_family(&unsafe { instance.get_physical_device_queue_family_properties(phys) })
}

fn call_family_count(instance: &ash::Instance, phys: vk::PhysicalDevice) -> u32 {
    unsafe { instance.get_physical_device_queue_family_properties(phys) }.len() as u32
}

fn call_surface_family(
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    loader: &ash::khr::surface::Instance,
    surface: vk::SurfaceKHR,
) -> bool {
    (0..call_family_count(instance, phys))
        .any(|family| call_surface_supported(loader, phys, family, surface))
}

fn device_extensions_to_enable(
    instance_enabled: &[String],
    listed: &[String],
    support: bool,
) -> Vec<&'static str> {
    let has_surface = instance_enabled.iter().any(|one| one.as_str() == EXT_SURFACE);
    let mut out: Vec<&'static str> = Vec::new();
    match has_surface && listed.iter().any(|one| one.as_str() == EXT_SWAPCHAIN) {
        true => out.push(EXT_SWAPCHAIN),
        false => (),
    }
    match support && listed.iter().any(|one| one.as_str() == EXT_PORTABILITY_SUBSET) {
        true => out.push(EXT_PORTABILITY_SUBSET),
        false => (),
    }
    out
}

fn call_create_device(
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    family: u32,
    instance_enabled: &[String],
    support: bool,
) -> Option<(ash::Device, bool)> {
    let listed = device_extension_names(instance, phys);
    let wanted = device_extensions_to_enable(instance_enabled, &listed, support);
    let names: Vec<CString> = wanted
        .iter()
        .filter_map(|name| CString::new(*name).ok())
        .collect();
    let pointers: Vec<*const c_char> = names.iter().map(|name| name.as_ptr()).collect();
    let priorities = [QUEUE_PRIORITY];
    let queue = vk::DeviceQueueCreateInfo {
        queue_family_index: family,
        queue_count: QUEUE_COUNT,
        p_queue_priorities: priorities.as_ptr(),
        ..Default::default()
    };
    let info = vk::DeviceCreateInfo {
        queue_create_info_count: QUEUE_COUNT,
        p_queue_create_infos: &queue,
        enabled_extension_count: pointers.len() as u32,
        pp_enabled_extension_names: pointers.as_ptr(),
        ..Default::default()
    };
    unsafe { instance.create_device(phys, &info, None) }
        .ok()
        .map(|device| (device, wanted.contains(&EXT_SWAPCHAIN)))
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
    match call_surface_family(instance, phys, surfaces, surface) {
        true => (),
        false => return None,
    }
    let caps = call_surface_caps(surfaces, phys, surface)?;
    match surface_usable(&caps) {
        true => (),
        false => return None,
    }
    let format = call_first_format(surfaces, phys, surface)?;
    match call_format_supported(instance, phys, format.format) {
        true => (),
        false => return None,
    }
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
    instance_enabled: &[String],
    backend: &Backend,
) -> Option<()> {
    match instance_enabled.iter().any(|name| name.as_str() == backend.extension) {
        false => None,
        true => {
            let handles = (backend.open)()?;
            let done = call_on_surface(entry, instance, phys, device, backend, &handles);
            (backend.close)(&handles);
            done
        }
    }
}

fn call_every_backend(
    entry: &ash::Entry,
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    device: &ash::Device,
    instance_enabled: &[String],
) {
    BACKENDS.iter().for_each(|backend| {
        let _ = call_on_backend(entry, instance, phys, device, instance_enabled, backend);
    });
}

fn call_on_device(
    entry: &ash::Entry,
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    device: &ash::Device,
    instance_enabled: &[String],
    swapchain: bool,
) -> Option<()> {
    call_exercise_sampler(device)?;
    match swapchain {
        true => call_every_backend(entry, instance, phys, device, instance_enabled),
        false => (),
    }
    Some(())
}

fn call_with_device(
    entry: &ash::Entry,
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    instance_enabled: &[String],
    support: bool,
) -> Option<()> {
    let family = call_drawing_family(instance, phys)?;
    let (device, swapchain) =
        call_create_device(instance, phys, family, instance_enabled, support)?;
    let done = call_on_device(entry, instance, phys, &device, instance_enabled, swapchain);
    unsafe { device.destroy_device(None) };
    done
}

fn exit_of(done: Option<()>) -> i32 {
    match done {
        Some(()) => EXIT_OK,
        None => EXIT_FAIL,
    }
}

fn call_on_instance(
    entry: &ash::Entry,
    instance: &ash::Instance,
    instance_enabled: &[String],
    support: bool,
) -> i32 {
    match call_first_physical(instance, support) {
        DeviceOutcome::Missing => EXIT_FAIL,
        DeviceOutcome::Unsupported => EXIT_UNSUPPORTED,
        DeviceOutcome::Ready(phys) => exit_of(call_with_device(
            entry,
            instance,
            phys,
            instance_enabled,
            support,
        )),
    }
}

fn call_with_instance(entry: &ash::Entry) -> i32 {
    let enabled = enabled_name_list(entry);
    let support = portability_support(&enabled);
    match call_create_instance(entry, &enabled) {
        None => EXIT_FAIL,
        Some(instance) => {
            let code = call_on_instance(entry, &instance, &enabled, support);
            unsafe { instance.destroy_instance(None) };
            code
        }
    }
}

fn call_status() -> i32 {
    match call_entry() {
        None => EXIT_FAIL,
        Some(entry) => call_with_instance(&entry),
    }
}

fn main() {
    exit(call_status());
}
