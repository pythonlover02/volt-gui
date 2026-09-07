use crate::logging::log_at;
use crate::logging::LogLevel;

fn restored<T>(wanted: Vec<T>, rest: Vec<T>, warn: &str) -> Vec<T> {
    match wanted.is_empty() {
        true => {
            log_at(LogLevel::Warn, warn);
            rest
        }
        false => wanted,
    }
}

pub(crate) fn forced<T>(choice: Option<T>, original: T) -> T {
    match choice {
        Some(value) => value,
        None => original,
    }
}

pub(crate) fn kept<T, F>(items: Vec<T>, keep: F, warn: &str) -> Vec<T>
where
    F: Fn(&T) -> bool,
{
    let (wanted, rest): (Vec<T>, Vec<T>) = items.into_iter().partition(|item| keep(item));
    restored(wanted, rest, warn)
}

pub(crate) fn filtered<T, V, F>(
    items: Vec<T>,
    choice: Option<V>,
    value_of: F,
    warn: &str,
) -> Vec<T>
where
    V: PartialEq + Copy,
    F: Fn(&T) -> Option<V>,
{
    match choice {
        Some(value) => kept(items, |item| value_of(item) == Some(value), warn),
        None => items,
    }
}
