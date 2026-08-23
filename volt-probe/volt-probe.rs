use std::ffi::c_char;
use std::ffi::c_int;
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
const WINDOW_EDGE: u16 = 1;
const WINDOW_ORIGIN: i16 = 0;
const WINDOW_BORDER: u16 = 0;
const WINDOW_INPUT_OUTPUT: u16 = 1;
const COPY_FROM_PARENT: u8 = 0;
const NO_VALUES: u32 = 0;
const NO_FLAGS: u32 = 0;
const NO_ERROR: c_int = 0;
const IMAGE_LAYERS: u32 = 1;
const QUEUE_COUNT: u32 = 1;
const QUEUE_PRIORITY: f32 = 1.0;
const SURFACE_TYPE: i32 = 1000005000;

const EXT_SURFACE: &str = "VK_KHR_surface";
const EXT_XCB_SURFACE: &str = "VK_KHR_xcb_surface";
const EXT_SWAPCHAIN: &str = "VK_KHR_swapchain";
const FN_CREATE_SURFACE: &str = "vkCreateXcbSurfaceKHR";

const WANTED_EXTENSIONS: [&str; 2] = [EXT_SURFACE, EXT_XCB_SURFACE];

#[repr(C)]
pub struct XcbConnection {
    _opaque: [u8; 0],
}

#[repr(C)]
pub struct XcbSetup {
    _opaque: [u8; 0],
}

#[repr(C)]
pub struct XcbScreen {
    pub root: u32,
    pub default_colormap: u32,
    pub white_pixel: u32,
    pub black_pixel: u32,
    pub current_input_masks: u32,
    pub width_in_pixels: u16,
    pub height_in_pixels: u16,
    pub width_in_millimeters: u16,
    pub height_in_millimeters: u16,
    pub min_installed_maps: u16,
    pub max_installed_maps: u16,
    pub root_visual: u32,
    pub backing_stores: u8,
    pub save_unders: u8,
    pub root_depth: u8,
    pub allowed_depths_len: u8,
}

#[repr(C)]
pub struct XcbScreenIterator {
    pub data: *mut XcbScreen,
    pub rem: c_int,
    pub index: c_int,
}

#[repr(C)]
pub struct VkXcbSurfaceCreateInfo {
    pub s_type: vk::StructureType,
    pub p_next: *const c_void,
    pub flags: u32,
    pub connection: *mut XcbConnection,
    pub window: u32,
}

pub type PfnCreateXcbSurface = unsafe extern "system" fn(
    vk::Instance,
    *const VkXcbSurfaceCreateInfo,
    *const vk::AllocationCallbacks,
    *mut vk::SurfaceKHR,
) -> vk::Result;

pub struct Window {
    pub connection: *mut XcbConnection,
    pub handle: u32,
}

#[link(name = "xcb")]
extern "C" {
    fn xcb_connect(name: *const c_char, screen: *mut c_int) -> *mut XcbConnection;
    fn xcb_disconnect(connection: *mut XcbConnection);
    fn xcb_connection_has_error(connection: *mut XcbConnection) -> c_int;
    fn xcb_get_setup(connection: *mut XcbConnection) -> *const XcbSetup;
    fn xcb_setup_roots_iterator(setup: *const XcbSetup) -> XcbScreenIterator;
    fn xcb_generate_id(connection: *mut XcbConnection) -> u32;
    fn xcb_create_window(
        connection: *mut XcbConnection,
        depth: u8,
        window: u32,
        parent: u32,
        x: i16,
        y: i16,
        width: u16,
        height: u16,
        border: u16,
        class: u16,
        visual: u32,
        mask: u32,
        values: *const u32,
    ) -> u32;
    fn xcb_flush(connection: *mut XcbConnection) -> c_int;
}

fn available_name(one: &vk::ExtensionProperties) -> Option<String> {
    unsafe { CStr::from_ptr(one.extension_name.as_ptr()) }
        .to_str()
        .ok()
        .map(str::to_owned)
}

fn available_names(entry: &ash::Entry) -> Vec<String> {
    entry
        .enumerate_instance_extension_properties(None)
        .unwrap_or_default()
        .iter()
        .filter_map(available_name)
        .collect()
}

fn enabled_names(entry: &ash::Entry) -> Vec<CString> {
    let available = available_names(entry);
    WANTED_EXTENSIONS
        .iter()
        .filter(|name| available.iter().any(|one| one == *name))
        .filter_map(|name| CString::new(*name).ok())
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
) -> vk::SwapchainCreateInfoKHR {
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

fn sampler_info() -> vk::SamplerCreateInfo {
    vk::SamplerCreateInfo {
        mag_filter: vk::Filter::LINEAR,
        min_filter: vk::Filter::LINEAR,
        mipmap_mode: vk::SamplerMipmapMode::LINEAR,
        ..Default::default()
    }
}

fn surface_info(window: &Window) -> VkXcbSurfaceCreateInfo {
    VkXcbSurfaceCreateInfo {
        s_type: vk::StructureType::from_raw(SURFACE_TYPE),
        p_next: std::ptr::null(),
        flags: NO_FLAGS,
        connection: window.connection,
        window: window.handle,
    }
}

fn call_connected(connection: *mut XcbConnection) -> Option<*mut XcbConnection> {
    match unsafe { xcb_connection_has_error(connection) } {
        NO_ERROR => Some(connection),
        _ => None,
    }
}

fn call_open_connection() -> Option<*mut XcbConnection> {
    call_connected(unsafe { xcb_connect(std::ptr::null(), std::ptr::null_mut()) })
}

fn call_root_screen(connection: *mut XcbConnection) -> Option<*mut XcbScreen> {
    match unsafe { xcb_setup_roots_iterator(xcb_get_setup(connection)) }.data {
        screen if screen.is_null() => None,
        screen => Some(screen),
    }
}

fn call_place_window(connection: *mut XcbConnection, screen: *mut XcbScreen) -> u32 {
    let handle = unsafe { xcb_generate_id(connection) };
    unsafe {
        xcb_create_window(
            connection,
            COPY_FROM_PARENT,
            handle,
            (*screen).root,
            WINDOW_ORIGIN,
            WINDOW_ORIGIN,
            WINDOW_EDGE,
            WINDOW_EDGE,
            WINDOW_BORDER,
            WINDOW_INPUT_OUTPUT,
            (*screen).root_visual,
            NO_VALUES,
            std::ptr::null(),
        )
    };
    unsafe { xcb_flush(connection) };
    handle
}

fn call_open_window() -> Option<Window> {
    let connection = call_open_connection()?;
    let screen = call_root_screen(connection)?;
    Some(Window {
        connection,
        handle: call_place_window(connection, screen),
    })
}

fn call_close_window(window: &Window) {
    unsafe { xcb_disconnect(window.connection) };
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

fn call_surface_fn(entry: &ash::Entry, instance: &ash::Instance) -> Option<PfnCreateXcbSurface> {
    let name = CString::new(FN_CREATE_SURFACE).ok()?;
    unsafe { entry.get_instance_proc_addr(instance.handle(), name.as_ptr()) }
        .map(|found| unsafe { std::mem::transmute(found) })
}

fn call_surface_result(result: vk::Result, surface: vk::SurfaceKHR) -> Option<vk::SurfaceKHR> {
    match result {
        vk::Result::SUCCESS => Some(surface),
        _ => None,
    }
}

fn call_create_surface(
    entry: &ash::Entry,
    instance: &ash::Instance,
    window: &Window,
) -> Option<vk::SurfaceKHR> {
    let create = call_surface_fn(entry, instance)?;
    let info = surface_info(window);
    let mut surface = vk::SurfaceKHR::null();
    call_surface_result(
        unsafe { create(instance.handle(), &info, std::ptr::null(), &mut surface) },
        surface,
    )
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
    loader: &ash::extensions::khr::Surface,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
) -> Option<vk::SurfaceFormatKHR> {
    unsafe { loader.get_physical_device_surface_formats(phys, surface) }
        .ok()
        .and_then(|all| all.first().copied())
}

fn call_surface_caps(
    loader: &ash::extensions::khr::Surface,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
) -> Option<vk::SurfaceCapabilitiesKHR> {
    unsafe { loader.get_physical_device_surface_capabilities(phys, surface) }.ok()
}

fn call_create_swapchain(
    loader: &ash::extensions::khr::Swapchain,
    surface: vk::SurfaceKHR,
    format: vk::SurfaceFormatKHR,
    caps: &vk::SurfaceCapabilitiesKHR,
) -> Option<vk::SwapchainKHR> {
    unsafe { loader.create_swapchain(&swapchain_info(surface, format, caps), None) }.ok()
}

fn call_create_sampler(device: &ash::Device) -> Option<vk::Sampler> {
    unsafe { device.create_sampler(&sampler_info(), None) }.ok()
}

fn call_on_device(
    entry: &ash::Entry,
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
    device: &ash::Device,
) -> Option<()> {
    let surfaces = ash::extensions::khr::Surface::new(entry, instance);
    let caps = call_surface_caps(&surfaces, phys, surface)?;
    let format = call_first_format(&surfaces, phys, surface)?;
    let swapchains = ash::extensions::khr::Swapchain::new(instance, device);
    let swapchain = call_create_swapchain(&swapchains, surface, format, &caps)?;
    let sampler = call_create_sampler(device)?;
    unsafe { device.destroy_sampler(sampler, None) };
    unsafe { swapchains.destroy_swapchain(swapchain, None) };
    unsafe { surfaces.destroy_surface(surface, None) };
    Some(())
}

fn call_with_device(
    entry: &ash::Entry,
    instance: &ash::Instance,
    phys: vk::PhysicalDevice,
    surface: vk::SurfaceKHR,
) -> Option<()> {
    let device = call_create_device(instance, phys, call_graphics_family(instance, phys)?)?;
    let done = call_on_device(entry, instance, phys, surface, &device);
    unsafe { device.destroy_device(None) };
    done
}

fn call_exercise(entry: &ash::Entry, instance: &ash::Instance, window: &Window) -> Option<()> {
    let surface = call_create_surface(entry, instance, window)?;
    let phys = call_first_physical(instance)?;
    call_with_device(entry, instance, phys, surface)
}

fn call_with_instance(entry: &ash::Entry, window: &Window) -> Option<()> {
    let instance = call_create_instance(entry)?;
    let done = call_exercise(entry, &instance, window);
    unsafe { instance.destroy_instance(None) };
    done
}

fn call_probe() -> Option<()> {
    let entry = call_entry()?;
    let window = call_open_window()?;
    let done = call_with_instance(&entry, &window);
    call_close_window(&window);
    done
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
