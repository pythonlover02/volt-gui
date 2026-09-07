use std::ffi::c_char;
use std::ffi::c_int;
use std::ffi::c_void;
use std::ffi::CStr;
use std::ffi::CString;
use std::mem;
use std::ptr;
use std::sync::OnceLock;

use ash::vk;

use crate::dl::call_open_library;
use crate::dl::Library;
use crate::Backend;
use crate::Handles;

const LIBRARIES: [&str; 2] = ["libwayland-client.so.0", "libwayland-client.so"];
const EXT_SURFACE: &str = "VK_KHR_wayland_surface";
const FN_CREATE_SURFACE: &str = "vkCreateWaylandSurfaceKHR";
const SURFACE_TYPE: i32 = 1000006000;
const COMPOSITOR_NAME: &[u8] = b"wl_compositor";
const COMPOSITOR_VERSION: u32 = 1;
const DISPLAY_GET_REGISTRY: u32 = 1;
const REGISTRY_BIND: u32 = 0;
const COMPOSITOR_CREATE_SURFACE: u32 = 0;
const SURFACE_DESTROY: u32 = 0;
const MARSHAL_DESTROY: u32 = 1;
const NO_FLAGS: u32 = 0;

pub(crate) const BACKEND: Backend = Backend {
    extension: EXT_SURFACE,
    open: call_open,
    create_surface: call_create_surface,
    close: call_close,
};

#[repr(C)]
struct WlInterfaceHead {
    name: *const c_char,
}

#[repr(C)]
struct RegistryListener {
    global: unsafe extern "C" fn(*mut c_void, *mut c_void, u32, *const c_char, u32),
    global_remove: unsafe extern "C" fn(*mut c_void, *mut c_void, u32),
}

#[repr(C)]
struct VkWaylandSurfaceCreateInfo {
    s_type: vk::StructureType,
    p_next: *const c_void,
    flags: u32,
    display: *mut c_void,
    surface: *mut c_void,
}

type PfnCreateWaylandSurface = unsafe extern "system" fn(
    vk::Instance,
    *const VkWaylandSurfaceCreateInfo,
    *const vk::AllocationCallbacks<'_>,
    *mut vk::SurfaceKHR,
) -> vk::Result;

type PfnMarshal =
    unsafe extern "C" fn(*mut c_void, u32, *const c_void, u32, u32, ...) -> *mut c_void;

struct Wl {
    connect: unsafe extern "C" fn(*const c_char) -> *mut c_void,
    disconnect: unsafe extern "C" fn(*mut c_void),
    roundtrip: unsafe extern "C" fn(*mut c_void) -> c_int,
    marshal: PfnMarshal,
    add_listener: unsafe extern "C" fn(*mut c_void, *const c_void, *mut c_void) -> c_int,
    get_version: unsafe extern "C" fn(*mut c_void) -> u32,
    registry_interface: *const c_void,
    compositor_interface: *const c_void,
    surface_interface: *const c_void,
}

unsafe impl Send for Wl {}
unsafe impl Sync for Wl {}

struct BindState {
    wl: &'static Wl,
    compositor: *mut c_void,
}

static WL: OnceLock<Option<Wl>> = OnceLock::new();

static LISTENER: RegistryListener = RegistryListener {
    global: on_global,
    global_remove: on_global_remove,
};

fn loaded(library: &Library) -> Option<Wl> {
    Some(Wl {
        connect: library.symbol("wl_display_connect")?,
        disconnect: library.symbol("wl_display_disconnect")?,
        roundtrip: library.symbol("wl_display_roundtrip")?,
        marshal: library.symbol("wl_proxy_marshal_flags")?,
        add_listener: library.symbol("wl_proxy_add_listener")?,
        get_version: library.symbol("wl_proxy_get_version")?,
        registry_interface: library.address("wl_registry_interface")?,
        compositor_interface: library.address("wl_compositor_interface")?,
        surface_interface: library.address("wl_surface_interface")?,
    })
}

fn wayland() -> Option<&'static Wl> {
    WL.get_or_init(|| call_open_library(&LIBRARIES).and_then(|library| loaded(&library)))
        .as_ref()
}

fn interface_name(interface: *const c_void) -> *const c_char {
    unsafe { (*(interface as *const WlInterfaceHead)).name }
}

fn call_bind(wl: &Wl, registry: *mut c_void, name: u32) -> *mut c_void {
    unsafe {
        (wl.marshal)(
            registry,
            REGISTRY_BIND,
            wl.compositor_interface,
            COMPOSITOR_VERSION,
            NO_FLAGS,
            name,
            interface_name(wl.compositor_interface),
            COMPOSITOR_VERSION,
            ptr::null_mut::<c_void>(),
        )
    }
}

unsafe extern "C" fn on_global(
    data: *mut c_void,
    registry: *mut c_void,
    name: u32,
    interface: *const c_char,
    _version: u32,
) {
    unsafe {
        let state = &mut *(data as *mut BindState);
        if CStr::from_ptr(interface).to_bytes() == COMPOSITOR_NAME {
            state.compositor = call_bind(state.wl, registry, name);
        }
    }
}

unsafe extern "C" fn on_global_remove(_data: *mut c_void, _registry: *mut c_void, _name: u32) {}

fn call_registry(wl: &Wl, display: *mut c_void) -> *mut c_void {
    unsafe {
        (wl.marshal)(
            display,
            DISPLAY_GET_REGISTRY,
            wl.registry_interface,
            (wl.get_version)(display),
            NO_FLAGS,
            ptr::null_mut::<c_void>(),
        )
    }
}

fn call_compositor(wl: &'static Wl, display: *mut c_void) -> *mut c_void {
    let registry = call_registry(wl, display);
    let mut state = BindState {
        wl,
        compositor: ptr::null_mut(),
    };
    unsafe {
        (wl.add_listener)(
            registry,
            &LISTENER as *const RegistryListener as *const c_void,
            &mut state as *mut BindState as *mut c_void,
        )
    };
    unsafe { (wl.roundtrip)(display) };
    state.compositor
}

fn call_wl_surface(wl: &Wl, compositor: *mut c_void) -> *mut c_void {
    unsafe {
        (wl.marshal)(
            compositor,
            COMPOSITOR_CREATE_SURFACE,
            wl.surface_interface,
            (wl.get_version)(compositor),
            NO_FLAGS,
            ptr::null_mut::<c_void>(),
        )
    }
}

fn call_dropped(wl: &Wl, display: *mut c_void) -> Option<Handles> {
    unsafe { (wl.disconnect)(display) };
    None
}

fn call_handles(wl: &Wl, display: *mut c_void, surface: *mut c_void) -> Option<Handles> {
    match surface.is_null() {
        true => call_dropped(wl, display),
        false => Some(Handles {
            display,
            window: surface as u64,
        }),
    }
}

fn call_bound(wl: &Wl, display: *mut c_void, compositor: *mut c_void) -> Option<Handles> {
    match compositor.is_null() {
        true => call_dropped(wl, display),
        false => call_handles(wl, display, call_wl_surface(wl, compositor)),
    }
}

fn call_connected(display: *mut c_void) -> Option<*mut c_void> {
    match display.is_null() {
        true => None,
        false => Some(display),
    }
}

fn call_open() -> Option<Handles> {
    let wl = wayland()?;
    let display = call_connected(unsafe { (wl.connect)(ptr::null()) })?;
    call_bound(wl, display, call_compositor(wl, display))
}

fn call_destroy_wl_surface(wl: &Wl, surface: *mut c_void) {
    unsafe {
        (wl.marshal)(
            surface,
            SURFACE_DESTROY,
            ptr::null::<c_void>(),
            (wl.get_version)(surface),
            MARSHAL_DESTROY,
        )
    };
}

fn call_teardown(wl: &Wl, handles: &Handles) {
    call_destroy_wl_surface(wl, handles.window as *mut c_void);
    unsafe { (wl.disconnect)(handles.display) };
}

fn call_close(handles: &Handles) {
    if let Some(wl) = wayland() {
        call_teardown(wl, handles);
    }
}

fn surface_info(handles: &Handles) -> VkWaylandSurfaceCreateInfo {
    VkWaylandSurfaceCreateInfo {
        s_type: vk::StructureType::from_raw(SURFACE_TYPE),
        p_next: ptr::null(),
        flags: NO_FLAGS,
        display: handles.display,
        surface: handles.window as *mut c_void,
    }
}

fn call_surface_fn(
    entry: &ash::Entry,
    instance: &ash::Instance,
) -> Option<PfnCreateWaylandSurface> {
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
