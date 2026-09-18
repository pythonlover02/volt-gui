use std::fs;
use std::path::PathBuf;
use std::sync::OnceLock;

use ash::vk;

use crate::consts::ANISO_OFF;
use crate::consts::CADENCE_DYNAMIC;
use crate::consts::CADENCE_FIXED;
use crate::consts::CADENCE_SMOOTH;
use crate::consts::CadenceChoice;
use crate::consts::DEFAULT_PROFILE;
use crate::consts::FILTER_LINEAR;
use crate::consts::FILTER_NEAREST;
use crate::consts::FRAME_LIMIT_MIN;
use crate::consts::FRAME_LIMIT_OFFSET_MAX;
use crate::consts::HOME_FALLBACK;
use crate::consts::KEY_ALPHA_TO_COVERAGE;
use crate::consts::KEY_ALPHA_TO_ONE;
use crate::consts::KEY_ANISOTROPY;
use crate::consts::KEY_CLIPPED;
use crate::consts::KEY_COMPOSITE_ALPHA;
use crate::consts::KEY_DEPTH_CLAMP;
use crate::consts::KEY_DEVICE;
use crate::consts::KEY_FRAME_LIMIT;
use crate::consts::KEY_FRAME_LIMIT_CADENCE;
use crate::consts::KEY_FRAME_LIMIT_METHOD;
use crate::consts::KEY_FRAME_LIMIT_OFFSET;
use crate::consts::KEY_FRAME_PACING;
use crate::consts::KEY_IMAGE_COUNT;
use crate::consts::KEY_LOD_BIAS;
use crate::consts::KEY_MAG_FILTER;
use crate::consts::KEY_MIN_FILTER;
use crate::consts::KEY_MIPMAP_MODE;
use crate::consts::KEY_MIP_CEILING;
use crate::consts::KEY_MIP_FLOOR;
use crate::consts::KEY_PRESENT_MODE;
use crate::consts::KEY_SAMPLE_SHADING;
use crate::consts::LOG_INVALID_PROFILE;
use crate::consts::NAME_DEFAULT;
use crate::consts::NAME_EMPTY;
use crate::consts::HOME_UNSET_WARN;
use crate::consts::METHOD_EARLY;
use crate::consts::METHOD_LATE;
use crate::consts::METHOD_REACTIVE;
use crate::consts::MethodChoice;
use crate::consts::MIPMAP_LINEAR;
use crate::consts::MIPMAP_NEAREST;
use crate::consts::PACING_PRECISE;
use crate::consts::PACING_SLEEP;
use crate::consts::PACING_SLICED;
use crate::consts::PACING_SPIN;
use crate::consts::PacingChoice;
use crate::consts::RESERVED_PROFILES;
use crate::consts::SECTION_DISPLAY;
use crate::consts::SECTION_FRAMERATE;
use crate::consts::SECTION_GPU;
use crate::consts::SECTION_RENDERING;
use crate::consts::SECTION_TEXTURES;
use crate::consts::SETTINGS_FROZEN_INFO;
use crate::consts::SHADING_MAX;
use crate::consts::SHADING_OFF;
use crate::consts::TEXT_LINEAR;
use crate::consts::TEXT_NEAREST;
use crate::consts::TEXT_OFF;
use crate::consts::TEXT_ON;
use crate::consts::TOGGLE_OFF;
use crate::consts::TOGGLE_ON;
use crate::env::env_config_name;
use crate::env::env_home;
use crate::logging::init_log_level;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::ranks::alpha_parse;
use crate::ranks::present_parse;

#[derive(Default)]
pub(crate) struct Settings {
    pub(crate) gpu: Option<u32>,
    pub(crate) present_mode: Option<vk::PresentModeKHR>,
    pub(crate) image_count: Option<u32>,
    pub(crate) composite_alpha: Option<vk::CompositeAlphaFlagsKHR>,
    pub(crate) clipped: Option<vk::Bool32>,
    pub(crate) mag_filter: Option<vk::Filter>,
    pub(crate) min_filter: Option<vk::Filter>,
    pub(crate) mipmap: Option<vk::SamplerMipmapMode>,
    pub(crate) anisotropy: Option<f32>,
    pub(crate) lod_bias: Option<f32>,
    pub(crate) mip_floor: Option<f32>,
    pub(crate) mip_ceiling: Option<f32>,
    pub(crate) sample_shading: Option<f32>,
    pub(crate) alpha_coverage: Option<vk::Bool32>,
    pub(crate) alpha_to_one: Option<vk::Bool32>,
    pub(crate) depth_clamp: Option<vk::Bool32>,
    pub(crate) frame_limit: Option<f32>,
    pub(crate) frame_limit_offset: Option<f32>,
    pub(crate) cadence: Option<CadenceChoice>,
    pub(crate) limit_method: Option<MethodChoice>,
    pub(crate) pacing: Option<PacingChoice>,
}

static SETTINGS: OnceLock<Settings> = OnceLock::new();

fn table_value<'a>(doc: &'a toml::Table, section: &str, key: &str) -> Option<&'a str> {
    doc.get(section)
        .and_then(|v| v.as_table())
        .and_then(|t| t.get(key))
        .and_then(|v| v.as_str())
}

fn non_default(text: &str) -> Option<&str> {
    match text {
        NAME_DEFAULT | NAME_EMPTY => None,
        other => Some(other),
    }
}

pub(crate) fn parse_float(text: &str) -> Option<f32> {
    text.parse::<f32>().ok().filter(|value| value.is_finite())
}

fn parse_uint(text: &str) -> Option<u32> {
    text.parse::<u32>().ok()
}

fn parse_filter(text: &str) -> Option<vk::Filter> {
    match text {
        TEXT_NEAREST => Some(vk::Filter::from_raw(FILTER_NEAREST)),
        TEXT_LINEAR => Some(vk::Filter::from_raw(FILTER_LINEAR)),
        _ => None,
    }
}

fn parse_mipmap(text: &str) -> Option<vk::SamplerMipmapMode> {
    match text {
        TEXT_NEAREST => Some(vk::SamplerMipmapMode::from_raw(MIPMAP_NEAREST)),
        TEXT_LINEAR => Some(vk::SamplerMipmapMode::from_raw(MIPMAP_LINEAR)),
        _ => None,
    }
}

fn parse_toggle(text: &str) -> Option<vk::Bool32> {
    match text {
        TEXT_OFF => Some(TOGGLE_OFF),
        TEXT_ON => Some(TOGGLE_ON),
        _ => None,
    }
}

fn parse_off_only(text: &str) -> Option<vk::Bool32> {
    match text {
        TEXT_OFF => Some(TOGGLE_OFF),
        _ => None,
    }
}

fn parse_aniso(text: &str) -> Option<f32> {
    match text {
        TEXT_OFF => Some(ANISO_OFF),
        other => parse_float(other).filter(|v| *v >= ANISO_OFF),
    }
}

fn parse_shading(text: &str) -> Option<f32> {
    match text {
        TEXT_OFF => Some(SHADING_OFF),
        other => parse_float(other).filter(|v| (SHADING_OFF..=SHADING_MAX).contains(v)),
    }
}

fn parse_limit(text: &str) -> Option<f32> {
    parse_float(text).filter(|v| *v >= FRAME_LIMIT_MIN)
}

fn parse_offset(text: &str) -> Option<f32> {
    parse_float(text).filter(|v| v.abs() <= FRAME_LIMIT_OFFSET_MAX)
}

fn parse_gpu(text: &str) -> Option<u32> {
    parse_uint(text).filter(|v| *v >= 1)
}

fn parse_cadence(text: &str) -> Option<CadenceChoice> {
    match text {
        CADENCE_FIXED => Some(CadenceChoice::Fixed),
        CADENCE_SMOOTH => Some(CadenceChoice::Smooth),
        CADENCE_DYNAMIC => Some(CadenceChoice::Dynamic),
        _ => None,
    }
}

fn parse_method(text: &str) -> Option<MethodChoice> {
    match text {
        METHOD_EARLY => Some(MethodChoice::Early),
        METHOD_LATE => Some(MethodChoice::Late),
        METHOD_REACTIVE => Some(MethodChoice::Reactive),
        _ => None,
    }
}

fn parse_pacing(text: &str) -> Option<PacingChoice> {
    match text {
        PACING_SLEEP => Some(PacingChoice::Sleep),
        PACING_SLICED => Some(PacingChoice::Sliced),
        PACING_PRECISE => Some(PacingChoice::Precise),
        PACING_SPIN => Some(PacingChoice::Spin),
        _ => None,
    }
}

pub(crate) struct Parsed {
    pub(crate) settings: Settings,
    pub(crate) warnings: Vec<String>,
}

fn checked<T>(
    warnings: &mut Vec<String>,
    section: &str,
    key: &str,
    text: &str,
    value: Option<T>,
) -> Option<T> {
    match value {
        Some(v) => Some(v),
        None => {
            warnings.push(format!(
                "{}.{} names \"{}\", which is not a value this build can read: that setting was left alone",
                section, key, text
            ));
            None
        }
    }
}

fn field<T, F>(
    doc: &toml::Table,
    warnings: &mut Vec<String>,
    section: &str,
    key: &str,
    parse: F,
) -> Option<T>
where
    F: Fn(&str) -> Option<T>,
{
    match table_value(doc, section, key).and_then(non_default) {
        None => None,
        Some(text) => checked(warnings, section, key, text, parse(text)),
    }
}

fn parse_doc(text: &str, warnings: &mut Vec<String>) -> toml::Table {
    match text.parse::<toml::Table>() {
        Ok(d) => d,
        Err(e) => {
            warnings.push(format!("config parse failed: {}, using defaults", e));
            toml::Table::new()
        }
    }
}

pub(crate) fn parse_settings(text: &str) -> Parsed {
    let mut warnings = Vec::new();
    let doc = parse_doc(text, &mut warnings);
    let settings = Settings {
        gpu: field(&doc, &mut warnings, SECTION_GPU, KEY_DEVICE, parse_gpu),
        present_mode: field(&doc, &mut warnings, SECTION_DISPLAY, KEY_PRESENT_MODE, present_parse),
        image_count: field(&doc, &mut warnings, SECTION_DISPLAY, KEY_IMAGE_COUNT, parse_uint),
        composite_alpha: field(&doc, &mut warnings, SECTION_DISPLAY, KEY_COMPOSITE_ALPHA, alpha_parse),
        clipped: field(&doc, &mut warnings, SECTION_DISPLAY, KEY_CLIPPED, parse_toggle),
        mag_filter: field(&doc, &mut warnings, SECTION_TEXTURES, KEY_MAG_FILTER, parse_filter),
        min_filter: field(&doc, &mut warnings, SECTION_TEXTURES, KEY_MIN_FILTER, parse_filter),
        mipmap: field(&doc, &mut warnings, SECTION_TEXTURES, KEY_MIPMAP_MODE, parse_mipmap),
        anisotropy: field(&doc, &mut warnings, SECTION_TEXTURES, KEY_ANISOTROPY, parse_aniso),
        lod_bias: field(&doc, &mut warnings, SECTION_TEXTURES, KEY_LOD_BIAS, parse_float),
        mip_floor: field(&doc, &mut warnings, SECTION_TEXTURES, KEY_MIP_FLOOR, parse_float),
        mip_ceiling: field(&doc, &mut warnings, SECTION_TEXTURES, KEY_MIP_CEILING, parse_float),
        sample_shading: field(&doc, &mut warnings, SECTION_RENDERING, KEY_SAMPLE_SHADING, parse_shading),
        alpha_coverage: field(&doc, &mut warnings, SECTION_RENDERING, KEY_ALPHA_TO_COVERAGE, parse_off_only),
        alpha_to_one: field(&doc, &mut warnings, SECTION_RENDERING, KEY_ALPHA_TO_ONE, parse_toggle),
        depth_clamp: field(&doc, &mut warnings, SECTION_RENDERING, KEY_DEPTH_CLAMP, parse_toggle),
        frame_limit: field(&doc, &mut warnings, SECTION_FRAMERATE, KEY_FRAME_LIMIT, parse_limit),
        frame_limit_offset: field(&doc, &mut warnings, SECTION_FRAMERATE, KEY_FRAME_LIMIT_OFFSET, parse_offset),
        cadence: field(&doc, &mut warnings, SECTION_FRAMERATE, KEY_FRAME_LIMIT_CADENCE, parse_cadence),
        limit_method: field(&doc, &mut warnings, SECTION_FRAMERATE, KEY_FRAME_LIMIT_METHOD, parse_method),
        pacing: field(&doc, &mut warnings, SECTION_FRAMERATE, KEY_FRAME_PACING, parse_pacing),
    };
    Parsed { settings, warnings }
}

fn reserved_name(raw: &str) -> bool {
    RESERVED_PROFILES
        .iter()
        .any(|name| raw.eq_ignore_ascii_case(name))
}

fn name_is_valid(raw: &str) -> bool {
    !raw.is_empty()
        && !raw.contains('/')
        && !raw.contains('\\')
        && !raw.contains("..")
        && !raw.contains('\0')
        && !reserved_name(raw)
        && raw.chars().all(|ch| ch.is_ascii_graphic())
}

fn folded_name(raw: &str) -> String {
    match raw.eq_ignore_ascii_case(DEFAULT_PROFILE) {
        true => DEFAULT_PROFILE.into(),
        false => raw.into(),
    }
}

pub(crate) fn sanitized_name(raw: &str) -> Option<String> {
    match name_is_valid(raw) {
        true => Some(folded_name(raw)),
        false => None,
    }
}

pub(crate) fn call_sanitize_name(raw: &str) -> String {
    match sanitized_name(raw) {
        Some(name) => name,
        None => {
            log_at(LogLevel::Warn, LOG_INVALID_PROFILE);
            DEFAULT_PROFILE.into()
        }
    }
}

fn call_fallback_home() -> String {
    log_at(LogLevel::Warn, HOME_UNSET_WARN);
    HOME_FALLBACK.into()
}

fn home_text() -> String {
    match env_home() {
        Some(path) => path,
        None => call_fallback_home(),
    }
}

pub(crate) fn home_dir() -> PathBuf {
    PathBuf::from(home_text())
}

pub(crate) fn config_dir() -> PathBuf {
    home_dir().join(".config").join("volt-gui")
}

pub(crate) fn profile_name() -> String {
    call_sanitize_name(&env_config_name())
}

pub(crate) fn config_path(name: &str) -> PathBuf {
    config_dir().join(format!("{}.toml", name))
}

fn call_logged_settings(parsed: Parsed) -> Settings {
    parsed
        .warnings
        .iter()
        .for_each(|warning| log_at(LogLevel::Warn, warning));
    parsed.settings
}

fn call_read_config(path: &PathBuf) -> Settings {
    match fs::read_to_string(path) {
        Ok(text) => call_logged_settings(parse_settings(&text)),
        Err(e) => {
            log_at(
                LogLevel::Warn,
                &format!("{}: {}, every setting left alone", path.display(), e),
            );
            Settings::default()
        }
    }
}

fn call_load_settings() -> Settings {
    init_log_level();
    let loaded = call_read_config(&config_path(&profile_name()));
    log_at(LogLevel::Info, SETTINGS_FROZEN_INFO);
    loaded
}

pub(crate) fn ensure_settings() -> &'static Settings {
    SETTINGS.get_or_init(call_load_settings)
}
