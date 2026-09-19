use ash::vk;

use crate::consts::ALPHA_UNKNOWN_PREFIX;
use crate::consts::PRESENT_UNKNOWN_PREFIX;

const PRESENT_MODES: [(i32, &str, bool, bool); 7] = [
    (0, "immediate", true, false),
    (1, "mailbox", true, false),
    (2, "fifo", true, false),
    (3, "fifo_relaxed", true, false),
    (1000111000, "shared_demand_refresh", false, true),
    (1000111001, "shared_continuous_refresh", false, true),
    (1000361000, "fifo_latest_ready", false, false),
];

const COMPOSITE_ALPHAS: [(u32, &str, bool); 4] = [
    (1, "opaque", false),
    (2, "pre_multiplied", true),
    (4, "post_multiplied", true),
    (8, "inherit", true),
];

#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) struct PresentFacts {
    pub(crate) floor: bool,
    pub(crate) shared: bool,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) struct AlphaFacts {
    pub(crate) blends: bool,
}

fn unknown_display(prefix: &str, value: i64) -> String {
    format!("{}{}", prefix, value)
}

fn present_row(value: i32) -> Option<(i32, &'static str, bool, bool)> {
    PRESENT_MODES
        .iter()
        .copied()
        .find(|(known, _, _, _)| *known == value)
}

fn alpha_row(value: u32) -> Option<(u32, &'static str, bool)> {
    COMPOSITE_ALPHAS
        .iter()
        .copied()
        .find(|(known, _, _)| *known == value)
}

pub(crate) fn present_display(value: vk::PresentModeKHR) -> String {
    match present_row(value.as_raw()) {
        Some((_, name, _, _)) => name.to_string(),
        None => unknown_display(PRESENT_UNKNOWN_PREFIX, value.as_raw() as i64),
    }
}

pub(crate) fn present_parse(text: &str) -> Option<vk::PresentModeKHR> {
    PRESENT_MODES
        .iter()
        .find(|(_, name, floor, _)| *name == text && *floor)
        .map(|(value, _, _, _)| vk::PresentModeKHR::from_raw(*value))
}

pub(crate) fn present_semantic(value: vk::PresentModeKHR) -> Option<PresentFacts> {
    present_row(value.as_raw()).map(|(_, _, floor, shared)| PresentFacts { floor, shared })
}

pub(crate) fn alpha_display(value: vk::CompositeAlphaFlagsKHR) -> String {
    match alpha_row(value.as_raw()) {
        Some((_, name, _)) => name.to_string(),
        None => unknown_display(ALPHA_UNKNOWN_PREFIX, value.as_raw() as i64),
    }
}

pub(crate) fn alpha_parse(text: &str) -> Option<vk::CompositeAlphaFlagsKHR> {
    COMPOSITE_ALPHAS
        .iter()
        .find(|(_, name, _)| *name == text)
        .map(|(value, _, _)| vk::CompositeAlphaFlagsKHR::from_raw(*value))
}

pub(crate) fn alpha_semantic(value: vk::CompositeAlphaFlagsKHR) -> Option<AlphaFacts> {
    alpha_row(value.as_raw()).map(|(_, _, blends)| AlphaFacts { blends })
}
