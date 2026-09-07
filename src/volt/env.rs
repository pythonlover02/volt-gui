use std::env;

use crate::consts::DEFAULT_PROFILE;
use crate::consts::ENV_CONFIG_NAME;
use crate::consts::ENV_HOME;
use crate::consts::ENV_LIB_PATH;
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

pub(crate) fn env_home() -> Option<String> {
    read_var(ENV_HOME)
}

pub(crate) fn env_lib_path() -> Option<String> {
    read_var(ENV_LIB_PATH)
}

pub fn process_args() -> Vec<String> {
    env::args().skip(1).collect()
}
