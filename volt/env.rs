use std::env;

use crate::consts::DEFAULT_PROFILE;
use crate::consts::ENV_CONFIG_NAME;
use crate::consts::ENV_LOG;
use crate::consts::ENV_PROBE;

fn read_var(key: &str) -> Option<String> {
    env::var(key).ok().filter(|v| !v.is_empty())
}

pub(crate) fn env_string(key: &str, default: &str) -> String {
    read_var(key).unwrap_or_else(|| default.into())
}

pub(crate) fn env_log_level() -> String {
    env_string(ENV_LOG, "warn")
}

pub(crate) fn env_config_name() -> String {
    env_string(ENV_CONFIG_NAME, DEFAULT_PROFILE)
}

pub(crate) fn env_probe_active() -> bool {
    read_var(ENV_PROBE).is_some()
}

pub(crate) fn env_home() -> String {
    env::var("HOME").unwrap_or_else(|_| "/tmp".into())
}

pub fn process_args() -> Vec<String> {
    env::args().skip(1).collect()
}
