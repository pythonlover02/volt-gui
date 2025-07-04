import os
import re
import glob
import tempfile
import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTabWidget, QScrollArea, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt


class GPULaunchManager:
    """
    Main class for managing GPU launch settings and configurations.
    """
    
    VOLT_SCRIPT_PATH = "/usr/local/bin/volt"
    VOLT_HELPER_PATH = "/usr/local/bin/volt-helper"
    ICD_DIR = "/usr/share/vulkan/icd.d/"
    MANGOHUD_SEARCH_PATHS = ["/usr/bin/", "/usr/local/bin/"]
    
    MESA_SETTINGS = [
        ("Vulkan Vsync:", 'mesa_vsync_vk_combo', ["unset", "mailbox", "adaptive vsync", "on", "off"]),
        ("OpenGL Vsync:", 'mesa_vsync_gl_combo', ["unset", "default interval 0", "default interval 1", "on", "off"]),
        ("OpenGL Thread Optimizations:", 'mesa_thread_opt_combo', ["unset", "on", "off"]),
        ("OpenGL Extension Overrides:", 'mesa_extension_override_combo', 
         ["unset", "try to disable anisotropic", "try to disable antialiasing", "try to disable both"]),
        ("Texture Dithering:", 'mesa_dither_combo', ["unset", "on", "off"]),
        ("Shader Cache:", 'mesa_shader_cache_combo', ["unset", "on", "off"]),
        ("Shader Cache Size (GB):", 'mesa_cache_size_combo', ["unset"] + [str(i) for i in range(1, 11)]),
        ("Error Checking:", 'mesa_error_check_combo', ["unset", "on", "off"]),
        ("Vulkan Version Spoofing:", 'mesa_fake_vk_combo', ["unset", "1.1", "1.2", "1.3", "1.4"]),
        ("OpenGL Version Spoofing:", 'mesa_fake_gl_combo', ["unset", "3.3", "3.3compat", "4.6", "4.6compat"]),
        ("GLSL Version Spoofing:", 'mesa_fake_glsl_combo', ["unset", "330", "460"]),
    ]
    
    NVIDIA_SETTINGS = [
        ("OpenGL Vsync:", 'nvidia_vsync_gl_combo', ["unset", "on", "off"]),
        ("OpenGL G-SYNC:", 'nvidia_gsync_combo', ["unset", "on", "off"]),
        ("OpenGL Thread Optimizations:", 'nvidia_thread_opt_combo', ["unset", "on", "off"]),
        ("OpenGL Full Scene Antialiasing:", 'nvidia_fsaa_combo', [
            "unset", "0 - off", "1 - 2x (2xms)", "5 - 4x (4xms)", 
            "7 - 8x (4xms, 4xcs)", "8 - 16x (4xms, 12xcs)", 
            "9 - 8x (4xss, 2xms)", "10 - 8x (8xms)", 
            "11 - 16x (4xss, 4xms)", "12 - 16x (8xms, 8xcs)", 
            "14 - 32x (8xms, 24xcs)"
        ]),
        ("OpenGL FXAA:", 'nvidia_fxaa_combo', ["unset", "on", "off"]),
        ("OpenGL Anisotropic Filtering:", 'nvidia_aniso_combo', [
            "unset", "0 - no anisotropic filtering",
            "1 - 2x anisotropic filtering", "2 - 4x anisotropic filtering",
            "3 - 8x anisotropic filtering", "4 - 16x anisotropic filtering"
        ]),
        ("OpenGL Texture Quality:", 'nvidia_tex_quality_combo', ["unset", "quality", "mixed", "performance"]),
        ("Shader Cache:", 'nvidia_shader_cache_combo', ["unset", "on", "off"]),
        ("Shader Cache Size (GB):", 'nvidia_cache_size_combo', ["unset"] + [str(i) for i in range(1, 11)]),
        ("Ignore GLSL Extensions Requirements:", 'nvidia_glsl_ext_combo', ["unset", "on", "off"]),
        ("Use Unofficial GLX Protocol:", 'nvidia_glx_combo', ["unset", "on", "off"])
    ]

    RENDER_SETTINGS = [
        ("OpenGL Provider:", 'ogl_provider_combo', [
            "unset", 
            "nvidia", 
            "mesa", 
            "mesa (software rendering)", 
            "mesa (zink)"
        ]),
        ("Mesa Select GPU:", 'dri_prime_combo', ["unset"] + [str(i) for i in range(0, 11)]),
        ("Vulkan ICD:", 'vulkan_render_combo', ["unset"]),
    ]

    RENDER_PIPELINE_SETTINGS = [
        ("Display Elements:", 'display_combo', ["unset", "no hud", "fps only", "horizontal", "extended", "detailed"]),
        ("Fps Limit:", 'fps_limit_combo', ["unset", "unlimited", "15", "20", "24", "25", "30", "40", "45", "50", "60", "72", "75", "90", "100", "120", "144", "165", "180", "200", "240", "360"]),
        ("Fps Limit Method:", 'fps_method_combo', ["unset", "early - smoothest frametimes", "late - lowest latency"]),
        ("Texture Filtering:", 'texture_filter_combo', ["unset", "bicubic", "retro", "trilinear"]),
        ("Mipmap LOD Bias:", 'mipmap_lod_bias_combo', ["unset"] + [str(i) for i in range(-16, 17)]),
        ("Anisotropic Filtering:", 'anisotropic_filter_combo', ["unset"] + [str(i) for i in range(0, 17)]),
    ]
    
    MESA_ENV_MAPPINGS = {
        'mesa_vsync_vk_combo': {
            'var_name': 'MESA_VK_WSI_PRESENT_MODE',
            'values': {'mailbox': 'mailbox', 'adaptive vsync': 'relaxed', 'on': 'fifo', 'off': 'immediate'}
        },
        'mesa_vsync_gl_combo': {
            'var_name': 'vblank_mode',
            'values': {'default interval 0': '1', 'default interval 1': '2', 'on': '3', 'off': '0'}
        },
        'mesa_thread_opt_combo': {
            'var_name': 'mesa_glthread',
            'values': {'on': 'true', 'off': 'false'}
        },
        'mesa_dither_combo': {
            'var_name': 'MESA_NO_DITHER',
            'values': {'on': '0', 'off': '1'}
        },
        'mesa_shader_cache_combo': {
            'var_name': 'MESA_SHADER_CACHE_DISABLE',
            'values': {'on': 'false', 'off': 'true'}
        },
        'mesa_cache_size_combo': {
            'var_name': 'MESA_SHADER_CACHE_MAX_SIZE',
            'direct_value': True
        },
        'mesa_error_check_combo': {
            'var_name': 'MESA_NO_ERROR',
            'values': {'on': 'false', 'off': 'true'}
        },
        'mesa_fake_gl_combo': {
            'var_name': 'MESA_GL_VERSION_OVERRIDE',
            'direct_value': True
        },
        'mesa_fake_glsl_combo': {
            'var_name': 'MESA_GLSL_VERSION_OVERRIDE',
            'direct_value': True
        },
        'mesa_fake_vk_combo': {
            'var_name': 'MESA_VK_VERSION_OVERRIDE',
            'direct_value': True
        },
        'mesa_extension_override_combo': {
            'var_name': 'MESA_EXTENSION_OVERRIDE',
            'values': {
                'try to disable anisotropic': '-GL_EXT_texture_filter_anisotropic',
                'try to disable antialiasing': '-GL_EXT_framebuffer_multisample -GL_EXT_framebuffer_multisample_blit_scaled',
                'try to disable both': '-GL_EXT_framebuffer_multisample -GL_EXT_framebuffer_multisample_blit_scaled -GL_EXT_texture_filter_anisotropic'
            }
        }
    }
    
    NVIDIA_ENV_MAPPINGS = {
        'nvidia_vsync_gl_combo': {
            'var_name': '__GL_SYNC_TO_VBLANK',
            'values': {'on': '1', 'off': '0'}
        },
        'nvidia_thread_opt_combo': {
            'var_name': '__GL_THREADED_OPTIMIZATIONS',
            'values': {'on': '1', 'off': '0'}
        },
        'nvidia_tex_quality_combo': {
            'var_name': '__GL_OpenGLImageSettings',
            'values': {'quality': '1', 'mixed': '2', 'performance': '3'}
        },
        'nvidia_fsaa_combo': {
            'var_name': '__GL_FSAA_MODE',
            'extract_prefix': True
        },
        'nvidia_fxaa_combo': {
            'var_name': '__GL_ALLOW_FXAA_USAGE',
            'values': {'on': '1', 'off': '0'}
        },
        'nvidia_aniso_combo': {
            'var_name': '__GL_LOG_MAX_ANISO',
            'extract_prefix': True
        },
        'nvidia_gsync_combo': {
            'var_name': '__GL_VRR_ALLOWED',
            'values': {'on': '1', 'off': '0'}
        },
        'nvidia_shader_cache_combo': {
            'var_name': '__GL_SHADER_DISK_CACHE',
            'values': {'on': '1', 'off': '0'}
        },
        'nvidia_cache_size_combo': {
            'var_name': '__GL_SHADER_DISK_CACHE_SIZE',
            'convert_to_bytes': True
        },
        'nvidia_glsl_ext_combo': {
            'var_name': '__GL_IGNORE_GLSL_EXT_REQ',
            'values': {'on': '1', 'off': '0'}
        },
        'nvidia_glx_combo': {
            'var_name': '__GL_ALLOW_UNOFFICIAL_PROTOCOL',
            'values': {'on': '1', 'off': '0'}
        }
    }
    
    RENDER_ENV_MAPPINGS = {
        'ogl_provider_combo': {
            'var_name': '__GLX_VENDOR_LIBRARY_NAME',
            'values': {
                'nvidia': 'nvidia',
                'mesa': 'mesa',
                'mesa (software rendering)': 'mesa',
                'mesa (zink)': 'mesa'
            }
        },
        'dri_prime_combo': {
            'var_name': 'DRI_PRIME',
            'direct_value': True,
            'dependency': 'mesa_only'
        },
        'vulkan_render_combo': {
            'var_name': 'VK_DRIVER_FILES',
            'special_handling': 'vulkan_icd'
        }
    }

    RENDER_PIPELINE_ENV_MAPPINGS = {
        'display_combo': {
            'var_name': 'MANGOHUD_CONFIG',
            'values': {'no hud': 'preset=0', 'fps only': 'preset=1', 'horizontal': 'preset=2', 'extended': 'preset=3', 'detailed': 'preset=4',}
        },
        'fps_limit_combo': {
            'var_name': 'MANGOHUD_CONFIG',
            'values': {'unlimited': '0'},
            'direct_value': True,
            'prefix': 'fps_limit='
        },
        'fps_method_combo': {
            'var_name': 'MANGOHUD_CONFIG',
            'values': {'early - smoothest frametimes': 'early', 'late - lowest latency': 'late'},
            'prefix': 'fps_limit_method='
        },
        'texture_filter_combo': {
            'var_name': 'MANGOHUD_CONFIG',
            'values': {
                'bicubic': 'bicubic',
                'retro': 'retro',
                'trilinear': 'trilinear'
            }
        },
        'mipmap_lod_bias_combo': {
            'var_name': 'MANGOHUD_CONFIG',
            'direct_value': True,
            'prefix': 'picmip='
        },
        'anisotropic_filter_combo': {
            'var_name': 'MANGOHUD_CONFIG',
            'direct_value': True,
            'prefix': 'af='
        }
    }

    @staticmethod
    def find_available_mangohud():
        """
        Dynamically find MangoHUD availability in system paths and Flatpak.
        """
        for search_path in GPULaunchManager.MANGOHUD_SEARCH_PATHS:
            try:
                mangohud_files = glob.glob(os.path.join(search_path, "mangohud*"))
                for file_path in mangohud_files:
                    if os.access(file_path, os.X_OK):
                        return True
            except Exception:
                continue
        
        try:
            result = subprocess.run(["flatpak", "list"], capture_output=True, text=True, check=True)
            if "mangohud" in result.stdout.lower():
                return True
        except Exception:
            pass
        
        return False

    @staticmethod
    def _get_vulkan_icd_options():
        """
        Gets available Vulkan ICD (Installable Client Driver) options.
        """
        options = []
        
        try:
            icd_files = {}
            for file in os.listdir(GPULaunchManager.ICD_DIR):
                if file.endswith('.json'):
                    base_name = file[:-5]
                    
                    if '.' in base_name:
                        pure_name = base_name.split('.')[0]
                        if pure_name not in icd_files:
                            icd_files[pure_name] = []
                        icd_files[pure_name].append(os.path.join(GPULaunchManager.ICD_DIR, file))
                    else:
                        if base_name not in icd_files:
                            icd_files[base_name] = []
                        icd_files[base_name].append(os.path.join(GPULaunchManager.ICD_DIR, file))
            
            for name, paths in icd_files.items():
                if 'lvp' in name.lower():
                    options.append(f"{name} (software rendering)")
                else:
                    options.append(name)
        except OSError:
            pass
        
        return sorted(options)

    @staticmethod
    def create_gpu_settings_tab():
        """
        Creates the GPU settings tab with Mesa, NVIDIA, render selector, and render pipeline subtabs.
        """
        gpu_tab = QWidget()
        gpu_layout = QVBoxLayout(gpu_tab)
        gpu_layout.setSpacing(10)
        
        gpu_subtabs = QTabWidget()
        mesa_tab, mesa_widgets = GPULaunchManager._create_mesa_tab()
        nvidia_tab, nvidia_widgets = GPULaunchManager._create_nvidia_tab()
        render_selector_tab, render_selector_widgets = GPULaunchManager._create_render_selector_tab()
        render_pipeline_tab, render_pipeline_widgets = GPULaunchManager._create_render_pipeline_tab()
        
        gpu_subtabs.addTab(mesa_tab, "Mesa")
        gpu_subtabs.addTab(nvidia_tab, "NVIDIA (Proprietary)")
        gpu_subtabs.addTab(render_selector_tab, "Render Selector")
        gpu_subtabs.addTab(render_pipeline_tab, "Render Pipeline")
        gpu_layout.addWidget(gpu_subtabs)
        
        widgets = {
            'mesa': mesa_widgets,
            'nvidia': nvidia_widgets,
            'render_selector': render_selector_widgets,
            'render_pipeline': render_pipeline_widgets
        }
        
        return gpu_tab, widgets

    @staticmethod
    def _create_mesa_tab():
        """
        Creates the Mesa settings tab.
        """
        return GPULaunchManager._create_settings_tab(GPULaunchManager.MESA_SETTINGS, "mesa_apply_button")

    @staticmethod
    def _create_nvidia_tab():
        """
        Creates the NVIDIA settings tab.
        """
        return GPULaunchManager._create_settings_tab(GPULaunchManager.NVIDIA_SETTINGS, "nvidia_apply_button")
    
    @staticmethod
    def _create_settings_tab(settings_layouts, apply_button_name):
        """
        Helper method to create a settings tab with the specified configuration.
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
        scroll_layout.setContentsMargins(0, 10, 0, 0)
        
        widgets = {}
        
        for label_text, combo_name, items in settings_layouts:
            layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            
            widgets[combo_name] = QComboBox()
            widgets[combo_name].addItems(items)
            widgets[combo_name].setCurrentText("unset")
            widgets[combo_name].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            
            layout.addWidget(label)
            layout.addWidget(widgets[combo_name])
            scroll_layout.addLayout(layout)
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        GPULaunchManager.create_gpu_apply_button(main_layout, widgets, apply_button_name)
        
        return tab, widgets

    @staticmethod
    def _create_render_selector_tab():
        """
        Creates the render selector tab for choosing OpenGL/Vulkan rendering devices.
        """
        render_tab, widgets = GPULaunchManager._create_settings_tab(GPULaunchManager.RENDER_SETTINGS, "render_selector_apply_button")
        
        vulkan_options = ["unset"] + GPULaunchManager._get_vulkan_icd_options()
        widgets['vulkan_render_combo'].clear()
        widgets['vulkan_render_combo'].addItems(vulkan_options)
        widgets['vulkan_render_combo'].setCurrentText("unset")

        return render_tab, widgets

    @staticmethod
    def _create_render_pipeline_tab():
        """
        Creates the render pipeline tab for managing FPS, filters and display settings.
        """
        mangohud_available = GPULaunchManager.find_available_mangohud()
        
        render_pipeline_tab, widgets = GPULaunchManager._create_settings_tab(GPULaunchManager.RENDER_PIPELINE_SETTINGS, "render_pipeline_apply_button")
        
        if not mangohud_available:
            for widget in widgets.values():
                widget.setEnabled(False)

        return render_pipeline_tab, widgets

    @staticmethod
    def create_launch_options_tab():
        """
        Creates the launch options tab for specifying additional launch commands.
        """
        launch_tab = QWidget()
        main_layout = QVBoxLayout(launch_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_widget.setProperty("scrollContainer", True)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        setting_container = QWidget()
        setting_container.setProperty("settingContainer", True)
        setting_layout = QVBoxLayout(setting_container)
        setting_layout.setContentsMargins(0, 10, 0, 0)
        
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
        
        main_layout.addSpacing(9)
        
        return launch_tab, widgets

    @staticmethod
    def create_gpu_apply_button(layout, widgets, button_name):
        """
        Creates and adds an apply button to the specified layout.
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
        Creates and adds an apply button specifically for the launch options tab.
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 0)

        widgets['launch_apply_button'] = QPushButton("Apply")
        widgets['launch_apply_button'].setMinimumSize(100, 30)
        widgets['launch_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets['launch_apply_button'])
        button_layout.addStretch(1)
        layout.addWidget(button_container)

    @staticmethod
    def _generate_mesa_env_vars(mesa_widgets):
        """
        Generates script content for Mesa environment variables.
        """
        env_vars = []
        
        for widget_key, mapping in GPULaunchManager.MESA_ENV_MAPPINGS.items():
            if widget_key not in mesa_widgets:
                continue
                
            value = mesa_widgets[widget_key].currentText()
            if value == "unset":
                continue
                
            var_name = mapping['var_name']
            
            if mapping.get('direct_value', False):
                env_vars.append(f'{var_name}={value}')
            else:
                mapped_value = mapping['values'].get(value)
                if mapped_value:
                    env_vars.append(f'{var_name}={mapped_value}')
        
        return env_vars

    @staticmethod
    def _generate_nvidia_env_vars(nvidia_widgets):
        """
        Generates script content for NVIDIA environment variables.
        """
        env_vars = []
        
        for widget_key, mapping in GPULaunchManager.NVIDIA_ENV_MAPPINGS.items():
            if widget_key not in nvidia_widgets:
                continue
                
            value = nvidia_widgets[widget_key].currentText()
            if value == "unset":
                continue
                
            var_name = mapping['var_name']
            
            if mapping.get('extract_prefix', False):
                extracted_value = value.split(' - ')[0]
                env_vars.append(f'{var_name}={extracted_value}')
            elif mapping.get('convert_to_bytes', False):
                bytes_value = int(value) * 1073741824
                env_vars.append(f'{var_name}={bytes_value}')
            elif mapping.get('direct_value', False):
                env_vars.append(f'{var_name}={value}')
            else:
                mapped_value = mapping['values'].get(value)
                if mapped_value:
                    env_vars.append(f'{var_name}={mapped_value}')
        
        return env_vars

    @staticmethod
    def _generate_render_selector_env_vars(render_widgets):
        """
        Generates environment variables for render selector settings in key=value format.
        """
        env_vars = []
        
        if not render_widgets or 'ogl_provider_combo' not in render_widgets:
            return env_vars
            
        provider = render_widgets['ogl_provider_combo'].currentText()
        vulkan_selection = render_widgets['vulkan_render_combo'].currentText()
        
        if provider != "unset":
            mapping = GPULaunchManager.RENDER_ENV_MAPPINGS['ogl_provider_combo']
            mapped_value = mapping['values'].get(provider)
            if mapped_value:
                env_vars.append(f"{mapping['var_name']}={mapped_value}")
                
                if provider == "mesa (software rendering)":
                    env_vars.append("LIBGL_ALWAYS_SOFTWARE=1")
                elif provider == "mesa (zink)":
                    env_vars.append("MESA_LOADER_DRIVER_OVERRIDE=zink")
                    env_vars.append("LIBGL_KOPPER_DRI2=1")
                    if "(software rendering)" in vulkan_selection.lower():
                        env_vars.append("LIBGL_ALWAYS_SOFTWARE=1")
        
        if provider.startswith("mesa"):
            mapping = GPULaunchManager.RENDER_ENV_MAPPINGS['dri_prime_combo']
            value = render_widgets['dri_prime_combo'].currentText()
            if value != "unset":
                env_vars.append(f"{mapping['var_name']}={value}")
        
        mapping = GPULaunchManager.RENDER_ENV_MAPPINGS['vulkan_render_combo']
        value = vulkan_selection
        if value != "unset":
            if "(software rendering)" in value.lower():
                vulkan_selection_name = re.sub(r'\s*\(software rendering\)', '', value, flags=re.IGNORECASE)
            else:
                vulkan_selection_name = value
            
            icd_files = []
            
            try:
                for file in os.listdir(GPULaunchManager.ICD_DIR):
                    if file.endswith('.json'):
                        base_name = file[:-5]
                        if '.' in base_name:
                            pure_name = base_name.split('.')[0]
                            if pure_name == vulkan_selection_name:
                                icd_files.append(os.path.join(GPULaunchManager.ICD_DIR, file))
                        else:
                            if base_name == vulkan_selection_name:
                                icd_files.append(os.path.join(GPULaunchManager.ICD_DIR, file))
            except OSError:
                pass
            
            if icd_files:
                driver_paths = ":".join(icd_files)
                env_vars.append(f"{mapping['var_name']}={driver_paths}")
                env_vars.append('DISABLE_LAYER_AMD_SWITCHABLE_GRAPHICS_1=1')
        
        return env_vars

    @staticmethod
    def _generate_render_pipeline_env_vars(render_pipeline_widgets):
        """
        Generates environment variables for render pipeline settings.
        """
        env_vars = []
        mangohud_config_parts = []
        use_mangohud = False
        
        for widget_key, mapping in GPULaunchManager.RENDER_PIPELINE_ENV_MAPPINGS.items():
            if widget_key not in render_pipeline_widgets:
                continue
                
            widget = render_pipeline_widgets[widget_key]
            value = widget.currentText()
            if value == "unset":
                continue
                
            use_mangohud = True
            
            if mapping.get('direct_value', False):
                prefix = mapping.get('prefix', '')
                if value == 'unlimited':
                    mapped_value = mapping['values'].get(value, '0')
                    mangohud_config_parts.append(f'{prefix}{mapped_value}')
                else:
                    mangohud_config_parts.append(f'{prefix}{value}')
            
            elif 'values' in mapping:
                mapped_value = mapping['values'].get(value)
                if mapped_value:
                    prefix = mapping.get('prefix', '')
                    mangohud_config_parts.append(f'{prefix}{mapped_value}')
            
            else:
                mapped_value = mapping['values'].get(value)
                if mapped_value:
                    mangohud_config_parts.append(mapped_value)
        
        if mangohud_config_parts:
            config_value = ','.join(mangohud_config_parts)
            env_vars.append(f'MANGOHUD_CONFIG={config_value}')
        
        return env_vars, use_mangohud

    @staticmethod
    def write_settings_file(mesa_widgets, nvidia_widgets, render_selector_widgets, render_pipeline_widgets, launch_options_widgets):
        """
        Writes GPU settings to a temporary file for volt-helper to process.
        """
        mesa_env_vars = GPULaunchManager._generate_mesa_env_vars(mesa_widgets)
        nvidia_env_vars = GPULaunchManager._generate_nvidia_env_vars(nvidia_widgets)
        render_env_vars = GPULaunchManager._generate_render_selector_env_vars(render_selector_widgets)
            
        launch_options = ""
        if 'launch_options_input' in launch_options_widgets:
            launch_options = launch_options_widgets['launch_options_input'].text().strip()

        render_pipeline_env_vars, use_mangohud = GPULaunchManager._generate_render_pipeline_env_vars(render_pipeline_widgets)

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