use std::fs;
use std::path::PathBuf;
use std::sync::Once;
use std::sync::RwLock;

use crate::consts::AnisoChoice;
use crate::consts::ANISO_MIN;
use crate::consts::DEFAULT_PROFILE;
use crate::consts::DepthChoice;
use crate::consts::FilterChoice;
use crate::consts::FRAME_LIMIT_MIN;
use crate::consts::MethodChoice;
use crate::consts::MipmapChoice;
use crate::consts::PresentChoice;
use crate::consts::PacingChoice;
use crate::consts::SECTION_DISPLAY;
use crate::consts::SECTION_FRAMERATE;
use crate::consts::SECTION_GPU;
use crate::consts::SECTION_RENDERING;
use crate::consts::SECTION_TEXTURES;
use crate::consts::ShadingChoice;
use crate::consts::SHADING_MAX;
use crate::env::env_config_name;
use crate::env::env_home;
use crate::logging::init_log_level;
use crate::logging::log_at;
use crate::logging::LogLevel;
use crate::watch::setup_watch;

#[derive(Clone, Default)]
pub(crate) struct Settings {
    pub(crate) present_mode: Option<PresentChoice>,
    pub(crate) frame_limit: Option<f32>,
    pub(crate) gpu: Option<u32>,
    pub(crate) limit_method: Option<MethodChoice>,
    pub(crate) pacing: Option<PacingChoice>,
    pub(crate) depth: Option<DepthChoice>,
    pub(crate) image_count: Option<u32>,
    pub(crate) image_count_min: Option<u32>,
    pub(crate) image_count_max: Option<u32>,
    pub(crate) filtering: Option<FilterChoice>,
    pub(crate) mipmap: Option<MipmapChoice>,
    pub(crate) anisotropy: Option<AnisoChoice>,
    pub(crate) lod_bias: Option<f32>,
    pub(crate) lod_bias_min: Option<f32>,
    pub(crate) lod_bias_max: Option<f32>,
    pub(crate) lod_min: Option<f32>,
    pub(crate) lod_max: Option<f32>,
    pub(crate) sample_shading: Option<ShadingChoice>,
}

static SETTINGS: RwLock<Option<Settings>> = RwLock::new(None);
static INIT: Once = Once::new();

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

fn parse_present(text: &str) -> Option<PresentChoice> {
    match text {
        "fifo" => Some(PresentChoice::Fifo),
        "fifo_relaxed" => Some(PresentChoice::FifoRelaxed),
        "mailbox" => Some(PresentChoice::Mailbox),
        "immediate" => Some(PresentChoice::Immediate),
        _ => None,
    }
}

fn parse_filter(text: &str) -> Option<FilterChoice> {
    match text {
        "retro" => Some(FilterChoice::Retro),
        "bilinear" => Some(FilterChoice::Bilinear),
        "trilinear" => Some(FilterChoice::Trilinear),
        _ => None,
    }
}

fn parse_mipmap(text: &str) -> Option<MipmapChoice> {
    match text {
        "nearest" => Some(MipmapChoice::Nearest),
        "linear" => Some(MipmapChoice::Linear),
        _ => None,
    }
}

fn parse_aniso(text: &str) -> Option<AnisoChoice> {
    match text {
        "off" => Some(AnisoChoice::Off),
        other => parse_float(other)
            .filter(|v| *v >= ANISO_MIN)
            .map(AnisoChoice::Level),
    }
}

fn parse_shading(text: &str) -> Option<ShadingChoice> {
    match text {
        "off" => Some(ShadingChoice::Off),
        other => parse_float(other)
            .filter(|v| (0.0..=SHADING_MAX).contains(v))
            .map(ShadingChoice::Rate),
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
        _ => None,
    }
}

fn parse_pacing(text: &str) -> Option<PacingChoice> {
    match text {
        "sleep" => Some(PacingChoice::Sleep),
        "precise" => Some(PacingChoice::Precise),
        _ => None,
    }
}

fn parse_depth(text: &str) -> Option<DepthChoice> {
    match text {
        "10bit" => Some(DepthChoice::TenBit),
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
        present_mode: field(&doc, SECTION_DISPLAY, "present_mode", parse_present),
        frame_limit: field(&doc, SECTION_FRAMERATE, "frame_limit", parse_limit),
        gpu: field(&doc, SECTION_GPU, "device", parse_gpu),
        limit_method: field(&doc, SECTION_FRAMERATE, "frame_limit_method", parse_method),
        pacing: field(&doc, SECTION_FRAMERATE, "frame_pacing", parse_pacing),
        depth: field(&doc, SECTION_DISPLAY, "color_depth", parse_depth),
        image_count: field(&doc, SECTION_DISPLAY, "image_count", parse_uint),
        image_count_min: field(&doc, SECTION_DISPLAY, "image_count_min", parse_uint),
        image_count_max: field(&doc, SECTION_DISPLAY, "image_count_max", parse_uint),
        filtering: field(&doc, SECTION_TEXTURES, "filtering", parse_filter),
        mipmap: field(&doc, SECTION_TEXTURES, "mipmap_mode", parse_mipmap),
        anisotropy: field(&doc, SECTION_TEXTURES, "anisotropy", parse_aniso),
        lod_bias: field(&doc, SECTION_TEXTURES, "lod_bias", parse_float),
        lod_bias_min: field(&doc, SECTION_TEXTURES, "lod_bias_min", parse_float),
        lod_bias_max: field(&doc, SECTION_TEXTURES, "lod_bias_max", parse_float),
        lod_min: field(&doc, SECTION_TEXTURES, "lod_min", parse_float),
        lod_max: field(&doc, SECTION_TEXTURES, "lod_max", parse_float),
        sample_shading: field(&doc, SECTION_RENDERING, "sample_shading", parse_shading),
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

pub(crate) fn home_dir() -> PathBuf {
    PathBuf::from(env_home())
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

pub(crate) fn read_config(path: &PathBuf) -> Settings {
    fs::read_to_string(path)
        .map(|t| parse_settings(&t))
        .unwrap_or_default()
}

pub(crate) fn store_settings(s: Settings) {
    match SETTINGS.write() {
        Ok(mut g) => *g = Some(s),
        Err(_) => (),
    }
}

pub(crate) fn load_settings() -> Settings {
    init_log_level();
    let s = read_config(&config_path(&profile_name()));
    store_settings(s.clone());
    setup_watch();
    log_at(LogLevel::Info, "settings loaded");
    s
}

pub(crate) fn ensure_settings() -> Settings {
    INIT.call_once(|| {
        load_settings();
    });
    SETTINGS
        .read()
        .ok()
        .and_then(|g| g.clone())
        .unwrap_or_else(|| load_settings())
}
