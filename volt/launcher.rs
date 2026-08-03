use std::fs;
use std::os::unix::process::CommandExt;
use std::path::PathBuf;
use std::process::Command;

use crate::config::config_dir;
use crate::config::config_path;
use crate::config::sanitize_name;
use crate::consts::DEFAULT_CONFIG;
use crate::consts::DEFAULT_PROFILE;
use crate::consts::ENABLE_VALUE;
use crate::consts::ENV_CONFIG_NAME;
use crate::consts::ENV_ENABLE;
use crate::consts::EXIT_EXEC_FAILED;
use crate::consts::EXIT_OK;
use crate::consts::EXIT_USAGE;
use crate::consts::FLATPAK_CMD;
use crate::consts::FLATPAK_INJECT;
use crate::consts::ENV_PROBE;
use crate::consts::FLATPAK_RUN;
use crate::consts::PROBE_FLAG;
use crate::consts::PROBE_UNSET;
use crate::consts::USAGE;
use crate::logging::init_log_level;
use crate::logging::log_at;
use crate::logging::LogLevel;

fn is_help_flag(a: &str) -> bool {
    a == "--help" || a == "-h"
}

fn wants_help(args: &[String]) -> bool {
    args.iter().take_while(|a| **a != "--").any(|a| is_help_flag(a))
}

fn is_probe_flag(a: &str) -> bool {
    a == PROBE_FLAG
}

fn wants_probe(head: &[String]) -> bool {
    head.iter().any(|a| is_probe_flag(a))
}

fn is_flag(a: &str) -> bool {
    a.starts_with('-')
}

fn head_profile(head: &[String]) -> String {
    sanitize_name(
        head.iter()
            .find(|a| !is_flag(a))
            .map(String::as_str)
            .unwrap_or(DEFAULT_PROFILE),
    )
}

fn probe_value(probe: bool) -> &'static str {
    match probe {
        true => ENABLE_VALUE,
        false => PROBE_UNSET,
    }
}

fn split_args(args: &[String]) -> (Vec<String>, Vec<String>) {
    let pos = args.iter().position(|a| a == "--").unwrap_or(args.len());
    (
        args[..pos].to_vec(),
        args.get(pos + 1..).unwrap_or(&[]).to_vec(),
    )
}

fn is_flatpak_bin(name: &str) -> bool {
    name == FLATPAK_CMD || name.ends_with("/flatpak")
}

fn is_flatpak_run(cmd: &[String]) -> bool {
    cmd.first().map(|s| is_flatpak_bin(s)).unwrap_or(false)
        && cmd.iter().any(|a| a == FLATPAK_RUN)
}

fn flatpak_run_pos(cmd: &[String]) -> Option<usize> {
    cmd.iter().position(|a| a == FLATPAK_RUN)
}

fn flatpak_user_flags(cmd: &[String]) -> Vec<String> {
    flatpak_run_pos(cmd)
        .map(|pos| {
            cmd[pos + 1..]
                .iter()
                .take_while(|a| a.starts_with('-'))
                .cloned()
                .collect()
        })
        .unwrap_or_default()
}

fn flatpak_app_pos(cmd: &[String]) -> Option<usize> {
    flatpak_run_pos(cmd).and_then(|pos| {
        cmd[pos + 1..]
            .iter()
            .position(|a| !a.starts_with('-'))
            .map(|rel| pos + 1 + rel)
    })
}

fn flatpak_app_id(cmd: &[String]) -> Option<String> {
    flatpak_app_pos(cmd).map(|p| cmd[p].clone())
}

fn flatpak_trailing(cmd: &[String]) -> Vec<String> {
    flatpak_app_pos(cmd)
        .map(|p| cmd.get(p + 1..).unwrap_or(&[]).to_vec())
        .unwrap_or_default()
}

fn build_flatpak_args(
    profile: &str,
    app_id: &str,
    probe: bool,
    flags: &[String],
    trailing: &[String],
) -> Vec<String> {
    [
        vec![
            FLATPAK_RUN.to_string(),
            format!("--command={}", FLATPAK_INJECT),
            format!("--env={}={}", ENV_CONFIG_NAME, profile),
            format!("--env={}={}", ENV_PROBE, probe_value(probe)),
        ],
        flags.to_vec(),
        vec![app_id.to_string()],
        trailing.to_vec(),
    ]
    .concat()
}

fn write_default_config(path: &PathBuf) {
    let _ = fs::create_dir_all(config_dir());
    match path.exists() {
        true => (),
        false => {
            let _ = fs::write(path, DEFAULT_CONFIG);
        }
    }
}

fn exec_native(cmd: &[String], profile: &str, probe: bool) -> i32 {
    let err = Command::new(&cmd[0])
        .args(&cmd[1..])
        .env(ENV_ENABLE, ENABLE_VALUE)
        .env(ENV_CONFIG_NAME, profile)
        .env(ENV_PROBE, probe_value(probe))
        .exec();
    log_at(LogLevel::Error, &format!("exec failed: {}", err));
    EXIT_EXEC_FAILED
}

fn exec_flatpak(cmd: &[String], profile: &str, probe: bool) -> i32 {
    match flatpak_app_id(cmd) {
        None => {
            log_at(LogLevel::Error, "flatpak run: no app id found");
            EXIT_USAGE
        }
        Some(app_id) => {
            let args = build_flatpak_args(
                profile,
                &app_id,
                probe,
                &flatpak_user_flags(cmd),
                &flatpak_trailing(cmd),
            );
            let err = Command::new(FLATPAK_CMD).args(&args).exec();
            log_at(LogLevel::Error, &format!("exec failed: {}", err));
            EXIT_EXEC_FAILED
        }
    }
}

fn launch_cmd(head: &[String], cmd: &[String]) -> i32 {
    let profile = head_profile(head);
    write_default_config(&config_path(&profile));
    match is_flatpak_run(cmd) {
        true => exec_flatpak(cmd, &profile, wants_probe(head)),
        false => exec_native(cmd, &profile, wants_probe(head)),
    }
}

fn launch(args: Vec<String>) -> i32 {
    let (head, cmd) = split_args(&args);
    match cmd.is_empty() {
        true => {
            print!("{}", USAGE);
            EXIT_USAGE
        }
        false => launch_cmd(&head, &cmd),
    }
}

pub fn run_launcher(args: Vec<String>) -> i32 {
    init_log_level();
    match wants_help(&args) {
        true => {
            print!("{}", USAGE);
            EXIT_OK
        }
        false => launch(args),
    }
}
