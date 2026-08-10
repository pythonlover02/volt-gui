use crate::config::parse_settings;
use crate::lists::filtered;
use crate::lists::forced;
use crate::lists::kept;
use crate::ranks::alpha_display;
use crate::ranks::alpha_parse;
use crate::ranks::alpha_semantic;
use crate::ranks::depth_label;
use crate::ranks::format_display;
use crate::ranks::format_semantic;
use crate::ranks::numeric_display;
use crate::ranks::numeric_parse;
use crate::ranks::numeric_semantic;
use crate::ranks::parse_depth_label;
use crate::ranks::present_display;
use crate::ranks::present_parse;
use crate::ranks::present_semantic;
use crate::ranks::space_display;
use crate::ranks::space_parse;
use crate::ranks::space_semantic;
use crate::ranks::Numeric;

const UNKNOWN_MODE: u32 = 4242;
const UNKNOWN_SPACE: u32 = 4243;
const UNKNOWN_FORMAT: u32 = 4244;
const UNKNOWN_ALPHA: u32 = 16;
const FIFO_MODE: u32 = 2;
const SHARED_MODE: u32 = 1000111000;
const HDR10_SPACE: u32 = 1000104008;
const SRGB_SPACE: u32 = 0;
const OPAQUE_ALPHA: u32 = 1;
const INHERIT_ALPHA: u32 = 8;
const SRGB_FORMAT: u32 = 43;
const UFLOAT_FORMAT: u32 = 122;
const EIGHT_BIT: u32 = 8;
const ELEVEN_BIT: u32 = 11;
const TEN_BIT: u32 = 10;
const UNNAMED_MODE_PROFILE: &str = "[display]\npresent_mode = \"present mode 4242\"\n";
const NAMED_MODE_PROFILE: &str = "[display]\npresent_mode = \"fifo\"\n";
const TRANSFER_PROFILE: &str = "[display]\ntransfer_function = \"ufloat\"\n";

#[test]
fn keeps_the_application_value_when_nothing_is_forced() {
    assert_eq!(forced(None, 3), 3);
    assert_eq!(forced(Some(2), 3), 2);
}

#[test]
fn restores_a_list_the_choice_emptied() {
    assert_eq!(kept(vec![1, 2, 3], |value: &i32| *value > 3, ""), vec![1, 2, 3]);
    assert_eq!(kept(vec![1, 2, 3], |value: &i32| *value > 1, ""), vec![2, 3]);
}

#[test]
fn keeps_only_what_the_choice_names() {
    assert_eq!(filtered(vec![1, 2, 3], Some(2), |v: &i32| Some(*v), ""), vec![2]);
    assert_eq!(filtered(vec![1, 2, 3], None, |v: &i32| Some(*v), ""), vec![1, 2, 3]);
    assert_eq!(filtered(vec![1, 2, 3], Some(9), |v: &i32| Some(*v), ""), vec![1, 2, 3]);
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
    assert_eq!(alpha_parse(&alpha_display(UNKNOWN_ALPHA)), Some(UNKNOWN_ALPHA));
}


#[test]
fn round_trips_a_transfer_function_through_its_name() {
    assert_eq!(numeric_parse(&numeric_display(Numeric::Srgb)), Some(Numeric::Srgb));
    assert_eq!(numeric_parse(&numeric_display(Numeric::Ufloat)), Some(Numeric::Ufloat));
}

#[test]
fn round_trips_a_color_depth_through_its_label() {
    assert_eq!(parse_depth_label(&depth_label(TEN_BIT)), Some(TEN_BIT));
}

#[test]
fn gives_each_enum_its_own_unknown_prefix() {
    assert_ne!(present_display(UNKNOWN_MODE), space_display(UNKNOWN_MODE));
    assert_ne!(space_display(UNKNOWN_MODE), format_display(UNKNOWN_MODE));
    assert_ne!(format_display(UNKNOWN_MODE), alpha_display(UNKNOWN_MODE));
}

#[test]
fn groups_an_unnamed_value_under_nothing() {
    assert!(present_semantic(UNKNOWN_MODE).is_none());
    assert!(space_semantic(UNKNOWN_SPACE).is_none());
    assert!(format_semantic(UNKNOWN_FORMAT).is_none());
    assert!(alpha_semantic(UNKNOWN_ALPHA).is_none());
}

#[test]
fn reads_the_facts_a_setting_branches_on() {
    assert_eq!(format_semantic(SRGB_FORMAT).map(|facts| facts.depth), Some(EIGHT_BIT));
    assert_eq!(format_semantic(UFLOAT_FORMAT).map(|facts| facts.depth), Some(ELEVEN_BIT));
    assert_eq!(
        format_semantic(UFLOAT_FORMAT).map(|facts| facts.numeric),
        Some(Numeric::Ufloat)
    );
    assert_eq!(alpha_semantic(OPAQUE_ALPHA).map(|facts| facts.blends), Some(false));
    assert_eq!(alpha_semantic(INHERIT_ALPHA).map(|facts| facts.blends), Some(true));
    assert_eq!(space_semantic(SRGB_SPACE).map(|facts| facts.extended), Some(false));
    assert_eq!(space_semantic(HDR10_SPACE).map(|facts| facts.extended), Some(true));
    assert_eq!(present_semantic(FIFO_MODE).map(|facts| facts.extended), Some(false));
    assert_eq!(present_semantic(SHARED_MODE).map(|facts| facts.extended), Some(true));
    assert_eq!(numeric_semantic(Numeric::Srgb).map(|facts| facts.encoded), Some(true));
    assert_eq!(numeric_semantic(Numeric::Unorm).map(|facts| facts.encoded), Some(false));
}

#[test]
fn forces_a_value_volt_has_no_name_for() {
    assert_eq!(parse_settings(UNNAMED_MODE_PROFILE).present_mode, Some(UNKNOWN_MODE));
    assert_eq!(parse_settings(NAMED_MODE_PROFILE).present_mode, Some(FIFO_MODE));
    assert_eq!(parse_settings(TRANSFER_PROFILE).transfer, Some(Numeric::Ufloat));
}
