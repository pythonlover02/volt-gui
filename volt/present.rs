use std::sync::atomic::AtomicU64;
use std::sync::atomic::Ordering;
use std::sync::OnceLock;
use std::thread;
use std::time::Duration;
use std::time::Instant;

use ash::vk;

use crate::config::Settings;
use crate::consts::LimitStage;
use crate::consts::MethodChoice;
use crate::consts::PacingChoice;
use crate::consts::NS_PER_S;
use crate::consts::SLICE_MARGIN_NS;
use crate::consts::SLICE_STEP_NS;
use crate::consts::SPIN_MARGIN_NS;
use crate::device::VkDevState;

static EPOCH: OnceLock<Instant> = OnceLock::new();
static TARGET_NS: AtomicU64 = AtomicU64::new(0);
static INTERVAL_NS: AtomicU64 = AtomicU64::new(0);

fn call_now_ns() -> u64 {
    EPOCH.get_or_init(Instant::now).elapsed().as_nanos() as u64
}

fn target_interval_ns(fps: f32) -> u64 {
    (NS_PER_S / fps as f64) as u64
}

fn overshoot_ns(now: u64, target: u64) -> u64 {
    now.saturating_sub(target)
}

fn next_target_ns(now: u64, previous: u64, interval: u64, fresh: bool) -> u64 {
    match (fresh, overshoot_ns(now, previous) >= interval) {
        (false, false) => previous + interval,
        (_, _) => now + interval,
    }
}

fn wait_deficit_ns(now: u64, target: u64) -> u64 {
    target.saturating_sub(now)
}

fn slice_length_ns(remaining: u64) -> u64 {
    remaining.saturating_sub(SLICE_MARGIN_NS).min(SLICE_STEP_NS)
}

fn restart_wanted(method: Option<MethodChoice>, interval_changed: bool) -> bool {
    match method {
        Some(MethodChoice::Reactive) => true,
        Some(MethodChoice::Early) | Some(MethodChoice::Late) | None => interval_changed,
    }
}

fn call_sleep_ns(ns: u64) {
    match ns {
        0 => (),
        n => thread::sleep(Duration::from_nanos(n)),
    }
}

fn call_spin_until(target: u64) {
    std::iter::repeat(())
        .take_while(|_| call_now_ns() < target)
        .for_each(|_| std::hint::spin_loop());
}

fn call_sleep_until(target: u64) {
    call_sleep_ns(wait_deficit_ns(call_now_ns(), target));
}

fn call_precise_until(target: u64) {
    call_sleep_ns(wait_deficit_ns(call_now_ns(), target.saturating_sub(SPIN_MARGIN_NS)));
    call_spin_until(target);
}

fn call_slice_until(target: u64) {
    std::iter::repeat(())
        .take_while(|_| call_now_ns() + SLICE_MARGIN_NS < target)
        .for_each(|_| call_sleep_ns(slice_length_ns(wait_deficit_ns(call_now_ns(), target))));
    call_spin_until(target);
}

fn call_wait_until(target: u64, pacing: PacingChoice) {
    match pacing {
        PacingChoice::Sleep => call_sleep_until(target),
        PacingChoice::Sliced => call_slice_until(target),
        PacingChoice::Precise => call_precise_until(target),
        PacingChoice::Spin => call_spin_until(target),
    }
}

fn call_swap_interval(interval: u64) -> u64 {
    INTERVAL_NS.swap(interval, Ordering::Relaxed)
}

fn call_frame_target(interval: u64, method: Option<MethodChoice>) -> u64 {
    let target = next_target_ns(
        call_now_ns(),
        TARGET_NS.load(Ordering::Relaxed),
        interval,
        restart_wanted(method, call_swap_interval(interval) != interval),
    );
    TARGET_NS.store(target, Ordering::Relaxed);
    target
}

fn call_limit_to(fps: f32, pacing: PacingChoice, method: Option<MethodChoice>) {
    call_wait_until(call_frame_target(target_interval_ns(fps), method), pacing);
}

fn pacing_or_default(pacing: Option<PacingChoice>) -> PacingChoice {
    match pacing {
        Some(choice) => choice,
        None => PacingChoice::Sleep,
    }
}

fn stage_wanted(method: Option<MethodChoice>) -> LimitStage {
    match method {
        Some(MethodChoice::Late) => LimitStage::After,
        Some(MethodChoice::Early) | Some(MethodChoice::Reactive) | None => LimitStage::Before,
    }
}

fn limit_fps(s: &Settings, stage: LimitStage) -> Option<f32> {
    s.frame_limit.filter(|_| stage_wanted(s.limit_method) == stage)
}

pub(crate) fn maybe_limit_frame(stage: LimitStage, s: &Settings) {
    match limit_fps(s, stage) {
        Some(fps) => call_limit_to(fps, pacing_or_default(s.pacing), s.limit_method),
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
