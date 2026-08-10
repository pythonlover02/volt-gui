#![allow(non_snake_case)]

mod consts;
mod logging;
mod bounds;
mod ranks;
mod env;
mod config;
mod instance;
mod device;
mod layer;
mod swapchain;
mod probe;
mod present;
mod sampler;
mod pipeline;
mod launcher;

#[cfg(test)]
mod checks;

pub use env::process_args;
pub use launcher::run_launcher;
