use std::sync::atomic::AtomicU64;
use std::sync::atomic::Ordering;
use std::sync::OnceLock;
use std::thread;
use std::time::Duration;
use std::time::Instant;

use ash::vk;

use crate::config::ensure_settings;
use crate::consts::PacingChoice;
use crate::consts::SPIN_MARGIN_US;
use crate::consts::US_PER_S;
use crate::device::VkDevState;

static EPOCH: OnceLock<Instant> = OnceLock::new();
static LAST_US: AtomicU64 = AtomicU64::new(0);

fn call_now_us() -> u64 {
    EPOCH.get_or_init(Instant::now).elapsed().as_micros() as u64
}

fn target_interval_us(fps: f32) -> u64 {
    (US_PER_S / fps) as u64
}

fn frame_target_us(last: u64, interval: u64) -> u64 {
    last + interval
}

fn wait_deficit_us(now: u64, target: u64) -> u64 {
    target.saturating_sub(now)
}

fn call_sleep_us(us: u64) {
    match us {
        0 => (),
        n => thread::sleep(Duration::from_micros(n)),
    }
}

fn call_spin_until(target: u64) {
    std::iter::repeat(())
        .take_while(|_| call_now_us() < target)
        .for_each(|_| std::hint::spin_loop());
}

fn call_wait_until(target: u64, precise: bool) {
    match precise {
        true => {
            call_sleep_us(wait_deficit_us(call_now_us(), target.saturating_sub(SPIN_MARGIN_US)));
            call_spin_until(target);
        }
        false => call_sleep_us(wait_deficit_us(call_now_us(), target)),
    }
}

fn pacing_is_precise(pacing: Option<PacingChoice>) -> bool {
    match pacing {
        Some(PacingChoice::Precise) => true,
        Some(PacingChoice::Sleep) | None => false,
    }
}

fn call_limit_to(fps: f32, precise: bool) {
    call_wait_until(
        frame_target_us(LAST_US.load(Ordering::Relaxed), target_interval_us(fps)),
        precise,
    );
    LAST_US.store(call_now_us(), Ordering::Relaxed);
}

pub(crate) fn maybe_limit_frame() {
    let s = ensure_settings();
    match s.frame_limit {
        Some(fps) => call_limit_to(fps, pacing_is_precise(s.pacing)),
        None => (),
    }
}

pub(crate) fn call_present_frame(
    dev: &VkDevState,
    queue: vk::Queue,
    info: *const vk::PresentInfoKHR,
) -> vk::Result {
    unsafe { (dev.swap_fp.queue_present_khr)(queue, info) }
}
