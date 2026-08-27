use std::collections::HashMap;
use std::collections::HashSet;
use std::sync::RwLock;

use crate::consts::FILTER_LINEAR;
use crate::consts::FILTER_NEAREST;
use crate::consts::FILTER_UNKNOWN_PREFIX;
use crate::consts::MIPMAP_LINEAR;
use crate::consts::MIPMAP_NEAREST;
use crate::consts::MIPMAP_UNKNOWN_PREFIX;
use crate::consts::NOTE_NOT_ENABLED;
use crate::consts::NOTE_NOT_SET;
use crate::consts::REPORT_ASKED;
use crate::consts::REPORT_FORCED;
use crate::consts::REPORT_MARK;
use crate::consts::REPORT_NOTE;
use crate::consts::REPORT_SEP;
use crate::consts::TEXT_LINEAR;
use crate::consts::TEXT_NEAREST;
use crate::consts::TEXT_OFF;
use crate::consts::TEXT_ON;
use crate::consts::TOGGLE_ON;
use crate::logging::info_wanted;
use crate::logging::log_at;
use crate::logging::LogLevel;

pub(crate) type ReportMap = HashMap<u64, HashSet<&'static str>>;

static REPORTS: RwLock<Option<ReportMap>> = RwLock::new(None);

pub(crate) fn call_claim(
    store: &RwLock<Option<ReportMap>>,
    owner: u64,
    name: &'static str,
) -> bool {
    match store.write() {
        Ok(mut guard) => guard
            .get_or_insert_with(HashMap::new)
            .entry(owner)
            .or_insert_with(HashSet::new)
            .insert(name),
        Err(_) => false,
    }
}

pub(crate) fn call_forget(store: &RwLock<Option<ReportMap>>, owner: u64) {
    match store.write() {
        Ok(mut guard) => {
            guard.get_or_insert_with(HashMap::new).remove(&owner);
        }
        Err(_) => (),
    }
}

fn call_claim_report(owner: u64, name: &'static str) -> bool {
    call_claim(&REPORTS, owner, name)
}

pub(crate) fn call_forget_reports(owner: u64) {
    match info_wanted() {
        true => call_forget(&REPORTS, owner),
        false => (),
    }
}

fn labelled(label: &str, text: Option<String>) -> Option<String> {
    text.map(|value| format!("{}{}", label, value))
}

fn values(asked: Option<String>, forced: Option<String>) -> String {
    [labelled(REPORT_ASKED, asked), labelled(REPORT_FORCED, forced)]
        .into_iter()
        .flatten()
        .collect::<Vec<String>>()
        .join(REPORT_SEP)
}

fn noted(body: String, note: Option<String>) -> String {
    match (body.is_empty(), note) {
        (_, None) => body,
        (true, Some(text)) => text,
        (false, Some(text)) => format!("{}{}{}", body, REPORT_NOTE, text),
    }
}

pub(crate) fn report_line(
    name: &str,
    asked: Option<String>,
    forced: Option<String>,
    note: Option<String>,
) -> String {
    format!(
        "{}{}{}",
        name,
        REPORT_MARK,
        noted(values(asked, forced), note)
    )
}

pub(crate) fn call_report_setting(
    name: &str,
    asked: Option<String>,
    forced: Option<String>,
    note: Option<String>,
) {
    log_at(LogLevel::Info, &report_line(name, asked, forced, note));
}

pub(crate) fn feature_note(set: bool, held: bool, feature: &str) -> Option<String> {
    match (set, held) {
        (true, false) => Some(format!("{}{}", NOTE_NOT_ENABLED, feature)),
        (_, _) => None,
    }
}

fn missing_note(forced: &Option<String>) -> Option<String> {
    match forced {
        Some(_) => None,
        None => Some(NOTE_NOT_SET.into()),
    }
}

pub(crate) fn forced_text<T: Copy + PartialEq>(
    set: bool,
    asked: T,
    held: T,
    text: fn(T) -> String,
) -> Option<String> {
    match (set, asked == held) {
        (true, false) => Some(text(held)),
        (_, _) => None,
    }
}

pub(crate) fn call_report_value<T: Copy + PartialEq>(
    owner: u64,
    name: &'static str,
    set: bool,
    asked: T,
    held: T,
    text: fn(T) -> String,
    note: Option<String>,
) {
    match call_claim_report(owner, name) {
        true => call_report_setting(
            name,
            Some(text(asked)),
            forced_text(set, asked, held, text),
            note,
        ),
        false => (),
    }
}

pub(crate) fn call_report_choice(owner: u64, name: &'static str, forced: Option<String>) {
    let note = missing_note(&forced);
    match call_claim_report(owner, name) {
        true => call_report_setting(name, None, forced, note),
        false => (),
    }
}

pub(crate) fn call_report_reading(owner: u64, name: &'static str, asked: String) {
    match call_claim_report(owner, name) {
        true => call_report_setting(name, Some(asked), None, None),
        false => (),
    }
}

pub(crate) fn number_text(value: f32) -> String {
    format!("{}", value)
}

pub(crate) fn count_text(value: u32) -> String {
    value.to_string()
}

pub(crate) fn toggle_text(value: u32) -> String {
    match value {
        TOGGLE_ON => TEXT_ON.into(),
        _ => TEXT_OFF.into(),
    }
}

pub(crate) fn filter_text(value: u32) -> String {
    match value {
        FILTER_NEAREST => TEXT_NEAREST.into(),
        FILTER_LINEAR => TEXT_LINEAR.into(),
        other => format!("{}{}", FILTER_UNKNOWN_PREFIX, other),
    }
}

pub(crate) fn mipmap_text(value: u32) -> String {
    match value {
        MIPMAP_NEAREST => TEXT_NEAREST.into(),
        MIPMAP_LINEAR => TEXT_LINEAR.into(),
        other => format!("{}{}", MIPMAP_UNKNOWN_PREFIX, other),
    }
}
