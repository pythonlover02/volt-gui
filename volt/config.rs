use std::fs;
use std::path::PathBuf;
use std::sync::OnceLock;

use crate::consts::ANISO_OFF;
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
use crate::consts::SHADING_MAX;
use crate::consts::SHADING_OFF;
use crate::consts::TOGGLE_OFF;
use crate::consts::TOGGLE_ON;
use crate::env::env_config_name;
use crate::env::env_home;
use crate::logging::init_log_level;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::ranks::alpha_parse;
use crate::ranks::numeric_parse;
use crate::ranks::parse_depth_label;
use crate::ranks::present_parse;
use crate::ranks::space_parse;
use crate::ranks::Numeric;

#[derive(Default)]
pub(crate) struct Settings {
    pub(crate) gpu: Option<u32>,
    pub(crate) present_mode: Option<u32>,
    pub(crate) image_count: Option<u32>,
    pub(crate) depth: Option<u32>,
    pub(crate) color_space: Option<u32>,
    pub(crate) transfer: Option<Numeric>,
    pub(crate) composite_alpha: Option<u32>,
    pub(crate) clipped: Option<u32>,
    pub(crate) filtering: Option<u32>,
    pub(crate) mipmap: Option<u32>,
    pub(crate) anisotropy: Option<f32>,
    pub(crate) lod_bias: Option<f32>,
    pub(crate) mip_floor: Option<f32>,
    pub(crate) mip_ceiling: Option<f32>,
    pub(crate) sample_shading: Option<f32>,
    pub(crate) alpha_coverage: Option<u32>,
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

fn parse_aniso(text: &str) -> Option<f32> {
    match text {
        "off" => Some(ANISO_OFF),
        other => parse_float(other).filter(|v| *v >= ANISO_OFF),
    }
}

fn parse_shading(text: &str) -> Option<f32> {
    match text {
        "off" => Some(SHADING_OFF),
        other => parse_float(other).filter(|v| (SHADING_OFF..=SHADING_MAX).contains(v)),
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

fn checked<T>(section: &str, key: &str, text: &str, value: Option<T>) -> Option<T> {
    match value {
        Some(v) => Some(v),
        None => {
            log_at(
                LogLevel::Warn,
                &format!(
                    "{}.{} names \"{}\", which is not a value this build can read: that setting was left alone",
                    section, key, text
                ),
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
        Some(text) => checked(section, key, text, parse(text)),
    }
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
        gpu: field(&doc, SECTION_GPU, "device", parse_gpu),
        present_mode: field(&doc, SECTION_DISPLAY, "present_mode", present_parse),
        image_count: field(&doc, SECTION_DISPLAY, "image_count", parse_uint),
        depth: field(&doc, SECTION_DISPLAY, "color_depth", parse_depth_label),
        color_space: field(&doc, SECTION_DISPLAY, "color_space", space_parse),
        transfer: field(&doc, SECTION_DISPLAY, "transfer_function", numeric_parse),
        composite_alpha: field(&doc, SECTION_DISPLAY, "composite_alpha", alpha_parse),
        clipped: field(&doc, SECTION_DISPLAY, "clipped", parse_toggle),
        filtering: field(&doc, SECTION_TEXTURES, "filtering", parse_filter),
        mipmap: field(&doc, SECTION_TEXTURES, "mipmap_mode", parse_mipmap),
        anisotropy: field(&doc, SECTION_TEXTURES, "anisotropy", parse_aniso),
        lod_bias: field(&doc, SECTION_TEXTURES, "lod_bias", parse_float),
        mip_floor: field(&doc, SECTION_TEXTURES, "mip_floor", parse_float),
        mip_ceiling: field(&doc, SECTION_TEXTURES, "mip_ceiling", parse_float),
        sample_shading: field(&doc, SECTION_RENDERING, "sample_shading", parse_shading),
        alpha_coverage: field(&doc, SECTION_RENDERING, "alpha_to_coverage", parse_toggle),
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
