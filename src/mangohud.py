def get_mangohud_settings():
    return {
        "_tab_metadata": (True,),
        "_executable_required": ("mangohud",),
        "enable": (
            "Enable MangoHud",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("argument", "mangohud", "", "", ""),
                ("environment_variable", "MANGOHUD", "", "", ""),
            ),
        ),
        "disable": (
            "Disable MangoHud",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "1"),
            ),
            (
                ("environment_variable", "DISABLE_MANGOHUD", "", "", ""),
            ),
        ),
        "opengl_vertical_synchronization": (
            "OpenGL Vertical Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("on", "1"),
                ("off", "0"),
                ("adaptive", "-1"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "gl_vsync=", ""),
            ),
        ),
        "opengl_libraries_path": (
            "OpenGL Libraries Path",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_OPENGL_LIBS", "", "", ""),
            ),
        ),
        "vulkan_vertical_synchronization": (
            "Vulkan Vertical Synchronization",
            (
                ("skip", None),
                ("default", ""),
                ("on", "3"),
                ("off", "1"),
                ("adaptive", "0"),
                ("mailbox", "2"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "vsync=", ""),
            ),
        ),
        "vulkan_driver": (
            "Vulkan Driver",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "vulkan_driver"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "configuration_file": (
            "Configuration File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIGFILE", "", "", ""),
            ),
        ),
        "presets_file": (
            "Presets File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_PRESETSFILE", "", "", ""),
            ),
        ),
        "read_configuration": (
            "Read Configuration File",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "read_cfg"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "anisotropic_filtering": (
            "Anisotropic Filtering",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
                ("4", "4"),
                ("8", "8"),
                ("16", "16"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "af=", ""),
            ),
        ),
        "mipmap_level_of_detail_bias": (
            "Mipmap Level of Detail Bias",
            (
                ("skip", None),
                ("default", ""),
                ("-16", "-16"),
                ("-8", "-8"),
                ("-4", "-4"),
                ("-2", "-2"),
                ("-1", "-1"),
                ("0", "0"),
                ("1", "1"),
                ("2", "2"),
                ("4", "4"),
                ("8", "8"),
                ("16", "16"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "picmip=", ""),
            ),
        ),
        "bicubic_filtering": (
            "Bicubic Filtering",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "bicubic"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "trilinear_filtering": (
            "Trilinear Filtering",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "trilinear"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "retro_filtering": (
            "Retro Filtering",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "retro"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "frames_per_second_limit": (
            "Frames Per Second Limit",
            (
                ("skip", None),
                ("default", ""),
                ("unlimited", "0"),
                ("10", "10"),
                ("15", "15"),
                ("20", "20"),
                ("24", "24"),
                ("25", "25"),
                ("30", "30"),
                ("35", "35"),
                ("40", "40"),
                ("45", "45"),
                ("48", "48"),
                ("50", "50"),
                ("55", "55"),
                ("60", "60"),
                ("70", "70"),
                ("72", "72"),
                ("75", "75"),
                ("85", "85"),
                ("90", "90"),
                ("100", "100"),
                ("110", "110"),
                ("120", "120"),
                ("144", "144"),
                ("165", "165"),
                ("180", "180"),
                ("200", "200"),
                ("240", "240"),
                ("280", "280"),
                ("300", "300"),
                ("360", "360"),
                ("480", "480"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "fps_limit=", ""),
            ),
        ),
        "frames_per_second_limit_method": (
            "Frames Per Second Limit Method",
            (
                ("skip", None),
                ("default", ""),
                ("late", "late"),
                ("early", "early"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "fps_limit_method=", ""),
            ),
        ),
        "preset": (
            "Preset",
            (
                ("skip", None),
                ("default", ""),
                ("no-overlay", "0"),
                ("frames-per-second-only", "1"),
                ("horizontal", "2"),
                ("extended", "3"),
                ("detailed", "4"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "preset=", ""),
            ),
        ),
        "full_overlay": (
            "Full Overlay",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "full"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "frames_per_second_only": (
            "Frames Per Second Only",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "fps_only"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "no_display": (
            "No Display",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "no_display"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "horizontal_layout": (
            "Horizontal Layout",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "horizontal"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "horizontal_stretch": (
            "Horizontal Stretch",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "horizontal_stretch"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "compact": (
            "Compact Overlay",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "hud_compact"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "no_margin": (
            "No Margin",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "hud_no_margin"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "position": (
            "Position",
            (
                ("skip", None),
                ("default", ""),
                ("top-left", "top-left"),
                ("top-right", "top-right"),
                ("top-center", "top-center"),
                ("middle-left", "middle-left"),
                ("middle-right", "middle-right"),
                ("bottom-left", "bottom-left"),
                ("bottom-right", "bottom-right"),
                ("bottom-center", "bottom-center"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "position=", ""),
            ),
        ),
        "width": (
            "Width",
            (
                ("skip", None),
                ("default", ""),
                ("200", "200"),
                ("250", "250"),
                ("300", "300"),
                ("350", "350"),
                ("400", "400"),
                ("450", "450"),
                ("500", "500"),
                ("600", "600"),
                ("700", "700"),
                ("800", "800"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "width=", ""),
            ),
        ),
        "height": (
            "Height",
            (
                ("skip", None),
                ("default", ""),
                ("100", "100"),
                ("150", "150"),
                ("200", "200"),
                ("250", "250"),
                ("300", "300"),
                ("400", "400"),
                ("500", "500"),
                ("600", "600"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "height=", ""),
            ),
        ),
        "offset_horizontal": (
            "Horizontal Offset",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("10", "10"),
                ("20", "20"),
                ("50", "50"),
                ("100", "100"),
                ("200", "200"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "offset_x=", ""),
            ),
        ),
        "offset_vertical": (
            "Vertical Offset",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("10", "10"),
                ("20", "20"),
                ("50", "50"),
                ("100", "100"),
                ("200", "200"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "offset_y=", ""),
            ),
        ),
        "table_columns": (
            "Table Columns",
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
                ("environment_variable", "MANGOHUD_CONFIG", ",", "table_columns=", ""),
            ),
        ),
        "cell_padding_vertical": (
            "Vertical Cell Padding",
            (
                ("skip", None),
                ("default", ""),
                ("-0.085", "-0.085"),
                ("-0.05", "-0.05"),
                ("0.0", "0.0"),
                ("0.05", "0.05"),
                ("0.1", "0.1"),
                ("0.15", "0.15"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "cellpadding_y=", ""),
            ),
        ),
        "round_corners": (
            "Round Corners",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("5", "5"),
                ("10", "10"),
                ("15", "15"),
                ("20", "20"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "round_corners=", ""),
            ),
        ),
        "frames_per_second_display": (
            "Frames Per Second Display",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "fps=", ""),
            ),
        ),
        "frames_per_second_sampling_period": (
            "Frames Per Second Sampling Period",
            (
                ("skip", None),
                ("default", ""),
                ("100", "100"),
                ("200", "200"),
                ("250", "250"),
                ("500", "500"),
                ("1000", "1000"),
                ("2000", "2000"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "fps_sampling_period=", ""),
            ),
        ),
        "frames_per_second_color_change": (
            "Frames Per Second Color Change",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "fps_color_change"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "frames_per_second_colors": (
            "Frames Per Second Colors",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "fps_color=", ""),
            ),
        ),
        "frames_per_second_color_breakpoints": (
            "Frames Per Second Color Breakpoints",
            (
                ("skip", None),
                ("default", ""),
                ("30,60", "30,60"),
                ("30,90", "30,90"),
                ("60,144", "60,144"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "fps_value=", ""),
            ),
        ),
        "frames_per_second_metrics": (
            "Frames Per Second Metrics",
            (
                ("skip", None),
                ("default", ""),
                ("avg", "avg"),
                ("avg,0.1", "avg,0.1"),
                ("avg,0.01,0.001", "avg,0.01,0.001"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "fps_metrics=", ""),
            ),
        ),
        "frames_per_second_text": (
            "Frames Per Second Text",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "fps_text=", ""),
            ),
        ),
        "show_frames_per_second_limit": (
            "Show Frames Per Second Limit",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "show_fps_limit"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "benchmark_percentiles": (
            "Benchmark Percentiles",
            (
                ("skip", None),
                ("default", ""),
                ("97,AVG,1,0.1", "97,AVG,1,0.1"),
                ("99,AVG,1,0.1", "99,AVG,1,0.1"),
                ("99.9,99,AVG,1,0.1", "99.9,99,AVG,1,0.1"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "benchmark_percentiles=", ""),
            ),
        ),
        "frame_count": (
            "Frame Count",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "frame_count"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "frametime": (
            "Frametime",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "frametime=", ""),
            ),
        ),
        "frame_timing": (
            "Frame Timing Graph",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "frame_timing=", ""),
            ),
        ),
        "frame_timing_detailed": (
            "Detailed Frame Timing",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "frame_timing_detailed"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "dynamic_frame_timing": (
            "Dynamic Frame Timing",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "dynamic_frame_timing"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "histogram": (
            "Histogram",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "histogram"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "cpu_statistics": (
            "CPU Statistics",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "cpu_stats=", ""),
            ),
        ),
        "cpu_temperature": (
            "CPU Temperature",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "cpu_temp"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "cpu_power": (
            "CPU Power",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "cpu_power"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "cpu_megahertz": (
            "CPU Megahertz",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "cpu_mhz"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "cpu_text": (
            "CPU Text Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "cpu_text=", ""),
            ),
        ),
        "cpu_load_color_change": (
            "CPU Load Color Change",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "cpu_load_change"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "cpu_load_thresholds": (
            "CPU Load Thresholds",
            (
                ("skip", None),
                ("default", ""),
                ("50,90", "50,90"),
                ("40,80", "40,80"),
                ("60,90", "60,90"),
                ("30,70", "30,70"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "cpu_load_value=", ""),
            ),
        ),
        "cpu_load_colors": (
            "CPU Load Colors",
            (
                ("skip", None),
                ("default", ""),
                ("0000FF,00FFFF,FF00FF", "0000FF,00FFFF,FF00FF"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "cpu_load_color=", ""),
            ),
        ),
        "cpu_efficiency": (
            "CPU Efficiency",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "cpu_efficiency"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "cpu_custom_temperature_sensor": (
            "CPU Custom Temperature Sensor",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "cpu_custom_temp_sensor=", ""),
            ),
        ),
        "core_load": (
            "Core Load",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "core_load"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "core_load_color_change": (
            "Core Load Color Change",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "core_load_change"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "core_load_bars": (
            "Core Load Bars",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "core_bars"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "core_type": (
            "Core Type",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "core_type"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_statistics": (
            "GPU Statistics",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "gpu_stats=", ""),
            ),
        ),
        "gpu_temperature": (
            "GPU Temperature",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_temp"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_junction_temperature": (
            "GPU Junction Temperature",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_junction_temp"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_memory_temperature": (
            "GPU Memory Temperature",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_mem_temp"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_power": (
            "GPU Power",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_power"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_core_clock": (
            "GPU Core Clock",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_core_clock"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_memory_clock": (
            "GPU Memory Clock",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_mem_clock"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_fan": (
            "GPU Fan",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_fan"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_voltage": (
            "GPU Voltage",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_voltage"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_name": (
            "GPU Name",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_name"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_text": (
            "GPU Text Override",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "gpu_text=", ""),
            ),
        ),
        "gpu_load_color_change": (
            "GPU Load Color Change",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_load_change"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_load_thresholds": (
            "GPU Load Thresholds",
            (
                ("skip", None),
                ("default", ""),
                ("50,90", "50,90"),
                ("40,80", "40,80"),
                ("60,90", "60,90"),
                ("30,70", "30,70"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "gpu_load_value=", ""),
            ),
        ),
        "gpu_load_colors": (
            "GPU Load Colors",
            (
                ("skip", None),
                ("default", ""),
                ("0000FF,00FFFF,FF00FF", "0000FF,00FFFF,FF00FF"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "gpu_load_color=", ""),
            ),
        ),
        "gpu_efficiency": (
            "GPU Efficiency",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_efficiency"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_power_limit": (
            "GPU Power Limit",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gpu_power_limit"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gpu_list": (
            "GPU List",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("1", "1"),
                ("0,1", "0,1"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "gpu_list=", ""),
            ),
        ),
        "pci_device": (
            "PCI Device",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "pci_dev=", ""),
            ),
        ),
        "throttling_status": (
            "Throttling Status",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "throttling_status"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "throttling_status_graph": (
            "Throttling Status Graph",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "throttling_status_graph"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "flip_efficiency": (
            "Flip Efficiency",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "flip_efficiency"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "ram_usage": (
            "RAM Usage",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "ram"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "vram_usage": (
            "VRAM Usage",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "vram"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "swap_usage": (
            "Swap Usage",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "swap"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "ram_temperature": (
            "RAM Temperature",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "ram_temp"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "process_memory_resident": (
            "Process Memory (Resident)",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "procmem"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "process_memory_shared": (
            "Process Memory (Shared)",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "procmem_shared"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "process_memory_virtual": (
            "Process Memory (Virtual)",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "procmem_virt"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "process_vram": (
            "Process VRAM",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "proc_vram"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "input_output_read": (
            "Input/Output Read",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "io_read"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "input_output_write": (
            "Input/Output Write",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "io_write"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "network": (
            "Network",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "network"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "battery": (
            "Battery",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "battery"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "battery_icon": (
            "Battery Icon",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "battery_icon"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "battery_wattage": (
            "Battery Wattage",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "battery_watt"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "battery_time_remaining": (
            "Battery Time Remaining",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "battery_time"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "device_battery": (
            "Device Battery",
            (
                ("skip", None),
                ("default", ""),
                ("gamepad", "gamepad"),
                ("mouse", "mouse"),
                ("gamepad,mouse", "gamepad,mouse"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "device_battery=", ""),
            ),
        ),
        "device_battery_icon": (
            "Device Battery Icon",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "device_battery_icon"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "engine_version": (
            "Engine Version",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "engine_version"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "engine_short_names": (
            "Engine Short Names",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "engine_short_names"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "wine_version": (
            "Wine/Proton Version",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "wine"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "wine_synchronization_method": (
            "Wine Synchronization Method",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "winesync"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "present_mode": (
            "Present Mode",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "present_mode"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "fsr_status": (
            "FSR Status",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "fsr"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "hide_fsr_sharpness": (
            "Hide FSR Sharpness",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "hide_fsr_sharpness"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "high_dynamic_range_status": (
            "High Dynamic Range Status",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "hdr"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "refresh_rate": (
            "Refresh Rate",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "refresh_rate"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "debug_graph": (
            "Debug Graph",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "debug"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "steam_deck_fan": (
            "Steam Deck Fan",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "fan"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "resolution": (
            "Resolution",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "resolution"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "display_server": (
            "Display Server",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "display_server"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "architecture": (
            "Architecture",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "arch"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "executable_name": (
            "Executable Name",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "exec_name"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "time": (
            "Time",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "time"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "time_format": (
            "Time Format",
            (
                ("skip", None),
                ("default", ""),
                ("%T", "%T"),
                ("%H:%M", "%H:%M"),
                ("%I:%M-%p", "%I:%M %p"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "time_format=", ""),
            ),
        ),
        "time_no_label": (
            "Time No Label",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "time_no_label"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "gamemode": (
            "GameMode",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "gamemode"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "vkbasalt": (
            "vkBasalt",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "vkbasalt"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "temperature_in_fahrenheit": (
            "Temperature in Fahrenheit",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "temp_fahrenheit"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "show_version": (
            "Show Version",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "version"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "custom_text": (
            "Custom Text",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "custom_text=", ""),
            ),
        ),
        "custom_text_center": (
            "Custom Text Center",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "custom_text_center=", ""),
            ),
        ),
        "execute": (
            "Execute Command",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "exec=", ""),
            ),
        ),
        "media_player": (
            "Media Player",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "media_player"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "media_player_name": (
            "Media Player Name",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "media_player_name=", ""),
            ),
        ),
        "media_player_format": (
            "Media Player Format",
            (
                ("skip", None),
                ("default", ""),
                ("{title};{artist};{album}", "{title};{artist};{album}"),
                ("{title};{artist}", "{title};{artist}"),
                ("{title}", "{title}"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "media_player_format=", ""),
            ),
        ),
        "font_size": (
            "Font Size",
            (
                ("skip", None),
                ("default", ""),
                ("12", "12"),
                ("14", "14"),
                ("16", "16"),
                ("18", "18"),
                ("20", "20"),
                ("22", "22"),
                ("24", "24"),
                ("26", "26"),
                ("28", "28"),
                ("30", "30"),
                ("32", "32"),
                ("36", "36"),
                ("40", "40"),
                ("48", "48"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "font_size=", ""),
            ),
        ),
        "font_size_secondary": (
            "Font Size Secondary",
            (
                ("skip", None),
                ("default", ""),
                ("10", "10"),
                ("11", "11"),
                ("12", "12"),
                ("13", "13"),
                ("14", "14"),
                ("16", "16"),
                ("18", "18"),
                ("20", "20"),
                ("22", "22"),
                ("24", "24"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "font_size_secondary=", ""),
            ),
        ),
        "font_size_text": (
            "Font Size Text",
            (
                ("skip", None),
                ("default", ""),
                ("12", "12"),
                ("14", "14"),
                ("16", "16"),
                ("18", "18"),
                ("20", "20"),
                ("22", "22"),
                ("24", "24"),
                ("26", "26"),
                ("28", "28"),
                ("32", "32"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "font_size_text=", ""),
            ),
        ),
        "font_scale": (
            "Font Scale",
            (
                ("skip", None),
                ("default", ""),
                ("0.5", "0.5"),
                ("0.75", "0.75"),
                ("1.0", "1.0"),
                ("1.25", "1.25"),
                ("1.5", "1.5"),
                ("2.0", "2.0"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "font_scale=", ""),
            ),
        ),
        "font_scale_media_player": (
            "Font Scale Media Player",
            (
                ("skip", None),
                ("default", ""),
                ("0.5", "0.5"),
                ("0.75", "0.75"),
                ("1.0", "1.0"),
                ("1.25", "1.25"),
                ("1.5", "1.5"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "font_scale_media_player=", ""),
            ),
        ),
        "font_file": (
            "Font File",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "font_file=", ""),
            ),
        ),
        "font_file_text": (
            "Font File (Text)",
            (
                ("skip", None),
                ("default", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "font_file_text=", ""),
            ),
        ),
        "font_glyph_ranges": (
            "Font Glyph Ranges",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("korean", "korean"),
                ("chinese", "chinese"),
                ("chinese-simplified", "chinese_simplified"),
                ("japanese", "japanese"),
                ("cyrillic", "cyrillic"),
                ("thai", "thai"),
                ("vietnamese", "vietnamese"),
                ("latin-extended-a", "latin_ext_a"),
                ("latin-extended-b", "latin_ext_b"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "font_glyph_ranges=", ""),
            ),
        ),
        "no_small_font": (
            "No Small Font",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "no_small_font"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "text_alpha": (
            "Text Alpha",
            (
                ("skip", None),
                ("default", ""),
                ("0.0", "0.0"),
                ("0.1", "0.1"),
                ("0.2", "0.2"),
                ("0.3", "0.3"),
                ("0.4", "0.4"),
                ("0.5", "0.5"),
                ("0.6", "0.6"),
                ("0.7", "0.7"),
                ("0.8", "0.8"),
                ("0.9", "0.9"),
                ("1.0", "1.0"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "alpha=", ""),
            ),
        ),
        "background_alpha": (
            "Background Alpha",
            (
                ("skip", None),
                ("default", ""),
                ("0.0", "0.0"),
                ("0.1", "0.1"),
                ("0.2", "0.2"),
                ("0.3", "0.3"),
                ("0.4", "0.4"),
                ("0.5", "0.5"),
                ("0.6", "0.6"),
                ("0.7", "0.7"),
                ("0.8", "0.8"),
                ("0.9", "0.9"),
                ("1.0", "1.0"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "background_alpha=", ""),
            ),
        ),
        "gpu_color": (
            "GPU Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "gpu_color=", ""),),
        ),
        "cpu_color": (
            "CPU Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "cpu_color=", ""),),
        ),
        "vram_color": (
            "VRAM Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "vram_color=", ""),),
        ),
        "ram_color": (
            "RAM Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "ram_color=", ""),),
        ),
        "input_output_color": (
            "Input/Output Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "io_color=", ""),),
        ),
        "engine_color": (
            "Engine Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "engine_color=", ""),),
        ),
        "frametime_color": (
            "Frametime Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "frametime_color=", ""),),
        ),
        "background_color": (
            "Background Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "background_color=", ""),),
        ),
        "text_color": (
            "Text Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "text_color=", ""),),
        ),
        "media_player_color": (
            "Media Player Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "media_player_color=", ""),),
        ),
        "network_color": (
            "Network Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "network_color=", ""),),
        ),
        "wine_color": (
            "Wine Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "wine_color=", ""),),
        ),
        "battery_color": (
            "Battery Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "battery_color=", ""),),
        ),
        "horizontal_separator_color": (
            "Horizontal Separator Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "horizontal_separator_color=", ""),),
        ),
        "text_outline": (
            "Text Outline",
            (
                ("skip", None),
                ("default", ""),
                ("off", "0"),
                ("on", ""),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "text_outline=", ""),
            ),
        ),
        "text_outline_color": (
            "Text Outline Color",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "text_outline_color=", ""),),
        ),
        "text_outline_thickness": (
            "Text Outline Thickness",
            (
                ("skip", None),
                ("default", ""),
                ("0.5", "0.5"),
                ("1.0", "1.0"),
                ("1.5", "1.5"),
                ("2.0", "2.0"),
                ("2.5", "2.5"),
                ("3.0", "3.0"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "text_outline_thickness=", ""),
            ),
        ),
        "autostart_log": (
            "Autostart Log",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("5", "5"),
                ("10", "10"),
                ("30", "30"),
                ("60", "60"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "autostart_log=", ""),
            ),
        ),
        "log_duration": (
            "Log Duration",
            (
                ("skip", None),
                ("default", ""),
                ("10", "10"),
                ("30", "30"),
                ("60", "60"),
                ("120", "120"),
                ("300", "300"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "log_duration=", ""),
            ),
        ),
        "log_interval": (
            "Log Interval",
            (
                ("skip", None),
                ("default", ""),
                ("0", "0"),
                ("100", "100"),
                ("250", "250"),
                ("500", "500"),
                ("1000", "1000"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "log_interval=", ""),
            ),
        ),
        "log_versioning": (
            "Log Versioning",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "log_versioning"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "output_folder": (
            "Output Folder",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "output_folder=", ""),),
        ),
        "output_file": (
            "Output File",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "output_file=", ""),),
        ),
        "permit_upload": (
            "Permit Upload",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "permit_upload"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "upload_logs": (
            "Auto Upload Logs",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "upload_logs"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "fcat": (
            "FCAT",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "fcat"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "fcat_overlay_width": (
            "FCAT Overlay Width",
            (
                ("skip", None),
                ("default", ""),
                ("12", "12"),
                ("24", "24"),
                ("48", "48"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "fcat_overlay_width=", ""),
            ),
        ),
        "fcat_screen_edge": (
            "FCAT Screen Edge",
            (
                ("skip", None),
                ("default", ""),
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
                ("4", "4"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "fcat_screen_edge=", ""),
            ),
        ),
        "toggle_overlay": (
            "Toggle Overlay Keybind",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "toggle_hud=", ""),),
        ),
        "toggle_logging": (
            "Toggle Logging Keybind",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "toggle_logging=", ""),),
        ),
        "toggle_frames_per_second_limit": (
            "Toggle Frames Per Second Limit Keybind",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "toggle_fps_limit=", ""),),
        ),
        "toggle_preset": (
            "Toggle Preset Keybind",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "toggle_preset=", ""),),
        ),
        "toggle_overlay_position": (
            "Toggle Overlay Position Keybind",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "toggle_hud_position=", ""),),
        ),
        "reload_configuration": (
            "Reload Configuration Keybind",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "reload_cfg=", ""),),
        ),
        "reset_frames_per_second_metrics": (
            "Reset Frames Per Second Metrics Keybind",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "reset_fps_metrics=", ""),),
        ),
        "upload_log": (
            "Upload Log Keybind",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "upload_log=", ""),),
        ),
        "control_socket": (
            "Control Socket",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "control=", ""),),
        ),
        "blacklist": (
            "Blacklist",
            (("skip", None), ("default", "")),
            (("environment_variable", "MANGOHUD_CONFIG", ",", "blacklist=", ""),),
        ),
        "fex_statistics": (
            "FEX Statistics",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "fex_stats"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
        "ftrace": (
            "ftrace",
            (
                ("skip", None),
                ("default", ""),
                ("off", ""),
                ("on", "ftrace"),
            ),
            (
                ("environment_variable", "MANGOHUD_CONFIG", ",", "", ""),
            ),
        ),
    }
