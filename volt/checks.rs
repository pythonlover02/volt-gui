use crate::bounds::accepts;
use crate::bounds::bounds_set;
use crate::bounds::kept;
use crate::bounds::ordered;
use crate::bounds::resolved;
use crate::bounds::Bounds;
use crate::config::parse_settings;
use crate::ranks::alpha_display;
use crate::ranks::alpha_parse;
use crate::ranks::alpha_semantic;
use crate::ranks::depth_label;
use crate::ranks::format_semantic;
use crate::ranks::parse_depth_label;
use crate::ranks::present_display;
use crate::ranks::present_parse;
use crate::ranks::present_semantic;
use crate::ranks::space_display;
use crate::ranks::space_parse;
use crate::ranks::transfer_display;
use crate::ranks::transfer_parse;
use crate::ranks::transfer_semantic;
use crate::ranks::Numeric;

const UNKNOWN_MODE: u32 = 4242;
const UNKNOWN_SPACE: u32 = 4243;
const FIFO_MODE: u32 = 2;
const HDR10_SPACE: u32 = 1000104008;
const OPAQUE_ALPHA: u32 = 1;
const SRGB_FORMAT: u32 = 43;
const EIGHT_BIT: u32 = 8;
const TEN_BIT: u32 = 10;
const CROSSED_BOUNDS: &str = "[display]\nimage_count_min = \"6\"\nimage_count_max = \"2\"\n";

#[test]
fn resolves_a_force_over_its_own_bounds() {
    assert_eq!(resolved(Bounds { force: Some(2), min: Some(0), max: Some(1) }, 3), 2);
}

#[test]
fn pulls_a_value_back_to_the_nearest_bound() {
    assert_eq!(resolved(Bounds { force: None, min: Some(2), max: Some(4) }, 0), 2);
    assert_eq!(resolved(Bounds { force: None, min: Some(2), max: Some(4) }, 9), 4);
    assert_eq!(resolved(Bounds { force: None, min: Some(2), max: Some(4) }, 3), 3);
}

#[test]
fn accepts_only_the_forced_rank() {
    assert!(accepts(Bounds { force: Some(1), min: None, max: None }, 1));
    assert!(!accepts(Bounds { force: Some(1), min: None, max: None }, 2));
}

#[test]
fn accepts_every_rank_inside_the_range() {
    assert!(accepts(Bounds { force: None, min: Some(1), max: Some(3) }, 2));
    assert!(!accepts(Bounds { force: None, min: Some(1), max: Some(3) }, 4));
}

#[test]
fn reads_an_untouched_setting_as_unset() {
    assert!(!bounds_set(&Bounds::<u32>::default()));
    assert!(bounds_set(&Bounds { force: None, min: Some(1), max: None }));
}

#[test]
fn rejects_a_minimum_above_its_maximum() {
    assert!(ordered(Some(1), Some(2)));
    assert!(ordered::<u32>(None, None));
    assert!(!ordered(Some(2), Some(1)));
}

#[test]
fn restores_a_list_its_bounds_emptied() {
    assert_eq!(kept(vec![1, 2, 3], |value: &i32| *value > 3, ""), vec![1, 2, 3]);
    assert_eq!(kept(vec![1, 2, 3], |value: &i32| *value > 1, ""), vec![2, 3]);
}

#[test]
fn drops_both_ends_of_a_crossed_bound() {
    let parsed = parse_settings(CROSSED_BOUNDS);
    assert_eq!(parsed.image_count.min, None);
    assert_eq!(parsed.image_count.max, None);
}

#[test]
fn round_trips_a_present_mode_through_its_name() {
    assert_eq!(present_parse(&present_display(FIFO_MODE)), Some(FIFO_MODE));
    assert_eq!(present_parse(&present_display(UNKNOWN_MODE)), Some(UNKNOWN_MODE));
}

#[test]
fn round_trips_a_color_space_through_its_name() {
    assert_eq!(space_parse(&space_display(HDR10_SPACE)), Some(HDR10_SPACE));
    assert_eq!(space_parse(&space_display(UNKNOWN_SPACE)), Some(UNKNOWN_SPACE));
}

#[test]
fn round_trips_a_composite_alpha_through_its_name() {
    assert_eq!(alpha_parse(&alpha_display(OPAQUE_ALPHA)), Some(OPAQUE_ALPHA));
}

#[test]
fn round_trips_a_color_depth_through_its_label() {
    assert_eq!(parse_depth_label(&depth_label(TEN_BIT)), Some(TEN_BIT));
}

#[test]
fn round_trips_a_transfer_function_through_its_name() {
    assert!(transfer_parse(&transfer_display(Numeric::Srgb)) == Some(Numeric::Srgb));
    assert!(transfer_parse(&transfer_display(Numeric::Sfloat)) == Some(Numeric::Sfloat));
}

#[test]
fn groups_an_unnamed_value_under_nothing() {
    assert!(present_semantic(UNKNOWN_MODE).is_none());
    assert!(format_semantic(UNKNOWN_MODE).is_none());
}

#[test]
fn reads_the_facts_a_setting_branches_on() {
    assert_eq!(format_semantic(SRGB_FORMAT).map(|facts| facts.depth), Some(EIGHT_BIT));
    assert_eq!(alpha_semantic(OPAQUE_ALPHA).map(|facts| facts.blends), Some(false));
    assert!(transfer_semantic(Numeric::Unorm).rank < transfer_semantic(Numeric::Srgb).rank);
}
