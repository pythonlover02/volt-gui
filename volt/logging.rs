use std::ffi::c_void;
use std::sync::atomic::AtomicBool;
use std::sync::atomic::AtomicI32;
use std::sync::atomic::Ordering;

use crate::consts::DEFAULT_LOG_LEVEL;
use crate::consts::LOG_FD;
use crate::consts::LOG_LEVEL_ERROR;
use crate::consts::LOG_LEVEL_INFO;
use crate::consts::LOG_LEVEL_OFF;
use crate::consts::LOG_LEVEL_WARN;
use crate::env::env_log_level;

pub(crate) enum LogLevel {
    Off,
    Error,
    Warn,
    Info,
}

static LEVEL: AtomicI32 = AtomicI32::new(DEFAULT_LOG_LEVEL);
static LEVEL_SET: AtomicBool = AtomicBool::new(false);

pub(crate) fn level_num(l: &LogLevel) -> i32 {
    match l {
        LogLevel::Off => LOG_LEVEL_OFF,
        LogLevel::Error => LOG_LEVEL_ERROR,
        LogLevel::Warn => LOG_LEVEL_WARN,
        LogLevel::Info => LOG_LEVEL_INFO,
    }
}

fn parse_level(s: &str) -> LogLevel {
    match s {
        "off" => LogLevel::Off,
        "error" => LogLevel::Error,
        "info" => LogLevel::Info,
        _ => LogLevel::Warn,
    }
}

fn should_emit(n: i32, cur: i32) -> bool {
    n <= cur && n > LOG_LEVEL_OFF
}

fn call_write_log(s: &str) {
    unsafe { libc::write(LOG_FD, s.as_ptr() as *const c_void, s.len()) };
}

pub(crate) fn log_at(level: LogLevel, msg: &str) {
    match should_emit(level_num(&level), LEVEL.load(Ordering::Relaxed)) {
        true => call_write_log(&format!("[volt] {}\n", msg)),
        false => (),
    }
}

pub(crate) fn init_log_level() {
    match LEVEL_SET.swap(true, Ordering::Relaxed) {
        true => (),
        false => LEVEL.store(
            level_num(&parse_level(&env_log_level())),
            Ordering::Relaxed,
        ),
    }
}
