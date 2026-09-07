use std::ffi::c_char;
use std::ffi::c_int;
use std::ffi::c_void;
use std::ffi::CString;
use std::mem;
use std::ptr;
use std::sync::OnceLock;

use ash::vk;

use crate::dl::call_open_library;
use crate::dl::Library;
use crate::Backend;
use crate::Handles;
use crate::WINDOW_EDGE;

const LIBRARIES: [&str; 2] = ["libxcb.so.1", "libxcb.so"];
const EXT_SURFACE: &str = "VK_KHR_xcb_surface";
const FN_CREATE_SURFACE: &str = "vkCreateXcbSurfaceKHR";
const SURFACE_TYPE: i32 = 1000005000;
const WINDOW_ORIGIN: i16 = 0;
const WINDOW_BORDER: u16 = 0;
const WINDOW_INPUT_OUTPUT: u16 = 1;
const COPY_FROM_PARENT: u8 = 0;
const NO_VALUES: u32 = 0;
const NO_FLAGS: u32 = 0;
const NO_ERROR: c_int = 0;

pub(crate) const BACKEND: Backend = Backend {
    extension: EXT_SURFACE,
    open: call_open,
    create_surface: call_create_surface,
    close: call_close,
};

#[repr(C)]
struct XcbScreen {
    root: u32,
    default_colormap: u32,
    white_pixel: u32,
    black_pixel: u32,
    current_input_masks: u32,
    width_in_pixels: u16,
    height_in_pixels: u16,
    width_in_millimeters: u16,
    height_in_millimeters: u16,
    min_installed_maps: u16,
    max_installed_maps: u16,
    root_visual: u32,
    backing_stores: u8,
    save_unders: u8,
    root_depth: u8,
    allowed_depths_len: u8,
}

#[repr(C)]
struct XcbScreenIterator {
    data: *mut XcbScreen,
    rem: c_int,
    index: c_int,
}

#[repr(C)]
struct VkXcbSurfaceCreateInfo {
    s_type: vk::StructureType,
    p_next: *const c_void,
    flags: u32,
    connection: *mut c_void,
    window: u32,
}

type PfnCreateXcbSurface = unsafe extern "system" fn(
    vk::Instance,
    *const VkXcbSurfaceCreateInfo,
    *const vk::AllocationCallbacks<'_>,
    *mut vk::SurfaceKHR,
) -> vk::Result;

struct Xcb {
    connect: unsafe extern "C" fn(*const c_char, *mut c_int) -> *mut c_void,
    disconnect: unsafe extern "C" fn(*mut c_void),
    has_error: unsafe extern "C" fn(*mut c_void) -> c_int,
    get_setup: unsafe extern "C" fn(*mut c_void) -> *const c_void,
    roots_iterator: unsafe extern "C" fn(*const c_void) -> XcbScreenIterator,
    generate_id: unsafe extern "C" fn(*mut c_void) -> u32,
    create_window: unsafe extern "C" fn(
        *mut c_void,
        u8,
        u32,
        u32,
        i16,
        i16,
        u16,
        u16,
        u16,
        u16,
        u32,
        u32,
        *const u32,
    ) -> u32,
    flush: unsafe extern "C" fn(*mut c_void) -> c_int,
}

unsafe impl Send for Xcb {}
unsafe impl Sync for Xcb {}

static XCB: OnceLock<Option<Xcb>> = OnceLock::new();

fn loaded(library: &Library) -> Option<Xcb> {
    Some(Xcb {
        connect: library.symbol("xcb_connect")?,
        disconnect: library.symbol("xcb_disconnect")?,
        has_error: library.symbol("xcb_connection_has_error")?,
        get_setup: library.symbol("xcb_get_setup")?,
        roots_iterator: library.symbol("xcb_setup_roots_iterator")?,
        generate_id: library.symbol("xcb_generate_id")?,
        create_window: library.symbol("xcb_create_window")?,
        flush: library.symbol("xcb_flush")?,
    })
}

fn xcb() -> Option<&'static Xcb> {
    XCB.get_or_init(|| call_open_library(&LIBRARIES).and_then(|library| loaded(&library)))
        .as_ref()
}

fn call_dropped<T>(xcb: &Xcb, connection: *mut c_void) -> Option<T> {
    unsafe { (xcb.disconnect)(connection) };
    None
}

fn call_connected(xcb: &Xcb, connection: *mut c_void) -> Option<*mut c_void> {
    match unsafe { (xcb.has_error)(connection) } {
        NO_ERROR => Some(connection),
        _ => call_dropped(xcb, connection),
    }
}

fn call_root_screen(xcb: &Xcb, connection: *mut c_void) -> Option<*mut XcbScreen> {
    match unsafe { (xcb.roots_iterator)((xcb.get_setup)(connection)) }.data {
        screen if screen.is_null() => None,
        screen => Some(screen),
    }
}

fn call_place_window(xcb: &Xcb, connection: *mut c_void, screen: *mut XcbScreen) -> u32 {
    let handle = unsafe { (xcb.generate_id)(connection) };
    unsafe {
        (xcb.create_window)(
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
            ptr::null(),
        )
    };
    unsafe { (xcb.flush)(connection) };
    handle
}

fn call_windowed(xcb: &Xcb, connection: *mut c_void) -> Option<Handles> {
    match call_root_screen(xcb, connection) {
        None => call_dropped(xcb, connection),
        Some(screen) => Some(Handles {
            display: connection,
            window: call_place_window(xcb, connection, screen) as u64,
        }),
    }
}

fn call_open() -> Option<Handles> {
    let xcb = xcb()?;
    let connection = call_connected(xcb, unsafe {
        (xcb.connect)(ptr::null(), ptr::null_mut())
    })?;
    call_windowed(xcb, connection)
}

fn call_close(handles: &Handles) {
    match xcb() {
        Some(xcb) => unsafe { (xcb.disconnect)(handles.display) },
        None => (),
    }
}

fn surface_info(handles: &Handles) -> VkXcbSurfaceCreateInfo {
    VkXcbSurfaceCreateInfo {
        s_type: vk::StructureType::from_raw(SURFACE_TYPE),
        p_next: ptr::null(),
        flags: NO_FLAGS,
        connection: handles.display,
        window: handles.window as u32,
    }
}

fn call_surface_fn(entry: &ash::Entry, instance: &ash::Instance) -> Option<PfnCreateXcbSurface> {
    let name = CString::new(FN_CREATE_SURFACE).ok()?;
    unsafe { entry.get_instance_proc_addr(instance.handle(), name.as_ptr()) }
        .map(|found| unsafe { mem::transmute(found) })
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
    handles: &Handles,
) -> Option<vk::SurfaceKHR> {
    let create = call_surface_fn(entry, instance)?;
    let info = surface_info(handles);
    let mut surface = vk::SurfaceKHR::null();
    call_surface_result(
        unsafe { create(instance.handle(), &info, ptr::null(), &mut surface) },
        surface,
    )
}
