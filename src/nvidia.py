def get_nvidia_settings():
    return {
        "_tab_metadata": (True,),
        "_executable_required": (),
        "opengl_vertical_synchronization": (
            "OpenGL Vertical Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "__GL_SYNC_TO_VBLANK", "", "", ""),
            ),
        ),
        "opengl_adaptive_synchronization": (
            "Adaptive Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("off", ("0", "0")),
                ("on", ("1", "1")),
            ),
            (
                ("environment_variable", "__GL_VRR_ALLOWED", "", "", ""),
                ("environment_variable", "__GL_GSYNC_ALLOWED", "", "", ""),
            ),
        ),
        "opengl_synchronization_display_device": (
            "Synchronization Display Device",
            (
                ("skip", None),
                ("default", ""),
                ("DFP-0", "DFP-0"),
                ("DFP-1", "DFP-1"),
                ("DFP-2", "DFP-2"),
                ("DFP-3", "DFP-3"),
                ("DP-0", "DP-0"),
                ("DP-1", "DP-1"),
                ("HDMI-0", "HDMI-0"),
                ("HDMI-1", "HDMI-1"),
                ("CRT-0", "CRT-0"),
                ("CRT-1", "CRT-1"),
            ),
            (
                ("environment_variable", "__GL_SYNC_DISPLAY_DEVICE", "", "", ""),
            ),
        ),
        "opengl_tearing_free_swap_present": (
            "Tearing-Free Swap Present",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_TearingFreeSwapPresent", "", "", ""),
            ),
        ),
        "opengl_constant_frame_rate_hint": (
            "Constant Frame Rate Hint",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_CONSTANT_FRAME_RATE_HINT", "", "", ""),
            ),
        ),
        "opengl_flush_control": (
            "Flush Control",
            (
                ("skip", None),
                ("default", ""),
                ("automatic", "0"),
                ("explicit", "1"),
            ),
            (
                ("environment_variable", "__GL_FLUSH_CONTROL", "", "", ""),
            ),
        ),
        "opengl_threaded_optimization": (
            "Threaded Optimization",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "__GL_THREADED_OPTIMIZATIONS", "", "", ""),
            ),
        ),
        "opengl_single_threaded": (
            "Single Threaded",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_SINGLE_THREADED", "", "", ""),
            ),
        ),
        "opengl_thread_affinity": (
            "Thread Affinity",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_ThreadAffinity", "", "", ""),
            ),
        ),
        "opengl_thread_control": (
            "Thread Control",
            (
                ("skip", None),
                ("default", ""),
                ("none", "NONE"),
                ("driver", "DRIVER"),
            ),
            (
                ("environment_variable", "__GL_ThreadControl", "", "", ""),
            ),
        ),
        "opengl_thread_control_secondary": (
            "Thread Control Secondary",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_ThreadControl2", "", "", ""),
            ),
        ),
        "opengl_wait_behavior": (
            "Wait Behavior",
            (
                ("skip", None),
                ("default", ""),
                ("active", "NOTHING"),
                ("sleep", "USLEEP"),
            ),
            (
                ("environment_variable", "__GL_YIELD", "", "", ""),
            ),
        ),
        "opengl_yield_function": (
            "Yield Function",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_yieldFunction", "", "", ""),
            ),
        ),
        "opengl_yield_function_fast": (
            "Yield Function Fast",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_yieldFunctionFast", "", "", ""),
            ),
        ),
        "opengl_yield_function_slow": (
            "Yield Function Slow",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_yieldFunctionSlow", "", "", ""),
            ),
        ),
        "opengl_yield_function_wait_display_controller_queue": (
            "Yield Function Wait Display Controller Queue",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_yieldFunctionWaitForDcQueue", "", "", ""),
            ),
        ),
        "opengl_yield_function_wait_frame": (
            "Yield Function Wait Frame",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_yieldFunctionWaitForFrame", "", "", ""),
            ),
        ),
        "opengl_yield_function_wait_graphics_processing_unit": (
            "Yield Function Wait Graphics Processing Unit",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_yieldFunctionWaitForGpu", "", "", ""),
            ),
        ),
        "opengl_maximum_prerendered_frames": (
            "Maximum Prerendered Frames",
            (
                ("skip", None),
                ("default", ""),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
                ("4", "4"),
            ),
            (
                ("environment_variable", "__GL_MaxFramesAllowed", "", "", ""),
            ),
        ),
        "opengl_texture_quality": (
            "Texture Quality",
            (
                ("skip", None),
                ("default", ""),
                ("quality", "1"),
                ("balanced", "2"),
                ("performance", "3"),
            ),
            (
                ("environment_variable", "__GL_OpenGLImageSettings", "", "", ""),
            ),
        ),
        "opengl_forced_antialiasing": (
            "Forced Antialiasing",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("2x-multisampling", "1"),
                ("2x-quincunx", "2"),
                ("4x-multisampling", "5"),
                ("4x-gaussian", "6"),
                ("8x-coverage", "7"),
                ("16x-coverage", "8"),
                ("8x-hybrid", "9"),
                ("8x-multisampling", "10"),
                ("16x-hybrid", "11"),
                ("16x-combined", "12"),
                ("32x-combined", "14"),
            ),
            (
                ("environment_variable", "__GL_FSAA_MODE", "", "", ""),
            ),
        ),
        "opengl_fast_approximate_antialiasing": (
            "Fast Approximate Antialiasing",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "__GL_ALLOW_FXAA_USAGE", "", "", ""),
            ),
        ),
        "opengl_forced_anisotropic_filtering": (
            "Forced Anisotropic Filtering",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("2x", "1"),
                ("4x", "2"),
                ("8x", "3"),
                ("16x", "4"),
            ),
            (
                ("environment_variable", "__GL_LOG_MAX_ANISO", "", "", ""),
            ),
        ),
        "opengl_cubemap_anisotropic_filtering": (
            "Cubemap Anisotropic Filtering",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_CubemapAniso", "", "", ""),
            ),
        ),
        "opengl_cubemap_filtering": (
            "Cubemap Filtering",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_CubemapFiltering", "", "", ""),
            ),
        ),
        "opengl_antialiased_line_gamma": (
            "Antialiased Line Gamma",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_AALineGamma", "", "", ""),
            ),
        ),
        "opengl_antialiased_line_tweaks": (
            "Antialiased Line Tweaks",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_AALineTweaks", "", "", ""),
            ),
        ),
        "opengl_s3tc_compression_quality": (
            "S3TC Compression Quality",
            (
                ("skip", None),
                ("default", ""),
                ("lowest", "0"),
                ("low", "1"),
                ("medium", "2"),
                ("high", "3"),
                ("highest", "4"),
            ),
            (
                ("environment_variable", "__GL_S3TCQuality", "", "", ""),
            ),
        ),
        "opengl_texture_level_of_detail_bias": (
            "Texture Level of Detail Bias",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_TexLODBias", "", "", ""),
            ),
        ),
        "opengl_texture_clamp_behavior": (
            "Texture Clamp Behavior",
            (
                ("skip", None),
                ("default", ""),
                ("permissive", "0"),
                ("strict", "1"),
            ),
            (
                ("environment_variable", "__GL_TexClampBehavior", "", "", ""),
            ),
        ),
        "opengl_texture_precache": (
            "Texture Precache",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_TexturePrecache", "", "", ""),
            ),
        ),
        "opengl_implicit_mipmap_generation": (
            "Implicit Mipmap Generation",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "__GL_IMPLICIT_GENERATE_MIPMAP", "", "", ""),
            ),
        ),
        "opengl_sparse_texture": (
            "Sparse Texture",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_SparseTexture", "", "", ""),
            ),
        ),
        "opengl_skip_texture_host_copies": (
            "Skip Texture Host Copies",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_SkipTextureHostCopies", "", "", ""),
            ),
        ),
        "opengl_skip_texture_host_copies_flags": (
            "Skip Texture Host Copies Flags",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_SkipTextureHostCopiesFlags", "", "", ""),
            ),
        ),
        "opengl_early_texture_hardware_allocation": (
            "Early Texture Hardware Allocation",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_EarlyTextureHWAllocation", "", "", ""),
            ),
        ),
        "opengl_framebuffer_blit_ignore_standard_rgb": (
            "Framebuffer Blit Ignore Standard RGB",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_FBO_BLIT_IGNORE_SRGB", "", "", ""),
            ),
        ),
        "opengl_image_sharpening": (
            "Image Sharpening",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_SHARPEN_ENABLE", "", "", ""),
            ),
        ),
        "opengl_image_sharpening_intensity": (
            "Image Sharpening Intensity",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("10", "10"),
                ("25", "25"),
                ("35", "35"),
                ("50", "50"),
                ("75", "75"),
                ("100", "100"),
            ),
            (
                ("environment_variable", "__GL_SHARPEN_VALUE", "", "", ""),
            ),
        ),
        "opengl_image_denoising_intensity": (
            "Image Denoising Intensity",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("17", "17"),
                ("25", "25"),
                ("50", "50"),
                ("75", "75"),
                ("100", "100"),
            ),
            (
                ("environment_variable", "__GL_SHARPEN_IGNORE_FILM_GRAIN", "", "", ""),
            ),
        ),
        "opengl_fast_geometry_shader": (
            "Fast Geometry Shader",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_FastGS", "", "", ""),
            ),
        ),
        "opengl_shader_atomics": (
            "Shader Atomics",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "__GL_ShaderAtomics", "", "", ""),
            ),
        ),
        "opengl_next_generation_compiler": (
            "Next Generation Compiler",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_NextGenCompiler", "", "", ""),
            ),
        ),
        "opengl_glsl_extension_validation": (
            "GLSL Extension Validation",
            (
                ("skip", None),
                ("default", ""),
                ("strict", "0"),
                ("relaxed", "1"),
            ),
            (
                ("environment_variable", "__GL_IGNORE_GLSL_EXT_REQS", "", "", ""),
            ),
        ),
        "opengl_extension_string_version": (
            "Extension String Version",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_ExtensionStringVersion", "", "", ""),
            ),
        ),
        "opengl_extension_string_architecture": (
            "Extension String Architecture",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_ExtensionStringNVArch", "", "", ""),
            ),
        ),
        "opengl_unofficial_glx_protocol": (
            "Unofficial GLX Protocol",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_ALLOW_UNOFFICIAL_PROTOCOL", "", "", ""),
            ),
        ),
        "opengl_force_requested_embedded_systems_version": (
            "Force Requested Embedded Systems Version",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_ForceRequestedESVersion", "", "", ""),
            ),
        ),
        "opengl_application_return_only_basic_glsl_type": (
            "Application Return Only Basic GLSL Type",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_AppReturnOnlyBasicGlslType", "", "", ""),
            ),
        ),
        "opengl_conformant_blit_framebuffer_scissor": (
            "Conformant Blit Framebuffer Scissor",
            (
                ("skip", None),
                ("default", ""),
                ("permissive", "0"),
                ("conformant", "1"),
            ),
            (
                ("environment_variable", "__GL_ConformantBlitFramebufferScissor", "", "", ""),
            ),
        ),
        "opengl_conformant_incomplete_texture": (
            "Conformant Incomplete Texture",
            (
                ("skip", None),
                ("default", ""),
                ("permissive", "0"),
                ("conformant", "1"),
            ),
            (
                ("environment_variable", "__GL_ConformantIncompleteTexture", "", "", ""),
            ),
        ),
        "opengl_disallow_software_fallback": (
            "Disallow Software Fallback",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_DISALLOW_SOFTWARE_FALLBACK", "", "", ""),
                ("environment_variable", "__GL_DisallowSWFallback", "", "", ""),
            ),
        ),
        "opengl_framebuffer_configuration_sorting": (
            "Framebuffer Configuration Sorting",
            (
                ("skip", None),
                ("default", ""),
                ("server", "0"),
                ("sorted", "1"),
            ),
            (
                ("environment_variable", "__GL_SORT_FBCONFIGS", "", "", ""),
            ),
        ),
        "opengl_force_direct_rendering": (
            "Force Direct Rendering",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_FORCE_DIRECT", "", "", ""),
            ),
        ),
        "opengl_force_indirect_rendering": (
            "Force Indirect Rendering",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_FORCE_INDIRECT", "", "", ""),
            ),
        ),
        "opengl_software_renderer": (
            "Software Renderer",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_SW_RENDERER", "", "", ""),
            ),
        ),
        "opengl_force_generic_cpu": (
            "Force Generic CPU",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_FORCE_GENERIC_CPU", "", "", ""),
            ),
        ),
        "opengl_strict_draw_range_elements": (
            "Strict Draw Range Elements",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_StrictDrawRangeElements", "", "", ""),
            ),
        ),
        "opengl_release_texture_image_error": (
            "Release Texture Image Error",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_RELEASE_TEX_IMAGE_ERROR", "", "", ""),
            ),
        ),
        "opengl_disallow_sixteen_bit_depth": (
            "Disallow Sixteen Bit Depth",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_DisallowZ16", "", "", ""),
            ),
        ),
        "opengl_scalable_link_interface_control": (
            "Scalable Link Interface Control",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
            ),
            (
                ("environment_variable", "__GL_SLI_DLI_CONTROL", "", "", ""),
            ),
        ),
        "opengl_mosaic_clip_to_sub_device": (
            "Mosaic Clip to Sub Device",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_MOSAIC_CLIP_TO_SUBDEV", "", "", ""),
            ),
        ),
        "opengl_mosaic_horizontal_overlap": (
            "Mosaic Horizontal Overlap",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_MOSAIC_CLIP_TO_SUBDEV_H_OVERLAP", "", "", ""),
            ),
        ),
        "opengl_mosaic_vertical_overlap": (
            "Mosaic Vertical Overlap",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_MOSAIC_CLIP_TO_SUBDEV_V_OVERLAP", "", "", ""),
            ),
        ),
        "opengl_executable_memory_workaround": (
            "Executable Memory Workaround",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "__GL_WRITE_TEXT_SECTION", "", "", ""),
            ),
        ),
        "opengl_doom_3_compatibility": (
            "Doom 3 Compatibility",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "true"),
            ),
            (
                ("environment_variable", "__GL_DOOM3", "", "", ""),
            ),
        ),
        "opengl_no_dynamic_shared_object_finalizer": (
            "No Dynamic Shared Object Finalizer",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_NO_DSO_FINALIZER", "", "", ""),
            ),
        ),
        "opengl_always_handle_fork": (
            "Always Handle Fork",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_ALWAYS_HANDLE_FORK", "", "", ""),
            ),
        ),
        "opengl_at_fork_mode": (
            "At Fork Mode",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
            ),
            (
                ("environment_variable", "__GL_ATFORK_MODE", "", "", ""),
            ),
        ),
        "opengl_force_exit_process_detach": (
            "Force Exit Process Detach",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_ForceExitProcessDetach", "", "", ""),
            ),
        ),
        "opengl_selinux_booleans": (
            "SELinux Booleans",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_SELINUX_BOOLEANS", ",", "", ""),
            ),
        ),
        "opengl_disable_low_level_driver_optimization": (
            "Disable Low Level Driver Optimization",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_dislldopt", "", "", ""),
            ),
        ),
        "opengl_hardware_context_control": (
            "Hardware Context Control",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_HCCTRL", "", "", ""),
            ),
        ),
        "opengl_maya_optimize": (
            "Maya Optimize",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_MAYA_OPTIMIZE", "", "", ""),
            ),
        ),
        "opengl_x_server_adapter_present": (
            "X Server Adapter Present",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_XNvAdapterPresent", "", "", ""),
            ),
        ),
        "opengl_texture_memory_space_enables": (
            "Texture Memory Space Enables",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_TEX_MEMORY_SPACE_ENABLES", "", "", ""),
                ("environment_variable", "__GL_TexMemorySpaceEnables", "", "", ""),
            ),
        ),
        "opengl_heap_allocation_limit": (
            "Heap Allocation Limit",
            (
                ("skip", None),
                ("default", ""),
                ("12MB", "12MB"),
                ("20MB", "20MB"),
                ("50MB", "50MB"),
                ("100MB", "100MB"),
                ("200MB", "200MB"),
                ("500MB", "500MB"),
            ),
            (
                ("environment_variable", "__GL_HEAP_ALLOC_LIMIT", "", "", ""),
            ),
        ),
        "opengl_device_shared_memory_pageable_allocations": (
            "Device Shared Memory Pageable Allocations",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_DevShmPageableAllocations", "", "", ""),
            ),
        ),
        "opengl_allocate_device_events": (
            "Allocate Device Events",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_AllocDeviceEvents", "", "", ""),
            ),
        ),
        "opengl_hardware_state_per_context": (
            "Hardware State Per Context",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_HWSTATE_PER_CTX", "", "", ""),
            ),
        ),
        "opengl_system_memory_texture_promotion": (
            "System Memory Texture Promotion",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_SysmemTexturePromotion", "", "", ""),
            ),
        ),
        "opengl_cache_disable": (
            "Cache Disable",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_CacheDisable", "", "", ""),
            ),
        ),
        "opengl_zero_bandwidth_compression_table_hysteresis": (
            "Zero Bandwidth Compression Table Hysteresis",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_ZbcTableAddHysteresis", "", "", ""),
            ),
        ),
        "opengl_vertex_pipe_format_bloat_limit": (
            "Vertex Pipe Format Bloat Limit",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_VpipeFormatBloatLimit", "", "", ""),
            ),
        ),
        "opengl_copy_buffer_method": (
            "Copy Buffer Method",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
            ),
            (
                ("environment_variable", "__GL_CopyBufferMethod", "", "", ""),
            ),
        ),
        "opengl_overlay_merge_blit_timer": (
            "Overlay Merge Blit Timer",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_OverlayMergeBlitTimerMs", "", "", ""),
            ),
        ),
        "opengl_disallow_copy_engine_mask": (
            "Disallow Copy Engine Mask",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_DisallowCEMask", "", "", ""),
            ),
        ),
        "opengl_robust_hardware_context": (
            "Robust Hardware Context",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "ENABLE_ROBUST"),
            ),
            (
                ("environment_variable", "OGL_DEDICATED_HW_STATE_PER_CONTEXT", "", "", ""),
            ),
        ),
        "opengl_application_profile": (
            "Application Profile",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "__GL_APPLICATION_PROFILE", "", "", ""),
            ),
        ),
        "opengl_application_profile_log": (
            "Application Profile Log",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_APPLICATION_PROFILE_LOG", "", "", ""),
            ),
        ),
        "opengl_application_key": (
            "Application Key",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_ApplicationKey", "", "", ""),
            ),
        ),
        "opengl_application_support_bitmask_secondary": (
            "Application Support Bitmask Secondary",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_App_SupportBits2", "", "", ""),
            ),
        ),
        "opengl_shader_disk_cache": (
            "Shader Disk Cache",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "__GL_SHADER_DISK_CACHE", "", "", ""),
            ),
        ),
        "opengl_shader_disk_cache_path": (
            "Shader Disk Cache Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_SHADER_DISK_CACHE_PATH", "", "", ""),
            ),
        ),
        "opengl_shader_disk_cache_maximum_size": (
            "Shader Disk Cache Maximum Size",
            (
                ("skip", None),
                ("default", ""),
                ("1GB", "1073741824"),
                ("2GB", "2147483648"),
                ("5GB", "5368709120"),
                ("10GB", "10737418240"),
                ("25GB", "26843545600"),
                ("50GB", "53687091200"),
            ),
            (
                ("environment_variable", "__GL_SHADER_DISK_CACHE_SIZE", "", "", ""),
            ),
        ),
        "opengl_shader_disk_cache_cleanup": (
            "Shader Disk Cache Cleanup",
            (
                ("skip", None),
                ("default", ""),
                ("off", "1"),
                ("on", ""),
            ),
            (
                ("environment_variable", "__GL_SHADER_DISK_CACHE_SKIP_CLEANUP", "", "", ""),
            ),
        ),
        "opengl_shader_disk_cache_read_only": (
            "Shader Disk Cache Read Only",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_SHADER_DISK_CACHE_READ_ONLY", "", "", ""),
            ),
        ),
        "opengl_shader_cache_initial_size": (
            "Shader Cache Initial Size",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_ShaderCacheInitSize", "", "", ""),
            ),
        ),
        "opengl_shader_portability_warnings": (
            "Shader Portability Warnings",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_SHADER_PORTABILITY_WARNINGS", "", "", ""),
            ),
        ),
        "opengl_graphics_on_screen_display": (
            "Graphics On-Screen Display",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_SHOW_GRAPHICS_OSD", "", "", ""),
            ),
        ),
        "opengl_debug_level": (
            "Debug Level",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
            ),
            (
                ("environment_variable", "__GL_DEBUG_LEVEL", "", "", ""),
            ),
        ),
        "opengl_debug_mask": (
            "Debug Mask",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_DEBUG_MASK", "", "", ""),
            ),
        ),
        "opengl_debug_options": (
            "Debug Options",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_DEBUG_OPTIONS", "", "", ""),
            ),
        ),
        "opengl_debug_bypass_assert": (
            "Debug Bypass Assert",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_DEBUG_BYPASS_ASSERT", "", "", ""),
            ),
        ),
        "opengl_debugger": (
            "Debugger",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_DEBUGGER", "", "", ""),
            ),
        ),
        "opengl_event_log_file": (
            "Event Log File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_EVENT_LOGFILE", "", "", ""),
            ),
        ),
        "opengl_event_log_level": (
            "Event Log Level",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
            ),
            (
                ("environment_variable", "__GL_EVENT_LOGLEVEL", "", "", ""),
            ),
        ),
        "opengl_expert_detail_level": (
            "Expert Detail Level",
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
                ("environment_variable", "__GL_EXPERT_DETAIL_LEVEL", "", "", ""),
            ),
        ),
        "opengl_expert_output_mask": (
            "Expert Output Mask",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_EXPERT_OUTPUT_MASK", "", "", ""),
            ),
        ),
        "opengl_expert_report_mask": (
            "Expert Report Mask",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_EXPERT_REPORT_MASK", "", "", ""),
            ),
        ),
        "opengl_performance_monitor_mode": (
            "Performance Monitor Mode",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
            ),
            (
                ("environment_variable", "__GL_PerfmonMode", "", "", ""),
            ),
        ),
        "opengl_graphics_video_interface_timeout_control": (
            "Graphics Video Interface Timeout Control",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__GL_GVITimeOutControl", "", "", ""),
            ),
        ),
        "opengl_use_graphics_video_interface_events": (
            "Use Graphics Video Interface Events",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_UseGVIEvents", "", "", ""),
            ),
        ),
        "vulkan_layer_optimus": (
            "Vulkan Layer Optimus",
            (
                ("skip", None),
                ("default", ""),
                ("nvidia-only", "NVIDIA_only"),
                ("non-nvidia-only", "non_NVIDIA_only"),
            ),
            (
                ("environment_variable", "__VK_LAYER_NV_optimus", "", "", ""),
            ),
        ),
        "vulkan_disable_layer_optimus": (
            "Disable Layer Optimus",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "DISABLE_LAYER_NV_OPTIMUS_1", "", "", ""),
            ),
        ),
        "vulkan_ray_tracing_validation": (
            "Ray Tracing Validation",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NV_ALLOW_RAYTRACING_VALIDATION", "", "", ""),
            ),
        ),
        "vulkan_smooth_motion_frame_generation": (
            "Smooth Motion Frame Generation",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NVPRESENT_ENABLE_SMOOTH_MOTION", "", "", ""),
            ),
        ),
        "vulkan_nvpresent_log_file": (
            "NVPresent Log File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "NVPRESENT_LOG_FILE", "", "", ""),
            ),
        ),
        "vulkan_nvpresent_log_level": (
            "NVPresent Log Level",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
            ),
            (
                ("environment_variable", "NVPRESENT_LOG_LEVEL", "", "", ""),
            ),
        ),
        "vulkan_nvpresent_queue_family": (
            "NVPresent Queue Family",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "NVPRESENT_QUEUE_FAMILY", "", "", ""),
            ),
        ),
        "prime_render_offload": (
            "PRIME Render Offload",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__NV_PRIME_RENDER_OFFLOAD", "", "", ""),
            ),
        ),
        "prime_render_offload_provider": (
            "PRIME Render Offload Provider",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "__NV_PRIME_RENDER_OFFLOAD_PROVIDER", "", "", ""),
            ),
        ),
        "disable_explicit_synchronization": (
            "Disable Explicit Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__NV_DISABLE_EXPLICIT_SYNC", "", "", ""),
            ),
        ),
        "vdpau_no_overlay": (
            "VDPAU No Overlay",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VDPAU_NVIDIA_NO_OVERLAY", "", "", ""),
            ),
        ),
        "vdpau_synchronization_display_device": (
            "VDPAU Synchronization Display Device",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "VDPAU_NVIDIA_SYNC_DISPLAY_DEVICE", "", "", ""),
            ),
        ),
        "vdpau_debug": (
            "VDPAU Debug",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VDPAU_NVIDIA_DEBUG", "", "", ""),
            ),
        ),
        "vdpau_disable_error_concealment": (
            "VDPAU Disable Error Concealment",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "VDPAU_NVIDIA_DISABLE_ERROR_CONCEALMENT", "", "", ""),
            ),
        ),
        "vdpau_xinerama_physical_screen": (
            "VDPAU Xinerama Physical Screen",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
            ),
            (
                ("environment_variable", "VDPAU_NVIDIA_XINERAMA_PHYSICAL_SCREEN", "", "", ""),
            ),
        ),
        "nvidia_video_decode_backend": (
            "NVIDIA Video Decode Backend",
            (
                ("skip", None),
                ("default", ""),
                ("nvdec", "nvdec"),
                ("cuda", "cuda"),
                ("gl", "gl"),
            ),
            (
                ("environment_variable", "NVD_BACKEND", "", "", ""),
            ),
        ),
        "nvidia_video_decode_graphics_processing_unit": (
            "NVIDIA Video Decode Graphics Processing Unit",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "NVD_GPU", "", "", ""),
            ),
        ),
        "nvidia_video_decode_log": (
            "NVIDIA Video Decode Log",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "NVD_LOG", "", "", ""),
            ),
        ),
        "nvidia_video_decode_maximum_instances": (
            "NVIDIA Video Decode Maximum Instances",
            (
                ("skip", None),
                ("default", ""),
                ("1", "1"),
                ("2", "2"),
                ("4", "4"),
            ),
            (
                ("environment_variable", "NVD_MAX_INSTANCES", "", "", ""),
            ),
        ),
        "experimental_performance_strategy": (
            "Experimental Performance Strategy",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "__GL_ExperimentalPerfStrategy", "", "", ""),
            ),
        ),
    }
