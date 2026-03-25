def get_gamescope_settings():
    return {
        "_tab_metadata": (True,),
        "_executable_required": ("gamescope",),
        "enable": (
            "Gamescope",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gamescope"),
            ),
            (
                ("argument", "gamescope", "", "", " --"),
            ),
        ),
        "enable_gamescope_wsi_layer": (
            "Gamescope Window System Integration Layer",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "ENABLE_GAMESCOPE_WSI", "", "", ""),
            ),
        ),
        "vulkan_wsi_minimum_image_count": (
            "Vulkan Window System Integration Minimum Image Count",
            (
                ("skip", None),
                ("default", ""),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
                ("4", "4"),
                ("5", "5"),
                ("6", "6"),
            ),
            (
                ("environment_variable", "GAMESCOPE_WSI_MIN_IMAGE_COUNT", "", "", ""),
            ),
        ),
        "vulkan_preferred_device": (
            "Vulkan Preferred Device",
            (
                ("skip", None),
                ("default", ""),
                ("1002:7300", "1002:7300"),
            ),
            (
                ("argument", "gamescope", "", "--prefer-vk-device ", ""),
            ),
        ),
        "output_width": (
            "Output Width",
            (
                ("skip", None),
                ("default", ""),
                ("1280", "1280"),
                ("1920", "1920"),
                ("2560", "2560"),
                ("3840", "3840"),
            ),
            (
                ("argument", "gamescope", "", "-W ", ""),
            ),
        ),
        "output_height": (
            "Output Height",
            (
                ("skip", None),
                ("default", ""),
                ("720", "720"),
                ("1080", "1080"),
                ("1440", "1440"),
                ("2160", "2160"),
            ),
            (
                ("argument", "gamescope", "", "-H ", ""),
            ),
        ),
        "game_width": (
            "Game Width",
            (
                ("skip", None),
                ("default", ""),
                ("1280", "1280"),
                ("1920", "1920"),
                ("2560", "2560"),
            ),
            (
                ("argument", "gamescope", "", "-w ", ""),
            ),
        ),
        "game_height": (
            "Game Height",
            (
                ("skip", None),
                ("default", ""),
                ("720", "720"),
                ("1080", "1080"),
                ("1440", "1440"),
            ),
            (
                ("argument", "gamescope", "", "-h ", ""),
            ),
        ),
        "nested_refresh_rate": (
            "Nested Refresh Rate",
            (
                ("skip", None),
                ("default", ""),
                ("30", "30"),
                ("60", "60"),
                ("120", "120"),
                ("144", "144"),
                ("165", "165"),
                ("240", "240"),
            ),
            (
                ("argument", "gamescope", "", "-r ", ""),
            ),
        ),
        "nested_unfocused_refresh_rate": (
            "Nested Unfocused Refresh Rate",
            (
                ("skip", None),
                ("default", ""),
                ("15", "15"),
                ("30", "30"),
                ("60", "60"),
            ),
            (
                ("argument", "gamescope", "", "-o ", ""),
            ),
        ),
        "framerate_limit": (
            "Framerate Limit",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("30", "30"),
                ("60", "60"),
                ("120", "120"),
                ("144", "144"),
            ),
            (
                ("argument", "gamescope", "", "--framerate-limit ", ""),
            ),
        ),
        "maximum_scale_factor": (
            "Maximum Scale Factor",
            (
                ("skip", None),
                ("default", ""),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
                ("4", "4"),
            ),
            (
                ("argument", "gamescope", "", "-m ", ""),
            ),
        ),
        "force_orientation": (
            "Force Orientation",
            (
                ("skip", None),
                ("default", ""),
                ("normal", "normal"),
                ("left", "left"),
                ("right", "right"),
                ("upsidedown", "upsidedown"),
            ),
            (
                ("argument", "gamescope", "", "--force-orientation ", ""),
            ),
        ),
        "display_index": (
            "Display Index",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
            ),
            (
                ("argument", "gamescope", "", "--display-index ", ""),
            ),
        ),
        "preferred_output_connectors": (
            "Preferred Output Connectors",
            (
                ("skip", None),
                ("default", ""),
                ("DP-1", "DP-1"),
                ("HDMI-A-1", "HDMI-A-1"),
            ),
            (
                ("argument", "gamescope", "", "-O ", ""),
            ),
        ),
        "fullscreen": (
            "Fullscreen",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "-f", ""),
            ),
        ),
        "borderless": (
            "Borderless",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "-b", ""),
            ),
        ),
        "force_windows_fullscreen": (
            "Force Windows Fullscreen",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--force-windows-fullscreen", ""),
            ),
        ),
        "scaler_backend": (
            "Scaler Backend",
            (
                ("skip", None),
                ("default", ""),
                ("auto", "auto"),
                ("integer", "integer"),
                ("fit", "fit"),
                ("fill", "fill"),
                ("stretch", "stretch"),
            ),
            (
                ("argument", "gamescope", "", "--scaler ", ""),
            ),
        ),
        "upscale_filter": (
            "Upscale Filter",
            (
                ("skip", None),
                ("default", ""),
                ("linear", "linear"),
                ("nearest", "nearest"),
                ("fsr", "fsr"),
                ("nis", "nis"),
                ("pixel", "pixel"),
            ),
            (
                ("argument", "gamescope", "", "--filter ", ""),
            ),
        ),
        "upscaler_sharpness": (
            "Upscaler Sharpness",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("2", "2"),
                ("5", "5"),
                ("10", "10"),
                ("15", "15"),
                ("20", "20"),
            ),
            (
                ("argument", "gamescope", "", "--sharpness ", ""),
            ),
        ),
        "grab_keyboard": (
            "Grab Keyboard",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "-g", ""),
            ),
        ),
        "force_grab_cursor": (
            "Force Grab Cursor",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--force-grab-cursor", ""),
            ),
        ),
        "mouse_sensitivity": (
            "Mouse Sensitivity",
            (
                ("skip", None),
                ("default", ""),
                ("0.5", "0.5"),
                ("1.0", "1.0"),
                ("1.5", "1.5"),
                ("2.0", "2.0"),
            ),
            (
                ("argument", "gamescope", "", "-s ", ""),
            ),
        ),
        "default_touch_mode": (
            "Default Touch Mode",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
                ("4", "4"),
            ),
            (
                ("argument", "gamescope", "", "--default-touch-mode ", ""),
            ),
        ),
        "cursor_image_path": (
            "Cursor Image Path",
            (
                ("skip", None),
                ("default", ""),
                ("/usr/share/steamos/steamos-cursor.png", "/usr/share/steamos/steamos-cursor.png"),
            ),
            (
                ("argument", "gamescope", "", "--cursor ", ""),
            ),
        ),
        "hide_cursor_delay": (
            "Hide Cursor Delay",
            (
                ("skip", None),
                ("default", ""),
                ("3000", "3000"),
                ("5000", "5000"),
                ("10000", "10000"),
            ),
            (
                ("argument", "gamescope", "", "-C ", ""),
            ),
        ),
        "cursor_scale_height": (
            "Cursor Scale Height",
            (
                ("skip", None),
                ("default", ""),
                ("720", "720"),
                ("1080", "1080"),
                ("1440", "1440"),
            ),
            (
                ("argument", "gamescope", "", "--cursor-scale-height ", ""),
            ),
        ),
        "rendering_backend": (
            "Rendering Backend",
            (
                ("skip", None),
                ("default", ""),
                ("auto", "auto"),
                ("drm", "drm"),
                ("sdl", "sdl"),
                ("openvr", "openvr"),
                ("headless", "headless"),
                ("wayland", "wayland"),
            ),
            (
                ("argument", "gamescope", "", "--backend ", ""),
            ),
        ),
        "expose_wayland": (
            "Expose Wayland",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--expose-wayland", ""),
            ),
        ),
        "xwayland_server_count": (
            "XWayland Server Count",
            (
                ("skip", None),
                ("default", ""),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
            ),
            (
                ("argument", "gamescope", "", "--xwayland-count ", ""),
            ),
        ),
        "adaptive_sync": (
            "Adaptive Sync",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--adaptive-sync", ""),
            ),
        ),
        "immediate_flips": (
            "Immediate Flips",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--immediate-flips", ""),
            ),
        ),
        "generate_direct_rendering_manager_mode": (
            "Generate Direct Rendering Manager Mode",
            (
                ("skip", None),
                ("default", ""),
                ("cvt", "cvt"),
                ("fixed", "fixed"),
            ),
            (
                ("argument", "gamescope", "", "--generate-drm-mode ", ""),
            ),
        ),
        "high_dynamic_range_output": (
            "High Dynamic Range Output",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--hdr-enabled", ""),
            ),
        ),
        "standard_dynamic_range_gamut_wideness": (
            "Standard Dynamic Range Gamut Wideness",
            (
                ("skip", None),
                ("default", ""),
                ("0.0", "0.0"),
                ("0.25", "0.25"),
                ("0.5", "0.5"),
                ("0.75", "0.75"),
                ("1.0", "1.0"),
            ),
            (
                ("argument", "gamescope", "", "--sdr-gamut-wideness ", ""),
            ),
        ),
        "high_dynamic_range_standard_dynamic_range_content_nits": (
            "High Dynamic Range Standard Dynamic Range Content Nits",
            (
                ("skip", None),
                ("default", ""),
                ("200", "200"),
                ("400", "400"),
                ("600", "600"),
                ("800", "800"),
            ),
            (
                ("argument", "gamescope", "", "--hdr-sdr-content-nits ", ""),
            ),
        ),
        "high_dynamic_range_inverse_tone_mapping": (
            "High Dynamic Range Inverse Tone Mapping",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--hdr-itm-enabled", ""),
            ),
        ),
        "high_dynamic_range_inverse_tone_mapping_standard_dynamic_range_nits": (
            "High Dynamic Range Inverse Tone Mapping Standard Dynamic Range Input Nits",
            (
                ("skip", None),
                ("default", ""),
                ("100", "100"),
                ("200", "200"),
                ("400", "400"),
                ("600", "600"),
                ("1000", "1000"),
            ),
            (
                ("argument", "gamescope", "", "--hdr-itm-sdr-nits ", ""),
            ),
        ),
        "high_dynamic_range_inverse_tone_mapping_target_nits": (
            "High Dynamic Range Inverse Tone Mapping Target Nits",
            (
                ("skip", None),
                ("default", ""),
                ("400", "400"),
                ("1000", "1000"),
                ("2000", "2000"),
                ("4000", "4000"),
                ("10000", "10000"),
            ),
            (
                ("argument", "gamescope", "", "--hdr-itm-target-nits ", ""),
            ),
        ),
        "disable_color_management": (
            "Disable Color Management",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--disable-color-management", ""),
            ),
        ),
        "steam_integration": (
            "Steam Integration",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "-e", ""),
            ),
        ),
        "mangoapp_overlay": (
            "MangoApp Overlay",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--mangoapp", ""),
            ),
        ),
        "reshade_effect": (
            "Reshade Effect",
            (
                ("skip", None),
                ("default", ""),
                ("CRT.fx", "CRT.fx"),
            ),
            (
                ("argument", "gamescope", "", "--reshade-effect ", ""),
            ),
        ),
        "reshade_technique_index": (
            "Reshade Technique Index",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
            ),
            (
                ("argument", "gamescope", "", "--reshade-technique-idx ", ""),
            ),
        ),
        "mura_compensation_map": (
            "Mura Compensation Map",
            (
                ("skip", None),
                ("default", ""),
                ("/usr/share/steamos/steamos-mura.png", "/usr/share/steamos/steamos-mura.png"),
            ),
            (
                ("argument", "gamescope", "", "--mura-map ", ""),
            ),
        ),
        "disable_hardware_planes": (
            "Disable Hardware Planes",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--disable-layers", ""),
            ),
        ),
        "realtime_scheduling": (
            "Realtime Scheduling",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--rt", ""),
            ),
        ),
        "keep_alive": (
            "Keep Alive",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--keep-alive", ""),
            ),
        ),
        "allow_deferred_backend": (
            "Allow Deferred Backend Initialization",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--allow-deferred-backend", ""),
            ),
        ),
        "statistics_path": (
            "Statistics Path",
            (
                ("skip", None),
                ("default", ""),
                ("/tmp/gamescope-stats", "/tmp/gamescope-stats"),
            ),
            (
                ("argument", "gamescope", "", "-T ", ""),
            ),
        ),
        "ready_file_descriptor": (
            "Ready File Descriptor",
            (
                ("skip", None),
                ("default", ""),
                ("3", "3"),
                ("4", "4"),
            ),
            (
                ("argument", "gamescope", "", "-R ", ""),
            ),
        ),
        "virtual_connector_strategy": (
            "Virtual Connector Strategy",
            (
                ("skip", None),
                ("default", ""),
                ("single-application", "single_application"),
                ("steam-controlled", "steam_controlled"),
            ),
            (
                ("argument", "gamescope", "", "--virtual-connector-strategy ", ""),
            ),
        ),
        "virtual_reality_overlay_key": (
            "Virtual Reality Overlay Key",
            (
                ("skip", None),
                ("default", ""),
                ("gamescope", "gamescope"),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-key ", ""),
            ),
        ),
        "virtual_reality_application_overlay_key": (
            "Virtual Reality Application Overlay Key",
            (
                ("skip", None),
                ("default", ""),
                ("gamescope_child", "gamescope_child"),
            ),
            (
                ("argument", "gamescope", "", "--vr-app-overlay-key ", ""),
            ),
        ),
        "virtual_reality_overlay_explicit_name": (
            "Virtual Reality Overlay Explicit Name",
            (
                ("skip", None),
                ("default", ""),
                ("Gamescope", "Gamescope"),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-explicit-name ", ""),
            ),
        ),
        "virtual_reality_overlay_default_name": (
            "Virtual Reality Overlay Default Name",
            (
                ("skip", None),
                ("default", ""),
                ("Gamescope", "Gamescope"),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-default-name ", ""),
            ),
        ),
        "virtual_reality_overlay_icon": (
            "Virtual Reality Overlay Icon",
            (
                ("skip", None),
                ("default", ""),
                ("/usr/share/icons/gamescope.png", "/usr/share/icons/gamescope.png"),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-icon ", ""),
            ),
        ),
        "virtual_reality_overlay_show_immediately": (
            "Virtual Reality Overlay Show Immediately",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-show-immediately", ""),
            ),
        ),
        "virtual_reality_overlay_control_bar": (
            "Virtual Reality Overlay Control Bar",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-enable-control-bar", ""),
            ),
        ),
        "virtual_reality_overlay_keyboard_button": (
            "Virtual Reality Overlay Keyboard Button",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-enable-control-bar-keyboard", ""),
            ),
        ),
        "virtual_reality_overlay_close_button": (
            "Virtual Reality Overlay Close Button",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-enable-control-bar-close", ""),
            ),
        ),
        "virtual_reality_overlay_click_stabilization": (
            "Virtual Reality Overlay Click Stabilization",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-enable-click-stabilization", ""),
            ),
        ),
        "virtual_reality_overlay_modal": (
            "Virtual Reality Overlay Modal",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-modal", ""),
            ),
        ),
        "virtual_reality_overlay_physical_width": (
            "Virtual Reality Overlay Physical Width",
            (
                ("skip", None),
                ("default", ""),
                ("1.0", "1.0"),
                ("1.5", "1.5"),
                ("2.0", "2.0"),
                ("2.5", "2.5"),
                ("3.0", "3.0"),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-physical-width ", ""),
            ),
        ),
        "virtual_reality_overlay_physical_curvature": (
            "Virtual Reality Overlay Physical Curvature",
            (
                ("skip", None),
                ("default", ""),
                ("0.0", "0.0"),
                ("0.1", "0.1"),
                ("0.25", "0.25"),
                ("0.5", "0.5"),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-physical-curvature ", ""),
            ),
        ),
        "virtual_reality_overlay_pre_curve_pitch": (
            "Virtual Reality Overlay Pre Curve Pitch",
            (
                ("skip", None),
                ("default", ""),
                ("0.0", "0.0"),
                ("0.1", "0.1"),
                ("0.25", "0.25"),
            ),
            (
                ("argument", "gamescope", "", "--vr-overlay-physical-pre-curve-pitch ", ""),
            ),
        ),
        "virtual_reality_trackpad_scroll_speed": (
            "Virtual Reality Trackpad Scroll Speed",
            (
                ("skip", None),
                ("default", ""),
                ("2.0", "2.0"),
                ("4.0", "4.0"),
                ("8.0", "8.0"),
                ("12.0", "12.0"),
                ("16.0", "16.0"),
            ),
            (
                ("argument", "gamescope", "", "--vr-scrolls-speed ", ""),
            ),
        ),
        "debug_hardware_planes": (
            "Debug Hardware Planes",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--debug-layers", ""),
            ),
        ),
        "debug_focus": (
            "Debug Focus",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--debug-focus", ""),
            ),
        ),
        "synchronous_x11": (
            "Synchronous X11",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--synchronous-x11", ""),
            ),
        ),
        "debug_heads_up_display": (
            "Debug Heads Up Display",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--debug-hud", ""),
            ),
        ),
        "debug_x11_events": (
            "Debug X11 Events",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--debug-events", ""),
            ),
        ),
        "force_composition": (
            "Force Composition",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--force-composition", ""),
            ),
        ),
        "composite_debug_markers": (
            "Composite Debug Markers",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--composite-debug", ""),
            ),
        ),
        "disable_x_resource": (
            "Disable X Resource",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--disable-xres", ""),
            ),
        ),
        "high_dynamic_range_debug_force_support": (
            "High Dynamic Range Debug Force Support",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--hdr-debug-force-support", ""),
            ),
        ),
        "high_dynamic_range_debug_force_output": (
            "High Dynamic Range Debug Force Output",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--hdr-debug-force-output", ""),
            ),
        ),
        "high_dynamic_range_debug_heatmap": (
            "High Dynamic Range Debug Heatmap",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", ""),
            ),
            (
                ("argument", "gamescope", "", "--hdr-debug-heatmap", ""),
            ),
        ),
    }
