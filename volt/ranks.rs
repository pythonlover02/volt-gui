use crate::consts::DEPTH_SUFFIX;
use crate::consts::UNKNOWN_PREFIX;

const PRESENT_MODES: [(u32, &str); 7] = [
    (0, "immediate"),
    (1, "mailbox"),
    (2, "fifo"),
    (3, "fifo_relaxed"),
    (1000111000, "shared_demand_refresh"),
    (1000111001, "shared_continuous_refresh"),
    (1000361000, "fifo_latest_ready"),
];

const COLOR_SPACES: [(u32, &str, bool); 16] = [
    (0, "srgb_nonlinear", false),
    (1000104001, "display_p3_nonlinear", true),
    (1000104002, "extended_srgb_linear", true),
    (1000104003, "display_p3_linear", true),
    (1000104004, "dci_p3_nonlinear", true),
    (1000104005, "bt709_linear", true),
    (1000104006, "bt709_nonlinear", true),
    (1000104007, "bt2020_linear", true),
    (1000104008, "hdr10_st2084", true),
    (1000104009, "dolbyvision", true),
    (1000104010, "hdr10_hlg", true),
    (1000104011, "adobergb_linear", true),
    (1000104012, "adobergb_nonlinear", true),
    (1000104013, "pass_through", true),
    (1000104014, "extended_srgb_nonlinear", true),
    (1000213000, "display_native_amd", true),
];

const COMPOSITE_ALPHAS: [(u32, &str); 4] = [
    (1, "opaque"),
    (2, "pre_multiplied"),
    (4, "post_multiplied"),
    (8, "inherit"),
];

const FORMATS: [(u32, u32, Numeric); 12] = [
    (4, 5, Numeric::Unorm),
    (5, 5, Numeric::Unorm),
    (37, 8, Numeric::Unorm),
    (43, 8, Numeric::Srgb),
    (44, 8, Numeric::Unorm),
    (50, 8, Numeric::Srgb),
    (51, 8, Numeric::Unorm),
    (57, 8, Numeric::Srgb),
    (58, 10, Numeric::Unorm),
    (64, 10, Numeric::Unorm),
    (91, 16, Numeric::Unorm),
    (97, 16, Numeric::Sfloat),
];

const TRANSFER_UNORM: (&str, u32) = ("unorm", 4);
const TRANSFER_SRGB: (&str, u32) = ("srgb", 43);
const TRANSFER_SFLOAT: (&str, u32) = ("sfloat", 97);

const OPAQUE_ALPHA: u32 = 1;

#[derive(Clone, Copy, PartialEq, Eq)]
pub(crate) enum Numeric {
    Unorm,
    Srgb,
    Sfloat,
}

#[derive(Clone, Copy)]
pub(crate) struct PresentFacts {
    pub(crate) rank: u32,
}

#[derive(Clone, Copy)]
pub(crate) struct SpaceFacts {
    pub(crate) rank: u32,
    pub(crate) extended: bool,
}

#[derive(Clone, Copy)]
pub(crate) struct AlphaFacts {
    pub(crate) rank: u32,
    pub(crate) blends: bool,
}

#[derive(Clone, Copy)]
pub(crate) struct FormatFacts {
    pub(crate) depth: u32,
    pub(crate) numeric: Numeric,
}

#[derive(Clone, Copy)]
pub(crate) struct TransferFacts {
    pub(crate) rank: u32,
}

fn unknown_display(value: u32) -> String {
    format!("{}{}", UNKNOWN_PREFIX, value)
}

fn parse_unknown(text: &str) -> Option<u32> {
    text.strip_prefix(UNKNOWN_PREFIX)
        .and_then(|raw| raw.parse::<u32>().ok())
}

fn present_row(value: u32) -> Option<(u32, &'static str)> {
    PRESENT_MODES.iter().copied().find(|(known, _)| *known == value)
}

fn space_row(value: u32) -> Option<(u32, &'static str, bool)> {
    COLOR_SPACES.iter().copied().find(|(known, _, _)| *known == value)
}

fn alpha_row(value: u32) -> Option<(u32, &'static str)> {
    COMPOSITE_ALPHAS.iter().copied().find(|(known, _)| *known == value)
}

fn format_row(value: u32) -> Option<(u32, u32, Numeric)> {
    FORMATS.iter().copied().find(|(known, _, _)| *known == value)
}

fn transfer_row(numeric: Numeric) -> (&'static str, u32) {
    match numeric {
        Numeric::Unorm => TRANSFER_UNORM,
        Numeric::Srgb => TRANSFER_SRGB,
        Numeric::Sfloat => TRANSFER_SFLOAT,
    }
}

pub(crate) fn present_display(value: u32) -> String {
    match present_row(value) {
        Some((_, name)) => name.to_string(),
        None => unknown_display(value),
    }
}

pub(crate) fn present_parse(text: &str) -> Option<u32> {
    match PRESENT_MODES.iter().find(|(_, name)| *name == text) {
        Some((value, _)) => Some(*value),
        None => parse_unknown(text),
    }
}

pub(crate) fn present_semantic(value: u32) -> Option<PresentFacts> {
    present_row(value).map(|(rank, _)| PresentFacts { rank })
}

pub(crate) fn space_display(value: u32) -> String {
    match space_row(value) {
        Some((_, name, _)) => name.to_string(),
        None => unknown_display(value),
    }
}

pub(crate) fn space_parse(text: &str) -> Option<u32> {
    match COLOR_SPACES.iter().find(|(_, name, _)| *name == text) {
        Some((value, _, _)) => Some(*value),
        None => parse_unknown(text),
    }
}

pub(crate) fn space_semantic(value: u32) -> Option<SpaceFacts> {
    space_row(value).map(|(rank, _, extended)| SpaceFacts { rank, extended })
}

pub(crate) fn alpha_display(value: u32) -> String {
    match alpha_row(value) {
        Some((_, name)) => name.to_string(),
        None => unknown_display(value),
    }
}

pub(crate) fn alpha_parse(text: &str) -> Option<u32> {
    match COMPOSITE_ALPHAS.iter().find(|(_, name)| *name == text) {
        Some((value, _)) => Some(*value),
        None => parse_unknown(text),
    }
}

pub(crate) fn alpha_semantic(value: u32) -> Option<AlphaFacts> {
    alpha_row(value).map(|(rank, _)| AlphaFacts {
        rank,
        blends: rank != OPAQUE_ALPHA,
    })
}

pub(crate) fn format_semantic(value: u32) -> Option<FormatFacts> {
    format_row(value).map(|(_, depth, numeric)| FormatFacts { depth, numeric })
}

pub(crate) fn transfer_display(numeric: Numeric) -> String {
    transfer_row(numeric).0.to_string()
}

pub(crate) fn transfer_parse(text: &str) -> Option<Numeric> {
    match text {
        name if name == TRANSFER_UNORM.0 => Some(Numeric::Unorm),
        name if name == TRANSFER_SRGB.0 => Some(Numeric::Srgb),
        name if name == TRANSFER_SFLOAT.0 => Some(Numeric::Sfloat),
        _ => None,
    }
}

pub(crate) fn transfer_semantic(numeric: Numeric) -> TransferFacts {
    TransferFacts { rank: transfer_row(numeric).1 }
}

pub(crate) fn depth_label(bits: u32) -> String {
    format!("{}{}", bits, DEPTH_SUFFIX)
}

pub(crate) fn parse_depth_label(text: &str) -> Option<u32> {
    text.strip_suffix(DEPTH_SUFFIX)
        .and_then(|bits| bits.parse::<u32>().ok())
}
