use ash::vk;

use crate::consts::DEPTH_SUFFIX;
use crate::consts::PRESENT_ORDER;
use crate::consts::RED_MARK;
use crate::consts::UNKNOWN_PREFIX;

fn only_digits(raw: &str) -> String {
    raw.chars().filter(|c| c.is_ascii_digit()).collect()
}

fn normalized(raw: String) -> String {
    match raw.contains('(') {
        true => format!("{}{}", UNKNOWN_PREFIX, only_digits(&raw)),
        false => raw,
    }
}

fn leading_digits(text: &str) -> String {
    text.chars().take_while(|c| c.is_ascii_digit()).collect()
}

fn red_channel_bits(name: &str) -> Option<u32> {
    name.match_indices(RED_MARK)
        .map(|(at, _)| leading_digits(&name[at + 1..]))
        .find(|found| !found.is_empty())
        .and_then(|found| found.parse::<u32>().ok())
}

pub(crate) fn present_name(mode: vk::PresentModeKHR) -> String {
    normalized(format!("{:?}", mode).to_lowercase())
}

pub(crate) fn present_rank_of(name: &str) -> u32 {
    PRESENT_ORDER
        .iter()
        .position(|known| *known == name)
        .map(|at| at as u32)
        .unwrap_or(PRESENT_ORDER.len() as u32)
}

pub(crate) fn present_rank(mode: vk::PresentModeKHR) -> u32 {
    present_rank_of(&present_name(mode))
}

pub(crate) fn format_name(format: vk::Format) -> String {
    normalized(format!("{:?}", format).to_lowercase())
}

pub(crate) fn depth_rank(f: &vk::SurfaceFormatKHR) -> u32 {
    red_channel_bits(&format_name(f.format)).unwrap_or(0)
}

pub(crate) fn depth_label(bits: u32) -> String {
    format!("{}{}", bits, DEPTH_SUFFIX)
}

pub(crate) fn parse_depth_label(text: &str) -> Option<u32> {
    text.strip_suffix(DEPTH_SUFFIX)
        .and_then(|bits| bits.parse::<u32>().ok())
}
