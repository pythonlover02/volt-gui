use std::ffi::c_void;
use std::ffi::CString;
use std::mem;

pub(crate) struct Library {
    handle: *mut c_void,
}

fn found(address: *mut c_void) -> Option<*mut c_void> {
    match address.is_null() {
        true => None,
        false => Some(address),
    }
}

fn call_open_one(name: &str) -> Option<*mut c_void> {
    let text = CString::new(name).ok()?;
    found(unsafe { libc::dlopen(text.as_ptr(), libc::RTLD_NOW | libc::RTLD_LOCAL) })
}

pub(crate) fn call_open_library(names: &[&str]) -> Option<Library> {
    names
        .iter()
        .find_map(|name| call_open_one(name))
        .map(|handle| Library { handle })
}

impl Library {
    pub(crate) fn address(&self, name: &str) -> Option<*mut c_void> {
        let text = CString::new(name).ok()?;
        found(unsafe { libc::dlsym(self.handle, text.as_ptr()) })
    }

    pub(crate) fn symbol<T>(&self, name: &str) -> Option<T> {
        self.address(name)
            .map(|address| unsafe { mem::transmute_copy(&address) })
    }
}
