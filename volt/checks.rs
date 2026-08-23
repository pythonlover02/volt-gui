use crate::config::parse_settings;
use crate::consts::CadenceChoice;
use crate::consts::FRAME_LIMIT_MIN;
use crate::consts::MethodChoice;
use crate::consts::TOGGLE_OFF;
use crate::consts::TOGGLE_ON;
use crate::lists::filtered;
use crate::lists::forced;
use crate::lists::kept;
use crate::present::advanced;
use crate::present::shifted_fps;
use crate::present::target_interval_ns;
use crate::present::Timeline;
use crate::ranks::alpha_display;
use crate::ranks::alpha_parse;
use crate::ranks::alpha_semantic;
use crate::ranks::present_display;
use crate::ranks::present_parse;
use crate::ranks::present_semantic;

const UNKNOWN_MODE: u32 = 4242;
const UNKNOWN_ALPHA: u32 = 16;
const FIFO_MODE: u32 = 2;
const SHARED_MODE: u32 = 1000111000;
const OPAQUE_ALPHA: u32 = 1;
const NEAREST_FILTER: u32 = 0;
const LINEAR_FILTER: u32 = 1;
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
fn round_trips_a_present_mode_through_its_name() {
    assert_eq!(present_parse(&present_display(FIFO_MODE)), Some(FIFO_MODE));
    assert_eq!(present_parse(&present_display(UNKNOWN_MODE)), Some(UNKNOWN_MODE));
}

#[test]
fn round_trips_a_composite_alpha_through_its_name() {
    assert_eq!(alpha_parse(&alpha_display(OPAQUE_ALPHA)), Some(OPAQUE_ALPHA));
    assert_eq!(alpha_parse(&alpha_display(UNKNOWN_ALPHA)), Some(UNKNOWN_ALPHA));
}


#[test]
fn gives_each_enum_its_own_unknown_prefix() {
    assert_ne!(present_display(UNKNOWN_MODE), alpha_display(UNKNOWN_MODE));
}

#[test]
fn groups_an_unnamed_value_under_nothing() {
    assert!(present_semantic(UNKNOWN_MODE).is_none());
    assert!(alpha_semantic(UNKNOWN_ALPHA).is_none());
}

#[test]
fn reads_the_facts_a_setting_branches_on() {
    assert_eq!(alpha_semantic(OPAQUE_ALPHA).map(|facts| facts.blends), Some(false));
    assert_eq!(alpha_semantic(INHERIT_ALPHA).map(|facts| facts.blends), Some(true));
    assert_eq!(present_semantic(FIFO_MODE).map(|facts| facts.extended), Some(false));
    assert_eq!(present_semantic(SHARED_MODE).map(|facts| facts.extended), Some(true));
}

#[test]
fn forces_a_value_volt_has_no_name_for() {
    assert_eq!(parse_settings(UNNAMED_MODE_PROFILE).present_mode, Some(UNKNOWN_MODE));
    assert_eq!(parse_settings(NAMED_MODE_PROFILE).present_mode, Some(FIFO_MODE));
}

#[test]
fn reads_the_two_feature_gated_toggles_from_a_profile() {
    assert_eq!(parse_settings(ALPHA_ONE_PROFILE).alpha_to_one, Some(TOGGLE_ON));
    assert_eq!(parse_settings(CLAMP_PROFILE).depth_clamp, Some(TOGGLE_OFF));
}

#[test]
fn reads_each_sampler_filter_on_its_own() {
    assert_eq!(parse_settings(FILTER_PROFILE).mag_filter, Some(NEAREST_FILTER));
    assert_eq!(parse_settings(FILTER_PROFILE).min_filter, Some(LINEAR_FILTER));
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
        LIMIT_START_NS + LIMIT_INTERVAL_NS + LIMIT_INTERVAL_NS + LIMIT_INTERVAL_NS
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
