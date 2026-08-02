use crate::logging::log_at;
use crate::logging::LogLevel;

#[derive(Clone, Copy, Default)]
pub(crate) struct Bounds<T> {
    pub(crate) force: Option<T>,
    pub(crate) min: Option<T>,
    pub(crate) max: Option<T>,
}

fn larger<T: PartialOrd>(a: T, b: T) -> T {
    match a < b {
        true => b,
        false => a,
    }
}

fn smaller<T: PartialOrd>(a: T, b: T) -> T {
    match a > b {
        true => b,
        false => a,
    }
}

fn floored<T: PartialOrd>(value: T, lower: Option<T>) -> T {
    match lower {
        Some(l) => larger(value, l),
        None => value,
    }
}

fn ceiled<T: PartialOrd>(value: T, upper: Option<T>) -> T {
    match upper {
        Some(u) => smaller(value, u),
        None => value,
    }
}

fn above_min<T: PartialOrd>(value: T, lower: Option<T>) -> bool {
    match lower {
        Some(l) => value >= l,
        None => true,
    }
}

fn below_max<T: PartialOrd>(value: T, upper: Option<T>) -> bool {
    match upper {
        Some(u) => value <= u,
        None => true,
    }
}

fn within<T: PartialOrd + Copy>(value: T, min: Option<T>, max: Option<T>) -> bool {
    above_min(value, min) && below_max(value, max)
}

fn restored<T>(wanted: Vec<T>, rest: Vec<T>, warn: &str) -> Vec<T> {
    match wanted.is_empty() {
        true => {
            log_at(LogLevel::Warn, warn);
            rest
        }
        false => wanted,
    }
}

pub(crate) fn bounds_set<T>(b: &Bounds<T>) -> bool {
    b.force.is_some() || b.min.is_some() || b.max.is_some()
}

pub(crate) fn ordered<T: PartialOrd + Copy>(min: Option<T>, max: Option<T>) -> bool {
    match (min, max) {
        (Some(l), Some(u)) => l <= u,
        (_, _) => true,
    }
}

pub(crate) fn resolved<T: PartialOrd + Copy>(b: Bounds<T>, original: T) -> T {
    match b.force {
        Some(v) => v,
        None => ceiled(floored(original, b.min), b.max),
    }
}

pub(crate) fn accepts<T: PartialOrd + Copy>(b: Bounds<T>, rank: T) -> bool {
    match b.force {
        Some(v) => v == rank,
        None => within(rank, b.min, b.max),
    }
}

pub(crate) fn kept<T, F>(items: Vec<T>, keep: F, warn: &str) -> Vec<T>
where
    F: Fn(&T) -> bool,
{
    let (wanted, rest): (Vec<T>, Vec<T>) = items.into_iter().partition(|item| keep(item));
    restored(wanted, rest, warn)
}
