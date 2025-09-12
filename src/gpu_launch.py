import os, glob, tempfile
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTabWidget, QScrollArea, QSizePolicy, QLineEdit
from PySide6.QtCore import Qt, QProcess
from workarounds import WorkaroundManager

class GPULaunchManager:

    SEARCH_PATHS = ["/usr/bin/", "/usr/local/bin/"]

    GPU_SETTINGS_CATEGORIES = {
        "Mesa": {
            'mesa_vsync_vk': {
                'label': "Vulkan Vsync:",
                'items': ["unset", "mailbox", "adaptive vsync", "on", "off"],
                'env_mapping': {
                    'var_names': ['MESA_VK_WSI_PRESENT_MODE'],
                    'values': {'mailbox': 'mailbox', 'adaptive vsync': 'relaxed', 'on': 'fifo', 'off': 'immediate'}
                }
            },
            'mesa_vsync_gl': {
                'label': "OpenGL Vsync:",
                'items': ["unset", "default interval 0", "default interval 1", "on", "off"],
                'env_mapping': {
                    'var_names': ['vblank_mode'],
                    'values': {'default interval 0': '1', 'default interval 1': '2', 'on': '3', 'off': '0'}
                }
            },
            'mesa_thread_opt': {
                'label': "OpenGL Thread Optimizations:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['mesa_glthread'],
                    'values': {'on': 'true', 'off': 'false'}
                }
            },
            'mesa_msaa': {
                'label': "OpenGL MSAA:",
                'items': ["unset", "on", 'off'],
                'env_mapping': {
                    'var_names': ['DRI_NO_MSAA'],
                    'values': {'on': '0', 'off': '1'}
                }
            },
            'mesa_dither': {
                'label': "Texture Dithering:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['MESA_NO_DITHER'],
                    'values': {'on': '0', 'off': '1'}
                }
            },
            'mesa_shader_cache': {
                'label': "Shader Cache:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['MESA_SHADER_CACHE_DISABLE', 'MESA_GLSL_CACHE_DISABLE'],
                    'values': {'on': 'false', 'off': 'true'}
                }
            },
            'mesa_cache_size': {
                'label': "Shader Cache Size (GB):",
                'items': ["unset"] + [str(i) for i in range(1, 11)],
                'env_mapping': {
                    'var_names': ['MESA_SHADER_CACHE_MAX_SIZE', 'MESA_GLSL_CACHE_MAX_SIZE'],
                    'direct_value': True
                }
            },
            'mesa_error_check': {
                'label': "Error Checking:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['MESA_NO_ERROR'],
                    'values': {'on': '0', 'off': '1'}
                }
            },
            'mesa_fake_vk': {
                'label': "Vulkan Version Spoofing:",
                'items': ["unset", "1.1", "1.2", "1.3", "1.4"],
                'env_mapping': {
                    'var_names': ['MESA_VK_VERSION_OVERRIDE'],
                    'direct_value': True
                }
            },
            'mesa_fake_gl': {
                'label': "OpenGL Version Spoofing:",
                'items': ["unset", "3.3", "3.3compat", "4.6", "4.6compat"],
                'env_mapping': {
                    'var_names': ['MESA_GL_VERSION_OVERRIDE'],
                    'direct_value': True
                }
            },
            'mesa_fake_glsl': {
                'label': "GLSL Version Spoofing:",
                'items': ["unset", "330", "460"],
                'env_mapping': {
                    'var_names': ['MESA_GLSL_VERSION_OVERRIDE'],
                    'direct_value': True
                }
            },
            'intel_precise_trig': {
            'label': "Intel Driver Preference on Trigonometric Functions:",
            'items': ["unset", "accuracy", "performance"],
            'env_mapping': {
                'var_names': ['INTEL_PRECISE_TRIG'],
                'values': {'accuracy': 'true', 'performance': 'false'}
                }
            },
            'radv_profile_pstate': {
            'label': "RADV Profile Pstate:",
            'items': [
                "unset",
                "gpu clocks on arbitrary level",
                "minimum shader clock",
                "minimum memory clock",
                "maximum gpu clocks"
            ],
            'env_mapping': {
                'var_names': ['RADV_PROFILE_PSTATE'],
                'values': {
                    'gpu clocks on arbitrary level': 'standard',
                    'minimum shader clock': 'min_sclk',
                    'minimum memory clock': 'min_mclk',
                    'maximum gpu clocks': 'peak'
                    }
                }
            },
            'nvk_broken_driver': {
            'label': "Enable NVK for Experimental/Untested GPUs:",
            'items': ["unset", "on", "off"],
            'env_mapping': {
                'var_names': ['NVK_I_WANT_A_BROKEN_VULKAN_DRIVER'],
                'values': {'on': 'true', 'off': 'false'}
                }
            }
        },
        "NVIDIA": {
            'nvidia_vsync_gl': {
                'label': "OpenGL Vsync:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['__GL_SYNC_TO_VBLANK'],
                    'values': {'on': '1', 'off': '0'}
                }
            },
            'nvidia_gsync': {
                'label': "OpenGL G-SYNC:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['__GL_VRR_ALLOWED'],
                    'values': {'on': '1', 'off': '0'}
                }
            },
            'nvidia_thread_opt': {
                'label': "OpenGL Thread Optimizations:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['__GL_THREADED_OPTIMIZATIONS'],
                    'values': {'on': '1', 'off': '0'}
                }
            },
            'nvidia_yield': {
                'label': "OpenGL Yield Behavior:",
                'items': ["unset", "call sched_yield() to yield", "never yield", "call usleep(0) to yield"],
                'env_mapping': {
                    'var_names': ['__GL_YIELD'],
                    'values': {'call sched_yield() to yield': '0', 'never yield': 'NOTHING', 'call usleep(0) to yield': 'USLEEP'}
                }
            },
            'nvidia_tex_quality': {
                'label': "OpenGL Texture Quality:",
                'items': ["unset", "quality", "mixed", "performance"],
                'env_mapping': {
                    'var_names': ['__GL_OpenGLImageSettings'],
                    'values': {'quality': '1', 'mixed': '2', 'performance': '3'}
                }
            },
            'nvidia_fsaa': {
                'label': "OpenGL Full Scene Antialiasing:",
                'items': [
                    "unset", "0 - off", "1 - 2x (2xms)", "5 - 4x (4xms)",
                    "7 - 8x (4xms, 4xcs)", "8 - 16x (4xms, 12xcs)",
                    "9 - 8x (4xss, 2xms)", "10 - 8x (8xms)",
                    "11 - 16x (4xss, 4xms)", "12 - 16x (8xms, 8xcs)",
                    "14 - 32x (8xms, 24xcs)"
                ],
                'env_mapping': {
                    'var_names': ['__GL_FSAA_MODE'],
                    'extract_prefix': True
                }
            },
            'nvidia_fxaa': {
                'label': "OpenGL FXAA:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['__GL_ALLOW_FXAA_USAGE'],
                    'values': {'on': '1', 'off': '0'}
                }
            },
            'nvidia_aniso': {
                'label': "OpenGL Anisotropic Filtering:",
                'items': [
                    "unset", "0 - no anisotropic filtering",
                    "1 - 2x anisotropic filtering", "2 - 4x anisotropic filtering",
                    "3 - 8x anisotropic filtering", "4 - 16x anisotropic filtering"
                ],
                'env_mapping': {
                    'var_names': ['__GL_LOG_MAX_ANISO'],
                    'extract_prefix': True
                }
            },
            'nvidia_shader_cache': {
                'label': "Shader Cache:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['__GL_SHADER_DISK_CACHE'],
                    'values': {'on': '1', 'off': '0'}
                }
            },
            'nvidia_cache_size': {
                'label': "Shader Cache Size (GB):",
                'items': ["unset"] + [str(i) for i in range(1, 11)],
                'env_mapping': {
                    'var_names': ['__GL_SHADER_DISK_CACHE_SIZE'],
                    'convert_to_bytes': True
                }
            },
            'nvidia_max_frames': {
                'label': "Maximum Pre-rendered Frames:",
                'items': ["unset"] + [str(i) for i in range(1, 5)],
                'env_mapping': {
                    'var_names': ['__GL_MaxFramesAllowed'],
                    'direct_value': True
                }
            },
            'nvidia_sharpen': {
                'label': "Image Sharpening:",
                'items': ["unset"] + [str(i) for i in range(0, 101)],
                'env_mapping': {
                    'var_names': ['__GL_SHARPEN_VALUE'],
                    'direct_value': True
                }
            },
            'nvidia_denoising': {
                'label': "Image Denoising",
                'items': ["unset"] + [str(i) for i in range(0, 101)],
                'env_mapping': {
                    'var_names': ['__GL_SHARPEN_IGNORE_FILM_GRAIN'],
                    'direct_value': True
                }
            },
            'nvidia_smooth_motion': {
                'label': "Smooth Motion (RTX 40 Series+):",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['NVPRESENT_ENABLE_SMOOTH_MOTION'],
                    'values': {'on': '1', 'off': '0'}
                }
            },
            'nvidia_glsl_ext': {
                'label': "Ignore GLSL Extensions Requirements:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['__GL_IGNORE_GLSL_EXT_REQ'],
                    'values': {'on': '1', 'off': '0'}
                }
            },
            'nvidia_perf_exp': {
                'label': "Experimental Performance Strategy:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['__GL_ExperimentalPerfStrategy'],
                    'values': {'on': '1', 'off': '0'}
                }
            },
            'nvidia_glx_unofficial': {
                'label': "Unofficial GLX Protocol:",
                'items': ["unset", "on", "off"],
                'env_mapping': {
                    'var_names': ['__GL_ALLOW_UNOFFICIAL_PROTOCOL'],
                    'values': {'on': '1', 'off': '0'}
                }
            }
        },
        "RenderSelector": {
            'ogl_renderer': {
                'label': "OpenGL Renderer:",
                'items': ["unset", "llvmpipe (software rendering)", "zink"]
            },
            'vulkan_device': {
                'label': "Select Vulkan Renderer:",
                'items': ["unset"]
            }
        },
        "RenderPipeline": {
            'display': {
                'label': "Display Elements:",
                'items': ["unset", "no hud", "fps only", "horizontal", "extended", "detailed"],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'values': {'no hud': 'preset=0', 'fps only': 'preset=1', 'horizontal': 'preset=2', 'extended': 'preset=3', 'detailed': 'preset=4'}
                }
            },
            'fps_limit': {
                'label': "Fps Limit:",
                'items': ["unset", "unlimited", "10", "15", "20", "24", "25", "30", "35", "40", "45", "48", "50", "55", "60", "70", "72", "75", "85", "90", "100", "110", "120", "144", "165", "180", "200", "240", "280", "300", "360", "480"],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'values': {'unlimited': '0'},
                    'direct_value': True,
                    'prefix': 'fps_limit='
                }
            },
            'fps_method': {
                'label': "Fps Limit Method:",
                'items': ["unset", "early - smoothest frametimes", "late - lowest latency"],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'values': {'early - smoothest frametimes': 'early', 'late - lowest latency': 'late'},
                    'prefix': 'fps_limit_method='
                }
            },
            'texture_filter': {
                'label': "Texture Filtering:",
                'items': ["unset", "bicubic", "retro", "trilinear"],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'values': {'bicubic': 'bicubic', 'retro': 'retro', 'trilinear': 'trilinear'}
                }
            },
            'mipmap_lod_bias': {
                'label': "Mipmap LOD Bias:",
                'items': ["unset"] + [str(i) for i in range(-16, 17)],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'direct_value': True,
                    'prefix': 'picmip='
                }
            },
            'anisotropic_filter': {
                'label': "Anisotropic Filtering:",
                'items': ["unset"] + [str(i) for i in range(0, 17)],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'direct_value': True,
                    'prefix': 'af='
                }
            }
        }
    }

    GPU_SETTINGS = {}
    for category in GPU_SETTINGS_CATEGORIES.values():
        GPU_SETTINGS.update(category)

    @staticmethod
    def truncate_name(name):
        """
        Truncate device name at slash or parenthesis.
        """
        if '/' in name:
            return name.split('/')[0].strip()
        if '(' in name:
            return name.split('(')[0].strip()
        return name

    @staticmethod
    def get_available(program_name, search_flatpak=True):
        """
        Check if a program is available in system paths or flatpak.
        """
        for search_path in GPULaunchManager.SEARCH_PATHS:
            try:
                program_files = glob.glob(os.path.join(search_path, f"{program_name}*"))
                for file_path in program_files:
                    if os.access(file_path, os.X_OK):
                        return True
            except Exception:
                continue

        if search_flatpak:
            try:
                process = QProcess()
                WorkaroundManager.setup_clean_process(process)
                process.start("flatpak", ["list"])

                if process.waitForFinished(10000):
                    output = process.readAllStandardOutput().data().decode()
                    if program_name.lower() in output.lower():
                        return True
            except Exception:
                pass

        return False

    @staticmethod
    def get_available_vulkaninfo():
        """
        Check if vulkaninfo is available.
        """
        return GPULaunchManager.get_available("vulkaninfo", search_flatpak=False)

    @staticmethod
    def get_available_glxinfo():
        """
        Check if glxinfo is available.
        """
        return GPULaunchManager.get_available("glxinfo", search_flatpak=False)

    @staticmethod
    def get_available_mangohud():
        """
        Check if MangoHUD is available.
        """
        return GPULaunchManager.get_available("mangohud", search_flatpak=True)

    @staticmethod
    def get_vulkan_device_options():
        """
        Get available Vulkan device options from vulkaninfo.
        """
        devices = []
        device_map = {}

        if not GPULaunchManager.get_available_vulkaninfo():
            return devices, device_map

        try:
            process = QProcess()
            WorkaroundManager.setup_clean_process(process)
            process.start("vulkaninfo")

            if process.waitForFinished(10000):
                output = process.readAllStandardOutput().data().decode()
                lines = output.split('\n')

                current_device = {}
                for line in lines:
                    line = line.strip()
                    if 'vendorID' in line and '=' in line:
                        vendor_id = line.split('=')[1].strip()
                        current_device['vendorID'] = vendor_id
                    elif 'deviceID' in line and '=' in line:
                        device_id = line.split('=')[1].strip()
                        current_device['deviceID'] = device_id
                    elif 'deviceName' in line and '=' in line:
                        device_name = line.split('=')[1].strip()
                        current_device['deviceName'] = device_name

                        if all(key in current_device for key in ['vendorID', 'deviceID', 'deviceName']):
                            truncated_name = GPULaunchManager.truncate_name(current_device['deviceName'])
                            display_name = truncated_name.lower()

                            if 'llvmpipe' in display_name:
                                display_name = 'llvmpipe (software rendering)'
                            else:
                                display_name = truncated_name.lower()

                            device_key = f"{current_device['vendorID']}:{current_device['deviceID']}"
                            devices.append(display_name)
                            device_map[display_name] = device_key

                            current_device = {}

        except Exception:
            pass

        return devices, device_map

    @staticmethod
    def get_opengl_gpu_options():
        """
        Get available OpenGL GPU options from glxinfo.
        """
        gpu_list = []
        gpu_env_map = {}

        if not GPULaunchManager.get_available_glxinfo():
            fixed_options = {
                "llvmpipe (software rendering)": {
                    "__GLX_VENDOR_LIBRARY_NAME": "mesa",
                    "LIBGL_ALWAYS_SOFTWARE": "1"
                },
                "zink": {
                    "__GLX_VENDOR_LIBRARY_NAME": "mesa",
                    "MESA_LOADER_DRIVER_OVERRIDE": "zink",
                    "LIBGL_KOPPER_DRI2": "1"
                }
            }

            for name, env_vars in fixed_options.items():
                gpu_env_map[name] = env_vars

            options = ["unset"] + list(fixed_options.keys())
            return options, gpu_env_map

        try:
            process = QProcess()
            clean_env = WorkaroundManager.get_clean_env()
            clean_env.append("__GLX_VENDOR_LIBRARY_NAME=nvidia")
            process.setEnvironment(clean_env)
            process.start("glxinfo")

            if process.waitForFinished(10000):
                output = process.readAllStandardOutput().data().decode()
                for line in output.split('\n'):
                    if "OpenGL renderer string:" in line:
                        gpu_name = line.split(':', 1)[1].strip()
                        gpu_name = GPULaunchManager.truncate_name(gpu_name)
                        gpu_name = gpu_name.lower()

                        if gpu_name not in gpu_env_map:
                            gpu_list.append(gpu_name)
                            gpu_env_map[gpu_name] = {"__GLX_VENDOR_LIBRARY_NAME": "nvidia"}
                        break
        except Exception:
            pass

        index = 0
        while index < 5:
            try:
                process = QProcess()
                clean_env = WorkaroundManager.get_clean_env()
                clean_env.append("__GLX_VENDOR_LIBRARY_NAME=mesa")
                clean_env.append(f"DRI_PRIME={index}")
                process.setEnvironment(clean_env)
                process.start("glxinfo")

                if process.waitForFinished(10000):
                    output = process.readAllStandardOutput().data().decode()

                    renderer_found = False
                    for line in output.split('\n'):
                        if "OpenGL renderer string:" in line:
                            gpu_name = line.split(':', 1)[1].strip()
                            gpu_name = GPULaunchManager.truncate_name(gpu_name)
                            gpu_name = gpu_name.lower()

                            if "llvmpipe" in gpu_name or gpu_name in gpu_env_map:
                                break

                            gpu_list.append(gpu_name)
                            gpu_env_map[gpu_name] = {
                                "__GLX_VENDOR_LIBRARY_NAME": "mesa",
                                "DRI_PRIME": str(index)
                            }
                            renderer_found = True
                            break

                    if not renderer_found:
                        break

                index += 1
            except Exception:
                break

        fixed_options = {
            "llvmpipe (software rendering)": {
                "__GLX_VENDOR_LIBRARY_NAME": "mesa",
                "LIBGL_ALWAYS_SOFTWARE": "1"
            },
            "zink": {
                "__GLX_VENDOR_LIBRARY_NAME": "mesa",
                "MESA_LOADER_DRIVER_OVERRIDE": "zink",
                "LIBGL_KOPPER_DRI2": "1"
            }
        }

        for name, env_vars in fixed_options.items():
            gpu_env_map[name] = env_vars

        options = ["unset"] + gpu_list + list(fixed_options.keys())

        return options, gpu_env_map

    @staticmethod
    def create_gpu_settings_tab():
        """
        Create the main GPU settings tab with subtabs.
        """
        gpu_tab = QWidget()
        gpu_layout = QVBoxLayout(gpu_tab)
        gpu_layout.setSpacing(10)

        gpu_subtabs = QTabWidget()
        mesa_tab, mesa_widgets = GPULaunchManager.create_category_tab("Mesa")
        nvidia_tab, nvidia_widgets = GPULaunchManager.create_category_tab("NVIDIA")
        render_selector_tab, render_selector_widgets = GPULaunchManager.create_category_tab("RenderSelector")
        render_pipeline_tab, render_pipeline_widgets = GPULaunchManager.create_category_tab("RenderPipeline")

        gpu_subtabs.addTab(mesa_tab, "Mesa")
        gpu_subtabs.addTab(nvidia_tab, "NVIDIA (Proprietary)")
        gpu_subtabs.addTab(render_selector_tab, "Render Selector")
        gpu_subtabs.addTab(render_pipeline_tab, "Render Pipeline")
        gpu_layout.addWidget(gpu_subtabs)

        widgets = {
            'Mesa': mesa_widgets,
            'NVIDIA': nvidia_widgets,
            'RenderSelector': render_selector_widgets,
            'RenderPipeline': render_pipeline_widgets
        }

        return gpu_tab, widgets

    @staticmethod
    def create_category_tab(category_name):
        """
        Create a settings tab for a specific category.
        """
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 0)

        widgets = {}

        for setting_key, setting_info in GPULaunchManager.GPU_SETTINGS_CATEGORIES[category_name].items():
            layout = QHBoxLayout()
            label = QLabel(setting_info['label'])
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            widgets[setting_key] = QComboBox()
            widgets[setting_key].addItems(setting_info['items'])
            widgets[setting_key].setCurrentText("unset")
            widgets[setting_key].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            layout.addWidget(label)
            layout.addWidget(widgets[setting_key])
            scroll_layout.addLayout(layout)

        if category_name == "RenderSelector":
            if GPULaunchManager.get_available_glxinfo():
                opengl_options, gpu_env_map = GPULaunchManager.get_opengl_gpu_options()
                widgets['ogl_renderer'].clear()
                widgets['ogl_renderer'].addItems(opengl_options)
                widgets['ogl_renderer'].env_map = gpu_env_map
            else:
                widgets['ogl_renderer'].setEnabled(False)
                widgets['ogl_renderer'].setToolTip("glxinfo not found - OpenGL renderer selection disabled")

            if GPULaunchManager.get_available_vulkaninfo():
                vulkan_devices, device_map = GPULaunchManager.get_vulkan_device_options()
                vulkan_options = ["unset"] + vulkan_devices
                widgets['vulkan_device'].clear()
                widgets['vulkan_device'].addItems(vulkan_options)
                widgets['vulkan_device'].device_map = device_map
            else:
                widgets['vulkan_device'].setEnabled(False)
                widgets['vulkan_device'].setToolTip("vulkaninfo not found - Vulkan device selection disabled")

        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        GPULaunchManager.create_gpu_apply_button(main_layout, widgets, f"{category_name.lower()}_apply_button")

        return tab, widgets

    @staticmethod
    def create_render_selector_tab():
        """
        Create the render selector tab with OpenGL and Vulkan options.
        """
        render_tab, widgets = GPULaunchManager.create_category_tab("RenderSelector")

        if GPULaunchManager.get_available_glxinfo():
            opengl_options, gpu_env_map = GPULaunchManager.get_opengl_gpu_options()
            widgets['ogl_renderer'].clear()
            widgets['ogl_renderer'].addItems(opengl_options)
            widgets['ogl_renderer'].env_map = gpu_env_map
        else:
            widgets['ogl_renderer'].setEnabled(False)
            widgets['ogl_renderer'].setToolTip("glxinfo not found - OpenGL renderer selection disabled")

        if GPULaunchManager.get_available_vulkaninfo():
            vulkan_devices, device_map = GPULaunchManager.get_vulkan_device_options()
            vulkan_options = ["unset"] + vulkan_devices
            widgets['vulkan_device'].clear()
            widgets['vulkan_device'].addItems(vulkan_options)
            widgets['vulkan_device'].device_map = device_map
        else:
            widgets['vulkan_device'].setEnabled(False)
            widgets['vulkan_device'].setToolTip("vulkaninfo not found - Vulkan device selection disabled")

        return render_tab, widgets

    @staticmethod
    def create_render_pipeline_tab():
        """
        Create the render pipeline tab with MangoHUD options.
        """
        mangohud_available = GPULaunchManager.get_available_mangohud()

        render_pipeline_tab, widgets = GPULaunchManager.create_category_tab("RenderPipeline")

        if not mangohud_available:
            for widget in widgets.values():
                if hasattr(widget, 'setEnabled'):
                    widget.setEnabled(False)
                    widget.setToolTip("MangoHUD not found - Render pipeline options disabled")

        return render_pipeline_tab, widgets

    @staticmethod
    def create_launch_options_tab():
        """
        Create the launch options tab with additional launch parameters.
        """
        launch_tab = QWidget()
        main_layout = QVBoxLayout(launch_tab)
        main_layout.setContentsMargins(9, 9, 9, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 0)

        setting_container = QWidget()
        setting_container.setProperty("settingContainer", True)
        setting_layout = QVBoxLayout(setting_container)
        setting_layout.setContentsMargins(0, 0, 0, 0)

        path_label = QLabel("Launch Options:")
        path_label.setWordWrap(True)
        setting_layout.addWidget(path_label)

        example_text = "Additional programs and environment variables to launch with the game, arguments are not supported.\nExample: gamemoderun PROTON_USE_WINED3D=1"

        text_label = QLabel(example_text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 5px;")
        setting_layout.addWidget(text_label)

        launch_options_input = QLineEdit()
        launch_options_input.setPlaceholderText("enter launch options")
        setting_layout.addWidget(launch_options_input)

        scroll_layout.addWidget(setting_container)
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        widgets = {'launch_options_input': launch_options_input}

        GPULaunchManager.create_launch_apply_button(main_layout, widgets)

        return launch_tab, widgets

    @staticmethod
    def create_gpu_apply_button(layout, widgets, button_name):
        """
        Create an apply button for GPU settings.
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 0)

        widgets[button_name] = QPushButton("Apply")
        widgets[button_name].setMinimumSize(100, 30)
        widgets[button_name].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets[button_name])
        button_layout.addStretch(1)

        layout.addWidget(button_container)

    @staticmethod
    def create_launch_apply_button(layout, widgets):
        """
        Create an apply button for launch options.
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(11, 10, 11, 0)

        widgets['launch_apply_button'] = QPushButton("Apply")
        widgets['launch_apply_button'].setMinimumSize(100, 30)
        widgets['launch_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets['launch_apply_button'])
        button_layout.addStretch(1)
        layout.addWidget(button_container)
        layout.addSpacing(9)

    @staticmethod
    def generate_env_vars(widgets, category_name):
        """
        Generate environment variables for a settings category.
        """
        env_vars = []

        if category_name == "RenderPipeline":
            mangohud_parts = []

            for setting_key, widget in widgets.items():
                if setting_key.endswith('_apply_button'):
                    continue

                value = widget.currentText()
                if value == "unset":
                    continue

                setting_info = GPULaunchManager.GPU_SETTINGS_CATEGORIES[category_name][setting_key]

                if 'env_mapping' not in setting_info:
                    continue

                mapping = setting_info['env_mapping']

                if mapping.get('direct_value', False):
                    prefix = mapping.get('prefix', '')
                    if value == 'unlimited':
                        mapped_value = mapping['values'].get(value, '0')
                        mangohud_parts.append(f'{prefix}{mapped_value}')
                    else:
                        mangohud_parts.append(f'{prefix}{value}')
                elif 'values' in mapping:
                    mapped_value = mapping['values'].get(value)
                    if mapped_value:
                        prefix = mapping.get('prefix', '')
                        mangohud_parts.append(f'{prefix}{mapped_value}')

            if mangohud_parts:
                config_value = ','.join(mangohud_parts)
                env_vars.append(f'MANGOHUD_CONFIG={config_value}')
        else:
            sharpen_enabled = False

            for setting_key, widget in widgets.items():
                if setting_key.endswith('_apply_button'):
                    continue

                value = widget.currentText()
                if value == "unset":
                    continue

                setting_info = GPULaunchManager.GPU_SETTINGS_CATEGORIES[category_name][setting_key]

                if 'env_mapping' not in setting_info:
                    continue

                mapping = setting_info['env_mapping']
                var_names = mapping['var_names']

                if mapping.get('direct_value', False):
                    final_value = value
                elif mapping.get('extract_prefix', False):
                    final_value = value.split(' - ')[0]
                elif mapping.get('convert_to_bytes', False):
                    final_value = str(int(value) * 1073741824)
                elif 'values' in mapping:
                    mapped_value = mapping['values'].get(value)
                    prefix = mapping.get('prefix', '')
                    final_value = f"{prefix}{mapped_value}" if mapped_value else None
                else:
                    final_value = None

                if final_value is not None:
                    for var_name in var_names:
                        env_vars.append(f'{var_name}={final_value}')

                if category_name == "NVIDIA" and setting_key in ['nvidia_sharpen', 'nvidia_denoising']:
                    sharpen_enabled = True

            if category_name == "NVIDIA" and sharpen_enabled:
                env_vars.append('__GL_SHARPEN_ENABLE=1')

        return env_vars

    @staticmethod
    def generate_render_selector_env_vars(render_widgets):
        """
        Generate environment variables for render selector settings.
        """
        env_vars = []

        if 'ogl_renderer' in render_widgets:
            selected = render_widgets['ogl_renderer'].currentText()
            if selected != "unset":
                env_map = getattr(render_widgets['ogl_renderer'], 'env_map', {})
                env_dict = env_map.get(selected, {})
                for var, value in env_dict.items():
                    env_vars.append(f"{var}={value}")

        if 'vulkan_device' in render_widgets:
            vulkan_selection = render_widgets['vulkan_device'].currentText()
            if vulkan_selection != "unset":
                device_map = getattr(render_widgets['vulkan_device'], 'device_map', {})
                device_key = device_map.get(vulkan_selection)
                if device_key:
                    env_vars.append(f"MESA_VK_DEVICE_SELECT={device_key}!")

        return env_vars

    @staticmethod
    def write_settings_file(mesa_widgets, nvidia_widgets, render_selector_widgets, render_pipeline_widgets, launch_options_widgets):
        """
        Write all settings to a temporary configuration file.
        """
        mesa_env_vars = GPULaunchManager.generate_env_vars(mesa_widgets, "Mesa")
        nvidia_env_vars = GPULaunchManager.generate_env_vars(nvidia_widgets, "NVIDIA")
        render_env_vars = GPULaunchManager.generate_render_selector_env_vars(render_selector_widgets)
        render_pipeline_env_vars = GPULaunchManager.generate_env_vars(render_pipeline_widgets, "RenderPipeline")

        launch_options = ""
        if 'launch_options_input' in launch_options_widgets:
            launch_options = launch_options_widgets['launch_options_input'].text().strip()

        use_mangohud = any(widget.currentText() != "unset" for widget in render_pipeline_widgets.values()
                          if not isinstance(widget, QPushButton))

        if use_mangohud and launch_options:
            launch_options = f"mangohud {launch_options}"
        elif use_mangohud and not launch_options:
            launch_options = "mangohud"

        all_env_vars = mesa_env_vars + nvidia_env_vars + render_env_vars + render_pipeline_env_vars

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as temp_file:
            for env_var in all_env_vars:
                temp_file.write(f"{env_var}\n")

            if launch_options:
                temp_file.write(f"launch_options={launch_options}\n")

            return temp_file.name
