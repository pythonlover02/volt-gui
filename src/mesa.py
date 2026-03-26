def get_mesa_settings():
    return {
        "_tab_metadata": (True,),
        "_executable_required": (),
        "opengl_vertical_synchronization": (
            "OpenGL Vertical Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("permissive", "1"),
                ("standard", "2"),
                ("on", "3"),
            ),
            (
                ("environment_variable", "vblank_mode", "", "", ""),
            ),
        ),
        "opengl_threaded_command_processing": (
            "OpenGL Threaded Command Processing",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "mesa_glthread", "", "", ""),
            ),
        ),
        "opengl_adaptive_synchronization": (
            "OpenGL Adaptive Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "adaptive_sync", "", "", ""),
            ),
        ),
        "opengl_texture_dithering": (
            "OpenGL Texture Dithering",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MESA_NO_DITHER", "", "", ""),
            ),
        ),
        "opengl_multisample_antialiasing": (
            "OpenGL Multisample Antialiasing",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "DRI_NO_MSAA", "", "", ""),
            ),
        ),
        "opengl_error_checking": (
            "OpenGL Error Checking",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MESA_NO_ERROR", "", "", ""),
            ),
        ),
        "opengl_error_checking_driver_configuration": (
            "OpenGL Error Checking (Driver Configuration)",
            (
                ("skip", None),
                ("default", ""),
                ("off", "true"),
                ("on", ""),
            ),
            (
                ("environment_variable", "mesa_no_error", "", "", ""),
            ),
        ),
        "opengl_version_override": (
            "OpenGL Version Override",
            (
                ("skip", None),
                ("default", ""),
                ("3.0", "3.0"),
                ("3.0-forward-compatible", "3.0FC"),
                ("3.0-compatibility", "3.0COMPAT"),
                ("3.1", "3.1"),
                ("3.1-forward-compatible", "3.1FC"),
                ("3.1-compatibility", "3.1COMPAT"),
                ("3.2", "3.2"),
                ("3.2-forward-compatible", "3.2FC"),
                ("3.2-compatibility", "3.2COMPAT"),
                ("3.3", "3.3"),
                ("3.3-forward-compatible", "3.3FC"),
                ("3.3-compatibility", "3.3COMPAT"),
                ("4.0", "4.0"),
                ("4.0-forward-compatible", "4.0FC"),
                ("4.0-compatibility", "4.0COMPAT"),
                ("4.1", "4.1"),
                ("4.1-forward-compatible", "4.1FC"),
                ("4.1-compatibility", "4.1COMPAT"),
                ("4.2", "4.2"),
                ("4.2-forward-compatible", "4.2FC"),
                ("4.2-compatibility", "4.2COMPAT"),
                ("4.3", "4.3"),
                ("4.3-forward-compatible", "4.3FC"),
                ("4.3-compatibility", "4.3COMPAT"),
                ("4.4", "4.4"),
                ("4.4-forward-compatible", "4.4FC"),
                ("4.4-compatibility", "4.4COMPAT"),
                ("4.5", "4.5"),
                ("4.5-forward-compatible", "4.5FC"),
                ("4.5-compatibility", "4.5COMPAT"),
                ("4.6", "4.6"),
                ("4.6-forward-compatible", "4.6FC"),
                ("4.6-compatibility", "4.6COMPAT"),
            ),
            (
                ("environment_variable", "MESA_GL_VERSION_OVERRIDE", "", "", ""),
            ),
        ),
        "opengl_es_version_override": (
            "OpenGL ES Version Override",
            (
                ("skip", None),
                ("default", ""),
                ("1.0", "1.0"),
                ("1.1", "1.1"),
                ("2.0", "2.0"),
                ("3.0", "3.0"),
                ("3.1", "3.1"),
                ("3.2", "3.2"),
            ),
            (
                ("environment_variable", "MESA_GLES_VERSION_OVERRIDE", "", "", ""),
            ),
        ),
        "opengl_glsl_version_override": (
            "OpenGL GLSL Version Override",
            (
                ("skip", None),
                ("default", ""),
                ("110", "110"),
                ("120", "120"),
                ("130", "130"),
                ("140", "140"),
                ("150", "150"),
                ("330", "330"),
                ("400", "400"),
                ("410", "410"),
                ("420", "420"),
                ("430", "430"),
                ("440", "440"),
                ("450", "450"),
                ("460", "460"),
            ),
            (
                ("environment_variable", "MESA_GLSL_VERSION_OVERRIDE", "", "", ""),
            ),
        ),
        "opengl_extension_maximum_year": (
            "OpenGL Extension Maximum Year",
            (
                ("skip", None),
                ("default", ""),
                ("2001", "2001"),
                ("2003", "2003"),
                ("2005", "2005"),
                ("2007", "2007"),
                ("2010", "2010"),
                ("2012", "2012"),
                ("2014", "2014"),
                ("2016", "2016"),
                ("2018", "2018"),
                ("2020", "2020"),
            ),
            (
                ("environment_variable", "MESA_EXTENSION_MAX_YEAR", "", "", ""),
            ),
        ),
        "opengl_indirect_rendering": (
            "OpenGL Indirect Rendering",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "true"),
            ),
            (
                ("environment_variable", "LIBGL_ALWAYS_INDIRECT", "", "", ""),
            ),
        ),
        "opengl_software_rendering": (
            "OpenGL Software Rendering",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "true"),
            ),
            (
                ("environment_variable", "LIBGL_ALWAYS_SOFTWARE", "", "", ""),
            ),
        ),
        "opengl_disable_draw_arrays": (
            "OpenGL Disable Draw Arrays",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "true"),
            ),
            (
                ("environment_variable", "LIBGL_NO_DRAWARRAYS", "", "", ""),
            ),
        ),
        "opengl_dri3_buffer_sharing": (
            "OpenGL DRI3 Buffer Sharing",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "LIBGL_DRI3_DISABLE", "", "", ""),
            ),
        ),
        "opengl_dri2_buffer_sharing": (
            "OpenGL DRI2 Buffer Sharing",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "LIBGL_DRI2_DISABLE", "", "", ""),
            ),
        ),
        "opengl_kopper_display_interface": (
            "OpenGL Kopper Display Interface",
            (
                ("skip", None),
                ("default", ""),
                ("off", "true"),
                ("on", ""),
            ),
            (
                ("environment_variable", "LIBGL_KOPPER_DISABLE", "", "", ""),
            ),
        ),
        "opengl_kopper_dri2_mode": (
            "OpenGL Kopper DRI2 Mode",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "true"),
            ),
            (
                ("environment_variable", "LIBGL_KOPPER_DRI2", "", "", ""),
            ),
        ),
        "opengl_frames_per_second_counter": (
            "OpenGL Frames Per Second Counter",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LIBGL_SHOW_FPS", "", "", ""),
            ),
        ),
        "opengl_loader_debug": (
            "OpenGL Loader Debug",
            (
                ("skip", None),
                ("default", ""),
                ("verbose", "verbose"),
            ),
            (
                ("environment_variable", "LIBGL_DEBUG", "", "", ""),
            ),
        ),
        "opengl_drivers_path": (
            "OpenGL Drivers Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "LIBGL_DRIVERS_PATH", ":", "", ""),
            ),
        ),
        "opengl_glx_vendor_library": (
            "OpenGL GLX Vendor Library",
            (
                ("skip", None),
                ("default", ""),
                ("nvidia", "nvidia"),
                ("mesa", "mesa"),
            ),
            (
                ("environment_variable", "__GLX_VENDOR_LIBRARY_NAME", "", "", ""),
            ),
        ),
        "opengl_glx_force_vendor_library_display_0": (
            "OpenGL GLX Force Vendor Library Display 0",
            (
                ("skip", None),
                ("default", ""),
                ("nvidia", "nvidia"),
                ("mesa", "mesa"),
            ),
            (
                ("environment_variable", "__GLX_FORCE_VENDOR_LIBRARY_0", "", "", ""),
            ),
        ),
        "opengl_glx_disable_oml_synchronization_control": (
            "OpenGL GLX Disable OML Synchronization Control",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "glx_disable_oml_sync_control", "", "", ""),
            ),
        ),
        "opengl_glx_disable_buffer_age": (
            "OpenGL GLX Disable Buffer Age",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "glx_disable_ext_buffer_age", "", "", ""),
            ),
        ),
        "opengl_glx_disable_sgi_video_synchronization": (
            "OpenGL GLX Disable SGI Video Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "glx_disable_sgi_video_sync", "", "", ""),
            ),
        ),
        "opengl_glx_extension_override": (
            "OpenGL GLX Extension Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "glx_extension_override", "", "", ""),
            ),
        ),
        "opengl_keep_native_window_glx_drawable": (
            "OpenGL Keep Native Window GLX Drawable",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "keep_native_window_glx_drawable", "", "", ""),
            ),
        ),
        "opengl_force_direct_glx_context": (
            "OpenGL Force Direct GLX Context",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "force_direct_glx_context", "", "", ""),
            ),
        ),
        "opengl_allow_invalid_glx_destroy_window": (
            "OpenGL Allow Invalid GLX Destroy Window",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_invalid_glx_destroy_window", "", "", ""),
            ),
        ),
        "opengl_xlib_rgb_visual": (
            "OpenGL Xlib RGB Visual",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_RGB_VISUAL", "", "", ""),
            ),
        ),
        "opengl_xlib_back_buffer": (
            "OpenGL Xlib Back Buffer",
            (
                ("skip", None),
                ("default", ""),
                ("pixmap", "pixmap"),
                ("ximage", "ximage"),
            ),
            (
                ("environment_variable", "MESA_BACK_BUFFER", "", "", ""),
            ),
        ),
        "opengl_xlib_synchronous_mode": (
            "OpenGL Xlib Synchronous Mode",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_XSYNC", "", "", ""),
            ),
        ),
        "opengl_xlib_force_alpha_channel": (
            "OpenGL Xlib Force Alpha Channel",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_GLX_FORCE_ALPHA", "", "", ""),
            ),
        ),
        "opengl_xlib_depth_bits": (
            "OpenGL Xlib Depth Bits",
            (
                ("skip", None),
                ("default", ""),
                ("16", "16"),
                ("24", "24"),
                ("32", "32"),
            ),
            (
                ("environment_variable", "MESA_GLX_DEPTH_BITS", "", "", ""),
            ),
        ),
        "opengl_xlib_alpha_bits": (
            "OpenGL Xlib Alpha Bits",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("8", "8"),
            ),
            (
                ("environment_variable", "MESA_GLX_ALPHA_BITS", "", "", ""),
            ),
        ),
        "opengl_xlib_force_color_index": (
            "OpenGL Xlib Force Color Index",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_GLX_FORCE_CI", "", "", ""),
            ),
        ),
        "opengl_extension_override": (
            "OpenGL Extension Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_EXTENSION_OVERRIDE", " ", "", ""),
            ),
        ),
        "opengl_extension_override_driver_configuration": (
            "OpenGL Extension Override (Driver Configuration)",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "mesa_extension_override", "", "", ""),
            ),
        ),
        "opengl_threaded_command_application_profile": (
            "OpenGL Threaded Command Application Profile",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "mesa_glthread_app_profile", "", "", ""),
            ),
        ),
        "opengl_threaded_command_driver_mode": (
            "OpenGL Threaded Command Driver Mode",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "mesa_glthread_driver", "", "", ""),
            ),
        ),
        "opengl_threaded_command_skip_framebuffer_status_check": (
            "OpenGL Threaded Command Skip Framebuffer Status Check",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "glthread_nop_check_framebuffer_status", "", "", ""),
            ),
        ),
        "opengl_b10x6_format_support": (
            "OpenGL B10X6 Format Support",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "mesa_b10x6_format_supported", "", "", ""),
            ),
        ),
        "opengl_force_glsl_version": (
            "OpenGL Force GLSL Version",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "force_glsl_version", "", "", ""),
            ),
        ),
        "opengl_glsl_zero_initialization": (
            "OpenGL GLSL Zero Initialization",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "glsl_zero_init", "", "", ""),
            ),
        ),
        "opengl_glsl_extension_midshader": (
            "OpenGL GLSL Extension Midshader",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_glsl_extension_directive_midshader", "", "", ""),
            ),
        ),
        "opengl_glsl_correct_derivatives_after_discard": (
            "OpenGL GLSL Correct Derivatives After Discard",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "glsl_correct_derivatives_after_discard", "", "", ""),
            ),
        ),
        "opengl_glsl_ignore_write_to_readonly_variable": (
            "OpenGL GLSL Ignore Write to Read-Only Variable",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "glsl_ignore_write_to_readonly_var", "", "", ""),
            ),
        ),
        "opengl_glsl_debug_dump_on_error": (
            "OpenGL GLSL Debug Dump On Error",
            (
                ("skip", None),
                ("default", ""),
                ("on", "dump_on_error"),
            ),
            (
                ("environment_variable", "MESA_GLSL", ",", "", ""),
            ),
        ),
        "opengl_glsl_debug_log": (
            "OpenGL GLSL Debug Log",
            (
                ("skip", None),
                ("default", ""),
                ("on", "log"),
            ),
            (
                ("environment_variable", "MESA_GLSL", ",", "", ""),
            ),
        ),
        "opengl_glsl_debug_no_optimizations": (
            "OpenGL GLSL Debug No Optimizations",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nopt"),
            ),
            (
                ("environment_variable", "MESA_GLSL", ",", "", ""),
            ),
        ),
        "opengl_glsl_debug_no_vertex_program": (
            "OpenGL GLSL Debug No Vertex Program",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nopvert"),
            ),
            (
                ("environment_variable", "MESA_GLSL", ",", "", ""),
            ),
        ),
        "opengl_glsl_debug_zero_uninitialized": (
            "OpenGL GLSL Debug Zero Uninitialized",
            (
                ("skip", None),
                ("default", ""),
                ("on", "zero_uninit"),
            ),
            (
                ("environment_variable", "MESA_GLSL", ",", "", ""),
            ),
        ),
        "opengl_glsl_debug_errors": (
            "OpenGL GLSL Debug Errors",
            (
                ("skip", None),
                ("default", ""),
                ("on", "errors"),
            ),
            (
                ("environment_variable", "MESA_GLSL", ",", "", ""),
            ),
        ),
        "opengl_glsl_debug_cache": (
            "OpenGL GLSL Debug Cache",
            (
                ("skip", None),
                ("default", ""),
                ("on", "cache"),
            ),
            (
                ("environment_variable", "MESA_GLSL", ",", "", ""),
            ),
        ),
        "opengl_glsl_debug_cache_information": (
            "OpenGL GLSL Debug Cache Information",
            (
                ("skip", None),
                ("default", ""),
                ("on", "cache_info"),
            ),
            (
                ("environment_variable", "MESA_GLSL", ",", "", ""),
            ),
        ),
        "opengl_texture_program_emulation": (
            "OpenGL Texture Program Emulation",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_TEX_PROG", "", "", ""),
            ),
        ),
        "opengl_transform_lighting_program_emulation": (
            "OpenGL Transform and Lighting Program Emulation",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_TNL_PROG", "", "", ""),
            ),
        ),
        "opengl_minimum_maximum_index_cache": (
            "OpenGL Minimum Maximum Index Cache",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MESA_NO_MINMAX_CACHE", "", "", ""),
            ),
        ),
        "opengl_assembly_optimizations": (
            "OpenGL Assembly Optimizations",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MESA_NO_ASM", "", "", ""),
            ),
        ),
        "opengl_3dnow_optimizations": (
            "OpenGL 3DNow Optimizations",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MESA_NO_3DNOW", "", "", ""),
            ),
        ),
        "opengl_mmx_optimizations": (
            "OpenGL MMX Optimizations",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MESA_NO_MMX", "", "", ""),
            ),
        ),
        "opengl_sse_optimizations": (
            "OpenGL SSE Optimizations",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MESA_NO_SSE", "", "", ""),
            ),
        ),
        "opengl_gamma_correction": (
            "OpenGL Gamma Correction",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_GAMMA", "", "", ""),
            ),
        ),
        "opengl_allow_draw_out_of_order": (
            "OpenGL Allow Draw Out of Order",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_draw_out_of_order", "", "", ""),
            ),
        ),
        "opengl_allow_glsl_builtin_constant_expression": (
            "OpenGL Allow GLSL Built-in Constant Expression",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_glsl_builtin_const_expression", "", "", ""),
            ),
        ),
        "opengl_allow_glsl_builtin_variable_redeclaration": (
            "OpenGL Allow GLSL Built-in Variable Redeclaration",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_glsl_builtin_variable_redeclaration", "", "", ""),
            ),
        ),
        "opengl_allow_glsl_compatibility_shaders": (
            "OpenGL Allow GLSL Compatibility Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_glsl_compat_shaders", "", "", ""),
            ),
        ),
        "opengl_allow_glsl_cross_stage_interpolation_mismatch": (
            "OpenGL Allow GLSL Cross-Stage Interpolation Mismatch",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_glsl_cross_stage_interpolation_mismatch", "", "", ""),
            ),
        ),
        "opengl_allow_glsl_layout_qualifier_on_function_parameters": (
            "OpenGL Allow GLSL Layout Qualifier on Function Parameters",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_glsl_layout_qualifier_on_function_parameters", "", "", ""),
            ),
        ),
        "opengl_allow_glsl_relaxed_es": (
            "OpenGL Allow GLSL Relaxed ES",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_glsl_relaxed_es", "", "", ""),
            ),
        ),
        "opengl_allow_higher_compatibility_version": (
            "OpenGL Allow Higher Compatibility Version",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_higher_compat_version", "", "", ""),
            ),
        ),
        "opengl_allow_incorrect_primitive_identifier": (
            "OpenGL Allow Incorrect Primitive Identifier",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_incorrect_primitive_id", "", "", ""),
            ),
        ),
        "opengl_allow_multisampled_copy_texture_image": (
            "OpenGL Allow Multisampled Copy Texture Image",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_multisampled_copyteximage", "", "", ""),
            ),
        ),
        "opengl_allow_rgb10_configurations": (
            "OpenGL Allow RGB10 Configurations",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_rgb10_configs", "", "", ""),
            ),
        ),
        "opengl_allow_rgb565_configurations": (
            "OpenGL Allow RGB565 Configurations",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_rgb565_configs", "", "", ""),
            ),
        ),
        "opengl_allow_vertex_texture_bias": (
            "OpenGL Allow Vertex Texture Bias",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_vertex_texture_bias", "", "", ""),
            ),
        ),
        "opengl_allow_extra_preprocessor_tokens": (
            "OpenGL Allow Extra Preprocessor Tokens",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_extra_pp_tokens", "", "", ""),
            ),
        ),
        "opengl_allow_fp16_configurations": (
            "OpenGL Allow FP16 Configurations",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_fp16_configs", "", "", ""),
            ),
        ),
        "opengl_allow_glsl_120_subset_in_110": (
            "OpenGL Allow GLSL 1.20 Subset in 1.10",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_glsl_120_subset_in_110", "", "", ""),
            ),
        ),
        "opengl_allow_compressed_fallback": (
            "OpenGL Allow Compressed Fallback",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "allow_compressed_fallback", "", "", ""),
            ),
        ),
        "opengl_always_flush_batch": (
            "OpenGL Always Flush Batch",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "always_flush_batch", "", "", ""),
            ),
        ),
        "opengl_always_flush_cache": (
            "OpenGL Always Flush Cache",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "always_flush_cache", "", "", ""),
            ),
        ),
        "opengl_always_have_depth_buffer": (
            "OpenGL Always Have Depth Buffer",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "always_have_depth_buffer", "", "", ""),
            ),
        ),
        "opengl_block_on_depleted_buffers": (
            "OpenGL Block on Depleted Buffers",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "block_on_depleted_buffers", "", "", ""),
            ),
        ),
        "opengl_disable_arb_gpu_shader5": (
            "OpenGL Disable ARB GPU Shader5",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "disable_arb_gpu_shader5", "", "", ""),
            ),
        ),
        "opengl_disable_blend_function_extended": (
            "OpenGL Disable Blend Function Extended",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "disable_blend_func_extended", "", "", ""),
            ),
        ),
        "opengl_disable_glsl_line_continuations": (
            "OpenGL Disable GLSL Line Continuations",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "disable_glsl_line_continuations", "", "", ""),
            ),
        ),
        "opengl_disable_shader_bit_encoding": (
            "OpenGL Disable Shader Bit Encoding",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "disable_shader_bit_encoding", "", "", ""),
            ),
        ),
        "opengl_disable_uniform_array_resize": (
            "OpenGL Disable Uniform Array Resize",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "disable_uniform_array_resize", "", "", ""),
            ),
        ),
        "opengl_dead_code_elimination_before_clip_cull_analysis": (
            "OpenGL Dead Code Elimination Before Clip Cull Analysis",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "do_dce_before_clip_cull_analysis", "", "", ""),
            ),
        ),
        "opengl_dual_color_blend_by_location": (
            "OpenGL Dual Color Blend by Location",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "dual_color_blend_by_location", "", "", ""),
            ),
        ),
        "opengl_force_compatibility_profile": (
            "OpenGL Force Compatibility Profile",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "force_compat_profile", "", "", ""),
            ),
        ),
        "opengl_force_compatibility_shaders": (
            "OpenGL Force Compatibility Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "force_compat_shaders", "", "", ""),
            ),
        ),
        "opengl_force_depth_component_type_integer": (
            "OpenGL Force Depth Component Type Integer",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "force_gl_depth_component_type_int", "", "", ""),
            ),
        ),
        "opengl_force_map_buffer_synchronized": (
            "OpenGL Force Map Buffer Synchronized",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "force_gl_map_buffer_synchronized", "", "", ""),
            ),
        ),
        "opengl_force_renderer_string": (
            "OpenGL Force Renderer String",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "force_gl_renderer", "", "", ""),
            ),
        ),
        "opengl_force_vendor_string": (
            "OpenGL Force Vendor String",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "force_gl_vendor", "", "", ""),
            ),
        ),
        "opengl_force_glsl_absolute_square_root": (
            "OpenGL Force GLSL Absolute Square Root",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "force_glsl_abs_sqrt", "", "", ""),
            ),
        ),
        "opengl_force_glsl_extensions_warn": (
            "OpenGL Force GLSL Extensions Warn",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "force_glsl_extensions_warn", "", "", ""),
            ),
        ),
        "opengl_force_integer_texture_nearest": (
            "OpenGL Force Integer Texture Nearest",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "force_integer_tex_nearest", "", "", ""),
            ),
        ),
        "opengl_format_l8_srgb_enable_readback": (
            "OpenGL Format L8 sRGB Enable Readback",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "format_l8_srgb_enable_readback", "", "", ""),
            ),
        ),
        "opengl_fp64_workaround": (
            "OpenGL FP64 Workaround",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "fp64_workaround_enabled", "", "", ""),
            ),
        ),
        "opengl_gles_apply_bgra_destination_swizzle": (
            "OpenGL GLES Apply BGRA Destination Swizzle",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "gles_apply_bgra_dest_swizzle", "", "", ""),
            ),
        ),
        "opengl_gles_emulate_bgra": (
            "OpenGL GLES Emulate BGRA",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "gles_emulate_bgra", "", "", ""),
            ),
        ),
        "opengl_gles_samples_passed_value": (
            "OpenGL GLES Samples Passed Value",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "gles_samples_passed_value", "", "", ""),
            ),
        ),
        "opengl_ignore_discard_framebuffer": (
            "OpenGL Ignore Discard Framebuffer",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "ignore_discard_framebuffer", "", "", ""),
            ),
        ),
        "opengl_ignore_map_unsynchronized": (
            "OpenGL Ignore Map Unsynchronized",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "ignore_map_unsynchronized", "", "", ""),
            ),
        ),
        "opengl_indirect_extension_override": (
            "OpenGL Indirect Extension Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "indirect_gl_extension_override", "", "", ""),
            ),
        ),
        "opengl_limit_trigonometric_input_range": (
            "OpenGL Limit Trigonometric Input Range",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "limit_trig_input_range", "", "", ""),
            ),
        ),
        "opengl_lower_depth_range_rate": (
            "OpenGL Lower Depth Range Rate",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "lower_depth_range_rate", "", "", ""),
            ),
        ),
        "opengl_no_16bit": (
            "OpenGL No 16-Bit Arithmetic",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "no_16bit", "", "", ""),
            ),
        ),
        "opengl_no_fp16": (
            "OpenGL No FP16 Operations",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "no_fp16", "", "", ""),
            ),
        ),
        "opengl_shader_optimization_level": (
            "OpenGL Shader Optimization Level",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
            ),
            (
                ("environment_variable", "opt", "", "", ""),
            ),
        ),
        "opengl_precise_trigonometry": (
            "OpenGL Precise Trigonometry",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "precise_trig", "", "", ""),
            ),
        ),
        "opengl_postprocessing_cell_shading": (
            "OpenGL Post-Processing Cell Shading",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", "1"),
            ),
            (
                ("environment_variable", "pp_celshade", "", "", ""),
            ),
        ),
        "opengl_postprocessing_jimenez_mlaa": (
            "OpenGL Post-Processing Jimenez MLAA",
            (
                ("skip", None),
                ("default", ""),
                ("none", "0"),
                ("low", "2"),
                ("medium", "4"),
                ("high", "8"),
            ),
            (
                ("environment_variable", "pp_jimenezmlaa", "", "", ""),
            ),
        ),
        "opengl_postprocessing_jimenez_mlaa_color": (
            "OpenGL Post-Processing Jimenez MLAA Color",
            (
                ("skip", None),
                ("default", ""),
                ("none", "0"),
                ("low", "2"),
                ("medium", "4"),
                ("high", "8"),
            ),
            (
                ("environment_variable", "pp_jimenezmlaa_color", "", "", ""),
            ),
        ),
        "opengl_postprocessing_no_blue": (
            "OpenGL Post-Processing No Blue",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", "1"),
            ),
            (
                ("environment_variable", "pp_noblue", "", "", ""),
            ),
        ),
        "opengl_postprocessing_no_green": (
            "OpenGL Post-Processing No Green",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", "1"),
            ),
            (
                ("environment_variable", "pp_nogreen", "", "", ""),
            ),
        ),
        "opengl_postprocessing_no_red": (
            "OpenGL Post-Processing No Red",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", "1"),
            ),
            (
                ("environment_variable", "pp_nored", "", "", ""),
            ),
        ),
        "opengl_glsl_cache_disable_legacy": (
            "OpenGL GLSL Cache Disable (Legacy)",
            (
                ("skip", None),
                ("default", ""),
                ("off", "true"),
                ("on", "false"),
            ),
            (
                ("environment_variable", "MESA_GLSL_CACHE_DISABLE", "", "", ""),
            ),
        ),
        "opengl_glsl_cache_maximum_size_legacy": (
            "OpenGL GLSL Cache Maximum Size (Legacy)",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_GLSL_CACHE_MAX_SIZE", "", "", ""),
            ),
        ),
        "opengl_glsl_cache_directory_legacy": (
            "OpenGL GLSL Cache Directory (Legacy)",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_GLSL_CACHE_DIR", "", "", ""),
            ),
        ),
        "opengl_skip_argb_visuals": (
            "OpenGL Skip ARGB Visuals",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "XLIB_SKIP_ARGB_VISUALS", "", "", ""),
            ),
        ),
        "opengl_mesa_ci_visual": (
            "OpenGL Mesa CI Visual",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_CI_VISUAL", "", "", ""),
            ),
        ),
        "vulkan_presentation_mode": (
            "Vulkan Presentation Mode",
            (
                ("skip", None),
                ("default", ""),
                ("immediate", "immediate"),
                ("mailbox", "mailbox"),
                ("fifo", "fifo"),
                ("relaxed", "relaxed"),
            ),
            (
                ("environment_variable", "MESA_VK_WSI_PRESENT_MODE", "", "", ""),
            ),
        ),
        "vulkan_submission_thread": (
            "Vulkan Submission Thread",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_VK_ENABLE_SUBMIT_THREAD", "", "", ""),
            ),
        ),
        "vulkan_version_override": (
            "Vulkan Version Override",
            (
                ("skip", None),
                ("default", ""),
                ("1.0", "1.0"),
                ("1.1", "1.1"),
                ("1.2", "1.2"),
                ("1.3", "1.3"),
                ("1.4", "1.4"),
            ),
            (
                ("environment_variable", "MESA_VK_VERSION_OVERRIDE", "", "", ""),
            ),
        ),
        "vulkan_abort_on_device_loss": (
            "Vulkan Abort on Device Loss",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_VK_ABORT_ON_DEVICE_LOSS", "", "", ""),
            ),
        ),
        "vulkan_headless_swapchain": (
            "Vulkan Headless Swapchain",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_VK_WSI_HEADLESS_SWAPCHAIN", "", "", ""),
            ),
        ),
        "vulkan_shader_binary_validation": (
            "Vulkan Shader Binary Validation",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_VK_VALIDATE_SHADER_BINARIES", "", "", ""),
            ),
        ),
        "vulkan_device_select": (
            "Vulkan Device Select",
            (
                ("skip", None),
                ("default", ""),
                ("list", "list"),
            ),
            (
                ("environment_variable", "MESA_VK_DEVICE_SELECT", "", "", ""),
            ),
        ),
        "vulkan_device_select_force_default": (
            "Vulkan Device Select Force Default",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_VK_DEVICE_SELECT_FORCE_DEFAULT_DEVICE", "", "", ""),
            ),
        ),
        "vulkan_device_select_debug": (
            "Vulkan Device Select Debug",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_VK_DEVICE_SELECT_DEBUG", "", "", ""),
            ),
        ),
        "vulkan_trace_radeon_memory_visualizer": (
            "Vulkan Trace Radeon Memory Visualizer",
            (
                ("skip", None),
                ("default", ""),
                ("on", "rmv"),
            ),
            (
                ("environment_variable", "MESA_VK_TRACE", ",", "", ""),
            ),
        ),
        "vulkan_trace_radeon_gpu_profiler": (
            "Vulkan Trace Radeon GPU Profiler",
            (
                ("skip", None),
                ("default", ""),
                ("on", "rgp"),
            ),
            (
                ("environment_variable", "MESA_VK_TRACE", ",", "", ""),
            ),
        ),
        "vulkan_trace_radeon_raytracing_analyzer": (
            "Vulkan Trace Radeon Raytracing Analyzer",
            (
                ("skip", None),
                ("default", ""),
                ("on", "rra"),
            ),
            (
                ("environment_variable", "MESA_VK_TRACE", ",", "", ""),
            ),
        ),
        "vulkan_trace_context_roll": (
            "Vulkan Trace Context Roll",
            (
                ("skip", None),
                ("default", ""),
                ("on", "ctxroll"),
            ),
            (
                ("environment_variable", "MESA_VK_TRACE", ",", "", ""),
            ),
        ),
        "vulkan_trace_per_submit": (
            "Vulkan Trace Per Submit",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_VK_TRACE_PER_SUBMIT", "", "", ""),
            ),
        ),
        "vulkan_trace_frame": (
            "Vulkan Trace Frame",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_VK_TRACE_FRAME", "", "", ""),
            ),
        ),
        "vulkan_trace_trigger_file": (
            "Vulkan Trace Trigger File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_VK_TRACE_TRIGGER", "", "", ""),
            ),
        ),
        "vulkan_device_chooser_layer": (
            "Vulkan Device Chooser Layer",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "ENABLE_DEVICE_CHOOSER_LAYER", "", "", ""),
            ),
        ),
        "vulkan_mesa_overlay_layer": (
            "Vulkan Mesa Overlay Layer",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "ENABLE_VK_LAYER_MESA_OVERLAY", "", "", ""),
            ),
        ),
        "vulkan_mesa_overlay_layer_disable": (
            "Vulkan Mesa Overlay Layer Disable",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "DISABLE_VK_LAYER_MESA_OVERLAY", "", "", ""),
            ),
        ),
        "vulkan_hdr_wsi_layer": (
            "Vulkan HDR WSI Layer",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "ENABLE_HDR_WSI", "", "", ""),
            ),
        ),
        "vulkan_hdr_wsi_layer_disable": (
            "Vulkan HDR WSI Layer Disable",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "DISABLE_HDR_WSI", "", "", ""),
            ),
        ),
        "vulkan_device_selection_layer_disable": (
            "Vulkan Device Selection Layer Disable",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NODEVICE_SELECT", "", "", ""),
            ),
        ),
        "vulkan_layer_settings_path": (
            "Vulkan Layer Settings Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LAYER_SETTINGS_PATH", "", "", ""),
            ),
        ),
        "vulkan_icd_filenames": (
            "Vulkan ICD Filenames",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_ICD_FILENAMES", ":", "", ""),
            ),
        ),
        "vulkan_driver_files": (
            "Vulkan Driver Files",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_DRIVER_FILES", ":", "", ""),
            ),
        ),
        "vulkan_add_driver_files": (
            "Vulkan Add Driver Files",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_ADD_DRIVER_FILES", ":", "", ""),
            ),
        ),
        "vulkan_drivers_path": (
            "Vulkan Drivers Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_DRIVERS_PATH", ":", "", ""),
            ),
        ),
        "vulkan_layer_path": (
            "Vulkan Layer Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LAYER_PATH", ":", "", ""),
            ),
        ),
        "vulkan_add_layer_path": (
            "Vulkan Add Layer Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_ADD_LAYER_PATH", ":", "", ""),
            ),
        ),
        "vulkan_implicit_layer_path": (
            "Vulkan Implicit Layer Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_IMPLICIT_LAYER_PATH", ":", "", ""),
            ),
        ),
        "vulkan_add_implicit_layer_path": (
            "Vulkan Add Implicit Layer Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_ADD_IMPLICIT_LAYER_PATH", ":", "", ""),
            ),
        ),
        "vulkan_instance_layers": (
            "Vulkan Instance Layers",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_INSTANCE_LAYERS", ":", "", ""),
            ),
        ),
        "vulkan_layer_disables": (
            "Vulkan Layer Disables",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LAYER_DISABLES", ":", "", ""),
            ),
        ),
        "vulkan_layer_enables": (
            "Vulkan Layer Enables",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LAYER_ENABLES", ":", "", ""),
            ),
        ),
        "vulkan_mesa_overlay_configuration": (
            "Vulkan Mesa Overlay Configuration",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LAYER_MESA_OVERLAY_CONFIG", ",", "", ""),
            ),
        ),
        "vulkan_layer_message_identifier_filter": (
            "Vulkan Layer Message Identifier Filter",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LAYER_MESSAGE_ID_FILTER", ",", "", ""),
            ),
        ),
        "vulkan_loader_debug_all": (
            "Vulkan Loader Debug All",
            (
                ("skip", None),
                ("default", ""),
                ("on", "all"),
            ),
            (
                ("environment_variable", "VK_LOADER_DEBUG", ",", "", ""),
            ),
        ),
        "vulkan_loader_debug_error": (
            "Vulkan Loader Debug Error",
            (
                ("skip", None),
                ("default", ""),
                ("on", "error"),
            ),
            (
                ("environment_variable", "VK_LOADER_DEBUG", ",", "", ""),
            ),
        ),
        "vulkan_loader_debug_warning": (
            "Vulkan Loader Debug Warning",
            (
                ("skip", None),
                ("default", ""),
                ("on", "warn"),
            ),
            (
                ("environment_variable", "VK_LOADER_DEBUG", ",", "", ""),
            ),
        ),
        "vulkan_loader_debug_information": (
            "Vulkan Loader Debug Information",
            (
                ("skip", None),
                ("default", ""),
                ("on", "info"),
            ),
            (
                ("environment_variable", "VK_LOADER_DEBUG", ",", "", ""),
            ),
        ),
        "vulkan_loader_debug_verbose": (
            "Vulkan Loader Debug Verbose",
            (
                ("skip", None),
                ("default", ""),
                ("on", "debug"),
            ),
            (
                ("environment_variable", "VK_LOADER_DEBUG", ",", "", ""),
            ),
        ),
        "vulkan_loader_debug_performance": (
            "Vulkan Loader Debug Performance",
            (
                ("skip", None),
                ("default", ""),
                ("on", "perf"),
            ),
            (
                ("environment_variable", "VK_LOADER_DEBUG", ",", "", ""),
            ),
        ),
        "vulkan_loader_debug_environment": (
            "Vulkan Loader Debug Environment",
            (
                ("skip", None),
                ("default", ""),
                ("on", "environ"),
            ),
            (
                ("environment_variable", "VK_LOADER_DEBUG", ",", "", ""),
            ),
        ),
        "vulkan_loader_debug_prolog": (
            "Vulkan Loader Debug Prolog",
            (
                ("skip", None),
                ("default", ""),
                ("on", "prolog"),
            ),
            (
                ("environment_variable", "VK_LOADER_DEBUG", ",", "", ""),
            ),
        ),
        "vulkan_loader_debug_validate": (
            "Vulkan Loader Debug Validate",
            (
                ("skip", None),
                ("default", ""),
                ("on", "validate"),
            ),
            (
                ("environment_variable", "VK_LOADER_DEBUG", ",", "", ""),
            ),
        ),
        "vulkan_loader_debug_implementation": (
            "Vulkan Loader Debug Implementation",
            (
                ("skip", None),
                ("default", ""),
                ("on", "impl"),
            ),
            (
                ("environment_variable", "VK_LOADER_DEBUG", ",", "", ""),
            ),
        ),
        "vulkan_loader_layers_allow": (
            "Vulkan Loader Layers Allow",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LOADER_LAYERS_ALLOW", ":", "", ""),
            ),
        ),
        "vulkan_loader_layers_disable": (
            "Vulkan Loader Layers Disable",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LOADER_LAYERS_DISABLE", ":", "", ""),
            ),
        ),
        "vulkan_loader_layers_enable": (
            "Vulkan Loader Layers Enable",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LOADER_LAYERS_ENABLE", ":", "", ""),
            ),
        ),
        "vulkan_loader_drivers_select": (
            "Vulkan Loader Drivers Select",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LOADER_DRIVERS_SELECT", "", "", ""),
            ),
        ),
        "vulkan_loader_drivers_disable": (
            "Vulkan Loader Drivers Disable",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LOADER_DRIVERS_DISABLE", "", "", ""),
            ),
        ),
        "vulkan_loader_driver_identifier_filter": (
            "Vulkan Loader Driver Identifier Filter",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LOADER_DRIVER_ID_FILTER", "", "", ""),
            ),
        ),
        "vulkan_loader_device_identifier_filter": (
            "Vulkan Loader Device Identifier Filter",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LOADER_DEVICE_ID_FILTER", "", "", ""),
            ),
        ),
        "vulkan_loader_vendor_identifier_filter": (
            "Vulkan Loader Vendor Identifier Filter",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LOADER_VENDOR_ID_FILTER", "", "", ""),
            ),
        ),
        "vulkan_loader_disable_dynamic_library_unloading": (
            "Vulkan Loader Disable Dynamic Library Unloading",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VK_LOADER_DISABLE_DYNAMIC_LIBRARY_UNLOADING", "", "", ""),
            ),
        ),
        "vulkan_loader_disable_instance_extension_filter": (
            "Vulkan Loader Disable Instance Extension Filter",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VK_LOADER_DISABLE_INST_EXT_FILTER", "", "", ""),
            ),
        ),
        "vulkan_loader_disable_select": (
            "Vulkan Loader Disable Select",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VK_LOADER_DISABLE_SELECT", "", "", ""),
            ),
        ),
        "vulkan_screenshot_directory": (
            "Vulkan Screenshot Directory",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_SCREENSHOT_DIR", "", "", ""),
            ),
        ),
        "vulkan_screenshot_format": (
            "Vulkan Screenshot Format",
            (
                ("skip", None),
                ("default", ""),
                ("bmp", "bmp"),
                ("ppm", "ppm"),
            ),
            (
                ("environment_variable", "VK_SCREENSHOT_FORMAT", "", "", ""),
            ),
        ),
        "vulkan_screenshot_frames": (
            "Vulkan Screenshot Frames",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_SCREENSHOT_FRAMES", ",", "", ""),
            ),
        ),
        "vulkan_layer_fine_grained_locking": (
            "Vulkan Layer Fine-Grained Locking",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VK_LAYER_FINE_GRAINED_LOCKING", "", "", ""),
            ),
        ),
        "vulkan_layer_settings_debug": (
            "Vulkan Layer Settings Debug",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VK_LAYER_SETTINGS_DEBUG", "", "", ""),
            ),
        ),
        "vulkan_layer_duplicate_message_limit": (
            "Vulkan Layer Duplicate Message Limit",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VK_LAYER_DUPLICATE_MESSAGE_LIMIT", "", "", ""),
            ),
        ),
        "vulkan_crash_diagnostic": (
            "Vulkan Crash Diagnostic",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VK_CRASH_DIAGNOSTIC_ENABLE", "", "", ""),
            ),
        ),
        "vulkan_crash_diagnostic_disable": (
            "Vulkan Crash Diagnostic Disable",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VK_CRASH_DIAGNOSTIC_DISABLE", "", "", ""),
            ),
        ),
        "vulkan_device_index": (
            "Vulkan Device Index",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
            ),
            (
                ("environment_variable", "VULKAN_DEVICE_INDEX", "", "", ""),
            ),
        ),
        "vulkan_custom_border_colors_without_format": (
            "Vulkan Custom Border Colors Without Format",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "custom_border_colors_without_format", "", "", ""),
            ),
        ),
        "vulkan_fake_sparse_resources": (
            "Vulkan Fake Sparse Resources",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "fake_sparse", "", "", ""),
            ),
        ),
        "vulkan_force_vendor": (
            "Vulkan Force Vendor",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "force_vk_vendor", "", "", ""),
            ),
        ),
        "vulkan_force_indirect_descriptors": (
            "Vulkan Force Indirect Descriptors",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "force_indirect_descriptors", "", "", ""),
            ),
        ),
        "vulkan_disable_protected_content_check": (
            "Vulkan Disable Protected Content Check",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "disable_protected_content_check", "", "", ""),
            ),
        ),
        "vulkan_force_protected_content_check": (
            "Vulkan Force Protected Content Check",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "force_protected_content_check", "", "", ""),
            ),
        ),
        "vulkan_dont_care_as_load": (
            "Vulkan Don't Care as Load",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_dont_care_as_load", "", "", ""),
            ),
        ),
        "vulkan_khr_present_wait": (
            "Vulkan KHR Present Wait",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_khr_present_wait", "", "", ""),
            ),
        ),
        "vulkan_lower_terminate_to_discard": (
            "Vulkan Lower Terminate to Discard",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_lower_terminate_to_discard", "", "", ""),
            ),
        ),
        "vulkan_require_astc": (
            "Vulkan Require ASTC",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_require_astc", "", "", ""),
            ),
        ),
        "vulkan_require_etc2": (
            "Vulkan Require ETC2",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_require_etc2", "", "", ""),
            ),
        ),
        "vulkan_wsi_disable_unordered_submits": (
            "Vulkan WSI Disable Unordered Submits",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_wsi_disable_unordered_submits", "", "", ""),
            ),
        ),
        "vulkan_wsi_force_bgra8_unorm_first": (
            "Vulkan WSI Force BGRA8 UNORM First",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_wsi_force_bgra8_unorm_first", "", "", ""),
            ),
        ),
        "vulkan_wsi_force_swapchain_to_current_extent": (
            "Vulkan WSI Force Swapchain to Current Extent",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_wsi_force_swapchain_to_current_extent", "", "", ""),
            ),
        ),
        "vulkan_x11_ensure_minimum_image_count": (
            "Vulkan X11 Ensure Minimum Image Count",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_x11_ensure_min_image_count", "", "", ""),
            ),
        ),
        "vulkan_x11_ignore_suboptimal": (
            "Vulkan X11 Ignore Suboptimal",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_x11_ignore_suboptimal", "", "", ""),
            ),
        ),
        "vulkan_x11_override_minimum_image_count": (
            "Vulkan X11 Override Minimum Image Count",
            (
                ("skip", None),
                ("default", ""),
                ("2", "2"),
                ("3", "3"),
                ("4", "4"),
            ),
            (
                ("environment_variable", "vk_x11_override_min_image_count", "", "", ""),
            ),
        ),
        "vulkan_x11_strict_image_count": (
            "Vulkan X11 Strict Image Count",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_x11_strict_image_count", "", "", ""),
            ),
        ),
        "vulkan_xwayland_wait_ready": (
            "Vulkan XWayland Wait Ready",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_xwayland_wait_ready", "", "", ""),
            ),
        ),
        "vulkan_zero_vram": (
            "Vulkan Zero VRAM",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vk_zero_vram", "", "", ""),
            ),
        ),
        "shader_precompile": (
            "Shader Precompile",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "shader_precompile", "", "", ""),
            ),
        ),
        "shader_spilling_rate": (
            "Shader Spilling Rate",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "shader_spilling_rate", "", "", ""),
            ),
        ),
        "transcode_astc": (
            "Transcode ASTC",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "transcode_astc", "", "", ""),
            ),
        ),
        "transcode_etc": (
            "Transcode ETC",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "transcode_etc", "", "", ""),
            ),
        ),
        "vertex_shader_position_always_invariant": (
            "Vertex Shader Position Always Invariant",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vs_position_always_invariant", "", "", ""),
            ),
        ),
        "vertex_shader_position_always_precise": (
            "Vertex Shader Position Always Precise",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "vs_position_always_precise", "", "", ""),
            ),
        ),
        "vertex_program_default_output": (
            "Vertex Program Default Output",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "vertex_program_default_out", "", "", ""),
            ),
        ),
        "alias_shader_extension": (
            "Alias Shader Extension",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "alias_shader_extension", "", "", ""),
            ),
        ),
        "disable_throttling": (
            "Disable Throttling",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "disable_throttling", "", "", ""),
            ),
        ),
        "disable_explicit_synchronization_heuristic": (
            "Disable Explicit Synchronization Heuristic",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "disable_explicit_sync_heuristic", "", "", ""),
            ),
        ),
        "compression_control": (
            "Compression Control",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "compression_control_enabled", "", "", ""),
            ),
        ),
        "generated_indirect_ring_threshold": (
            "Generated Indirect Ring Threshold",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "generated_indirect_ring_threshold", "", "", ""),
            ),
        ),
        "generated_indirect_threshold": (
            "Generated Indirect Threshold",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "generated_indirect_threshold", "", "", ""),
            ),
        ),
        "egl_platform": (
            "EGL Platform",
            (
                ("skip", None),
                ("default", ""),
                ("x11", "x11"),
                ("wayland", "wayland"),
                ("drm", "drm"),
                ("surfaceless", "surfaceless"),
                ("device", "device"),
            ),
            (
                ("environment_variable", "EGL_PLATFORM", "", "", ""),
            ),
        ),
        "egl_log_level": (
            "EGL Log Level",
            (
                ("skip", None),
                ("default", ""),
                ("fatal", "fatal"),
                ("warning", "warning"),
                ("information", "info"),
                ("debug", "debug"),
            ),
            (
                ("environment_variable", "EGL_LOG_LEVEL", "", "", ""),
            ),
        ),
        "egl_driver": (
            "EGL Driver",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "EGL_DRIVER", "", "", ""),
            ),
        ),
        "egl_software_rendering": (
            "EGL Software Rendering",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "EGL_SOFTWARE", "", "", ""),
            ),
        ),
        "egl_drivers_path": (
            "EGL Drivers Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "EGL_DRIVERS_PATH", ":", "", ""),
            ),
        ),
        "egl_external_platform_configuration_directories": (
            "EGL External Platform Configuration Directories",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__EGL_EXTERNAL_PLATFORM_CONFIG_DIRS", "", "", ""),
            ),
        ),
        "egl_vendor_library_filenames": (
            "EGL Vendor Library Filenames",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__EGL_VENDOR_LIBRARY_FILENAMES", ":", "", ""),
            ),
        ),
        "egl_vendor_library_directories": (
            "EGL Vendor Library Directories",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__EGL_VENDOR_LIBRARY_DIRS", ":", "", ""),
            ),
        ),
        "gbm_backend": (
            "GBM Backend",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "GBM_BACKEND", "", "", ""),
            ),
        ),
        "gbm_backends_path": (
            "GBM Backends Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "GBM_BACKENDS_PATH", "", "", ""),
            ),
        ),
        "dri_prime_gpu_selection": (
            "DRI PRIME GPU Selection",
            (
                ("skip", None),
                ("default", ""),
                ("integrated", "0"),
                ("discrete", "1"),
            ),
            (
                ("environment_variable", "DRI_PRIME", "", "", ""),
            ),
        ),
        "dri_prime_debug": (
            "DRI PRIME Debug",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "DRI_PRIME_DEBUG", "", "", ""),
            ),
        ),
        "dri_driver_override": (
            "DRI Driver Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "dri_driver", "", "", ""),
            ),
        ),
        "driver_configuration_directory": (
            "Driver Configuration Directory",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "DRIRC_CONFIGDIR", "", "", ""),
            ),
        ),
        "libdrm_debug": (
            "LibDRM Debug",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LIBDRM_DEBUG", "", "", ""),
            ),
        ),
        "process_name_override": (
            "Process Name Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_PROCESS_NAME", "", "", ""),
            ),
        ),
        "driver_configuration_executable_override": (
            "Driver Configuration Executable Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_DRICONF_EXECUTABLE_OVERRIDE", "", "", ""),
            ),
        ),
        "mesa_debug_output": (
            "Mesa Debug Output",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_DEBUG", "", "", ""),
            ),
        ),
        "mesa_debug_silent": (
            "Mesa Debug Silent",
            (
                ("skip", None),
                ("default", ""),
                ("on", "silent"),
            ),
            (
                ("environment_variable", "MESA_DEBUG", ",", "", ""),
            ),
        ),
        "mesa_debug_flush": (
            "Mesa Debug Flush",
            (
                ("skip", None),
                ("default", ""),
                ("on", "flush"),
            ),
            (
                ("environment_variable", "MESA_DEBUG", ",", "", ""),
            ),
        ),
        "mesa_debug_opengl_error": (
            "Mesa Debug OpenGL Error",
            (
                ("skip", None),
                ("default", ""),
                ("on", "gl_error"),
            ),
            (
                ("environment_variable", "MESA_DEBUG", ",", "", ""),
            ),
        ),
        "mesa_log_file": (
            "Mesa Log File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_LOG_FILE", "", "", ""),
            ),
        ),
        "mesa_log_level": (
            "Mesa Log Level",
            (
                ("skip", None),
                ("default", ""),
                ("debug", "debug"),
                ("information", "info"),
                ("warning", "warning"),
            ),
            (
                ("environment_variable", "MESA_LOG_LEVEL", "", "", ""),
            ),
        ),
        "mesa_log_file_automatic": (
            "Mesa Log File Automatic",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_LOG_FILE_AUTO", "", "", ""),
            ),
        ),
        "mesa_log_prefix": (
            "Mesa Log Prefix",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_LOG_PREFIX", ",", "", ""),
            ),
        ),
        "mesa_spirv_log_level": (
            "SPIR-V Log Level",
            (
                ("skip", None),
                ("default", ""),
                ("none", "none"),
                ("warning", "warning"),
                ("information", "info"),
                ("debug", "debug"),
            ),
            (
                ("environment_variable", "MESA_SPIRV_LOG_LEVEL", "", "", ""),
            ),
        ),
        "mesa_spirv_dump_path": (
            "SPIR-V Dump Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_SPIRV_DUMP_PATH", "", "", ""),
            ),
        ),
        "mesa_spirv_read_path": (
            "SPIR-V Read Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_SPIRV_READ_PATH", "", "", ""),
            ),
        ),
        "d3d12_default_adapter_name": (
            "D3D12 Default Adapter Name",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_D3D12_DEFAULT_ADAPTER_NAME", "", "", ""),
            ),
        ),
        "driver_override": (
            "Driver Override",
            (
                ("skip", None),
                ("default", ""),
                ("zink", "zink"),
                ("radeonsi", "radeonsi"),
                ("iris", "iris"),
                ("crocus", "crocus"),
                ("nouveau", "nouveau"),
                ("i915", "i915"),
                ("r600", "r600"),
                ("etnaviv", "etnaviv"),
                ("freedreno", "freedreno"),
                ("lima", "lima"),
                ("panfrost", "panfrost"),
                ("v3d", "v3d"),
                ("vc4", "vc4"),
                ("virgl", "virgl"),
                ("svga", "svga"),
                ("softpipe", "softpipe"),
                ("llvmpipe", "llvmpipe"),
            ),
            (
                ("environment_variable", "MESA_LOADER_DRIVER_OVERRIDE", "", "", ""),
            ),
        ),
        "device_identifier_override": (
            "Device Identifier Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "device_id", "", "", ""),
            ),
        ),
        "override_vram_size": (
            "Override VRAM Size",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "override_vram_size", "", "", ""),
            ),
        ),
        "shader_disk_cache": (
            "Shader Disk Cache",
            (
                ("skip", None),
                ("default", ""),
                ("off", "true"),
                ("on", "false"),
            ),
            (
                ("environment_variable", "MESA_SHADER_CACHE_DISABLE", "", "", ""),
            ),
        ),
        "shader_disk_cache_maximum_size": (
            "Shader Disk Cache Maximum Size",
            (
                ("skip", None),
                ("default", ""),
                ("100M", "100M"),
                ("256M", "256M"),
                ("512M", "512M"),
                ("1G", "1G"),
                ("2G", "2G"),
                ("5G", "5G"),
                ("10G", "10G"),
            ),
            (
                ("environment_variable", "MESA_SHADER_CACHE_MAX_SIZE", "", "", ""),
            ),
        ),
        "shader_disk_cache_directory": (
            "Shader Disk Cache Directory",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_SHADER_CACHE_DIR", "", "", ""),
            ),
        ),
        "shader_cache_statistics": (
            "Shader Cache Statistics",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "MESA_SHADER_CACHE_SHOW_STATS", "", "", ""),
            ),
        ),
        "disk_cache_fossilize_format": (
            "Disk Cache Fossilize Format",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_DISK_CACHE_SINGLE_FILE", "", "", ""),
            ),
        ),
        "disk_cache_multi_file": (
            "Disk Cache Multi File",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_DISK_CACHE_MULTI_FILE", "", "", ""),
            ),
        ),
        "disk_cache_mesa_database": (
            "Disk Cache Mesa Database",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_DISK_CACHE_DATABASE", "", "", ""),
            ),
        ),
        "disk_cache_database_partitions": (
            "Disk Cache Database Partitions",
            (
                ("skip", None),
                ("default", ""),
                ("10", "10"),
                ("25", "25"),
                ("50", "50"),
                ("100", "100"),
            ),
            (
                ("environment_variable", "MESA_DISK_CACHE_DATABASE_NUM_PARTS", "", "", ""),
            ),
        ),
        "disk_cache_eviction_period": (
            "Disk Cache Eviction Period",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_DISK_CACHE_DATABASE_EVICTION_SCORE_2X_PERIOD", "", "", ""),
            ),
        ),
        "disk_cache_readonly_fossilize_dynamic_list": (
            "Disk Cache Read-Only Fossilize Dynamic List",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_DISK_CACHE_READ_ONLY_FOZ_DBS_DYNAMIC_LIST", "", "", ""),
            ),
        ),
        "disk_cache_readonly_fossilize_databases": (
            "Disk Cache Read-Only Fossilize Databases",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_DISK_CACHE_READ_ONLY_FOZ_DBS", ":", "", ""),
            ),
        ),
        "disk_cache_combine_readwrite_with_readonly_fossilize": (
            "Disk Cache Combine Read-Write with Read-Only Fossilize",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", "1"),
            ),
            (
                ("environment_variable", "MESA_DISK_CACHE_COMBINE_RW_WITH_RO_FOZ", "", "", ""),
            ),
        ),
        "shader_capture_path": (
            "Shader Capture Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_SHADER_CAPTURE_PATH", "", "", ""),
            ),
        ),
        "shader_dump_path": (
            "Shader Dump Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_SHADER_DUMP_PATH", "", "", ""),
            ),
        ),
        "shader_read_path": (
            "Shader Read Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MESA_SHADER_READ_PATH", "", "", ""),
            ),
        ),
        "jit_symbol_map_directory": (
            "JIT Symbol Map Directory",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "JIT_SYMBOL_MAP_DIR", "", "", ""),
            ),
        ),
        "draw_fast_shader_execution": (
            "Draw Fast Shader Execution",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "DRAW_FSE", "", "", ""),
            ),
        ),
        "draw_no_fast_shader_execution": (
            "Draw No Fast Shader Execution",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "DRAW_NO_FSE", "", "", ""),
            ),
        ),
        "draw_use_llvm": (
            "Draw Use LLVM",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "DRAW_USE_LLVM", "", "", ""),
            ),
        ),
        "nir_print": (
            "NIR Print",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NIR_PRINT", "", "", ""),
            ),
        ),
        "nir_validate": (
            "NIR Validate",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "nir_validate", "", "", ""),
            ),
        ),
        "nir_test_clone": (
            "NIR Test Clone",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NIR_TEST_CLONE", "", "", ""),
            ),
        ),
        "nir_test_serialize": (
            "NIR Test Serialize",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NIR_TEST_SERIALIZE", "", "", ""),
            ),
        ),
        "nir_debug_clone": (
            "NIR Debug Clone",
            (
                ("skip", None),
                ("default", ""),
                ("on", "clone"),
            ),
            (
                ("environment_variable", "NIR_DEBUG", ",", "", ""),
            ),
        ),
        "nir_debug_serialize": (
            "NIR Debug Serialize",
            (
                ("skip", None),
                ("default", ""),
                ("on", "serialize"),
            ),
            (
                ("environment_variable", "NIR_DEBUG", ",", "", ""),
            ),
        ),
        "nir_debug_no_validate": (
            "NIR Debug No Validate",
            (
                ("skip", None),
                ("default", ""),
                ("on", "novalidate"),
            ),
            (
                ("environment_variable", "NIR_DEBUG", ",", "", ""),
            ),
        ),
        "nir_debug_validate_ssa": (
            "NIR Debug Validate SSA",
            (
                ("skip", None),
                ("default", ""),
                ("on", "validate_ssa"),
            ),
            (
                ("environment_variable", "NIR_DEBUG", ",", "", ""),
            ),
        ),
        "nir_debug_tgsi": (
            "NIR Debug TGSI",
            (
                ("skip", None),
                ("default", ""),
                ("on", "tgsi"),
            ),
            (
                ("environment_variable", "NIR_DEBUG", ",", "", ""),
            ),
        ),
        "nir_debug_print_vertex_shader": (
            "NIR Debug Print Vertex Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "print_vs"),
            ),
            (
                ("environment_variable", "NIR_DEBUG", ",", "", ""),
            ),
        ),
        "nir_debug_print_tessellation_control_shader": (
            "NIR Debug Print Tessellation Control Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "print_tcs"),
            ),
            (
                ("environment_variable", "NIR_DEBUG", ",", "", ""),
            ),
        ),
        "nir_debug_print_tessellation_evaluation_shader": (
            "NIR Debug Print Tessellation Evaluation Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "print_tes"),
            ),
            (
                ("environment_variable", "NIR_DEBUG", ",", "", ""),
            ),
        ),
        "nir_debug_print_geometry_shader": (
            "NIR Debug Print Geometry Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "print_gs"),
            ),
            (
                ("environment_variable", "NIR_DEBUG", ",", "", ""),
            ),
        ),
        "nir_debug_print_fragment_shader": (
            "NIR Debug Print Fragment Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "print_fs"),
            ),
            (
                ("environment_variable", "NIR_DEBUG", ",", "", ""),
            ),
        ),
        "nir_debug_print_compute_shader": (
            "NIR Debug Print Compute Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "print_cs"),
            ),
            (
                ("environment_variable", "NIR_DEBUG", ",", "", ""),
            ),
        ),
        "nir_skip_passes": (
            "NIR Skip Passes",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "NIR_SKIP", ",", "", ""),
            ),
        ),
        "tgsi_print_sanity": (
            "TGSI Print Sanity",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "TGSI_PRINT_SANITY", "", "", ""),
            ),
        ),
        "state_tracker_debug_no_optimization": (
            "State Tracker Debug No Optimization",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nopt"),
            ),
            (
                ("environment_variable", "ST_DEBUG", ",", "", ""),
            ),
        ),
        "state_tracker_debug_print_intermediate_representation": (
            "State Tracker Debug Print IR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "tgsi"),
            ),
            (
                ("environment_variable", "ST_DEBUG", ",", "", ""),
            ),
        ),
        "gallium_software_renderer": (
            "Gallium Software Renderer",
            (
                ("skip", None),
                ("default", ""),
                ("softpipe", "softpipe"),
                ("llvmpipe", "llvmpipe"),
            ),
            (
                ("environment_variable", "GALLIUM_DRIVER", "", "", ""),
            ),
        ),
        "gallium_overlay_default_visibility": (
            "Gallium Overlay Default Visibility",
            (
                ("skip", None),
                ("default", ""),
                ("visible", "true"),
                ("hidden", "false"),
            ),
            (
                ("environment_variable", "GALLIUM_HUD_VISIBLE", "", "", ""),
            ),
        ),
        "gallium_overlay_update_period": (
            "Gallium Overlay Update Period",
            (
                ("skip", None),
                ("default", ""),
                ("realtime", "0"),
                ("0.1", "0.1"),
                ("0.25", "0.25"),
                ("0.5", "0.5"),
                ("1.0", "1.0"),
                ("2.0", "2.0"),
            ),
            (
                ("environment_variable", "GALLIUM_HUD_PERIOD", "", "", ""),
            ),
        ),
        "gallium_overlay_opacity": (
            "Gallium Overlay Opacity",
            (
                ("skip", None),
                ("default", ""),
                ("25", "25"),
                ("50", "50"),
                ("66", "66"),
                ("75", "75"),
                ("100", "100"),
            ),
            (
                ("environment_variable", "GALLIUM_HUD_OPACITY", "", "", ""),
            ),
        ),
        "gallium_overlay_toggle_signal": (
            "Gallium Overlay Toggle Signal",
            (
                ("skip", None),
                ("default", ""),
                ("sigusr1", "10"),
                ("sigusr2", "12"),
            ),
            (
                ("environment_variable", "GALLIUM_HUD_TOGGLE_SIGNAL", "", "", ""),
            ),
        ),
        "gallium_overlay_scale": (
            "Gallium Overlay Scale",
            (
                ("skip", None),
                ("default", ""),
                ("1x", "1"),
                ("2x", "2"),
                ("3x", "3"),
                ("4x", "4"),
            ),
            (
                ("environment_variable", "GALLIUM_HUD_SCALE", "", "", ""),
            ),
        ),
        "gallium_overlay_rotation": (
            "Gallium Overlay Rotation",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("90", "90"),
                ("180", "180"),
                ("270", "270"),
            ),
            (
                ("environment_variable", "GALLIUM_HUD_ROTATION", "", "", ""),
            ),
        ),
        "gallium_overlay_dump_directory": (
            "Gallium Overlay Dump Directory",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "GALLIUM_HUD_DUMP_DIR", "", "", ""),
            ),
        ),
        "gallium_performance_overlay": (
            "Gallium Performance Overlay",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("fps", "fps"),
                ("fps-and-cpu", "fps,cpu"),
                ("full", "fps,cpu,GPU-load"),
                ("timing", "fps,frametime"),
                ("extended", "fps,cpu,GPU-load,VRAM-usage"),
            ),
            (
                ("environment_variable", "GALLIUM_HUD", ",", "", ""),
            ),
        ),
        "gallium_print_options": (
            "Gallium Print Options",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "GALLIUM_PRINT_OPTIONS", "", "", ""),
            ),
        ),
        "gallium_log_file": (
            "Gallium Log File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "GALLIUM_LOG_FILE", "", "", ""),
            ),
        ),
        "gallium_trace": (
            "Gallium Trace",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "GALLIUM_TRACE", "", "", ""),
            ),
        ),
        "gallium_trace_threaded_context": (
            "Gallium Trace Threaded Context",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "GALLIUM_TRACE_TC", "", "", ""),
            ),
        ),
        "gallium_trace_trigger": (
            "Gallium Trace Trigger",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "GALLIUM_TRACE_TRIGGER", "", "", ""),
            ),
        ),
        "gallium_dump_cpu": (
            "Gallium Dump CPU",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "GALLIUM_DUMP_CPU", "", "", ""),
            ),
        ),
        "gallium_override_cpu_capabilities": (
            "Gallium Override CPU Capabilities",
            (
                ("skip", None),
                ("default", ""),
                ("nosse", "nosse"),
                ("sse", "sse"),
                ("sse2", "sse2"),
                ("sse3", "sse3"),
                ("ssse3", "ssse3"),
                ("sse4.1", "sse4.1"),
                ("avx", "avx"),
            ),
            (
                ("environment_variable", "GALLIUM_OVERRIDE_CPU_CAPS", "", "", ""),
            ),
        ),
        "gallium_pipe_search_directory": (
            "Gallium Pipe Search Directory",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "GALLIUM_PIPE_SEARCH_DIR", "", "", ""),
            ),
        ),
        "gallium_multisample_antialiasing": (
            "Gallium Multisample Antialiasing",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("2", "2"),
                ("4", "4"),
                ("8", "8"),
                ("16", "16"),
            ),
            (
                ("environment_variable", "GALLIUM_MSAA", "", "", ""),
            ),
        ),
        "gallium_no_lazy_evaluation": (
            "Gallium No Lazy Evaluation",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "GALLIUM_NOLAZY", "", "", ""),
            ),
        ),
        "gallium_no_powerpc_optimizations": (
            "Gallium No PowerPC Optimizations",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "GALLIUM_NOPPC", "", "", ""),
            ),
        ),
        "gallium_no_sse": (
            "Gallium No SSE",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "GALLIUM_NOSSE", "", "", ""),
            ),
        ),
        "amd_vulkan_driver_selection": (
            "AMD Vulkan Driver Selection",
            (
                ("skip", None),
                ("default", ""),
                ("radv", "RADV"),
                ("amdvlk", "AMDVLK"),
            ),
            (
                ("environment_variable", "AMD_VULKAN_ICD", "", "", ""),
            ),
        ),
        "amd_force_variable_rate_shading": (
            "AMD Force Variable Rate Shading",
            (
                ("skip", None),
                ("default", ""),
                ("1x1", "1x1"),
                ("1x2", "1x2"),
                ("2x1", "2x1"),
                ("2x2", "2x2"),
            ),
            (
                ("environment_variable", "AMD_FORCE_VRS", "", "", ""),
            ),
        ),
        "amd_texture_anisotropy": (
            "AMD Texture Anisotropy",
            (
                ("skip", None),
                ("default", ""),
                ("1", "1"),
                ("2", "2"),
                ("4", "4"),
                ("8", "8"),
                ("16", "16"),
            ),
            (
                ("environment_variable", "AMD_TEX_ANISO", "", "", ""),
            ),
        ),
        "amd_debug_directory": (
            "AMD Debug Directory",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "AMD_DEBUG_DIR", "", "", ""),
            ),
        ),
        "amd_configuration_directory": (
            "AMD Configuration Directory",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "AMD_CONFIG_DIR", "", "", ""),
            ),
        ),
        "amd_debug_no_shader_prolog": (
            "AMD Debug No Shader Prolog",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no_shader_prolog"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_shaders": (
            "AMD Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_precompile": (
            "AMD Debug Precompile",
            (
                ("skip", None),
                ("default", ""),
                ("on", "precompile"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_vertex_shader": (
            "AMD Debug Vertex Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "vs"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_pixel_shader": (
            "AMD Debug Pixel Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "ps"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_compute_shader": (
            "AMD Debug Compute Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "cs"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_geometry_shader": (
            "AMD Debug Geometry Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "gs"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_tessellation_control_shader": (
            "AMD Debug Tessellation Control Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "tcs"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_tessellation_evaluation_shader": (
            "AMD Debug Tessellation Evaluation Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "tes"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_nir": (
            "AMD Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_llvm": (
            "AMD Debug LLVM",
            (
                ("skip", None),
                ("default", ""),
                ("on", "llvm"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_no_binary_export": (
            "AMD Debug No Binary Export",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nobinexport"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_no_cache": (
            "AMD Debug No Cache",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nocache"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_no_compute": (
            "AMD Debug No Compute",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nocompute"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_no_delta_color_compression": (
            "AMD Debug No Delta Color Compression",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nodcc"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_no_next_generation_geometry": (
            "AMD Debug No Next Generation Geometry",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nongg"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "amd_debug_reserve_vmid": (
            "AMD Debug Reserve VMID",
            (
                ("skip", None),
                ("default", ""),
                ("on", "reserve_vmid"),
            ),
            (
                ("environment_variable", "AMD_DEBUG", ",", "", ""),
            ),
        ),
        "radeonsi_infinite_interpolation_fix": (
            "RadeonSI Infinite Interpolation Fix",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radeonsi_no_infinite_interp", "", "", ""),
            ),
        ),
        "radeonsi_clamp_division_by_zero": (
            "RadeonSI Clamp Division by Zero",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radeonsi_clamp_div_by_zero", "", "", ""),
            ),
        ),
        "radeonsi_clear_video_memory": (
            "RadeonSI Clear Video Memory",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radeonsi_zerovram", "", "", ""),
            ),
        ),
        "radeonsi_assume_no_z_fighting": (
            "RadeonSI Assume No Z-Fighting",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radeonsi_assume_no_z_fights", "", "", ""),
            ),
        ),
        "radeonsi_commutative_blend_add": (
            "RadeonSI Commutative Blend Add",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radeonsi_commutative_blend_add", "", "", ""),
            ),
        ),
        "radeonsi_si_scheduler": (
            "RadeonSI SI Scheduler",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radeonsi_enable_sisched", "", "", ""),
            ),
        ),
        "radeonsi_force_fma32": (
            "RadeonSI Force FMA32",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radeonsi_force_use_fma32", "", "", ""),
            ),
        ),
        "radeonsi_synchronous_compile": (
            "RadeonSI Synchronous Compile",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radeonsi_sync_compile", "", "", ""),
            ),
        ),
        "radeonsi_clear_depth_buffer_cache_before_clear": (
            "RadeonSI Clear Depth Buffer Cache Before Clear",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radeonsi_clear_db_cache_before_clear", "", "", ""),
            ),
        ),
        "radv_forced_anisotropic_filtering": (
            "RADV Forced Anisotropic Filtering",
            (
                ("skip", None),
                ("default", ""),
                ("1x", "1"),
                ("2x", "2"),
                ("4x", "4"),
                ("8x", "8"),
                ("16x", "16"),
            ),
            (
                ("environment_variable", "RADV_TEX_ANISO", "", "", ""),
            ),
        ),
        "radv_performance_power_state": (
            "RADV Performance Power State",
            (
                ("skip", None),
                ("default", ""),
                ("standard", "standard"),
                ("minimum-shader-clock", "min_sclk"),
                ("minimum-memory-clock", "min_mclk"),
                ("peak", "peak"),
            ),
            (
                ("environment_variable", "RADV_PROFILE_PSTATE", "", "", ""),
            ),
        ),
        "radv_variable_rate_shading": (
            "RADV Variable Rate Shading",
            (
                ("skip", None),
                ("default", ""),
                ("1x1", "1x1"),
                ("1x2", "1x2"),
                ("2x1", "2x1"),
                ("2x2", "2x2"),
            ),
            (
                ("environment_variable", "RADV_FORCE_VRS", "", "", ""),
            ),
        ),
        "radv_variable_rate_shading_configuration_file": (
            "RADV Variable Rate Shading Configuration File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "RADV_FORCE_VRS_CONFIG_FILE", "", "", ""),
            ),
        ),
        "radv_profiler_buffer_size": (
            "RADV Profiler Buffer Size",
            (
                ("skip", None),
                ("default", ""),
                ("16-megabytes", "16777216"),
                ("32-megabytes", "33554432"),
                ("64-megabytes", "67108864"),
                ("128-megabytes", "134217728"),
                ("256-megabytes", "268435456"),
            ),
            (
                ("environment_variable", "RADV_THREAD_TRACE_BUFFER_SIZE", "", "", ""),
            ),
        ),
        "radv_sqtt_buffer_size": (
            "RADV SQTT Buffer Size",
            (
                ("skip", None),
                ("default", ""),
                ("32-megabytes", "33554432"),
                ("64-megabytes", "67108864"),
                ("128-megabytes", "134217728"),
            ),
            (
                ("environment_variable", "RADV_SQTT_BUFFER_SIZE", "", "", ""),
            ),
        ),
        "radv_profiler_cache_counters": (
            "RADV Profiler Cache Counters",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "RADV_THREAD_TRACE_CACHE_COUNTERS", "", "", ""),
            ),
        ),
        "radv_profiler_instruction_timing": (
            "RADV Profiler Instruction Timing",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "RADV_THREAD_TRACE_INSTRUCTION_TIMING", "", "", ""),
            ),
        ),
        "radv_profiler_queue_events": (
            "RADV Profiler Queue Events",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "RADV_THREAD_TRACE_QUEUE_EVENTS", "", "", ""),
            ),
        ),
        "radv_thread_trace": (
            "RADV Thread Trace",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "RADV_THREAD_TRACE", "", "", ""),
            ),
        ),
        "radv_thread_trace_pipeline": (
            "RADV Thread Trace Pipeline",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "RADV_THREAD_TRACE_PIPELINE", "", "", ""),
            ),
        ),
        "radv_thread_trace_trigger": (
            "RADV Thread Trace Trigger",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "RADV_THREAD_TRACE_TRIGGER", "", "", ""),
            ),
        ),
        "radv_trap_handler": (
            "RADV Trap Handler",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "RADV_TRAP_HANDLER", "", "", ""),
            ),
        ),
        "radv_trap_handler_exceptions": (
            "RADV Trap Handler Exceptions",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "RADV_TRAP_HANDLER_EXCP", ",", "", ""),
            ),
        ),
        "radv_raytracing_analyzer_trace_validation": (
            "RADV Raytracing Analyzer Trace Validation",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "RADV_RRA_TRACE_VALIDATE", "", "", ""),
            ),
        ),
        "radv_raytracing_analyzer_trace_buffer_size": (
            "RADV Raytracing Analyzer Trace Buffer Size",
            (
                ("skip", None),
                ("default", ""),
                ("64-megabytes", "67108864"),
                ("128-megabytes", "134217728"),
                ("256-megabytes", "268435456"),
            ),
            (
                ("environment_variable", "RADV_RRA_TRACE_BUFFER_SIZE", "", "", ""),
            ),
        ),
        "radv_raytracing_analyzer_trace_history_size": (
            "RADV Raytracing Analyzer Trace History Size",
            (
                ("skip", None),
                ("default", ""),
                ("50-megabytes", "52428800"),
                ("100-megabytes", "104857600"),
                ("200-megabytes", "209715200"),
            ),
            (
                ("environment_variable", "RADV_RRA_TRACE_HISTORY_SIZE", "", "", ""),
            ),
        ),
        "radv_raytracing_analyzer_resolution_scale": (
            "RADV Raytracing Analyzer Resolution Scale",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "RADV_RRA_TRACE_RESOLUTION_SCALE", "", "", ""),
            ),
        ),
        "radv_trace_file": (
            "RADV Trace File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "RADV_TRACE_FILE", "", "", ""),
            ),
        ),
        "radv_force_family": (
            "RADV Force Family",
            (
                ("skip", None),
                ("default", ""),
                ("gfx900", "gfx900"),
                ("gfx902", "gfx902"),
                ("gfx906", "gfx906"),
                ("gfx908", "gfx908"),
                ("gfx1010", "gfx1010"),
                ("gfx1030", "gfx1030"),
                ("gfx1031", "gfx1031"),
                ("gfx1032", "gfx1032"),
                ("gfx1100", "gfx1100"),
                ("gfx1101", "gfx1101"),
                ("gfx1102", "gfx1102"),
            ),
            (
                ("environment_variable", "RADV_FORCE_FAMILY", "", "", ""),
            ),
        ),
        "radv_secure_compile_threads": (
            "RADV Secure Compile Threads",
            (
                ("skip", None),
                ("default", ""),
                ("1", "1"),
                ("2", "2"),
                ("4", "4"),
            ),
            (
                ("environment_variable", "RADV_SECURE_COMPILE_THREADS", "", "", ""),
            ),
        ),
        "radv_gfx12_hierarchical_z_workaround": (
            "RADV GFX12 Hierarchical Z Workaround",
            (
                ("skip", None),
                ("default", ""),
                ("off", "disabled"),
                ("partial", "partial"),
                ("full", "full"),
            ),
            (
                ("environment_variable", "radv_gfx12_hiz_wa", "", "", ""),
            ),
        ),
        "radv_application_layer": (
            "RADV Application Layer",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "radv_app_layer", "", "", ""),
            ),
        ),
        "radv_override_uniform_offset_alignment": (
            "RADV Override Uniform Offset Alignment",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("64", "64"),
                ("256", "256"),
            ),
            (
                ("environment_variable", "radv_override_uniform_offset_alignment", "", "", ""),
            ),
        ),
        "radv_override_graphics_shader_version": (
            "RADV Override Graphics Shader Version",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "radv_override_graphics_shader_version", "", "", ""),
            ),
        ),
        "radv_override_compute_shader_version": (
            "RADV Override Compute Shader Version",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "radv_override_compute_shader_version", "", "", ""),
            ),
        ),
        "radv_override_ray_tracing_shader_version": (
            "RADV Override Ray Tracing Shader Version",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "radv_override_ray_tracing_shader_version", "", "", ""),
            ),
        ),
        "radv_hide_resizable_bar_on_discrete_gpu": (
            "RADV Hide Resizable BAR on Discrete GPU",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_hide_rebar_on_dgpu", "", "", ""),
            ),
        ),
        "radv_enable_unified_heap_on_apu": (
            "RADV Unified Heap on APU",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_enable_unified_heap_on_apu", "", "", ""),
            ),
        ),
        "radv_zero_vram": (
            "RADV Zero VRAM",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_zero_vram", "", "", ""),
            ),
        ),
        "radv_clear_local_data_share": (
            "RADV Clear Local Data Share",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_clear_lds", "", "", ""),
            ),
        ),
        "radv_lower_discard_to_demote": (
            "RADV Lower Discard to Demote",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_lower_discard_to_demote", "", "", ""),
            ),
        ),
        "radv_invariant_geometry": (
            "RADV Invariant Geometry",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_invariant_geom", "", "", ""),
            ),
        ),
        "radv_emulate_ray_tracing": (
            "RADV Emulate Ray Tracing",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_emulate_rt", "", "", ""),
            ),
        ),
        "radv_enable_mrt_output_nan_fixup": (
            "RADV MRT Output NaN Fixup",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_enable_mrt_output_nan_fixup", "", "", ""),
            ),
        ),
        "radv_enable_float16_gfx8": (
            "RADV Float16 GFX8",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_enable_float16_gfx8", "", "", ""),
            ),
        ),
        "radv_report_llvm9_version_string": (
            "RADV Report LLVM9 Version String",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_report_llvm9_version_string", "", "", ""),
            ),
        ),
        "radv_ray_tracing_wave64": (
            "RADV Ray Tracing Wave64",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_rt_wave64", "", "", ""),
            ),
        ),
        "radv_split_fused_multiply_add": (
            "RADV Split Fused Multiply-Add",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_split_fma", "", "", ""),
            ),
        ),
        "radv_ssbo_non_uniform_access": (
            "RADV SSBO Non-Uniform Access",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_ssbo_non_uniform", "", "", ""),
            ),
        ),
        "radv_texture_non_uniform_access": (
            "RADV Texture Non-Uniform Access",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_tex_non_uniform", "", "", ""),
            ),
        ),
        "radv_disable_delta_color_compression": (
            "RADV Disable Delta Color Compression",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_disable_dcc", "", "", ""),
            ),
        ),
        "radv_disable_delta_color_compression_mipmaps": (
            "RADV Disable DCC Mipmaps",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_disable_dcc_mips", "", "", ""),
            ),
        ),
        "radv_disable_delta_color_compression_stores": (
            "RADV Disable DCC Stores",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_disable_dcc_stores", "", "", ""),
            ),
        ),
        "radv_disable_depth_storage": (
            "RADV Disable Depth Storage",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_disable_depth_storage", "", "", ""),
            ),
        ),
        "radv_disable_ngg_geometry_shader": (
            "RADV Disable NGG Geometry Shader",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_disable_ngg_gs", "", "", ""),
            ),
        ),
        "radv_disable_aniso_single_level": (
            "RADV Disable Aniso Single Level",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_disable_aniso_single_level", "", "", ""),
            ),
        ),
        "radv_disable_shrink_image_store": (
            "RADV Disable Shrink Image Store",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_disable_shrink_image_store", "", "", ""),
            ),
        ),
        "radv_disable_sinking_load_input_fragment_shader": (
            "RADV Disable Sinking Load Input Fragment Shader",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_disable_sinking_load_input_fs", "", "", ""),
            ),
        ),
        "radv_disable_tc_compatible_htile_general": (
            "RADV Disable TC-Compatible HTILE General",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_disable_tc_compat_htile_general", "", "", ""),
            ),
        ),
        "radv_disable_truncated_coordinate": (
            "RADV Disable Truncated Coordinate",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_disable_trunc_coord", "", "", ""),
            ),
        ),
        "radv_no_dynamic_bounds": (
            "RADV No Dynamic Bounds",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_no_dynamic_bounds", "", "", ""),
            ),
        ),
        "radv_no_implicit_varying_subgroup_size": (
            "RADV No Implicit Varying Subgroup Size",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_no_implicit_varying_subgroup_size", "", "", ""),
            ),
        ),
        "radv_flush_before_query_copy": (
            "RADV Flush Before Query Copy",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_flush_before_query_copy", "", "", ""),
            ),
        ),
        "radv_flush_before_timestamp_write": (
            "RADV Flush Before Timestamp Write",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_flush_before_timestamp_write", "", "", ""),
            ),
        ),
        "radv_device_generated_commands": (
            "RADV Device Generated Commands",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_dgc", "", "", ""),
            ),
        ),
        "radv_cooperative_matrix2_nv": (
            "RADV Cooperative Matrix2 NV",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "radv_cooperative_matrix2_nv", "", "", ""),
            ),
        ),
        "radv_debug_llvm": (
            "RADV Debug LLVM",
            (
                ("skip", None),
                ("default", ""),
                ("on", "llvm"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_nir": (
            "RADV Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_spirv": (
            "RADV Debug SPIR-V",
            (
                ("skip", None),
                ("default", ""),
                ("on", "spirv"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_shaders": (
            "RADV Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_errors": (
            "RADV Debug Errors",
            (
                ("skip", None),
                ("default", ""),
                ("on", "errors"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_startup": (
            "RADV Debug Startup",
            (
                ("skip", None),
                ("default", ""),
                ("on", "startup"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_check_intermediate_representation": (
            "RADV Debug Check IR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "checkir"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_no_binary_export": (
            "RADV Debug No Binary Export",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nobinexport"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_no_cache": (
            "RADV Debug No Cache",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nocache"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_no_next_generation_geometry": (
            "RADV Debug No NGG",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nongg"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_no_delta_color_compression": (
            "RADV Debug No DCC",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nodcc"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_no_hierarchical_z": (
            "RADV Debug No Hierarchical Z",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nohiz"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_no_vrs_flat_shading": (
            "RADV Debug No VRS Flat Shading",
            (
                ("skip", None),
                ("default", ""),
                ("on", "novrsflatshading"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_split_fma": (
            "RADV Debug Split FMA",
            (
                ("skip", None),
                ("default", ""),
                ("on", "splitfma"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_zero_vram": (
            "RADV Debug Zero VRAM",
            (
                ("skip", None),
                ("default", ""),
                ("on", "zerovram"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_synchronize_shaders": (
            "RADV Debug Synchronize Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "sync_shaders"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_vm_faults": (
            "RADV Debug VM Faults",
            (
                ("skip", None),
                ("default", ""),
                ("on", "vmfaults"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_images": (
            "RADV Debug Images",
            (
                ("skip", None),
                ("default", ""),
                ("on", "img"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_ray_tracing": (
            "RADV Debug Ray Tracing",
            (
                ("skip", None),
                ("default", ""),
                ("on", "rt"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_debug_no_ngg_all": (
            "RADV Debug No NGG All",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nonggc"),
            ),
            (
                ("environment_variable", "RADV_DEBUG", ",", "", ""),
            ),
        ),
        "radv_performance_test_dcc_msaa": (
            "RADV Performance Test DCC MSAA",
            (
                ("skip", None),
                ("default", ""),
                ("on", "dcc_msaa"),
            ),
            (
                ("environment_variable", "RADV_PERFTEST", ",", "", ""),
            ),
        ),
        "radv_performance_test_no_ngg_streamout": (
            "RADV Performance Test No NGG Streamout",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no_ngg_streamout"),
            ),
            (
                ("environment_variable", "RADV_PERFTEST", ",", "", ""),
            ),
        ),
        "radv_performance_test_emulate_ray_tracing": (
            "RADV Performance Test Emulate Ray Tracing",
            (
                ("skip", None),
                ("default", ""),
                ("on", "emulate_rt"),
            ),
            (
                ("environment_variable", "RADV_PERFTEST", ",", "", ""),
            ),
        ),
        "radv_performance_test_ngg_streamout": (
            "RADV Performance Test NGG Streamout",
            (
                ("skip", None),
                ("default", ""),
                ("on", "ngg_streamout"),
            ),
            (
                ("environment_variable", "RADV_PERFTEST", ",", "", ""),
            ),
        ),
        "radv_performance_test_shader_object": (
            "RADV Performance Test Shader Object",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shader_object"),
            ),
            (
                ("environment_variable", "RADV_PERFTEST", ",", "", ""),
            ),
        ),
        "radv_performance_test_transfer_queue": (
            "RADV Performance Test Transfer Queue",
            (
                ("skip", None),
                ("default", ""),
                ("on", "transfer_queue"),
            ),
            (
                ("environment_variable", "RADV_PERFTEST", ",", "", ""),
            ),
        ),
        "radv_performance_test_video_decode": (
            "RADV Performance Test Video Decode",
            (
                ("skip", None),
                ("default", ""),
                ("on", "video_decode"),
            ),
            (
                ("environment_variable", "RADV_PERFTEST", ",", "", ""),
            ),
        ),
        "intel_precise_trigonometry": (
            "Intel Precise Trigonometry",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "INTEL_PRECISE_TRIG", "", "", ""),
            ),
        ),
        "intel_hardware_submission": (
            "Intel Hardware Submission",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "INTEL_NO_HW", "", "", ""),
            ),
        ),
        "intel_no_blit": (
            "Intel No Blit",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "INTEL_NO_BLIT", "", "", ""),
            ),
        ),
        "intel_scalar_vertex_shader": (
            "Intel Scalar Vertex Shader",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "INTEL_SCALAR_VS", "", "", ""),
            ),
        ),
        "intel_scalar_tessellation_control_shader": (
            "Intel Scalar Tessellation Control Shader",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "INTEL_SCALAR_TCS", "", "", ""),
            ),
        ),
        "intel_scalar_tessellation_evaluation_shader": (
            "Intel Scalar Tessellation Evaluation Shader",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "INTEL_SCALAR_TES", "", "", ""),
            ),
        ),
        "intel_scalar_geometry_shader": (
            "Intel Scalar Geometry Shader",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "INTEL_SCALAR_GS", "", "", ""),
            ),
        ),
        "intel_force_multisample_antialiasing": (
            "Intel Force Multisample Antialiasing",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("2", "2"),
                ("4", "4"),
                ("8", "8"),
            ),
            (
                ("environment_variable", "INTEL_FORCE_MSAA", "", "", ""),
            ),
        ),
        "intel_compute_class": (
            "Intel Compute Class",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_COMPUTE_CLASS", "", "", ""),
            ),
        ),
        "intel_strict_conformance": (
            "Intel Strict Conformance",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "INTEL_STRICT_CONFORMANCE", "", "", ""),
            ),
        ),
        "intel_shader_optimizer_path": (
            "Intel Shader Optimizer Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_SHADER_OPTIMIZER_PATH", "", "", ""),
            ),
        ),
        "intel_shader_assembly_read_path": (
            "Intel Shader Assembly Read Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_SHADER_ASM_READ_PATH", "", "", ""),
            ),
        ),
        "intel_shader_binary_dump_path": (
            "Intel Shader Binary Dump Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_SHADER_BIN_DUMP_PATH", "", "", ""),
            ),
        ),
        "intel_shader_dump_filter": (
            "Intel Shader Dump Filter",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_SHADER_DUMP_FILTER", "", "", ""),
            ),
        ),
        "intel_extended_metrics": (
            "Intel Extended Metrics",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "INTEL_EXTENDED_METRICS", "", "", ""),
            ),
        ),
        "intel_force_probe": (
            "Intel Force Probe",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_FORCE_PROBE", ",", "", ""),
            ),
        ),
        "intel_modifier_override": (
            "Intel Modifier Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_MODIFIER_OVERRIDE", "", "", ""),
            ),
        ),
        "intel_blackhole_default": (
            "Intel Blackhole Default",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "INTEL_BLACKHOLE_DEFAULT", "", "", ""),
            ),
        ),
        "intel_memory_debug_analyzer_output_directory": (
            "Intel Memory Debug Analyzer Output Directory",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MDA_OUTPUT_DIR", "", "", ""),
            ),
        ),
        "intel_memory_debug_analyzer_prefix": (
            "Intel Memory Debug Analyzer Prefix",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MDA_PREFIX", "", "", ""),
            ),
        ),
        "intel_memory_debug_analyzer_filter": (
            "Intel Memory Debug Analyzer Filter",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MDA_FILTER", ",", "", ""),
            ),
        ),
        "intel_debug_batch_frame_start": (
            "Intel Debug Batch Frame Start",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_DEBUG_BATCH_FRAME_START", "", "", ""),
            ),
        ),
        "intel_debug_batch_frame_stop": (
            "Intel Debug Batch Frame Stop",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_DEBUG_BATCH_FRAME_STOP", "", "", ""),
            ),
        ),
        "intel_debug_breakpoint_before_draw_count": (
            "Intel Debug Breakpoint Before Draw Count",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_DEBUG_BKP_BEFORE_DRAW_COUNT", "", "", ""),
            ),
        ),
        "intel_debug_breakpoint_after_draw_count": (
            "Intel Debug Breakpoint After Draw Count",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_DEBUG_BKP_AFTER_DRAW_COUNT", "", "", ""),
            ),
        ),
        "intel_debug_breakpoint_before_dispatch_count": (
            "Intel Debug Breakpoint Before Dispatch Count",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_DEBUG_BKP_BEFORE_DISPATCH_COUNT", "", "", ""),
            ),
        ),
        "intel_debug_breakpoint_after_dispatch_count": (
            "Intel Debug Breakpoint After Dispatch Count",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "INTEL_DEBUG_BKP_AFTER_DISPATCH_COUNT", "", "", ""),
            ),
        ),
        "intel_debug_blorp": (
            "Intel Debug BLORP",
            (
                ("skip", None),
                ("default", ""),
                ("on", "blorp"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_performance": (
            "Intel Debug Performance",
            (
                ("skip", None),
                ("default", ""),
                ("on", "perf"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_l3": (
            "Intel Debug L3",
            (
                ("skip", None),
                ("default", ""),
                ("on", "l3"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_no_simd16": (
            "Intel Debug No SIMD16",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no16"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_no_simd8": (
            "Intel Debug No SIMD8",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no8"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_no_simd32": (
            "Intel Debug No SIMD32",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no32"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_color": (
            "Intel Debug Color",
            (
                ("skip", None),
                ("default", ""),
                ("on", "color"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_reemit": (
            "Intel Debug Re-emit",
            (
                ("skip", None),
                ("default", ""),
                ("on", "reemit"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_spill_fragment_shader": (
            "Intel Debug Spill Fragment Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "spill_fs"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_spill_vertex_shader": (
            "Intel Debug Spill Vertex Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "spill_vs"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_compute_shader": (
            "Intel Debug Compute Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "cs"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_vertex_shader": (
            "Intel Debug Vertex Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "vs"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_geometry_shader": (
            "Intel Debug Geometry Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "gs"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_debug_fragment_shader": (
            "Intel Debug Fragment Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "wm"),
            ),
            (
                ("environment_variable", "INTEL_DEBUG", ",", "", ""),
            ),
        ),
        "intel_simd_debug_no_dual_object": (
            "Intel SIMD Debug No Dual Object",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nodualobj"),
            ),
            (
                ("environment_variable", "INTEL_SIMD_DEBUG", ",", "", ""),
            ),
        ),
        "intel_simd_debug_no_simd8": (
            "Intel SIMD Debug No SIMD8",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no8"),
            ),
            (
                ("environment_variable", "INTEL_SIMD_DEBUG", ",", "", ""),
            ),
        ),
        "intel_simd_debug_no_simd16": (
            "Intel SIMD Debug No SIMD16",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no16"),
            ),
            (
                ("environment_variable", "INTEL_SIMD_DEBUG", ",", "", ""),
            ),
        ),
        "intel_simd_debug_no_simd32": (
            "Intel SIMD Debug No SIMD32",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no32"),
            ),
            (
                ("environment_variable", "INTEL_SIMD_DEBUG", ",", "", ""),
            ),
        ),
        "intel_decode_ringbuffer": (
            "Intel Decode Ring Buffer",
            (
                ("skip", None),
                ("default", ""),
                ("on", "ringbuffer"),
            ),
            (
                ("environment_variable", "INTEL_DECODE", ",", "", ""),
            ),
        ),
        "intel_measure_all": (
            "Intel Measure All",
            (
                ("skip", None),
                ("default", ""),
                ("on", "all"),
            ),
            (
                ("environment_variable", "INTEL_MEASURE", ",", "", ""),
            ),
        ),
        "intel_measure_draw": (
            "Intel Measure Draw",
            (
                ("skip", None),
                ("default", ""),
                ("on", "draw"),
            ),
            (
                ("environment_variable", "INTEL_MEASURE", ",", "", ""),
            ),
        ),
        "intel_measure_render_target": (
            "Intel Measure Render Target",
            (
                ("skip", None),
                ("default", ""),
                ("on", "rt"),
            ),
            (
                ("environment_variable", "INTEL_MEASURE", ",", "", ""),
            ),
        ),
        "intel_sampler_route_to_lsc": (
            "Intel Sampler Route to LSC",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "intel_sampler_route_to_lsc", "", "", ""),
            ),
        ),
        "intel_storage_cache_policy_write_through": (
            "Intel Storage Cache Policy Write-Through",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "intel_storage_cache_policy_wt", "", "", ""),
            ),
        ),
        "intel_tile_based_image_memory_rendering": (
            "Intel Tile-Based Image Memory Rendering",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "intel_tbimr", "", "", ""),
            ),
        ),
        "intel_tessellation_engine_distribution": (
            "Intel Tessellation Engine Distribution",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "intel_te_distribution", "", "", ""),
            ),
        ),
        "intel_vertex_fetch_distribution": (
            "Intel Vertex Fetch Distribution",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "intel_vf_distribution", "", "", ""),
            ),
        ),
        "intel_disable_threaded_context": (
            "Intel Disable Threaded Context",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "intel_disable_threaded_context", "", "", ""),
            ),
        ),
        "intel_enable_workaround_14018912822": (
            "Intel Workaround 14018912822",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "intel_enable_wa_14018912822", "", "", ""),
            ),
        ),
        "intel_force_guc_low_latency": (
            "Intel Force GuC Low Latency",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "force_guc_low_latency", "", "", ""),
            ),
        ),
        "anv_wait_for_attach": (
            "ANV Wait For Attach",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "ANV_DEBUG_WAIT_FOR_ATTACH", "", "", ""),
            ),
        ),
        "anv_primitive_replication_maximum_views": (
            "ANV Primitive Replication Maximum Views",
            (
                ("skip", None),
                ("default", ""),
                ("1", "1"),
                ("2", "2"),
                ("4", "4"),
            ),
            (
                ("environment_variable", "ANV_PRIMITIVE_REPLICATION_MAX_VIEWS", "", "", ""),
            ),
        ),
        "anv_printf_buffer_size": (
            "ANV Printf Buffer Size",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "ANV_PRINTF_BUFFER_SIZE", "", "", ""),
            ),
        ),
        "anv_sparse_memory_resources": (
            "ANV Sparse Memory",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", ""),
            ),
            (
                ("environment_variable", "ANV_SPARSE", "", "", ""),
            ),
        ),
        "anv_sparse_memory_translation_table": (
            "ANV Sparse TRTT",
            (
                ("skip", None),
                ("default", ""),
                ("standard", "false"),
                ("trtt", "true"),
            ),
            (
                ("environment_variable", "ANV_SPARSE_USE_TRTT", "", "", ""),
            ),
        ),
        "anv_mesh_shader": (
            "ANV Mesh Shader",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "ANV_MESH_SHADER", "", "", ""),
            ),
        ),
        "anv_video_decode": (
            "ANV Video Decode",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "ANV_VIDEO_DECODE", "", "", ""),
            ),
        ),
        "anv_graphics_pipeline_library": (
            "ANV Graphics Pipeline Library",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "ANV_GPL", "", "", ""),
            ),
        ),
        "anv_disable_secondary_command_buffer_calls": (
            "ANV Disable Secondary Command Buffer Calls",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "ANV_DISABLE_SECONDARY_CMD_BUFFER_CALLS", "", "", ""),
            ),
        ),
        "anv_queue_override": (
            "ANV Queue Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "ANV_QUEUE_OVERRIDE", ",", "", ""),
            ),
        ),
        "anv_debug_no_secondary_command_buffer": (
            "ANV Debug No Secondary Command Buffer Calls",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no_secondary_cmd_buffer_calls"),
            ),
            (
                ("environment_variable", "ANV_DEBUG", ",", "", ""),
            ),
        ),
        "anv_debug_userspace_relocations": (
            "ANV Debug Userspace Relocations",
            (
                ("skip", None),
                ("default", ""),
                ("on", "userspace_relocs"),
            ),
            (
                ("environment_variable", "ANV_DEBUG", ",", "", ""),
            ),
        ),
        "anv_debug_bindless": (
            "ANV Debug Bindless",
            (
                ("skip", None),
                ("default", ""),
                ("on", "bindless"),
            ),
            (
                ("environment_variable", "ANV_DEBUG", ",", "", ""),
            ),
        ),
        "anv_debug_no_fast_clear": (
            "ANV Debug No Fast Clear",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no-fast-clear"),
            ),
            (
                ("environment_variable", "ANV_DEBUG", ",", "", ""),
            ),
        ),
        "anv_debug_hierarchical_z": (
            "ANV Debug Hierarchical Z",
            (
                ("skip", None),
                ("default", ""),
                ("on", "hiz"),
            ),
            (
                ("environment_variable", "ANV_DEBUG", ",", "", ""),
            ),
        ),
        "anv_emulate_read_without_format": (
            "ANV Emulate Read Without Format",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_emulate_read_without_format", "", "", ""),
            ),
        ),
        "anv_enable_buffer_compression": (
            "ANV Enable Buffer Compression",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_enable_buffer_comp", "", "", ""),
            ),
        ),
        "anv_external_memory_implicit_synchronization": (
            "ANV External Memory Implicit Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_external_memory_implicit_sync", "", "", ""),
            ),
        ),
        "anv_fake_nonlocal_memory": (
            "ANV Fake Non-Local Memory",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_fake_nonlocal_memory", "", "", ""),
            ),
        ),
        "anv_force_filter_address_rounding": (
            "ANV Force Filter Address Rounding",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_force_filter_addr_rounding", "", "", ""),
            ),
        ),
        "anv_force_vulkan_vendor": (
            "ANV Force Vulkan Vendor",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "anv_force_vk_vendor", "", "", ""),
            ),
        ),
        "anv_large_workgroup_non_coherent_image_workaround": (
            "ANV Large Workgroup Non-Coherent Image Workaround",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_large_workgroup_non_coherent_image_workaround", "", "", ""),
            ),
        ),
        "anv_mesh_convert_primitive_attributes_to_vertex_attributes": (
            "ANV Mesh Convert Primitive to Vertex Attributes",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_mesh_conv_prim_attrs_to_vert_attrs", "", "", ""),
            ),
        ),
        "anv_query_clear_with_blorp_threshold": (
            "ANV Query Clear BLORP Threshold",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "anv_query_clear_with_blorp_threshold", "", "", ""),
            ),
        ),
        "anv_sample_mask_out_opengl_behaviour": (
            "ANV Sample Mask OpenGL Behaviour",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_sample_mask_out_opengl_behaviour", "", "", ""),
            ),
        ),
        "anv_upper_bound_descriptor_pool_sampler": (
            "ANV Descriptor Pool Sampler Upper Bound",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "anv_upper_bound_descriptor_pool_sampler", "", "", ""),
            ),
        ),
        "anv_vertex_fetch_component_packing": (
            "ANV Vertex Fetch Component Packing",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_vf_component_packing", "", "", ""),
            ),
        ),
        "anv_disable_drm_ccs_modifiers": (
            "ANV Disable DRM CCS Modifiers",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_disable_drm_ccs_modifiers", "", "", ""),
            ),
        ),
        "anv_disable_fast_clear_value": (
            "ANV Disable Fast Clear Value",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_disable_fcv", "", "", ""),
            ),
        ),
        "anv_assume_full_subgroups": (
            "ANV Assume Full Subgroups",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_assume_full_subgroups", "", "", ""),
            ),
        ),
        "anv_assume_full_subgroups_with_barrier": (
            "ANV Assume Full Subgroups With Barrier",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_assume_full_subgroups_with_barrier", "", "", ""),
            ),
        ),
        "anv_assume_full_subgroups_with_shared_memory": (
            "ANV Assume Full Subgroups With Shared Memory",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "anv_assume_full_subgroups_with_shared_memory", "", "", ""),
            ),
        ),
        "query_clear_with_blorp_threshold": (
            "Query Clear With BLORP Threshold",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "query_clear_with_blorp_threshold", "", "", ""),
            ),
        ),
        "query_copy_with_shader_threshold": (
            "Query Copy With Shader Threshold",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "query_copy_with_shader_threshold", "", "", ""),
            ),
        ),
        "hasvk_bindless_descriptors": (
            "HASVK Bindless Descriptors",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "true"),
            ),
            (
                ("environment_variable", "HASVK_ALWAYS_BINDLESS", "", "", ""),
            ),
        ),
        "hasvk_userspace_memory_relocations": (
            "HASVK Userspace Memory Relocations",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "true"),
            ),
            (
                ("environment_variable", "HASVK_USERSPACE_RELOCS", "", "", ""),
            ),
        ),
        "hasvk_disable_secondary_command_buffer_calls": (
            "HASVK Disable Secondary Command Buffer Calls",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "HASVK_DISABLE_SECONDARY_CMD_BUFFER_CALLS", "", "", ""),
            ),
        ),
        "hasvk_queue_override": (
            "HASVK Queue Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "HASVK_QUEUE_OVERRIDE", ",", "", ""),
            ),
        ),
        "hasvk_report_vulkan_1_3_version": (
            "HASVK Report Vulkan 1.3",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "hasvk_report_vk_1_3_version", "", "", ""),
            ),
        ),
        "hasvk_debug_no_secondary_command_buffer": (
            "HASVK Debug No Secondary Command Buffer",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no_secondary_cmd_buffer_calls"),
            ),
            (
                ("environment_variable", "HK_DEBUG", ",", "", ""),
            ),
        ),
        "hasvk_fake_minimum_maximum": (
            "HASVK Fake Minimum Maximum",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "hk_fake_minmax", "", "", ""),
            ),
        ),
        "hasvk_image_view_minimum_lod": (
            "HASVK Image View Minimum LOD",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "hk_image_view_min_lod", "", "", ""),
            ),
        ),
        "hasvk_disable_border_emulation": (
            "HASVK Disable Border Emulation",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "hk_disable_border_emulation", "", "", ""),
            ),
        ),
        "i915_no_hardware": (
            "i915 No Hardware",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "I915_NO_HW", "", "", ""),
            ),
        ),
        "i915_dump_commands": (
            "i915 Dump Commands",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "I915_DUMP_CMD", "", "", ""),
            ),
        ),
        "i915_debug_shader": (
            "i915 Debug Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shader"),
            ),
            (
                ("environment_variable", "I915_DEBUG", ",", "", ""),
            ),
        ),
        "i915_debug_batch": (
            "i915 Debug Batch",
            (
                ("skip", None),
                ("default", ""),
                ("on", "bat"),
            ),
            (
                ("environment_variable", "I915_DEBUG", ",", "", ""),
            ),
        ),
        "i915_debug_buffer": (
            "i915 Debug Buffer",
            (
                ("skip", None),
                ("default", ""),
                ("on", "buf"),
            ),
            (
                ("environment_variable", "I915_DEBUG", ",", "", ""),
            ),
        ),
        "iris_enable_clover": (
            "Iris Enable Clover",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "IRIS_ENABLE_CLOVER", "", "", ""),
            ),
        ),
        "nouveau_libdrm_debug": (
            "Nouveau LibDRM Debug",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NOUVEAU_LIBDRM_DEBUG", "", "", ""),
            ),
        ),
        "nouveau_pmpeg": (
            "Nouveau PMPEG",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NOUVEAU_PMPEG", "", "", ""),
            ),
        ),
        "nouveau_mesa_debug_shaders": (
            "Nouveau Mesa Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "NOUVEAU_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "nouveau_mesa_debug_nir": (
            "Nouveau Mesa Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "NOUVEAU_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "nv50_program_debug": (
            "NV50 Program Debug",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NV50_PROG_DEBUG", "", "", ""),
            ),
        ),
        "nv50_program_optimize": (
            "NV50 Program Optimize",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
            ),
            (
                ("environment_variable", "NV50_PROG_OPTIMIZE", "", "", ""),
            ),
        ),
        "nv50_program_chipset": (
            "NV50 Program Chipset",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "NV50_PROG_CHIPSET", "", "", ""),
            ),
        ),
        "nvc0_program_debug": (
            "NVC0 Program Debug",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NVC0_PROG_DEBUG", "", "", ""),
            ),
        ),
        "nvc0_program_optimize": (
            "NVC0 Program Optimize",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
            ),
            (
                ("environment_variable", "NVC0_PROG_OPTIMIZE", "", "", ""),
            ),
        ),
        "nvc0_program_chipset": (
            "NVC0 Program Chipset",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "NVC0_PROG_CHIPSET", "", "", ""),
            ),
        ),
        "nvk_debug_push_dump": (
            "NVK Debug Push Dump",
            (
                ("skip", None),
                ("default", ""),
                ("on", "push_dump"),
            ),
            (
                ("environment_variable", "NVK_DEBUG", ",", "", ""),
            ),
        ),
        "nvk_debug_push_synchronization": (
            "NVK Debug Push Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("on", "push_sync"),
            ),
            (
                ("environment_variable", "NVK_DEBUG", ",", "", ""),
            ),
        ),
        "nvk_debug_zero_memory": (
            "NVK Debug Zero Memory",
            (
                ("skip", None),
                ("default", ""),
                ("on", "zero_memory"),
            ),
            (
                ("environment_variable", "NVK_DEBUG", ",", "", ""),
            ),
        ),
        "nvk_debug_no_hard_fault": (
            "NVK Debug No Hard Fault",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no_hard_fault"),
            ),
            (
                ("environment_variable", "NVK_DEBUG", ",", "", ""),
            ),
        ),
        "nak_debug_print_nak": (
            "NAK Debug Print NAK",
            (
                ("skip", None),
                ("default", ""),
                ("on", "print_nak"),
            ),
            (
                ("environment_variable", "NAK_DEBUG", ",", "", ""),
            ),
        ),
        "nak_debug_print_nir": (
            "NAK Debug Print NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "print_nir"),
            ),
            (
                ("environment_variable", "NAK_DEBUG", ",", "", ""),
            ),
        ),
        "nak_debug_spill_all": (
            "NAK Debug Spill All",
            (
                ("skip", None),
                ("default", ""),
                ("on", "spill_all"),
            ),
            (
                ("environment_variable", "NAK_DEBUG", ",", "", ""),
            ),
        ),
        "r600_debug_compute": (
            "R600 Debug Compute",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "R600_DEBUG_COMPUTE", "", "", ""),
            ),
        ),
        "r600_dump_shaders": (
            "R600 Dump Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "R600_DUMP_SHADERS", "", "", ""),
            ),
        ),
        "r600_hyperz": (
            "R600 HyperZ",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "R600_HYPERZ", "", "", ""),
            ),
        ),
        "r600_debug_no_compute": (
            "R600 Debug No Compute",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nocompute"),
            ),
            (
                ("environment_variable", "R600_DEBUG", ",", "", ""),
            ),
        ),
        "r600_debug_vertex_shader": (
            "R600 Debug Vertex Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "vs"),
            ),
            (
                ("environment_variable", "R600_DEBUG", ",", "", ""),
            ),
        ),
        "r600_debug_pixel_shader": (
            "R600 Debug Pixel Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "ps"),
            ),
            (
                ("environment_variable", "R600_DEBUG", ",", "", ""),
            ),
        ),
        "r600_debug_compute_shader": (
            "R600 Debug Compute Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "cs"),
            ),
            (
                ("environment_variable", "R600_DEBUG", ",", "", ""),
            ),
        ),
        "r600_debug_nir": (
            "R600 Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "R600_DEBUG", ",", "", ""),
            ),
        ),
        "r600_nir_debug_no_optimization": (
            "R600 NIR Debug No Optimization",
            (
                ("skip", None),
                ("default", ""),
                ("on", "noopt"),
            ),
            (
                ("environment_variable", "R600_NIR_DEBUG", ",", "", ""),
            ),
        ),
        "r600_nir_debug_vertex_shader": (
            "R600 NIR Debug Vertex Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "vs"),
            ),
            (
                ("environment_variable", "R600_NIR_DEBUG", ",", "", ""),
            ),
        ),
        "r600_nir_debug_pixel_shader": (
            "R600 NIR Debug Pixel Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "ps"),
            ),
            (
                ("environment_variable", "R600_NIR_DEBUG", ",", "", ""),
            ),
        ),
        "r600_nir_debug_compute_shader": (
            "R600 NIR Debug Compute Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "cs"),
            ),
            (
                ("environment_variable", "R600_NIR_DEBUG", ",", "", ""),
            ),
        ),
        "radeon_no_tcl": (
            "Radeon No TCL",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "RADEON_NO_TCL", "", "", ""),
            ),
        ),
        "radeon_debug_shaders": (
            "Radeon Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "RADEON_DEBUG", ",", "", ""),
            ),
        ),
        "zink_descriptor_management_mode": (
            "Zink Descriptor Management Mode",
            (
                ("skip", None),
                ("default", ""),
                ("auto", "auto"),
                ("lazy", "lazy"),
                ("db", "db"),
            ),
            (
                ("environment_variable", "ZINK_DESCRIPTORS", "", "", ""),
            ),
        ),
        "zink_inline_uniforms": (
            "Zink Inline Uniforms",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "ZINK_INLINE_UNIFORMS", "", "", ""),
            ),
        ),
        "zink_use_lavapipe": (
            "Zink Use Lavapipe",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "ZINK_USE_LAVAPIPE", "", "", ""),
            ),
        ),
        "zink_emulate_point_smooth": (
            "Zink Emulate Point Smooth",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "zink_emulate_point_smooth", "", "", ""),
            ),
        ),
        "zink_shader_object": (
            "Zink Shader Object",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "zink_shader_object_enable", "", "", ""),
            ),
        ),
        "zink_debug_no_reorder": (
            "Zink Debug No Reorder",
            (
                ("skip", None),
                ("default", ""),
                ("on", "noreorder"),
            ),
            (
                ("environment_variable", "ZINK_DEBUG", ",", "", ""),
            ),
        ),
        "zink_debug_flush_synchronization": (
            "Zink Debug Flush Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("on", "flushsync"),
            ),
            (
                ("environment_variable", "ZINK_DEBUG", ",", "", ""),
            ),
        ),
        "zink_debug_no_fallback": (
            "Zink Debug No Fallback",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nofallback"),
            ),
            (
                ("environment_variable", "ZINK_DEBUG", ",", "", ""),
            ),
        ),
        "zink_debug_synchronization": (
            "Zink Debug Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("on", "sync"),
            ),
            (
                ("environment_variable", "ZINK_DEBUG", ",", "", ""),
            ),
        ),
        "zink_debug_compact": (
            "Zink Debug Compact",
            (
                ("skip", None),
                ("default", ""),
                ("on", "compact"),
            ),
            (
                ("environment_variable", "ZINK_DEBUG", ",", "", ""),
            ),
        ),
        "zink_debug_nir_dump": (
            "Zink Debug NIR Dump",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nirdump"),
            ),
            (
                ("environment_variable", "ZINK_DEBUG", ",", "", ""),
            ),
        ),
        "zink_debug_spirv": (
            "Zink Debug SPIR-V",
            (
                ("skip", None),
                ("default", ""),
                ("on", "spirv"),
            ),
            (
                ("environment_variable", "ZINK_DEBUG", ",", "", ""),
            ),
        ),
        "zink_debug_tgsi": (
            "Zink Debug TGSI",
            (
                ("skip", None),
                ("default", ""),
                ("on", "tgsi"),
            ),
            (
                ("environment_variable", "ZINK_DEBUG", ",", "", ""),
            ),
        ),
        "zink_debug_validation": (
            "Zink Debug Validation",
            (
                ("skip", None),
                ("default", ""),
                ("on", "validation"),
            ),
            (
                ("environment_variable", "ZINK_DEBUG", ",", "", ""),
            ),
        ),
        "llvmpipe_rendering_thread_count": (
            "LLVMpipe Rendering Thread Count",
            (
                ("skip", None),
                ("default", ""),
                ("single", "0"),
                ("1", "1"),
                ("2", "2"),
                ("4", "4"),
                ("8", "8"),
                ("16", "16"),
                ("32", "32"),
            ),
            (
                ("environment_variable", "LP_NUM_THREADS", "", "", ""),
            ),
        ),
        "llvmpipe_rasterization": (
            "LLVMpipe Rasterization",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "LP_NO_RAST", "", "", ""),
            ),
        ),
        "llvmpipe_force_sse2": (
            "LLVMpipe Force SSE2",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LP_FORCE_SSE2", "", "", ""),
            ),
        ),
        "llvmpipe_native_vector_width": (
            "LLVMpipe Native Vector Width",
            (
                ("skip", None),
                ("default", ""),
                ("128", "128"),
                ("256", "256"),
                ("512", "512"),
            ),
            (
                ("environment_variable", "LP_NATIVE_VECTOR_WIDTH", "", "", ""),
            ),
        ),
        "llvmpipe_debug_rasterizer": (
            "LLVMpipe Debug Rasterizer",
            (
                ("skip", None),
                ("default", ""),
                ("on", "rast"),
            ),
            (
                ("environment_variable", "LP_DEBUG", ",", "", ""),
            ),
        ),
        "llvmpipe_debug_vertex_shader": (
            "LLVMpipe Debug Vertex Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "vs"),
            ),
            (
                ("environment_variable", "LP_DEBUG", ",", "", ""),
            ),
        ),
        "llvmpipe_debug_geometry_shader": (
            "LLVMpipe Debug Geometry Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "gs"),
            ),
            (
                ("environment_variable", "LP_DEBUG", ",", "", ""),
            ),
        ),
        "llvmpipe_debug_fragment_shader": (
            "LLVMpipe Debug Fragment Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "fs"),
            ),
            (
                ("environment_variable", "LP_DEBUG", ",", "", ""),
            ),
        ),
        "llvmpipe_performance_no_clamp": (
            "LLVMpipe Performance No Clamp",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no_clamp"),
            ),
            (
                ("environment_variable", "LP_PERF", ",", "", ""),
            ),
        ),
        "llvmpipe_performance_no_arithmetic": (
            "LLVMpipe Performance No Arithmetic",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no_arit"),
            ),
            (
                ("environment_variable", "LP_PERF", ",", "", ""),
            ),
        ),
        "llvmpipe_performance_no_blend": (
            "LLVMpipe Performance No Blend",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no_blend"),
            ),
            (
                ("environment_variable", "LP_PERF", ",", "", ""),
            ),
        ),
        "llvmpipe_performance_no_depth": (
            "LLVMpipe Performance No Depth",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no_depth"),
            ),
            (
                ("environment_variable", "LP_PERF", ",", "", ""),
            ),
        ),
        "lavapipe_debug_nir": (
            "Lavapipe Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "LVP_DEBUG", ",", "", ""),
            ),
        ),
        "lavapipe_debug_spirv": (
            "Lavapipe Debug SPIR-V",
            (
                ("skip", None),
                ("default", ""),
                ("on", "spirv"),
            ),
            (
                ("environment_variable", "LVP_DEBUG", ",", "", ""),
            ),
        ),
        "softpipe_dump_fragment_shader": (
            "Softpipe Dump Fragment Shader",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "SOFTPIPE_DUMP_FS", "", "", ""),
            ),
        ),
        "softpipe_dump_geometry_shader": (
            "Softpipe Dump Geometry Shader",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "SOFTPIPE_DUMP_GS", "", "", ""),
            ),
        ),
        "softpipe_no_rasterization": (
            "Softpipe No Rasterization",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "SOFTPIPE_NO_RAST", "", "", ""),
            ),
        ),
        "softpipe_use_llvm": (
            "Softpipe Use LLVM",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "SOFTPIPE_USE_LLVM", "", "", ""),
            ),
        ),
        "softpipe_debug_triangles": (
            "Softpipe Debug Triangles",
            (
                ("skip", None),
                ("default", ""),
                ("on", "tri"),
            ),
            (
                ("environment_variable", "SOFTPIPE_DEBUG", ",", "", ""),
            ),
        ),
        "softpipe_debug_points": (
            "Softpipe Debug Points",
            (
                ("skip", None),
                ("default", ""),
                ("on", "point"),
            ),
            (
                ("environment_variable", "SOFTPIPE_DEBUG", ",", "", ""),
            ),
        ),
        "softpipe_debug_lines": (
            "Softpipe Debug Lines",
            (
                ("skip", None),
                ("default", ""),
                ("on", "line"),
            ),
            (
                ("environment_variable", "SOFTPIPE_DEBUG", ",", "", ""),
            ),
        ),
        "freedreno_debug_shaders": (
            "Freedreno Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "FD_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "freedreno_debug_nir": (
            "Freedreno Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "FD_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "freedreno_debug_disassembly": (
            "Freedreno Debug Disassembly",
            (
                ("skip", None),
                ("default", ""),
                ("on", "disasm"),
            ),
            (
                ("environment_variable", "FD_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "freedreno_debug_command_stream": (
            "Freedreno Debug Command Stream",
            (
                ("skip", None),
                ("default", ""),
                ("on", "cs"),
            ),
            (
                ("environment_variable", "FD_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "freedreno_debug_no_hyperz": (
            "Freedreno Debug No HyperZ",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nohyperz"),
            ),
            (
                ("environment_variable", "FD_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "ir3_shader_debug_disassembly": (
            "IR3 Debug Disassembly",
            (
                ("skip", None),
                ("default", ""),
                ("on", "disasm"),
            ),
            (
                ("environment_variable", "IR3_SHADER_DEBUG", ",", "", ""),
            ),
        ),
        "ir3_shader_debug_optimizer_messages": (
            "IR3 Debug Optimizer Messages",
            (
                ("skip", None),
                ("default", ""),
                ("on", "optmsgs"),
            ),
            (
                ("environment_variable", "IR3_SHADER_DEBUG", ",", "", ""),
            ),
        ),
        "ir3_shader_debug_no_fp16": (
            "IR3 Debug No FP16",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nofp16"),
            ),
            (
                ("environment_variable", "IR3_SHADER_DEBUG", ",", "", ""),
            ),
        ),
        "ir3_shader_debug_no_cache": (
            "IR3 Debug No Cache",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nocache"),
            ),
            (
                ("environment_variable", "IR3_SHADER_DEBUG", ",", "", ""),
            ),
        ),
        "ir3_shader_override_path": (
            "IR3 Shader Override Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "IR3_SHADER_OVERRIDE_PATH", "", "", ""),
            ),
        ),
        "turnip_debug_nir": (
            "Turnip Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "TU_DEBUG", ",", "", ""),
            ),
        ),
        "turnip_debug_spirv": (
            "Turnip Debug SPIR-V",
            (
                ("skip", None),
                ("default", ""),
                ("on", "spirv"),
            ),
            (
                ("environment_variable", "TU_DEBUG", ",", "", ""),
            ),
        ),
        "turnip_debug_no_binning": (
            "Turnip Debug No Binning",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nobin"),
            ),
            (
                ("environment_variable", "TU_DEBUG", ",", "", ""),
            ),
        ),
        "turnip_debug_system_memory": (
            "Turnip Debug System Memory",
            (
                ("skip", None),
                ("default", ""),
                ("on", "sysmem"),
            ),
            (
                ("environment_variable", "TU_DEBUG", ",", "", ""),
            ),
        ),
        "turnip_debug_gmem": (
            "Turnip Debug GMEM",
            (
                ("skip", None),
                ("default", ""),
                ("on", "gmem"),
            ),
            (
                ("environment_variable", "TU_DEBUG", ",", "", ""),
            ),
        ),
        "turnip_debug_force_binning": (
            "Turnip Debug Force Binning",
            (
                ("skip", None),
                ("default", ""),
                ("on", "forcebin"),
            ),
            (
                ("environment_variable", "TU_DEBUG", ",", "", ""),
            ),
        ),
        "turnip_debug_file": (
            "Turnip Debug File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "TU_DEBUG_FILE", "", "", ""),
            ),
        ),
        "turnip_debug_stale_registers_range": (
            "Turnip Debug Stale Registers Range",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "TU_DEBUG_STALE_REGS_RANGE", "", "", ""),
            ),
        ),
        "turnip_debug_stale_registers_flags": (
            "Turnip Debug Stale Registers Flags",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "TU_DEBUG_STALE_REGS_FLAGS", ",", "", ""),
            ),
        ),
        "turnip_performance_test_binning_cache": (
            "Turnip Performance Test Binning Cache",
            (
                ("skip", None),
                ("default", ""),
                ("on", "binning_cache"),
            ),
            (
                ("environment_variable", "TU_PERFTEST", ",", "", ""),
            ),
        ),
        "turnip_performance_test_gmem_save_restore": (
            "Turnip Performance Test GMEM Save Restore",
            (
                ("skip", None),
                ("default", ""),
                ("on", "gmem_save_restore"),
            ),
            (
                ("environment_variable", "TU_PERFTEST", ",", "", ""),
            ),
        ),
        "turnip_allow_out_of_bounds_indirect_ubo_loads": (
            "Turnip Allow Out-of-Bounds Indirect UBO Loads",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "tu_allow_oob_indirect_ubo_loads", "", "", ""),
            ),
        ),
        "turnip_disable_d24s8_border_color_workaround": (
            "Turnip Disable D24S8 Border Color Workaround",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "tu_disable_d24s8_border_color_workaround", "", "", ""),
            ),
        ),
        "turnip_dont_reserve_descriptor_set": (
            "Turnip Don't Reserve Descriptor Set",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "tu_dont_reserve_descriptor_set", "", "", ""),
            ),
        ),
        "turnip_ignore_fragment_depth_direction": (
            "Turnip Ignore Fragment Depth Direction",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "tu_ignore_frag_depth_direction", "", "", ""),
            ),
        ),
        "turnip_use_texture_coordinate_round_nearest_even_mode": (
            "Turnip Texture Coordinate Round Nearest Even",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "tu_use_tex_coord_round_nearest_even_mode", "", "", ""),
            ),
        ),
        "disable_conservative_low_resolution_z": (
            "Disable Conservative Low Resolution Z",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "disable_conservative_lrz", "", "", ""),
            ),
        ),
        "panfrost_debug_shaders": (
            "Panfrost Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "PAN_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "panfrost_debug_nir": (
            "Panfrost Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "PAN_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "panfrost_debug_gl3": (
            "Panfrost Debug GL3",
            (
                ("skip", None),
                ("default", ""),
                ("on", "gl3"),
            ),
            (
                ("environment_variable", "PAN_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "panfrost_gpu_identifier": (
            "Panfrost GPU Identifier",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "PAN_GPU_ID", "", "", ""),
            ),
        ),
        "panfrost_compute_core_mask": (
            "Panfrost Compute Core Mask",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "pan_compute_core_mask", "", "", ""),
            ),
        ),
        "panfrost_fragment_core_mask": (
            "Panfrost Fragment Core Mask",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "pan_fragment_core_mask", "", "", ""),
            ),
        ),
        "panfrost_enable_vertex_pipeline_stores_atomics": (
            "Panfrost Vertex Pipeline Stores and Atomics",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "pan_enable_vertex_pipeline_stores_atomics", "", "", ""),
            ),
        ),
        "panfrost_force_enable_shader_atomics": (
            "Panfrost Force Shader Atomics",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "pan_force_enable_shader_atomics", "", "", ""),
            ),
        ),
        "panvk_debug_nir": (
            "PanVK Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "PANVK_DEBUG", ",", "", ""),
            ),
        ),
        "panvk_debug_spirv": (
            "PanVK Debug SPIR-V",
            (
                ("skip", None),
                ("default", ""),
                ("on", "spirv"),
            ),
            (
                ("environment_variable", "PANVK_DEBUG", ",", "", ""),
            ),
        ),
        "etnaviv_debug_shaders": (
            "Etnaviv Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "ETNA_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "etnaviv_debug_nir": (
            "Etnaviv Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "ETNA_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "etnaviv_debug_compiler": (
            "Etnaviv Debug Compiler",
            (
                ("skip", None),
                ("default", ""),
                ("on", "compiler"),
            ),
            (
                ("environment_variable", "ETNA_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "etnaviv_front_end_mask": (
            "Etnaviv Front End Mask",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "ETNAVIV_FE_MASK", "", "", ""),
            ),
        ),
        "lima_context_plb_count": (
            "Lima Context PLB Count",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "LIMA_CTX_NUM_PLB", "", "", ""),
            ),
        ),
        "lima_plb_maximum_block": (
            "Lima PLB Maximum Block",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "LIMA_PLB_MAX_BLK", "", "", ""),
            ),
        ),
        "lima_plb_pp_stream_cache_size": (
            "Lima PLB PP Stream Cache Size",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "LIMA_PLB_PP_STREAM_CACHE_SIZE", "", "", ""),
            ),
        ),
        "lima_ppir_force_spill": (
            "Lima PPIR Force Spill",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LIMA_PPIR_FORCE_SPILL", "", "", ""),
            ),
        ),
        "lima_debug_pixel_processor": (
            "Lima Debug Pixel Processor",
            (
                ("skip", None),
                ("default", ""),
                ("on", "pp"),
            ),
            (
                ("environment_variable", "LIMA_DEBUG", ",", "", ""),
            ),
        ),
        "lima_debug_geometry_processor": (
            "Lima Debug Geometry Processor",
            (
                ("skip", None),
                ("default", ""),
                ("on", "gp"),
            ),
            (
                ("environment_variable", "LIMA_DEBUG", ",", "", ""),
            ),
        ),
        "lima_debug_dump": (
            "Lima Debug Dump",
            (
                ("skip", None),
                ("default", ""),
                ("on", "dump"),
            ),
            (
                ("environment_variable", "LIMA_DEBUG", ",", "", ""),
            ),
        ),
        "v3d_simulator_file": (
            "V3D Simulator File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "V3D_SIMULATOR_FILE", "", "", ""),
            ),
        ),
        "v3d_non_msaa_texture_size_limit": (
            "V3D Non-MSAA Texture Size Limit",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "v3d_nonmsaa_texture_size_limit", "", "", ""),
            ),
        ),
        "v3d_debug_shaders": (
            "V3D Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "V3D_DEBUG", ",", "", ""),
            ),
        ),
        "v3d_debug_assembly": (
            "V3D Debug Assembly",
            (
                ("skip", None),
                ("default", ""),
                ("on", "asm"),
            ),
            (
                ("environment_variable", "V3D_DEBUG", ",", "", ""),
            ),
        ),
        "v3d_debug_nir": (
            "V3D Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "V3D_DEBUG", ",", "", ""),
            ),
        ),
        "vc4_debug_shaders": (
            "VC4 Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "VC4_DEBUG", ",", "", ""),
            ),
        ),
        "vc4_debug_assembly": (
            "VC4 Debug Assembly",
            (
                ("skip", None),
                ("default", ""),
                ("on", "asm"),
            ),
            (
                ("environment_variable", "VC4_DEBUG", ",", "", ""),
            ),
        ),
        "vmware_force_software_transform": (
            "VMware Force Software Transform",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "SVGA_FORCE_SWTNL", "", "", ""),
            ),
        ),
        "vmware_no_software_transform": (
            "VMware No Software Transform",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "SVGA_NO_SWTNL", "", "", ""),
            ),
        ),
        "vmware_extra_logging": (
            "VMware Extra Logging",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "SVGA_EXTRA_LOGGING", "", "", ""),
            ),
        ),
        "vmware_no_logging": (
            "VMware No Logging",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "SVGA_NO_LOGGING", "", "", ""),
            ),
        ),
        "vmware_opengl_4_3": (
            "VMware OpenGL 4.3",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "SVGA_GL43", "", "", ""),
            ),
        ),
        "svga_debug_shaders": (
            "SVGA Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "SVGA_DEBUG", ",", "", ""),
            ),
        ),
        "svga_debug_nir": (
            "SVGA Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "SVGA_DEBUG", ",", "", ""),
            ),
        ),
        "virgl_shader_synchronization": (
            "VirGL Shader Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "virgl_shader_sync", "", "", ""),
            ),
        ),
        "virgl_debug_shaders": (
            "VirGL Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "VIRGL_DEBUG", ",", "", ""),
            ),
        ),
        "virgl_debug_nir": (
            "VirGL Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "VIRGL_DEBUG", ",", "", ""),
            ),
        ),
        "venus_implicit_fencing": (
            "Venus Implicit Fencing",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "venus_implicit_fencing", "", "", ""),
            ),
        ),
        "venus_wsi_multi_plane_modifiers": (
            "Venus WSI Multi-Plane Modifiers",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "venus_wsi_multi_plane_modifiers", "", "", ""),
            ),
        ),
        "venus_debug_shaders": (
            "Venus Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "VENUS_DEBUG", ",", "", ""),
            ),
        ),
        "venus_debug_no_graphics_pipeline_library": (
            "Venus Debug No GPL",
            (
                ("skip", None),
                ("default", ""),
                ("on", "no_gpl"),
            ),
            (
                ("environment_variable", "VENUS_DEBUG", ",", "", ""),
            ),
        ),
        "vn_debug_initialization": (
            "VN Debug Initialization",
            (
                ("skip", None),
                ("default", ""),
                ("on", "init"),
            ),
            (
                ("environment_variable", "VN_DEBUG", ",", "", ""),
            ),
        ),
        "vn_debug_result": (
            "VN Debug Result",
            (
                ("skip", None),
                ("default", ""),
                ("on", "result"),
            ),
            (
                ("environment_variable", "VN_DEBUG", ",", "", ""),
            ),
        ),
        "vn_debug_vtest": (
            "VN Debug Vtest",
            (
                ("skip", None),
                ("default", ""),
                ("on", "vtest"),
            ),
            (
                ("environment_variable", "VN_DEBUG", ",", "", ""),
            ),
        ),
        "agx_mesa_debug_shaders": (
            "AGX Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "AGX_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "agx_mesa_debug_nir": (
            "AGX Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "AGX_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "agx_mesa_debug_assembly": (
            "AGX Debug Assembly",
            (
                ("skip", None),
                ("default", ""),
                ("on", "asm"),
            ),
            (
                ("environment_variable", "AGX_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "asahi_mesa_debug_shaders": (
            "Asahi Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "ASAHI_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "asahi_mesa_debug_nir": (
            "Asahi Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "ASAHI_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "agxdecode_dump_file": (
            "AGXDecode Dump File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "AGXDECODE_DUMP_FILE", "", "", ""),
            ),
        ),
        "bifrost_mesa_debug_shaders": (
            "Bifrost Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "BIFROST_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "bifrost_mesa_debug_nir": (
            "Bifrost Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "BIFROST_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "midgard_mesa_debug_shaders": (
            "Midgard Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "MIDGARD_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "midgard_mesa_debug_nir": (
            "Midgard Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "MIDGARD_MESA_DEBUG", ",", "", ""),
            ),
        ),
        "powervr_rogue_color_output": (
            "PowerVR Rogue Color Output",
            (
                ("skip", None),
                ("default", "auto"),
                ("off", "off"),
                ("on", "on"),
            ),
            (
                ("environment_variable", "ROGUE_COLOR", "", "", ""),
            ),
        ),
        "powervr_pco_color_output": (
            "PowerVR PCO Color Output",
            (
                ("skip", None),
                ("default", "auto"),
                ("off", "off"),
                ("on", "on"),
            ),
            (
                ("environment_variable", "PCO_COLOR", "", "", ""),
            ),
        ),
        "pvr_shim_device_bvnc": (
            "PVR Shim Device BVNC",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "PVR_SHIM_DEVICE_BVNC", "", "", ""),
            ),
        ),
        "pvr_shim_enhancements": (
            "PVR Shim Enhancements",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "PVR_SHIM_ENHANCEMENTS", "", "", ""),
            ),
        ),
        "pvr_shim_quirks": (
            "PVR Shim Quirks",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "PVR_SHIM_QUIRKS", "", "", ""),
            ),
        ),
        "pvr_shim_musthave_quirks": (
            "PVR Shim Must-Have Quirks",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "PVR_SHIM_MUSTHAVE_QUIRKS", "", "", ""),
            ),
        ),
        "pvr_debug_information": (
            "PVR Debug Information",
            (
                ("skip", None),
                ("default", ""),
                ("on", "info"),
            ),
            (
                ("environment_variable", "PVR_DEBUG", ",", "", ""),
            ),
        ),
        "pvr_debug_shader": (
            "PVR Debug Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shader"),
            ),
            (
                ("environment_variable", "PVR_DEBUG", ",", "", ""),
            ),
        ),
        "rogue_debug_nir": (
            "Rogue Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "ROGUE_DEBUG", ",", "", ""),
            ),
        ),
        "rogue_debug_assembly": (
            "Rogue Debug Assembly",
            (
                ("skip", None),
                ("default", ""),
                ("on", "asm"),
            ),
            (
                ("environment_variable", "ROGUE_DEBUG", ",", "", ""),
            ),
        ),
        "pco_debug_nir": (
            "PCO Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "PCO_DEBUG", ",", "", ""),
            ),
        ),
        "pco_print_shader": (
            "PCO Print Shader",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shader"),
            ),
            (
                ("environment_variable", "PCO_PRINT", ",", "", ""),
            ),
        ),
        "pco_skip_passes": (
            "PCO Skip Passes",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "PCO_SKIP_PASSES", ",", "", ""),
            ),
        ),
        "dzn_disable": (
            "DZN Disable",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "dzn_disable", "", "", ""),
            ),
        ),
        "dzn_claim_wide_lines": (
            "DZN Claim Wide Lines",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "dzn_claim_wide_lines", "", "", ""),
            ),
        ),
        "dzn_enable_8bit_loads_stores": (
            "DZN 8-Bit Loads and Stores",
            (
                ("skip", None),
                ("default", ""),
                ("off", "false"),
                ("on", "true"),
            ),
            (
                ("environment_variable", "dzn_enable_8bit_loads_stores", "", "", ""),
            ),
        ),
        "dzn_debug_all": (
            "DZN Debug All",
            (
                ("skip", None),
                ("default", ""),
                ("on", "all"),
            ),
            (
                ("environment_variable", "DZN_DEBUG", ",", "", ""),
            ),
        ),
        "dzn_debug_nir": (
            "DZN Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "DZN_DEBUG", ",", "", ""),
            ),
        ),
        "dzn_debug_dxil": (
            "DZN Debug DXIL",
            (
                ("skip", None),
                ("default", ""),
                ("on", "dxil"),
            ),
            (
                ("environment_variable", "DZN_DEBUG", ",", "", ""),
            ),
        ),
        "dxil_debug_all": (
            "DXIL Debug All",
            (
                ("skip", None),
                ("default", ""),
                ("on", "all"),
            ),
            (
                ("environment_variable", "DXIL_DEBUG", ",", "", ""),
            ),
        ),
        "dxil_debug_nir": (
            "DXIL Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "DXIL_DEBUG", ",", "", ""),
            ),
        ),
        "d3d12_debug_verbose": (
            "D3D12 Debug Verbose",
            (
                ("skip", None),
                ("default", ""),
                ("on", "verbose"),
            ),
            (
                ("environment_variable", "D3D12_DEBUG", ",", "", ""),
            ),
        ),
        "d3d12_debug_dxil": (
            "D3D12 Debug DXIL",
            (
                ("skip", None),
                ("default", ""),
                ("on", "dxil"),
            ),
            (
                ("environment_variable", "D3D12_DEBUG", ",", "", ""),
            ),
        ),
        "d3d12_gpu_preference": (
            "D3D12 GPU Preference",
            (
                ("skip", None),
                ("default", ""),
                ("unspecified", "unspecified"),
                ("minimum", "minimum"),
                ("high-performance", "high_performance"),
            ),
            (
                ("environment_variable", "D3D12_GPU_PREFERENCE", "", "", ""),
            ),
        ),
        "d3d_always_software": (
            "D3D Always Software",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "D3D_ALWAYS_SOFTWARE", "", "", ""),
            ),
        ),
        "d3d_module_path": (
            "D3D Module Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "D3D_MODULE_PATH", "", "", ""),
            ),
        ),
        "clc_debug_all": (
            "CLC Debug All",
            (
                ("skip", None),
                ("default", ""),
                ("on", "all"),
            ),
            (
                ("environment_variable", "CLC_DEBUG", ",", "", ""),
            ),
        ),
        "clc_debug_spirv": (
            "CLC Debug SPIR-V",
            (
                ("skip", None),
                ("default", ""),
                ("on", "spirv"),
            ),
            (
                ("environment_variable", "CLC_DEBUG", ",", "", ""),
            ),
        ),
        "clover_device_type": (
            "Clover Device Type",
            (
                ("skip", None),
                ("default", ""),
                ("gpu", "gpu"),
                ("cpu", "cpu"),
                ("all", "all"),
            ),
            (
                ("environment_variable", "CLOVER_DEVICE_TYPE", "", "", ""),
            ),
        ),
        "clover_device_version_override": (
            "Clover Device Version Override",
            (
                ("skip", None),
                ("default", ""),
                ("1.0", "1.0"),
                ("1.1", "1.1"),
                ("1.2", "1.2"),
                ("2.0", "2.0"),
            ),
            (
                ("environment_variable", "CLOVER_DEVICE_VERSION_OVERRIDE", "", "", ""),
            ),
        ),
        "clover_device_clc_version_override": (
            "Clover CLC Version Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "CLOVER_DEVICE_CLC_VERSION_OVERRIDE", "", "", ""),
            ),
        ),
        "clover_extra_build_options": (
            "Clover Extra Build Options",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "CLOVER_EXTRA_BUILD_OPTIONS", "", "", ""),
            ),
        ),
        "clover_extra_compile_options": (
            "Clover Extra Compile Options",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "CLOVER_EXTRA_COMPILE_OPTIONS", "", "", ""),
            ),
        ),
        "clover_extra_link_options": (
            "Clover Extra Link Options",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "CLOVER_EXTRA_LINK_OPTIONS", "", "", ""),
            ),
        ),
        "rusticl_debug_all": (
            "RustICL Debug All",
            (
                ("skip", None),
                ("default", ""),
                ("on", "all"),
            ),
            (
                ("environment_variable", "RUSTICL_DEBUG", ",", "", ""),
            ),
        ),
        "rusticl_debug_nir": (
            "RustICL Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "RUSTICL_DEBUG", ",", "", ""),
            ),
        ),
        "rusticl_opencl_version": (
            "RustICL OpenCL Version",
            (
                ("skip", None),
                ("default", ""),
                ("1.0", "1.0"),
                ("1.1", "1.1"),
                ("1.2", "1.2"),
                ("3.0", "3.0"),
            ),
            (
                ("environment_variable", "RUSTICL_CL_VERSION", "", "", ""),
            ),
        ),
        "rusticl_device_type": (
            "RustICL Device Type",
            (
                ("skip", None),
                ("default", ""),
                ("gpu", "gpu"),
                ("cpu", "cpu"),
            ),
            (
                ("environment_variable", "RUSTICL_DEVICE_TYPE", "", "", ""),
            ),
        ),
        "rusticl_maximum_work_groups": (
            "RustICL Maximum Work Groups",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "RUSTICL_MAX_WORK_GROUPS", "", "", ""),
            ),
        ),
        "rusticl_enable_extensions": (
            "RustICL Enable Extensions",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "RUSTICL_ENABLE", ",", "", ""),
            ),
        ),
        "rusticl_features": (
            "RustICL Features",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "RUSTICL_FEATURES", ",", "", ""),
            ),
        ),
        "vdpau_driver_selection": (
            "VDPAU Driver Selection",
            (
                ("skip", None),
                ("default", ""),
                ("nvidia", "nvidia"),
                ("nouveau", "nouveau"),
                ("radeonsi", "radeonsi"),
                ("va-gl", "va_gl"),
            ),
            (
                ("environment_variable", "VDPAU_DRIVER", "", "", ""),
            ),
        ),
        "vdpau_driver_path": (
            "VDPAU Driver Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VDPAU_DRIVER_PATH", "", "", ""),
            ),
        ),
        "vdpau_trace": (
            "VDPAU Trace",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("calls", "1"),
                ("detailed", "2"),
            ),
            (
                ("environment_variable", "VDPAU_TRACE", "", "", ""),
            ),
        ),
        "vdpau_trace_file": (
            "VDPAU Trace File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VDPAU_TRACE_FILE", "", "", ""),
            ),
        ),
        "vdpau_quirks_nvidia_force_mixed_mode": (
            "VDPAU Quirk NVIDIA Mixed Mode",
            (
                ("skip", None),
                ("default", ""),
                ("on", "NVidia_Force_Mixed_Mode"),
            ),
            (
                ("environment_variable", "VDPAU_QUIRKS", ",", "", ""),
            ),
        ),
        "vdpau_quirks_nvidia_force_windowed": (
            "VDPAU Quirk NVIDIA Windowed",
            (
                ("skip", None),
                ("default", ""),
                ("on", "NVidia_Force_Windowed"),
            ),
            (
                ("environment_variable", "VDPAU_QUIRKS", ",", "", ""),
            ),
        ),
        "vdpau_osd": (
            "VDPAU OSD",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VDPAU_OSD", "", "", ""),
            ),
        ),
        "vdpau_disable_g2d": (
            "VDPAU Disable G2D",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VDPAU_DISABLE_G2D", "", "", ""),
            ),
        ),
        "vaapi_mpeg4_enabled": (
            "VAAPI MPEG4 Enabled",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VAAPI_MPEG4_ENABLED", "", "", ""),
            ),
        ),
        "libva_driver_name": (
            "VA-API Driver Name",
            (
                ("skip", None),
                ("default", ""),
                ("radeonsi", "radeonsi"),
                ("nvidia", "nvidia"),
                ("iHD", "iHD"),
                ("i965", "i965"),
                ("nouveau", "nouveau"),
            ),
            (
                ("environment_variable", "LIBVA_DRIVER_NAME", "", "", ""),
            ),
        ),
        "libva_drivers_path": (
            "VA-API Drivers Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "LIBVA_DRIVERS_PATH", ":", "", ""),
            ),
        ),
        "libva_messaging_level": (
            "VA-API Messaging Level",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
            ),
            (
                ("environment_variable", "LIBVA_MESSAGING_LEVEL", "", "", ""),
            ),
        ),
        "libva_trace": (
            "VA-API Trace",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "LIBVA_TRACE", "", "", ""),
            ),
        ),
        "libva_trace_buffer_data": (
            "VA-API Trace Buffer Data",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LIBVA_TRACE_BUFDATA", "", "", ""),
            ),
        ),
        "libva_trace_coded_buffer": (
            "VA-API Trace Coded Buffer",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LIBVA_TRACE_CODEDBUF", "", "", ""),
            ),
        ),
        "libva_trace_surface": (
            "VA-API Trace Surface",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LIBVA_TRACE_SURFACE", "", "", ""),
            ),
        ),
        "libva_trace_surface_geometry": (
            "VA-API Trace Surface Geometry",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LIBVA_TRACE_SURFACE_GEOMETRY", "", "", ""),
            ),
        ),
        "libva_dri3_disable": (
            "VA-API DRI3 Disable",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "LIBVA_DRI3_DISABLE", "", "", ""),
            ),
        ),
        "nine_fixed_function_dump": (
            "Nine Fixed Function Dump",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NINE_FF_DUMP", "", "", ""),
            ),
        ),
        "nine_debug_shaders": (
            "Nine Debug Shaders",
            (
                ("skip", None),
                ("default", ""),
                ("on", "shaders"),
            ),
            (
                ("environment_variable", "NINE_DEBUG", ",", "", ""),
            ),
        ),
        "nine_debug_user": (
            "Nine Debug User",
            (
                ("skip", None),
                ("default", ""),
                ("on", "user"),
            ),
            (
                ("environment_variable", "NINE_DEBUG", ",", "", ""),
            ),
        ),
        "nine_shader_debug_nir": (
            "Nine Shader Debug NIR",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nir"),
            ),
            (
                ("environment_variable", "NINE_SHADER", ",", "", ""),
            ),
        ),
        "nine_shader_debug_no_optimization": (
            "Nine Shader Debug No Optimization",
            (
                ("skip", None),
                ("default", ""),
                ("on", "nopt"),
            ),
            (
                ("environment_variable", "NINE_SHADER", ",", "", ""),
            ),
        ),
        "nine_quirks_dynamic_texture": (
            "Nine Quirk Dynamic Texture",
            (
                ("skip", None),
                ("default", ""),
                ("on", "dynamic_texture"),
            ),
            (
                ("environment_variable", "NINE_QUIRKS", ",", "", ""),
            ),
        ),
        "nine_quirks_force_default_pool": (
            "Nine Quirk Force Default Pool",
            (
                ("skip", None),
                ("default", ""),
                ("on", "force_default_pool"),
            ),
            (
                ("environment_variable", "NINE_QUIRKS", ",", "", ""),
            ),
        ),
        "nvk_experimental_gpu_support": (
            "NVK Experimental GPU Support",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "true"),
            ),
            (
                ("environment_variable", "NVK_I_WANT_A_BROKEN_VULKAN_DRIVER", "", "", ""),
            ),
        ),
        "panfrost_experimental_gpu_support": (
            "Panfrost Experimental GPU Support",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "PAN_I_WANT_A_BROKEN_DRIVER", "", "", ""),
            ),
        ),
        "panvk_experimental_gpu_support": (
            "PanVK Experimental GPU Support",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "PAN_I_WANT_A_BROKEN_VULKAN_DRIVER", "", "", ""),
            ),
        ),
        "pvr_experimental_vulkan": (
            "PVR Experimental Vulkan",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "PVR_I_WANT_A_BROKEN_VULKAN_DRIVER", "", "", ""),
            ),
        ),
    }
