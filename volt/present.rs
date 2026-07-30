use std::ffi::c_void;
use std::sync::atomic::AtomicI32;
use std::sync::atomic::AtomicU64;
use std::sync::atomic::Ordering;
use std::sync::OnceLock;
use std::thread;
use std::time::Duration;
use std::time::Instant;

use ash::vk;
use ash::vk::Handle;

use crate::config::ensure_settings;
use crate::config::Settings;
use crate::consts::LatencyChoice;
use crate::consts::PacingChoice;
use crate::consts::SPIN_MARGIN_US;
use crate::consts::US_PER_S;
use crate::device::VkDevState;
use crate::ext::st;
use crate::ext::AntiLagDataAmd;
use crate::ext::LatencySleepModeInfoNv;
use crate::ext::SwapPresentModeInfoExt;
use crate::ext::ANTI_LAG_MODE_OFF;
use crate::ext::ANTI_LAG_MODE_ON;
use crate::ext::ST_ANTI_LAG_DATA;
use crate::ext::ST_LATENCY_SLEEP_MODE_INFO;
use crate::ext::ST_PRESENT_MODE_INFO;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::swapchain::present_vk;
use crate::swapchain::swaps_get;
use crate::swapchain::swaps_put;
use crate::swapchain::SwapModes;

const LATENCY_UNSET: i32 = -1;
const LATENCY_OFF: i32 = 0;
const LATENCY_ON: i32 = 1;
const LATENCY_BOOST: i32 = 2;

static EPOCH: OnceLock<Instant> = OnceLock::new();
static LAST_US: AtomicU64 = AtomicU64::new(0);
static LATENCY_STATE: AtomicI32 = AtomicI32::new(LATENCY_UNSET);

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
        Some(PacingChoice::Precise) | Some(PacingChoice::DisplayTiming) => true,
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

fn latency_code(wanted: Option<LatencyChoice>) -> i32 {
    match wanted {
        None => LATENCY_OFF,
        Some(LatencyChoice::On) => LATENCY_ON,
        Some(LatencyChoice::Boost) => LATENCY_BOOST,
    }
}

fn latency_interval_us(limit: Option<f32>) -> u32 {
    match limit {
        Some(fps) => (US_PER_S / fps) as u32,
        None => 0,
    }
}

fn call_set_latency_mode(dev: &VkDevState, sc: vk::SwapchainKHR, code: i32, s: &Settings) {
    match dev.latency_fp {
        Some(f) => {
            let info = LatencySleepModeInfoNv {
                s_type: st(ST_LATENCY_SLEEP_MODE_INFO),
                p_next: std::ptr::null(),
                low_latency_mode: match code {
                    LATENCY_OFF => vk::FALSE,
                    _ => vk::TRUE,
                },
                low_latency_boost: match code {
                    LATENCY_BOOST => vk::TRUE,
                    _ => vk::FALSE,
                },
                minimum_interval_us: latency_interval_us(s.frame_limit),
            };
            let _ = unsafe { f(dev.device.handle(), sc, &info) };
            log_at(LogLevel::Info, "nv low latency mode updated");
        }
        None => (),
    }
}

fn maybe_update_latency(dev: &VkDevState, sc: vk::SwapchainKHR, s: &Settings) {
    let wanted = latency_code(s.low_latency);
    match (dev.caps.low_latency, LATENCY_STATE.swap(wanted, Ordering::Relaxed) != wanted) {
        (true, true) => call_set_latency_mode(dev, sc, wanted, s),
        (_, _) => (),
    }
}

fn call_anti_lag_update(dev: &VkDevState, mode: u32, s: &Settings) {
    match dev.anti_lag_fp {
        Some(f) => {
            let data = AntiLagDataAmd {
                s_type: st(ST_ANTI_LAG_DATA),
                p_next: std::ptr::null(),
                mode,
                max_fps: s.frame_limit.map(|v| v as u32).unwrap_or(0),
                p_presentation_info: std::ptr::null(),
            };
            unsafe { f(dev.device.handle(), &data) };
        }
        None => (),
    }
}

fn maybe_anti_lag(dev: &VkDevState, s: &Settings) {
    match (dev.caps.anti_lag, s.anti_lag) {
        (true, Some(true)) => call_anti_lag_update(dev, ANTI_LAG_MODE_ON, s),
        (true, Some(false)) => call_anti_lag_update(dev, ANTI_LAG_MODE_OFF, s),
        (_, _) => (),
    }
}

fn switch_target(modes: &SwapModes, s: &Settings) -> Option<vk::PresentModeKHR> {
    s.present_mode
        .map(present_vk)
        .filter(|m| *m != modes.created && modes.supported.contains(m))
}

fn record_switch(sc_raw: u64, modes: &SwapModes, mode: vk::PresentModeKHR) {
    swaps_put(
        sc_raw,
        SwapModes {
            created: mode,
            supported: modes.supported.clone(),
            switchable: modes.switchable,
        },
    );
    log_at(LogLevel::Info, "present mode switched live");
}

fn live_mode_for(sc: vk::SwapchainKHR, s: &Settings) -> Option<vk::PresentModeKHR> {
    swaps_get(sc.as_raw())
        .filter(|m| m.switchable)
        .and_then(|m| {
            switch_target(&m, s).map(|mode| {
                record_switch(sc.as_raw(), &m, mode);
                mode
            })
        })
}

pub(crate) fn call_present_with_modes(
    dev: &VkDevState,
    queue: vk::Queue,
    info: *const vk::PresentInfoKHR,
) -> vk::Result {
    let s = ensure_settings();
    let (swapchains, first_sc) = unsafe {
        let n = (*info).swapchain_count as usize;
        let scs = std::slice::from_raw_parts((*info).p_swapchains, n).to_vec();
        let first = scs.first().copied().unwrap_or(vk::SwapchainKHR::null());
        (scs, first)
    };
    maybe_anti_lag(dev, &s);
    maybe_update_latency(dev, first_sc, &s);
    let switched: Vec<vk::PresentModeKHR> = swapchains
        .iter()
        .filter_map(|sc| live_mode_for(*sc, &s))
        .collect();
    match switched.len() == swapchains.len() && !switched.is_empty() {
        true => {
            let mode_info = SwapPresentModeInfoExt {
                s_type: st(ST_PRESENT_MODE_INFO),
                p_next: unsafe { (*info).p_next },
                swapchain_count: switched.len() as u32,
                p_present_modes: switched.as_ptr(),
            };
            let patched = vk::PresentInfoKHR {
                p_next: &mode_info as *const SwapPresentModeInfoExt as *const c_void,
                ..unsafe { *info }
            };
            unsafe { (dev.swap_fp.queue_present_khr)(queue, &patched) }
        }
        false => unsafe { (dev.swap_fp.queue_present_khr)(queue, info) },
    }
}
