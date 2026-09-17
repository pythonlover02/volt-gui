use std::ffi::c_void;
use std::mem;
use std::ptr;
use std::sync::RwLock;

use ash::vk;

use crate::config::parse_float;
use crate::config::parse_settings;
use crate::config::sanitize_name;
use crate::consts::CadenceChoice;
use crate::consts::DEFAULT_PROFILE;
use crate::consts::FEATURE_ANISOTROPY;
use crate::consts::FRAME_LIMIT_MIN;
use crate::consts::MethodChoice;
use crate::consts::NOTE_NOT_SET;
use crate::consts::SETTING_ANISOTROPY;
use crate::consts::SETTING_FRAME_LIMIT;
use crate::consts::SETTING_PRESENT_MODE;
use crate::consts::TEXT_LINEAR;
use crate::consts::TOGGLE_OFF;
use crate::consts::TOGGLE_ON;
use crate::consts::SOURCE_PUSH_INDEX;
use crate::consts::SOURCE_SHADER_RECORD_INDEX;
use crate::consts::SWAPCHAIN_COUNTER_TYPE;
use crate::consts::SWAPCHAIN_MODE_LIST_TYPE;
use crate::instance::copied_node;
use crate::instance::relinked_chain;
use crate::instance::VkChainNode;
use crate::instance::VkDescriptorSetAndBindingMappingEXT;
use crate::instance::VkSwapchainCounterCreateInfoEXT;
use crate::instance::provider_on;
use crate::layer::negotiated_version;
use crate::lists::filtered;
use crate::lists::forced;
use crate::lists::kept;
use crate::present::advanced;
use crate::present::shifted_fps;
use crate::present::target_interval_ns;
use crate::present::Timeline;
use crate::probe::render_surface;
use crate::probe::SurfaceFacts;
use crate::ranks::alpha_display;
use crate::ranks::alpha_parse;
use crate::ranks::alpha_semantic;
use crate::ranks::present_display;
use crate::ranks::present_parse;
use crate::ranks::present_semantic;
use crate::report::call_claim;
use crate::report::call_forget;
use crate::report::feature_note;
use crate::report::filter_text;
use crate::report::forced_text;
use crate::report::number_text;
use crate::report::report_line;
use crate::report::ReportMap;
use crate::sampler::embedded_sampler;
use crate::swapchain::present_filtered;

const UNKNOWN_MODE: i32 = 4242;
const UNKNOWN_ALPHA: u32 = 16;
const FIFO_MODE: i32 = 2;
const SHARED_MODE: i32 = 1000111000;
const OPAQUE_ALPHA: u32 = 1;
const NEAREST_FILTER: i32 = 0;
const LINEAR_FILTER: i32 = 1;
const FILTER_PROFILE: &str = "[textures]\nmag_filter = \"nearest\"\nmin_filter = \"linear\"\n";
const ALPHA_ONE_PROFILE: &str = "[rendering]\nalpha_to_one = \"on\"\n";
const CLAMP_PROFILE: &str = "[rendering]\ndepth_clamp = \"off\"\n";
const INHERIT_ALPHA: u32 = 8;
const UNNAMED_MODE_PROFILE: &str = "[display]\npresent_mode = \"present mode 4242\"\n";
const NAMED_MODE_PROFILE: &str = "[display]\npresent_mode = \"fifo\"\n";
const LIST_EMPTY_WARN: &str = "list emptied by the choice, restoring";
const LIMIT_START_NS: u64 = 10_000;
const LIMIT_INTERVAL_NS: u64 = 1_000;
const OTHER_INTERVAL_NS: u64 = 2_000;
const LATE_NS: u64 = 100;
const LATE_FRAME_NS: u64 = 1_500;
const TWO_HUNDRED_FPS: f32 = 200.0;
const TWO_HUNDRED_FPS_NS: u64 = 5_000_000;
const OFFSET_DOWN: f32 = -6.0;
const OFFSET_MIN: f32 = -10.0;
const REFRESH_FPS: f32 = 144.0;
const UNDER_REFRESH_FPS: f32 = 138.0;
const OFFSET_PROFILE: &str = "[framerate]\nframe_limit_offset = \"-6\"\n";
const FIXED_PROFILE: &str = "[framerate]\nframe_limit_cadence = \"fixed\"\n";
const DYNAMIC_PROFILE: &str = "[framerate]\nframe_limit_cadence = \"dynamic\"\n";
const PEAK_START_NS: u64 = 2_000;
const SLOW_FRAME_NS: u64 = 1_600;
const SMOOTH_TARGET_NS: u64 = 11_600;
const DYNAMIC_TARGET_NS: u64 = 11_750;
const FAST_FRAME_NS: u64 = 500;
const DECAY_FROM_NS: u64 = 4_000;
const DECAY_TO_NS: u64 = 3_000;
const SPIKE_PEAK_NS: u64 = 4_000;
const HITCH_NS: u64 = 100_000;
const ASKED_MODE: &str = "fifo";
const FORCED_MODE: &str = "mailbox";
const ASKED_ANISO: &str = "off";
const FORCED_LIMIT: &str = "60";
const ASKED_LINE: &str = "present_mode: asked fifo";
const BOTH_LINE: &str = "present_mode: asked fifo, forced mailbox";
const FORCED_LINE: &str = "frame_limit: forced 60";
const UNSET_LINE: &str = "frame_limit: the profile did not set it";
const BLOCKED_LINE: &str = "anisotropy: asked off; the application did not enable samplerAnisotropy";
const ANISO_SIXTEEN: f32 = 16.0;
const ANISO_SIXTEEN_TEXT: &str = "16";
const BIAS_DOWN_TEXT: &str = "-0.6";
const OWNER_ONE: u64 = 1;
const OWNER_TWO: u64 = 2;
const SURFACE_TAG: &str = "wayland";
const SURFACE_PRESENT: [&str; 2] = ["mailbox", "fifo"];
const SURFACE_ALPHA: [&str; 1] = ["opaque"];
const SURFACE_MIN_IMAGES: u32 = 4;
const SURFACE_MAX_IMAGES: u32 = 0;
const SURFACE_SECTION: &str = "[wayland]\npresent_modes = \"mailbox;fifo\"\ncomposite_alphas = \"opaque\"\nmin_image_count = \"4\"\nmax_image_count = \"0\"\n";
const UNKNOWN_CHAIN_TYPE: u32 = 424242;
const SOURCE_PUSH_DATA: i32 = 5;
const NO_COUNTERS: u32 = 0;
const MAILBOX_VALUE: i32 = 1;
const DEFAULT_NAME_MIXED: &str = "Default";
const RESERVED_NAME_MIXED: &str = "Probe";
const PLAIN_NAME: &str = "myprofile";
const CORE_ONE_ONE: u32 = 4198400;
const CORE_ONE_ZERO: u32 = 4194304;
const SURFACE_EXT_NAME: &str = "VK_KHR_surface";
const LOADER_OFFERS_LOW: u32 = 1;
const LOADER_OFFERS_HIGH: u32 = 5;
const LAYER_WANTS: u32 = 2;
const NAN_TEXT: &str = "NaN";
const INF_TEXT: &str = "inf";
const NEG_INF_TEXT: &str = "-inf";
const FINITE_TEXT: &str = "1.5";
const FINITE_VALUE: f32 = 1.5;

#[test]
fn reads_one_spelling_of_the_default_profile_name() {
    assert_eq!(sanitize_name(DEFAULT_NAME_MIXED), DEFAULT_PROFILE);
    assert_eq!(sanitize_name(RESERVED_NAME_MIXED), DEFAULT_PROFILE);
    assert_eq!(sanitize_name(PLAIN_NAME), PLAIN_NAME);
}

#[test]
fn hands_a_hook_out_where_any_one_provider_is_on() {
    let none: std::collections::HashSet<String> = std::collections::HashSet::new();
    let surface: std::collections::HashSet<String> =
        std::iter::once(SURFACE_EXT_NAME.to_string()).collect();
    assert!(provider_on(CORE_ONE_ONE, &none, "vkGetDeviceQueue2"));
    assert!(!provider_on(CORE_ONE_ZERO, &none, "vkGetDeviceQueue2"));
    assert!(provider_on(
        CORE_ONE_ZERO,
        &surface,
        "vkGetPhysicalDeviceSurfaceCapabilitiesKHR"
    ));
    assert!(!provider_on(
        CORE_ONE_ZERO,
        &none,
        "vkGetPhysicalDeviceSurfaceCapabilitiesKHR"
    ));
}

#[test]
fn negotiation_fails_where_the_loader_offers_less_than_the_layer_needs() {
    assert_eq!(negotiated_version(LOADER_OFFERS_LOW, LAYER_WANTS), None);
}

#[test]
fn negotiation_takes_the_lower_of_the_two_interface_versions() {
    assert_eq!(negotiated_version(LOADER_OFFERS_HIGH, LAYER_WANTS), Some(LAYER_WANTS));
    assert_eq!(negotiated_version(LAYER_WANTS, LAYER_WANTS), Some(LAYER_WANTS));
}

#[test]
fn a_number_that_is_not_finite_is_not_a_value() {
    assert_eq!(parse_float(NAN_TEXT), None);
    assert_eq!(parse_float(INF_TEXT), None);
    assert_eq!(parse_float(NEG_INF_TEXT), None);
    assert_eq!(parse_float(FINITE_TEXT), Some(FINITE_VALUE));
}

#[test]
fn keeps_the_application_value_when_nothing_is_forced() {
    assert_eq!(forced(None, 3), 3);
    assert_eq!(forced(Some(2), 3), 2);
}

#[test]
fn restores_a_list_the_choice_emptied() {
    assert_eq!(kept(vec![1, 2, 3], |value: &i32| *value > 3, LIST_EMPTY_WARN), vec![1, 2, 3]);
    assert_eq!(kept(vec![1, 2, 3], |value: &i32| *value > 1, LIST_EMPTY_WARN), vec![2, 3]);
}

#[test]
fn keeps_only_what_the_choice_names() {
    assert_eq!(filtered(vec![1, 2, 3], Some(2), |v: &i32| Some(*v), LIST_EMPTY_WARN), vec![2]);
    assert_eq!(filtered(vec![1, 2, 3], None, |v: &i32| Some(*v), LIST_EMPTY_WARN), vec![1, 2, 3]);
    assert_eq!(filtered(vec![1, 2, 3], Some(9), |v: &i32| Some(*v), LIST_EMPTY_WARN), vec![1, 2, 3]);
}

#[test]
fn round_trips_a_floor_present_mode_through_its_name() {
    let mode = vk::PresentModeKHR::from_raw(FIFO_MODE);
    assert_eq!(present_parse(&present_display(mode)), Some(mode));
}

#[test]
fn never_reads_a_present_mode_above_the_floor_back_from_a_profile() {
    let mode = vk::PresentModeKHR::from_raw(UNKNOWN_MODE);
    let shared = vk::PresentModeKHR::from_raw(SHARED_MODE);
    assert_eq!(present_parse(&present_display(mode)), None);
    assert_eq!(present_parse(&present_display(shared)), None);
}

#[test]
fn round_trips_a_composite_alpha_through_its_name() {
    let alpha = vk::CompositeAlphaFlagsKHR::from_raw(OPAQUE_ALPHA);
    assert_eq!(alpha_parse(&alpha_display(alpha)), Some(alpha));
}

#[test]
fn never_reads_a_composite_alpha_volt_has_no_name_for() {
    let alpha = vk::CompositeAlphaFlagsKHR::from_raw(UNKNOWN_ALPHA);
    assert_eq!(alpha_parse(&alpha_display(alpha)), None);
}

#[test]
fn gives_each_enum_its_own_unknown_prefix() {
    assert_ne!(
        present_display(vk::PresentModeKHR::from_raw(UNKNOWN_MODE)),
        alpha_display(vk::CompositeAlphaFlagsKHR::from_raw(UNKNOWN_MODE as u32))
    );
}

#[test]
fn groups_an_unnamed_value_under_nothing() {
    assert!(present_semantic(vk::PresentModeKHR::from_raw(UNKNOWN_MODE)).is_none());
    assert!(alpha_semantic(vk::CompositeAlphaFlagsKHR::from_raw(UNKNOWN_ALPHA)).is_none());
}

#[test]
fn reads_the_facts_a_setting_branches_on() {
    let opaque = vk::CompositeAlphaFlagsKHR::from_raw(OPAQUE_ALPHA);
    let inherit = vk::CompositeAlphaFlagsKHR::from_raw(INHERIT_ALPHA);
    let fifo = vk::PresentModeKHR::from_raw(FIFO_MODE);
    let shared = vk::PresentModeKHR::from_raw(SHARED_MODE);
    assert_eq!(alpha_semantic(opaque).map(|facts| facts.blends), Some(false));
    assert_eq!(alpha_semantic(inherit).map(|facts| facts.blends), Some(true));
    assert_eq!(present_semantic(fifo).map(|facts| facts.floor), Some(true));
    assert_eq!(present_semantic(shared).map(|facts| facts.floor), Some(false));
}

#[test]
fn leaves_a_value_above_the_floor_at_default() {
    assert_eq!(parse_settings(UNNAMED_MODE_PROFILE).present_mode, None);
    assert_eq!(
        parse_settings(NAMED_MODE_PROFILE).present_mode,
        Some(vk::PresentModeKHR::from_raw(FIFO_MODE))
    );
}

#[test]
fn reads_the_two_feature_gated_toggles_from_a_profile() {
    assert_eq!(parse_settings(ALPHA_ONE_PROFILE).alpha_to_one, Some(TOGGLE_ON));
    assert_eq!(parse_settings(CLAMP_PROFILE).depth_clamp, Some(TOGGLE_OFF));
}

#[test]
fn reads_each_sampler_filter_on_its_own() {
    assert_eq!(
        parse_settings(FILTER_PROFILE).mag_filter,
        Some(vk::Filter::from_raw(NEAREST_FILTER))
    );
    assert_eq!(
        parse_settings(FILTER_PROFILE).min_filter,
        Some(vk::Filter::from_raw(LINEAR_FILTER))
    );
}

#[test]
fn turns_a_frame_rate_into_an_interval() {
    assert_eq!(target_interval_ns(TWO_HUNDRED_FPS), TWO_HUNDRED_FPS_NS);
}

#[test]
fn starts_the_timeline_one_interval_after_the_first_frame() {
    assert_eq!(
        advanced(
            None,
            LIMIT_START_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            None,
        ),
        Timeline {
            target: LIMIT_START_NS + LIMIT_INTERVAL_NS,
            interval: LIMIT_INTERVAL_NS,
            last: LIMIT_START_NS + LIMIT_INTERVAL_NS,
            peak: LIMIT_INTERVAL_NS,
        }
    );
}

#[test]
fn holds_the_cadence_when_a_frame_runs_a_little_late() {
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: LIMIT_INTERVAL_NS,
            }),
            LIMIT_START_NS + LATE_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            None,
        )
        .target,
        LIMIT_START_NS + LIMIT_INTERVAL_NS
    );
}

#[test]
fn never_chases_a_slow_frame_with_a_fast_one() {
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: LIMIT_INTERVAL_NS,
            }),
            LIMIT_START_NS + LIMIT_INTERVAL_NS + LIMIT_INTERVAL_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            None,
        )
        .target,
        LIMIT_START_NS + LIMIT_INTERVAL_NS + LIMIT_INTERVAL_NS
    );
}

#[test]
fn a_frame_past_its_deadline_leaves_without_waiting() {
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: LIMIT_INTERVAL_NS,
            }),
            LIMIT_START_NS + LATE_FRAME_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            None,
        )
        .target,
        LIMIT_START_NS + LATE_FRAME_NS
    );
}

#[test]
fn measures_a_reactive_interval_from_the_frame_just_shown() {
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: LIMIT_INTERVAL_NS,
            }),
            LIMIT_START_NS + LATE_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Reactive),
            None,
        )
        .target,
        LIMIT_START_NS + LATE_NS + LIMIT_INTERVAL_NS
    );
}

#[test]
fn restarts_the_timeline_when_the_frame_limit_changes() {
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: LIMIT_INTERVAL_NS,
            }),
            LIMIT_START_NS + LATE_NS,
            OTHER_INTERVAL_NS,
            Some(MethodChoice::Late),
            None,
        ),
        Timeline {
            target: LIMIT_START_NS + LATE_NS + OTHER_INTERVAL_NS,
            interval: OTHER_INTERVAL_NS,
            last: LIMIT_START_NS + LATE_NS + OTHER_INTERVAL_NS,
            peak: OTHER_INTERVAL_NS,
        }
    );
}

#[test]
fn shifts_the_frame_limit_by_the_offset() {
    assert_eq!(shifted_fps(REFRESH_FPS, Some(OFFSET_DOWN)), UNDER_REFRESH_FPS);
    assert_eq!(shifted_fps(REFRESH_FPS, None), REFRESH_FPS);
}

#[test]
fn never_shifts_a_cap_below_one_frame_a_second() {
    assert_eq!(shifted_fps(FRAME_LIMIT_MIN, Some(OFFSET_MIN)), FRAME_LIMIT_MIN);
}

#[test]
fn reads_a_frame_limit_offset_from_a_profile() {
    assert_eq!(parse_settings(OFFSET_PROFILE).frame_limit_offset, Some(OFFSET_DOWN));
}

#[test]
fn reads_a_frame_limit_cadence_from_a_profile() {
    assert_eq!(parse_settings(FIXED_PROFILE).cadence, Some(CadenceChoice::Fixed));
    assert_eq!(parse_settings(DYNAMIC_PROFILE).cadence, Some(CadenceChoice::Dynamic));
}

#[test]
fn times_production_from_the_release_of_the_last_frame() {
    assert_eq!(
        advanced(
            None,
            LIMIT_START_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            Some(CadenceChoice::Smooth),
        )
        .last,
        LIMIT_START_NS + LIMIT_INTERVAL_NS
    );
}

#[test]
fn a_fixed_cadence_paces_at_the_cap() {
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: LIMIT_INTERVAL_NS,
            }),
            LIMIT_START_NS + FAST_FRAME_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            Some(CadenceChoice::Fixed),
        )
        .target,
        LIMIT_START_NS + LIMIT_INTERVAL_NS
    );
}

#[test]
fn smooth_paces_at_the_worst_recent_frame() {
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: PEAK_START_NS,
            }),
            LIMIT_START_NS + SLOW_FRAME_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            Some(CadenceChoice::Smooth),
        )
        .target,
        SMOOTH_TARGET_NS
    );
}

#[test]
fn dynamic_rounds_the_pace_to_a_quarter_step() {
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: PEAK_START_NS,
            }),
            LIMIT_START_NS + SLOW_FRAME_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            Some(CadenceChoice::Dynamic),
        )
        .target,
        DYNAMIC_TARGET_NS
    );
}

#[test]
fn neither_cadence_paces_faster_than_the_cap() {
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: FAST_FRAME_NS,
            }),
            LIMIT_START_NS + FAST_FRAME_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            Some(CadenceChoice::Smooth),
        )
        .target,
        LIMIT_START_NS + LIMIT_INTERVAL_NS
    );
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: FAST_FRAME_NS,
            }),
            LIMIT_START_NS + FAST_FRAME_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            Some(CadenceChoice::Dynamic),
        )
        .target,
        LIMIT_START_NS + LIMIT_INTERVAL_NS
    );
}

#[test]
fn the_peak_decays_so_the_pace_climbs_back() {
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: DECAY_FROM_NS,
            }),
            LIMIT_START_NS + LIMIT_INTERVAL_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            Some(CadenceChoice::Smooth),
        )
        .peak,
        DECAY_TO_NS
    );
}

#[test]
fn a_hitch_cannot_set_the_peak_past_the_spike_limit() {
    assert_eq!(
        advanced(
            Some(Timeline {
                target: LIMIT_START_NS,
                interval: LIMIT_INTERVAL_NS,
                last: LIMIT_START_NS,
                peak: LIMIT_INTERVAL_NS,
            }),
            LIMIT_START_NS + HITCH_NS,
            LIMIT_INTERVAL_NS,
            Some(MethodChoice::Early),
            Some(CadenceChoice::Smooth),
        )
        .peak,
        SPIKE_PEAK_NS
    );
}

#[test]
fn writes_only_the_parts_a_setting_line_has() {
    assert_eq!(
        report_line(SETTING_PRESENT_MODE, Some(ASKED_MODE.into()), None, None),
        ASKED_LINE
    );
    assert_eq!(
        report_line(
            SETTING_PRESENT_MODE,
            Some(ASKED_MODE.into()),
            Some(FORCED_MODE.into()),
            None,
        ),
        BOTH_LINE
    );
    assert_eq!(
        report_line(SETTING_FRAME_LIMIT, None, Some(FORCED_LIMIT.into()), None),
        FORCED_LINE
    );
    assert_eq!(
        report_line(SETTING_FRAME_LIMIT, None, None, Some(NOTE_NOT_SET.into())),
        UNSET_LINE
    );
    assert_eq!(
        report_line(
            SETTING_ANISOTROPY,
            Some(ASKED_ANISO.into()),
            None,
            feature_note(true, false, FEATURE_ANISOTROPY),
        ),
        BLOCKED_LINE
    );
}

#[test]
fn names_a_forced_value_only_where_the_profile_set_one() {
    let nearest = vk::Filter::from_raw(NEAREST_FILTER);
    let linear = vk::Filter::from_raw(LINEAR_FILTER);
    assert_eq!(forced_text(true, nearest, nearest, filter_text), None);
    assert_eq!(
        forced_text(true, nearest, linear, filter_text),
        Some(TEXT_LINEAR.into())
    );
    assert_eq!(forced_text(false, nearest, linear, filter_text), None);
}

#[test]
fn notes_a_feature_only_where_the_profile_set_the_setting() {
    assert!(feature_note(true, false, FEATURE_ANISOTROPY).is_some());
    assert!(feature_note(false, false, FEATURE_ANISOTROPY).is_none());
    assert!(feature_note(true, true, FEATURE_ANISOTROPY).is_none());
}

#[test]
fn writes_a_number_the_way_a_profile_writes_it() {
    assert_eq!(number_text(ANISO_SIXTEEN), ANISO_SIXTEEN_TEXT);
    assert_eq!(number_text(OFFSET_DOWN / 10.0), BIAS_DOWN_TEXT);
}

#[test]
fn reports_a_setting_once_per_device_until_the_device_dies() {
    let store: RwLock<Option<ReportMap>> = RwLock::new(None);
    assert!(call_claim(&store, OWNER_ONE, SETTING_PRESENT_MODE));
    assert!(!call_claim(&store, OWNER_ONE, SETTING_PRESENT_MODE));
    assert!(call_claim(&store, OWNER_ONE, SETTING_ANISOTROPY));
    assert!(call_claim(&store, OWNER_TWO, SETTING_PRESENT_MODE));
    call_forget(&store, OWNER_ONE);
    assert!(call_claim(&store, OWNER_ONE, SETTING_PRESENT_MODE));
    assert!(!call_claim(&store, OWNER_TWO, SETTING_PRESENT_MODE));
}

fn chain_node(s_type: u32, next: *mut c_void) -> VkChainNode {
    VkChainNode {
        s_type: vk::StructureType::from_raw(s_type as i32),
        p_next: next,
    }
}

fn mapping_with(
    source: i32,
    sampler: *const vk::SamplerCreateInfo<'static>,
) -> VkDescriptorSetAndBindingMappingEXT {
    let mut mapping: VkDescriptorSetAndBindingMappingEXT = unsafe { mem::zeroed() };
    mapping.source = source;
    mapping.source_data.push_index.p_embedded_sampler = sampler;
    mapping
}

#[test]
fn copies_every_chain_node_it_declares() {
    let declared = VkSwapchainCounterCreateInfoEXT {
        s_type: vk::StructureType::from_raw(SWAPCHAIN_COUNTER_TYPE as i32),
        p_next: ptr::null(),
        surface_counters: NO_COUNTERS,
    };
    let undeclared = chain_node(UNKNOWN_CHAIN_TYPE, ptr::null_mut());
    assert!(copied_node(
        &declared as *const VkSwapchainCounterCreateInfoEXT as *const VkChainNode
    )
    .is_some());
    assert!(copied_node(&undeclared as *const VkChainNode).is_none());
}

#[test]
fn chains_its_own_copy_in_front_of_the_replacement() {
    let mut target = chain_node(SWAPCHAIN_MODE_LIST_TYPE, ptr::null_mut());
    let front = VkSwapchainCounterCreateInfoEXT {
        s_type: vk::StructureType::from_raw(SWAPCHAIN_COUNTER_TYPE as i32),
        p_next: &mut target as *mut VkChainNode as *const c_void,
        surface_counters: NO_COUNTERS,
    };
    let replacement = chain_node(SWAPCHAIN_MODE_LIST_TYPE, ptr::null_mut());
    let built = relinked_chain(
        &front as *const VkSwapchainCounterCreateInfoEXT as *const c_void,
        SWAPCHAIN_MODE_LIST_TYPE,
        &replacement as *const VkChainNode as *const c_void,
    )
    .unwrap();
    let copy = built.head as *const VkChainNode;
    assert_ne!(
        built.head,
        &front as *const VkSwapchainCounterCreateInfoEXT as *const c_void
    );
    assert_eq!(
        unsafe { (*copy).s_type.as_raw() as u32 },
        SWAPCHAIN_COUNTER_TYPE
    );
    assert_eq!(
        unsafe { (*copy).p_next as *const c_void },
        &replacement as *const VkChainNode as *const c_void
    );
}

#[test]
fn passes_the_chain_down_when_a_node_in_front_is_undeclared() {
    let mut target = chain_node(SWAPCHAIN_MODE_LIST_TYPE, ptr::null_mut());
    let front = chain_node(
        UNKNOWN_CHAIN_TYPE,
        &mut target as *mut VkChainNode as *mut c_void,
    );
    let replacement = chain_node(SWAPCHAIN_MODE_LIST_TYPE, ptr::null_mut());
    assert!(relinked_chain(
        &front as *const VkChainNode as *const c_void,
        SWAPCHAIN_MODE_LIST_TYPE,
        &replacement as *const VkChainNode as *const c_void,
    )
    .is_none());
}

#[test]
fn reads_the_sampler_only_where_the_selector_names_one() {
    let sampler = vk::SamplerCreateInfo::default();
    let held =
        &sampler as *const vk::SamplerCreateInfo<'_> as *const vk::SamplerCreateInfo<'static>;
    assert!(embedded_sampler(&mapping_with(SOURCE_PUSH_INDEX, held)).is_some());
    assert!(embedded_sampler(&mapping_with(SOURCE_PUSH_DATA, held)).is_none());
    assert!(embedded_sampler(&mapping_with(SOURCE_PUSH_INDEX, ptr::null())).is_none());
    assert!(embedded_sampler(&mapping_with(SOURCE_SHADER_RECORD_INDEX, ptr::null())).is_none());
}

#[test]
fn narrows_a_chained_mode_list_to_the_choice() {
    let mailbox = vk::PresentModeKHR::from_raw(MAILBOX_VALUE);
    assert_eq!(
        present_filtered(vec![vk::PresentModeKHR::FIFO, mailbox], Some(mailbox)),
        vec![mailbox]
    );
    assert_eq!(
        present_filtered(vec![vk::PresentModeKHR::FIFO], Some(mailbox)),
        vec![vk::PresentModeKHR::FIFO]
    );
}

#[test]
fn leaves_a_mode_above_the_floor_where_it_was() {
    let mailbox = vk::PresentModeKHR::from_raw(MAILBOX_VALUE);
    let shared = vk::PresentModeKHR::from_raw(SHARED_MODE);
    assert_eq!(
        present_filtered(vec![vk::PresentModeKHR::FIFO, mailbox, shared], Some(mailbox)),
        vec![mailbox, shared]
    );
}

#[test]
fn restores_a_list_where_no_floor_mode_survives_beside_one_above_it() {
    let mailbox = vk::PresentModeKHR::from_raw(MAILBOX_VALUE);
    let shared = vk::PresentModeKHR::from_raw(SHARED_MODE);
    let modes = vec![vk::PresentModeKHR::FIFO, shared];
    assert_eq!(present_filtered(modes.clone(), Some(mailbox)), modes);
}

#[test]
fn heads_a_surface_section_with_the_backend_that_read_it() {
    assert_eq!(
        render_surface(
            SURFACE_TAG,
            &SurfaceFacts {
                present: SURFACE_PRESENT.iter().map(|name| (*name).into()).collect(),
                alphas: SURFACE_ALPHA.iter().map(|name| (*name).into()).collect(),
                min_images: SURFACE_MIN_IMAGES,
                max_images: SURFACE_MAX_IMAGES,
            },
        ),
        SURFACE_SECTION
    );
}
