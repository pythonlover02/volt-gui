use std::sync::atomic::AtomicU64;
use std::sync::atomic::Ordering;
use std::sync::OnceLock;
use std::thread;
use std::time::Duration;
use std::time::Instant;

use crate::config::ensure_settings;
use crate::consts::US_PER_S;

static EPOCH: OnceLock<Instant> = OnceLock::new();
static LAST_US: AtomicU64 = AtomicU64::new(0);

fn call_now_us() -> u64 {
    EPOCH.get_or_init(Instant::now).elapsed().as_micros() as u64
}

fn target_interval_us(fps: f32) -> u64 {
    (US_PER_S / fps) as u64
}

fn sleep_deficit_us(now: u64, last: u64, interval: u64) -> u64 {
    (last + interval).saturating_sub(now)
}

fn call_sleep_us(us: u64) {
    match us {
        0 => (),
        n => thread::sleep(Duration::from_micros(n)),
    }
}

fn call_limit_to(fps: f32) {
    let interval = target_interval_us(fps);
    let last = LAST_US.load(Ordering::Relaxed);
    call_sleep_us(sleep_deficit_us(call_now_us(), last, interval));
    LAST_US.store(call_now_us(), Ordering::Relaxed);
}

pub(crate) fn maybe_limit_frame() {
    match ensure_settings().frame_limit {
        Some(fps) => call_limit_to(fps),
        None => (),
    }
}
