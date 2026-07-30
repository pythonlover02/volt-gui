use std::ffi::c_void;
use std::ffi::CString;
use std::path::PathBuf;
use std::sync::atomic::AtomicBool;
use std::sync::atomic::Ordering;
use std::sync::Mutex;
use std::sync::OnceLock;
use std::thread;
use std::time::Duration;

use crate::config::config_dir;
use crate::config::config_path;
use crate::config::profile_name;
use crate::config::read_config;
use crate::config::store_settings;
use crate::consts::DEBOUNCE_MS;
use crate::consts::INOTIFY_BUF;
use crate::consts::POLL_INTERVAL_MS;
use crate::logging::log_at;
use crate::logging::LogLevel;

static NOTIFY_FD: OnceLock<i32> = OnceLock::new();
static DIRTY: AtomicBool = AtomicBool::new(false);
static SHUTDOWN: AtomicBool = AtomicBool::new(false);
static WATCHER: Mutex<Option<thread::JoinHandle<()>>> = Mutex::new(None);

fn call_inotify_init() -> i32 {
    unsafe { libc::inotify_init1(libc::IN_NONBLOCK) }
}

fn call_inotify_watch(fd: i32, dir: &PathBuf) -> i32 {
    let c = CString::new(dir.to_string_lossy().as_bytes()).unwrap_or_default();
    unsafe {
        libc::inotify_add_watch(
            fd,
            c.as_ptr(),
            libc::IN_CLOSE_WRITE | libc::IN_MOVED_TO | libc::IN_CREATE,
        )
    }
}

fn call_inotify_read(fd: i32) -> isize {
    let mut buf = [0u8; INOTIFY_BUF];
    unsafe { libc::read(fd, buf.as_mut_ptr() as *mut c_void, INOTIFY_BUF) }
}

fn call_poll_fd(fd: i32, timeout_ms: i32) -> i32 {
    let mut pfd = libc::pollfd { fd, events: libc::POLLIN, revents: 0 };
    unsafe { libc::poll(&mut pfd, 1, timeout_ms) }
}

fn has_events(result: i32) -> bool {
    result > 0
}

fn call_inotify_drain_all(fd: i32) {
    std::iter::repeat_with(|| call_inotify_read(fd))
        .take_while(|n| *n > 0)
        .for_each(drop);
}

fn fd_is_valid(fd: i32) -> bool {
    fd >= 0
}

fn poll_dirty() -> bool {
    DIRTY.swap(false, Ordering::Relaxed)
}

fn shutdown_requested() -> bool {
    SHUTDOWN.load(Ordering::Relaxed)
}

fn watch_step(fd: i32) {
    match has_events(call_poll_fd(fd, POLL_INTERVAL_MS)) {
        true => {
            call_inotify_drain_all(fd);
            thread::sleep(Duration::from_millis(DEBOUNCE_MS));
            call_inotify_drain_all(fd);
            DIRTY.store(true, Ordering::Relaxed);
        }
        false => (),
    }
}

fn watch_loop(fd: i32) {
    std::iter::repeat(())
        .take_while(|_| !shutdown_requested())
        .for_each(|_| watch_step(fd));
}

fn store_handle(h: thread::JoinHandle<()>) {
    match WATCHER.lock() {
        Ok(mut g) => *g = Some(h),
        Err(_) => (),
    }
}

fn take_handle() -> Option<thread::JoinHandle<()>> {
    WATCHER.lock().ok().and_then(|mut g| g.take())
}

fn join_handle(h: thread::JoinHandle<()>) {
    let _ = h.join();
}

fn start_watcher(fd: i32) {
    match fd_is_valid(call_inotify_watch(fd, &config_dir())) {
        true => store_handle(thread::spawn(move || watch_loop(fd))),
        false => log_at(LogLevel::Warn, "inotify add watch failed, hot reload disabled"),
    }
}

fn init_inotify() {
    NOTIFY_FD.get_or_init(|| {
        let fd = call_inotify_init();
        match fd_is_valid(fd) {
            true => {
                start_watcher(fd);
                fd
            }
            false => fd,
        }
    });
}

fn call_close_fd(fd: i32) {
    unsafe { libc::close(fd) };
}

fn close_notify_fd() {
    NOTIFY_FD
        .get()
        .copied()
        .filter(|fd| fd_is_valid(*fd))
        .into_iter()
        .for_each(call_close_fd);
}

pub(crate) fn maybe_shutdown_watch(last_instance: bool) {
    match last_instance {
        true => {
            SHUTDOWN.store(true, Ordering::Relaxed);
            take_handle().into_iter().for_each(join_handle);
            close_notify_fd();
        }
        false => (),
    }
}

pub(crate) fn setup_watch() {
    init_inotify();
}

pub(crate) fn maybe_reload() {
    match poll_dirty() {
        true => {
            store_settings(read_config(&config_path(&profile_name())));
            log_at(LogLevel::Info, "settings hot reloaded");
        }
        false => (),
    }
}
