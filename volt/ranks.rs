use crate::consts::ALPHA_UNKNOWN_PREFIX;
use crate::consts::PRESENT_UNKNOWN_PREFIX;

const PRESENT_MODES: [(u32, &str, bool); 7] = [
    (0, "immediate", false),
    (1, "mailbox", false),
    (2, "fifo", false),
    (3, "fifo_relaxed", false),
    (1000111000, "shared_demand_refresh", true),
    (1000111001, "shared_continuous_refresh", true),
    (1000361000, "fifo_latest_ready", true),
];

const COMPOSITE_ALPHAS: [(u32, &str, bool); 4] = [
    (1, "opaque", false),
    (2, "pre_multiplied", true),
    (4, "post_multiplied", true),
    (8, "inherit", true),
];

#[derive(Clone, Copy)]
pub(crate) struct PresentFacts {
    pub(crate) extended: bool,
}

#[derive(Clone, Copy)]
pub(crate) struct AlphaFacts {
    pub(crate) blends: bool,
}

fn unknown_display(prefix: &str, value: u32) -> String {
    format!("{}{}", prefix, value)
}

fn parse_unknown(prefix: &str, text: &str) -> Option<u32> {
    text.strip_prefix(prefix)
        .and_then(|raw| raw.parse::<u32>().ok())
}

fn present_row(value: u32) -> Option<(u32, &'static str, bool)> {
    PRESENT_MODES.iter().copied().find(|(known, _, _)| *known == value)
}

fn alpha_row(value: u32) -> Option<(u32, &'static str, bool)> {
    COMPOSITE_ALPHAS.iter().copied().find(|(known, _, _)| *known == value)
}

pub(crate) fn present_display(value: u32) -> String {
    match present_row(value) {
        Some((_, name, _)) => name.to_string(),
        None => unknown_display(PRESENT_UNKNOWN_PREFIX, value),
    }
}

pub(crate) fn present_parse(text: &str) -> Option<u32> {
    match PRESENT_MODES.iter().find(|(_, name, _)| *name == text) {
        Some((value, _, _)) => Some(*value),
        None => parse_unknown(PRESENT_UNKNOWN_PREFIX, text),
    }
}

pub(crate) fn present_semantic(value: u32) -> Option<PresentFacts> {
    present_row(value).map(|(_, _, extended)| PresentFacts { extended })
}

pub(crate) fn alpha_display(value: u32) -> String {
    match alpha_row(value) {
        Some((_, name, _)) => name.to_string(),
        None => unknown_display(ALPHA_UNKNOWN_PREFIX, value),
    }
}

pub(crate) fn alpha_parse(text: &str) -> Option<u32> {
    match COMPOSITE_ALPHAS.iter().find(|(_, name, _)| *name == text) {
        Some((value, _, _)) => Some(*value),
        None => parse_unknown(ALPHA_UNKNOWN_PREFIX, text),
    }
}

pub(crate) fn alpha_semantic(value: u32) -> Option<AlphaFacts> {
    alpha_row(value).map(|(_, _, blends)| AlphaFacts { blends })
}
