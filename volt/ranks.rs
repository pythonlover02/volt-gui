use crate::consts::ALPHA_UNKNOWN_PREFIX;
use crate::consts::DEPTH_SUFFIX;
use crate::consts::FORMAT_UNKNOWN_PREFIX;
use crate::consts::PRESENT_UNKNOWN_PREFIX;
use crate::consts::SPACE_UNKNOWN_PREFIX;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Numeric {
    Unorm,
    Srgb,
    Sfloat,
    Ufloat,
}

const PRESENT_MODES: [(u32, &str, bool); 7] = [
    (0, "immediate", false),
    (1, "mailbox", false),
    (2, "fifo", false),
    (3, "fifo_relaxed", false),
    (1000111000, "shared_demand_refresh", true),
    (1000111001, "shared_continuous_refresh", true),
    (1000361000, "fifo_latest_ready", true),
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

const COMPOSITE_ALPHAS: [(u32, &str, bool); 4] = [
    (1, "opaque", false),
    (2, "pre_multiplied", true),
    (4, "post_multiplied", true),
    (8, "inherit", true),
];

const FORMATS: [(u32, &str, u32, Numeric); 33] = [
    (2, "r4g4b4a4_unorm_pack16", 4, Numeric::Unorm),
    (3, "b4g4r4a4_unorm_pack16", 4, Numeric::Unorm),
    (4, "r5g6b5_unorm_pack16", 5, Numeric::Unorm),
    (5, "b5g6r5_unorm_pack16", 5, Numeric::Unorm),
    (6, "r5g5b5a1_unorm_pack16", 5, Numeric::Unorm),
    (7, "b5g5r5a1_unorm_pack16", 5, Numeric::Unorm),
    (8, "a1r5g5b5_unorm_pack16", 5, Numeric::Unorm),
    (23, "r8g8b8_unorm", 8, Numeric::Unorm),
    (29, "r8g8b8_srgb", 8, Numeric::Srgb),
    (30, "b8g8r8_unorm", 8, Numeric::Unorm),
    (36, "b8g8r8_srgb", 8, Numeric::Srgb),
    (37, "r8g8b8a8_unorm", 8, Numeric::Unorm),
    (43, "r8g8b8a8_srgb", 8, Numeric::Srgb),
    (44, "b8g8r8a8_unorm", 8, Numeric::Unorm),
    (50, "b8g8r8a8_srgb", 8, Numeric::Srgb),
    (51, "a8b8g8r8_unorm_pack32", 8, Numeric::Unorm),
    (57, "a8b8g8r8_srgb_pack32", 8, Numeric::Srgb),
    (58, "a2r10g10b10_unorm_pack32", 10, Numeric::Unorm),
    (64, "a2b10g10r10_unorm_pack32", 10, Numeric::Unorm),
    (84, "r16g16b16_unorm", 16, Numeric::Unorm),
    (90, "r16g16b16_sfloat", 16, Numeric::Sfloat),
    (91, "r16g16b16a16_unorm", 16, Numeric::Unorm),
    (97, "r16g16b16a16_sfloat", 16, Numeric::Sfloat),
    (106, "r32g32b32_sfloat", 32, Numeric::Sfloat),
    (109, "r32g32b32a32_sfloat", 32, Numeric::Sfloat),
    (118, "r64g64b64_sfloat", 64, Numeric::Sfloat),
    (121, "r64g64b64a64_sfloat", 64, Numeric::Sfloat),
    (122, "b10g11r11_ufloat_pack32", 11, Numeric::Ufloat),
    (123, "e5b9g9r9_ufloat_pack32", 9, Numeric::Ufloat),
    (1000340000, "a4r4g4b4_unorm_pack16", 4, Numeric::Unorm),
    (1000340001, "a4b4g4r4_unorm_pack16", 4, Numeric::Unorm),
    (1000470000, "a1b5g5r5_unorm_pack16", 5, Numeric::Unorm),
    (1000609011, "r14x2g14x2b14x2a14x2_unorm_4pack16_arm", 14, Numeric::Unorm),
];

const NUMERICS: [(Numeric, &str, bool); 4] = [
    (Numeric::Unorm, "unorm", false),
    (Numeric::Srgb, "srgb", true),
    (Numeric::Sfloat, "sfloat", false),
    (Numeric::Ufloat, "ufloat", false),
];

#[derive(Clone, Copy)]
pub(crate) struct PresentFacts {
    pub(crate) extended: bool,
}

#[derive(Clone, Copy)]
pub(crate) struct SpaceFacts {
    pub(crate) extended: bool,
}

#[derive(Clone, Copy)]
pub(crate) struct AlphaFacts {
    pub(crate) blends: bool,
}

#[derive(Clone, Copy)]
pub(crate) struct FormatFacts {
    pub(crate) depth: u32,
    pub(crate) numeric: Numeric,
}

#[derive(Clone, Copy)]
pub(crate) struct NumericFacts {
    pub(crate) encoded: bool,
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

fn space_row(value: u32) -> Option<(u32, &'static str, bool)> {
    COLOR_SPACES.iter().copied().find(|(known, _, _)| *known == value)
}

fn alpha_row(value: u32) -> Option<(u32, &'static str, bool)> {
    COMPOSITE_ALPHAS.iter().copied().find(|(known, _, _)| *known == value)
}

fn format_row(value: u32) -> Option<(u32, &'static str, u32, Numeric)> {
    FORMATS.iter().copied().find(|(known, _, _, _)| *known == value)
}

fn numeric_row(numeric: Numeric) -> Option<(Numeric, &'static str, bool)> {
    NUMERICS.iter().copied().find(|(known, _, _)| *known == numeric)
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

pub(crate) fn space_display(value: u32) -> String {
    match space_row(value) {
        Some((_, name, _)) => name.to_string(),
        None => unknown_display(SPACE_UNKNOWN_PREFIX, value),
    }
}

pub(crate) fn space_parse(text: &str) -> Option<u32> {
    match COLOR_SPACES.iter().find(|(_, name, _)| *name == text) {
        Some((value, _, _)) => Some(*value),
        None => parse_unknown(SPACE_UNKNOWN_PREFIX, text),
    }
}

pub(crate) fn space_semantic(value: u32) -> Option<SpaceFacts> {
    space_row(value).map(|(_, _, extended)| SpaceFacts { extended })
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

pub(crate) fn format_display(value: u32) -> String {
    match format_row(value) {
        Some((_, name, _, _)) => name.to_string(),
        None => unknown_display(FORMAT_UNKNOWN_PREFIX, value),
    }
}


pub(crate) fn format_semantic(value: u32) -> Option<FormatFacts> {
    format_row(value).map(|(_, _, depth, numeric)| FormatFacts { depth, numeric })
}

pub(crate) fn numeric_display(numeric: Numeric) -> String {
    match numeric_row(numeric) {
        Some((_, name, _)) => name.to_string(),
        None => String::new(),
    }
}

pub(crate) fn numeric_parse(text: &str) -> Option<Numeric> {
    match NUMERICS.iter().find(|(_, name, _)| *name == text) {
        Some((numeric, _, _)) => Some(*numeric),
        None => None,
    }
}

pub(crate) fn numeric_semantic(numeric: Numeric) -> Option<NumericFacts> {
    numeric_row(numeric).map(|(_, _, encoded)| NumericFacts { encoded })
}

pub(crate) fn depth_label(bits: u32) -> String {
    format!("{}{}", bits, DEPTH_SUFFIX)
}

pub(crate) fn parse_depth_label(text: &str) -> Option<u32> {
    text.strip_suffix(DEPTH_SUFFIX)
        .and_then(|bits| bits.parse::<u32>().ok())
}
