use crate::logging::log_at;
use crate::logging::LogLevel;

pub(crate) struct Narrowed<T> {
    pub(crate) items: Vec<T>,
    pub(crate) restored: bool,
}

pub(crate) fn untouched<T>(items: Vec<T>) -> Narrowed<T> {
    Narrowed {
        items,
        restored: false,
    }
}

fn restored<T>(wanted: Vec<T>, rest: Vec<T>) -> Narrowed<T> {
    match wanted.is_empty() {
        true => Narrowed {
            items: rest,
            restored: true,
        },
        false => untouched(wanted),
    }
}

pub(crate) fn forced<T>(choice: Option<T>, original: T) -> T {
    match choice {
        Some(value) => value,
        None => original,
    }
}

pub(crate) fn kept<T, F>(items: Vec<T>, keep: F) -> Narrowed<T>
where
    F: Fn(&T) -> bool,
{
    let (wanted, rest): (Vec<T>, Vec<T>) = items.into_iter().partition(|item| keep(item));
    restored(wanted, rest)
}

pub(crate) fn filtered<T, V, F>(items: Vec<T>, choice: Option<V>, value_of: F) -> Narrowed<T>
where
    V: PartialEq + Copy,
    F: Fn(&T) -> Option<V>,
{
    match choice {
        Some(value) => kept(items, |item| value_of(item) == Some(value)),
        None => untouched(items),
    }
}

fn call_warn_restored(restored: bool, warn: &str) {
    match restored {
        true => log_at(LogLevel::Warn, warn),
        false => (),
    }
}

pub(crate) fn call_warned<T>(narrowed: Narrowed<T>, warn: &str) -> Vec<T> {
    call_warn_restored(narrowed.restored, warn);
    narrowed.items
}
