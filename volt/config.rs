use std::fs;
use std::path::PathBuf;
use std::sync::OnceLock;

use crate::bounds::ordered;
use crate::bounds::Bounds;
use crate::consts::DEFAULT_PROFILE;
use crate::consts::FILTER_BILINEAR;
use crate::consts::FILTER_RETRO;
use crate::consts::FILTER_TRILINEAR;
use crate::consts::FRAME_LIMIT_MIN;
use crate::consts::HOME_FALLBACK;
use crate::consts::HOME_UNSET_WARN;
use crate::consts::MethodChoice;
use crate::consts::MIPMAP_LINEAR;
use crate::consts::MIPMAP_NEAREST;
use crate::consts::PacingChoice;
use crate::consts::SECTION_DISPLAY;
use crate::consts::SECTION_FRAMERATE;
use crate::consts::SECTION_GPU;
use crate::consts::SECTION_RENDERING;
use crate::consts::SECTION_TEXTURES;
use crate::consts::SETTINGS_FROZEN_INFO;
use crate::consts::SUFFIX_MAX;
use crate::consts::SUFFIX_MIN;
use crate::consts::TOGGLE_OFF;
use crate::consts::TOGGLE_ON;
use crate::env::env_config_name;
use crate::env::env_home;
use crate::logging::init_log_level;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::ranks::alpha_parse;
use crate::ranks::alpha_semantic;
use crate::ranks::parse_depth_label;
use crate::ranks::present_parse;
use crate::ranks::present_semantic;
use crate::ranks::space_parse;
use crate::ranks::space_semantic;
use crate::ranks::transfer_parse;
use crate::ranks::transfer_semantic;

#[derive(Default)]
pub(crate) struct Settings {
    pub(crate) gpu: Bounds<u32>,
    pub(crate) present_mode: Bounds<u32>,
    pub(crate) image_count: Bounds<u32>,
    pub(crate) depth: Bounds<u32>,
    pub(crate) color_space: Bounds<u32>,
    pub(crate) transfer: Bounds<u32>,
    pub(crate) composite_alpha: Bounds<u32>,
    pub(crate) clipped: Bounds<u32>,
    pub(crate) filtering: Bounds<u32>,
    pub(crate) mipmap: Bounds<u32>,
    pub(crate) lod_bias: Bounds<f32>,
    pub(crate) mip_floor: Bounds<f32>,
    pub(crate) mip_ceiling: Bounds<f32>,
    pub(crate) alpha_coverage: Bounds<u32>,
    pub(crate) frame_limit: Option<f32>,
    pub(crate) limit_method: Option<MethodChoice>,
    pub(crate) pacing: Option<PacingChoice>,
}

static SETTINGS: OnceLock<Settings> = OnceLock::new();

fn table_value<'a>(doc: &'a toml::Value, section: &str, key: &str) -> Option<&'a str> {
    doc.as_table()
        .and_then(|t| t.get(section))
        .and_then(|v| v.as_table())
        .and_then(|t| t.get(key))
        .and_then(|v| v.as_str())
}

fn non_default(text: &str) -> Option<&str> {
    match text {
        "default" | "" => None,
        other => Some(other),
    }
}

fn parse_float(text: &str) -> Option<f32> {
    text.parse::<f32>().ok()
}

fn parse_uint(text: &str) -> Option<u32> {
    text.parse::<u32>().ok()
}

fn parse_present(text: &str) -> Option<u32> {
    present_parse(text)
        .and_then(present_semantic)
        .map(|facts| facts.rank)
}

fn parse_depth(text: &str) -> Option<u32> {
    parse_depth_label(text)
}

fn parse_space(text: &str) -> Option<u32> {
    space_parse(text)
        .and_then(space_semantic)
        .map(|facts| facts.rank)
}

fn parse_transfer(text: &str) -> Option<u32> {
    transfer_parse(text).map(|numeric| transfer_semantic(numeric).rank)
}

fn parse_alpha(text: &str) -> Option<u32> {
    alpha_parse(text)
        .and_then(alpha_semantic)
        .map(|facts| facts.rank)
}

fn parse_filter(text: &str) -> Option<u32> {
    match text {
        "retro" => Some(FILTER_RETRO),
        "bilinear" => Some(FILTER_BILINEAR),
        "trilinear" => Some(FILTER_TRILINEAR),
        _ => None,
    }
}

fn parse_mipmap(text: &str) -> Option<u32> {
    match text {
        "nearest" => Some(MIPMAP_NEAREST),
        "linear" => Some(MIPMAP_LINEAR),
        _ => None,
    }
}

fn parse_toggle(text: &str) -> Option<u32> {
    match text {
        "off" => Some(TOGGLE_OFF),
        "on" => Some(TOGGLE_ON),
        _ => None,
    }
}

fn parse_limit(text: &str) -> Option<f32> {
    parse_float(text).filter(|v| *v >= FRAME_LIMIT_MIN)
}

fn parse_gpu(text: &str) -> Option<u32> {
    parse_uint(text).filter(|v| *v >= 1)
}

fn parse_method(text: &str) -> Option<MethodChoice> {
    match text {
        "early" => Some(MethodChoice::Early),
        "late" => Some(MethodChoice::Late),
        "reactive" => Some(MethodChoice::Reactive),
        _ => None,
    }
}

fn parse_pacing(text: &str) -> Option<PacingChoice> {
    match text {
        "sleep" => Some(PacingChoice::Sleep),
        "sliced" => Some(PacingChoice::Sliced),
        "precise" => Some(PacingChoice::Precise),
        "spin" => Some(PacingChoice::Spin),
        _ => None,
    }
}

fn checked<T>(section: &str, key: &str, value: Option<T>) -> Option<T> {
    match value {
        Some(v) => Some(v),
        None => {
            log_at(
                LogLevel::Warn,
                &format!("invalid value for {}.{}, keeping default", section, key),
            );
            None
        }
    }
}

fn field<T, F>(doc: &toml::Value, section: &str, key: &str, parse: F) -> Option<T>
where
    F: Fn(&str) -> Option<T>,
{
    match table_value(doc, section, key).and_then(non_default) {
        None => None,
        Some(text) => checked(section, key, parse(text)),
    }
}

fn checked_bounds<T: PartialOrd + Copy>(section: &str, key: &str, b: Bounds<T>) -> Bounds<T> {
    match ordered(b.min, b.max) {
        true => b,
        false => {
            log_at(
                LogLevel::Warn,
                &format!("{}.{} minimum is above its maximum, ignoring both", section, key),
            );
            Bounds { min: None, max: None, ..b }
        }
    }
}

fn bounds_field<T, F>(doc: &toml::Value, section: &str, key: &str, parse: F) -> Bounds<T>
where
    T: PartialOrd + Copy,
    F: Fn(&str) -> Option<T>,
{
    checked_bounds(
        section,
        key,
        Bounds {
            force: field(doc, section, key, &parse),
            min: field(doc, section, &format!("{}{}", key, SUFFIX_MIN), &parse),
            max: field(doc, section, &format!("{}{}", key, SUFFIX_MAX), &parse),
        },
    )
}

fn parse_doc(text: &str) -> toml::Value {
    match text.parse::<toml::Value>() {
        Ok(d) => d,
        Err(e) => {
            log_at(
                LogLevel::Warn,
                &format!("config parse failed: {}, using defaults", e),
            );
            toml::Value::Table(toml::map::Map::new())
        }
    }
}

pub(crate) fn parse_settings(text: &str) -> Settings {
    let doc = parse_doc(text);
    Settings {
        gpu: bounds_field(&doc, SECTION_GPU, "device", parse_gpu),
        present_mode: bounds_field(&doc, SECTION_DISPLAY, "present_mode", parse_present),
        image_count: bounds_field(&doc, SECTION_DISPLAY, "image_count", parse_uint),
        depth: bounds_field(&doc, SECTION_DISPLAY, "color_depth", parse_depth),
        color_space: bounds_field(&doc, SECTION_DISPLAY, "color_space", parse_space),
        transfer: bounds_field(&doc, SECTION_DISPLAY, "transfer_function", parse_transfer),
        composite_alpha: bounds_field(&doc, SECTION_DISPLAY, "composite_alpha", parse_alpha),
        clipped: bounds_field(&doc, SECTION_DISPLAY, "clipped", parse_toggle),
        filtering: bounds_field(&doc, SECTION_TEXTURES, "filtering", parse_filter),
        mipmap: bounds_field(&doc, SECTION_TEXTURES, "mipmap_mode", parse_mipmap),
        lod_bias: bounds_field(&doc, SECTION_TEXTURES, "lod_bias", parse_float),
        mip_floor: bounds_field(&doc, SECTION_TEXTURES, "mip_floor", parse_float),
        mip_ceiling: bounds_field(&doc, SECTION_TEXTURES, "mip_ceiling", parse_float),
        alpha_coverage: bounds_field(&doc, SECTION_RENDERING, "alpha_to_coverage", parse_toggle),
        frame_limit: field(&doc, SECTION_FRAMERATE, "frame_limit", parse_limit),
        limit_method: field(&doc, SECTION_FRAMERATE, "frame_limit_method", parse_method),
        pacing: field(&doc, SECTION_FRAMERATE, "frame_pacing", parse_pacing),
    }
}

fn name_is_valid(raw: &str) -> bool {
    !raw.is_empty()
        && !raw.contains('/')
        && !raw.contains('\\')
        && !raw.contains("..")
        && !raw.contains('\0')
        && raw.chars().all(|ch| ch.is_ascii_graphic())
}

pub(crate) fn sanitize_name(raw: &str) -> String {
    match name_is_valid(raw) {
        true => raw.into(),
        false => {
            log_at(LogLevel::Warn, "invalid profile name, using default profile");
            DEFAULT_PROFILE.into()
        }
    }
}

fn fallback_home() -> String {
    log_at(LogLevel::Warn, HOME_UNSET_WARN);
    HOME_FALLBACK.into()
}

fn home_text() -> String {
    match env_home() {
        Some(path) => path,
        None => fallback_home(),
    }
}

pub(crate) fn home_dir() -> PathBuf {
    PathBuf::from(home_text())
}

pub(crate) fn config_dir() -> PathBuf {
    home_dir().join(".config").join("volt-gui")
}

pub(crate) fn profile_name() -> String {
    sanitize_name(&env_config_name())
}

pub(crate) fn config_path(name: &str) -> PathBuf {
    config_dir().join(format!("{}.toml", name))
}

fn read_config(path: &PathBuf) -> Settings {
    fs::read_to_string(path)
        .map(|t| parse_settings(&t))
        .unwrap_or_default()
}

fn load_settings() -> Settings {
    init_log_level();
    let loaded = read_config(&config_path(&profile_name()));
    log_at(LogLevel::Info, SETTINGS_FROZEN_INFO);
    loaded
}

pub(crate) fn ensure_settings() -> &'static Settings {
    SETTINGS.get_or_init(load_settings)
}
