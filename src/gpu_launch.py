import os
import re
import tempfile
import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTabWidget, QScrollArea, QSizePolicy, QLineEdit,
    QSystemTrayIcon
)
from PySide6.QtCore import Qt


class GPULaunchManager:
    """
    Main class for managing GPU launch settings and configurations.
    Provides functionality to create UI tabs for Mesa, NVIDIA, render selector, and launch options,
    generate environment variable scripts, and manage the configuration file.
    """
    
    # Mesa driver settings configuration
    MESA_SETTINGS = [
        ("Vulkan Vsync:", 'mesa_vsync_vk_combo', ["unset", "on", "off"]),
        ("OpenGL Vsync:", 'mesa_vsync_gl_combo', ["unset", "on", "off"]),
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
    
    # NVIDIA driver settings configuration
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
    
    # Mapping between Mesa UI widgets and environment variables
    MESA_ENV_MAPPINGS = {
        'mesa_vsync_gl_combo': {
            'var_name': 'vblank_mode',
            'values': {'on': '3', 'off': '0'}
        },
        'mesa_vsync_vk_combo': {
            'var_name': 'MESA_VK_WSI_PRESENT_MODE',
            'values': {'on': 'fifo', 'off': 'immediate'}
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
    
    # Mapping between NVIDIA UI widgets and environment variables
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
    
    # OpenGL render device options
    OPENGL_RENDER_OPTIONS = [
        "dedicated gpu",
        "integrated gpu",
        "llvmpipe (Software Rendering)"
    ]

    # Mapping between OpenGL render options and environment variables
    OPENGL_RENDER_MAPPINGS = {
        "dedicated gpu": {
            "DRI_PRIME": "1",
            "__GLX_VENDOR_LIBRARY_NAME": "nvidia"
        },
        "integrated gpu": {
            "DRI_PRIME": "0",
            "__GLX_VENDOR_LIBRARY_NAME": "mesa"
        },
        "llvmpipe (Software Rendering)": {
            "LIBGL_ALWAYS_SOFTWARE": "1",
            "__GLX_VENDOR_LIBRARY_NAME": "mesa"
        }
    }
    
    # Path to the volt script
    VOLT_SCRIPT_PATH = "/usr/local/bin/volt"
    
    # Class variables to store widgets
    mesa_widgets = {}
    nvidia_widgets = {}
    render_selector_widgets = {}
    launch_options_widgets = {}
    tray_icon = None

    @staticmethod
    def _create_gpu_settings_tab():
        """
        Creates the GPU settings tab with Mesa, NVIDIA, and render selector subtabs.
        Returns:
            tuple: (QWidget, QTabWidget, dict, dict) The GPU tab widget, subtabs widget,
                   Mesa widgets dict, and NVIDIA widgets dict
        """
        gpu_tab = QWidget()
        gpu_layout = QVBoxLayout(gpu_tab)
        gpu_layout.setSpacing(10)
        
        gpu_subtabs = QTabWidget()
        mesa_tab, mesa_widgets = GPULaunchManager._create_mesa_tab()
        nvidia_tab, nvidia_widgets = GPULaunchManager._create_nvidia_tab()
        render_selector_tab = GPULaunchManager._create_render_selector_tab()
        
        gpu_subtabs.addTab(mesa_tab, "Mesa")
        gpu_subtabs.addTab(nvidia_tab, "NVIDIA (Proprietary)")
        gpu_subtabs.addTab(render_selector_tab, "Render Selector")
        gpu_layout.addWidget(gpu_subtabs)
        
        return gpu_tab, gpu_subtabs, mesa_widgets, nvidia_widgets

    @staticmethod
    def _create_mesa_tab():
        """
        Creates the Mesa settings tab.
        Returns:
            tuple: (QWidget, dict) The Mesa tab widget and its widgets dictionary
        """
        return GPULaunchManager._create_settings_tab(GPULaunchManager.MESA_SETTINGS, "mesa_apply_button")

    @staticmethod
    def _create_nvidia_tab():
        """
        Creates the NVIDIA settings tab.
        Returns:
            tuple: (QWidget, dict) The NVIDIA tab widget and its widgets dictionary
        """
        return GPULaunchManager._create_settings_tab(GPULaunchManager.NVIDIA_SETTINGS, "nvidia_apply_button")
    
    @staticmethod
    def _create_settings_tab(settings_layouts, apply_button_name):
        """
        Helper method to create a settings tab with the specified configuration.
        Args:
            settings_layouts: List of setting configurations
            apply_button_name: Name for the apply button widget
        Returns:
            tuple: (QWidget, dict) The created tab widget and its widgets dictionary
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
        
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 0)

        widgets[apply_button_name] = QPushButton("Apply")
        widgets[apply_button_name].setMinimumSize(100, 30)
        widgets[apply_button_name].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets[apply_button_name])
        button_layout.addStretch(1)
        main_layout.addWidget(button_container)
        
        return tab, widgets

    @staticmethod
    def _create_render_selector_tab():
        """
        Creates the render selector tab for choosing OpenGL/Vulkan rendering devices.
        Returns:
            QWidget: The created render selector tab widget
        """
        render_tab = QWidget()
        main_layout = QVBoxLayout(render_tab)
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
        
        opengl_layout = QHBoxLayout()
        opengl_label = QLabel("OpenGL Rendering Device:")
        opengl_label.setWordWrap(True)
        opengl_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['opengl_render_combo'] = QComboBox()
        widgets['opengl_render_combo'].addItems(["unset"] + GPULaunchManager.OPENGL_RENDER_OPTIONS)
        widgets['opengl_render_combo'].setCurrentText("unset")
        widgets['opengl_render_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        opengl_layout.addWidget(opengl_label)
        opengl_layout.addWidget(widgets['opengl_render_combo'])
        scroll_layout.addLayout(opengl_layout)
        
        vulkan_layout = QHBoxLayout()
        vulkan_label = QLabel("Vulkan Rendering Device:")
        vulkan_label.setWordWrap(True)
        vulkan_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        widgets['vulkan_render_combo'] = QComboBox()
        vulkan_options = ["unset"] + GPULaunchManager._get_vulkan_icd_options()
        widgets['vulkan_render_combo'].addItems(vulkan_options)
        widgets['vulkan_render_combo'].setCurrentText("unset")
        widgets['vulkan_render_combo'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        vulkan_layout.addWidget(vulkan_label)
        vulkan_layout.addWidget(widgets['vulkan_render_combo'])
        scroll_layout.addLayout(vulkan_layout)
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 0)

        widgets['render_selector_apply_button'] = QPushButton("Apply")
        widgets['render_selector_apply_button'].setMinimumSize(100, 30)
        widgets['render_selector_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets['render_selector_apply_button'])
        button_layout.addStretch(1)
        main_layout.addWidget(button_container)
        
        GPULaunchManager.render_selector_widgets = widgets
        
        return render_tab

    @staticmethod
    def _create_launch_options_tab():
        """
        Creates the launch options tab for specifying additional launch commands.
        Returns:
            QWidget: The created launch options tab widget
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
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 0)
        
        scroll_layout.addSpacing(10)
        
        launch_options_layout = QVBoxLayout()
        launch_options_label = QLabel("Launch Options:")
        launch_options_label.setWordWrap(True)
        launch_options_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        launch_options_input = QLineEdit()
        launch_options_input.setPlaceholderText(
            "Enter programs to be launched with the game and environment variables, "
            "example: gamemoderun PROTON_USE_WINED3D=1"
        )
        launch_options_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        launch_options_layout.addWidget(launch_options_label)
        launch_options_layout.addWidget(launch_options_input)
        scroll_layout.addLayout(launch_options_layout)
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 0)

        apply_button = QPushButton("Apply")
        apply_button.setMinimumSize(100, 30)
        apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(apply_button)
        button_layout.addStretch(1)
        main_layout.addWidget(button_container)
        
        main_layout.addSpacing(9)
        
        GPULaunchManager.launch_options_widgets = {
            'launch_options_input': launch_options_input,
            'apply_button': apply_button
        }
        
        return launch_tab

    @staticmethod
    def apply_gpu_launch_settings(tray_icon):
        """
        Apply GPU launch settings and show system tray notifications.
        Returns:
            bool: True if settings were applied successfully, False otherwise
        """
        try:
            script_path = GPULaunchManager._write_volt_script_with_all_settings(
                GPULaunchManager.mesa_widgets, 
                GPULaunchManager.nvidia_widgets
            )
            
            if tray_icon:
                tray_icon.showMessage(
                    "volt-gui",
                    f"GPU launch settings applied and saved to {script_path}",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
            
            return True
                
        except Exception as e:
            if tray_icon:
                tray_icon.showMessage(
                    "volt-gui",
                    f"Error applying GPU launch settings: {e}",
                    QSystemTrayIcon.MessageIcon.Critical,
                    2000
                )
            return False

    @staticmethod
    def _get_vulkan_icd_options():
        """
        Gets available Vulkan ICD (Installable Client Driver) options.
        Returns:
            list: Available Vulkan ICD options
        """
        icd_dir = "/usr/share/vulkan/icd.d/"
        options = []
        
        try:
            icd_files = {}
            for file in os.listdir(icd_dir):
                if file.endswith('.json'):
                    base_name = file[:-5]
                    
                    if '.' in base_name:
                        pure_name = base_name.split('.')[0]
                        if pure_name not in icd_files:
                            icd_files[pure_name] = []
                        icd_files[pure_name].append(os.path.join(icd_dir, file))
                    else:
                        if base_name not in icd_files:
                            icd_files[base_name] = []
                        icd_files[base_name].append(os.path.join(icd_dir, file))
            
            for name, paths in icd_files.items():
                if 'lvp' in name.lower():
                    options.append(f"{name} (Software Rendering)")
                else:
                    options.append(name)
        except OSError:
            pass
        
        return sorted(options)

    @staticmethod
    def _generate_render_selector_env_vars(render_widgets):
        """
        Generates environment variables for render selector settings.
        Args:
            render_widgets: Dictionary containing render selector widgets
        Returns:
            list: Generated environment variable strings
        """
        env_vars = []
        
        opengl_selection = render_widgets['opengl_render_combo'].currentText()
        if opengl_selection != "unset":
            mappings = GPULaunchManager.OPENGL_RENDER_MAPPINGS.get(opengl_selection, {})
            for var_name, value in mappings.items():
                env_vars.append(f'export {var_name}="{value}"')
        
        vulkan_selection = render_widgets['vulkan_render_combo'].currentText()
        if vulkan_selection != "unset":
            if "(Software Rendering)" in vulkan_selection:
                vulkan_selection = vulkan_selection.replace(" (Software Rendering)", "")
            
            icd_dir = "/usr/share/vulkan/icd.d/"
            icd_files = []
            
            try:
                for file in os.listdir(icd_dir):
                    if file.endswith('.json'):
                        if '.' in file[:-5]:
                            base_name = file[:-5].split('.')[0]
                            if base_name == vulkan_selection:
                                icd_files.append(os.path.join(icd_dir, file))
                        else:
                            if file[:-5] == vulkan_selection:
                                icd_files.append(os.path.join(icd_dir, file))
            except OSError:
                pass
            
            if icd_files:
                driver_paths = ":".join(icd_files)
                env_vars.append(f'export VK_DRIVER_FILES="{driver_paths}"')
                env_vars.append('export DISABLE_LAYER_AMD_SWITCHABLE_GRAPHICS_1="1"')
        
        return env_vars

    @staticmethod
    def _generate_mesa_script_content(mesa_widgets):
        """
        Generates script content for Mesa environment variables.
        Args:
            mesa_widgets: Dictionary containing Mesa settings widgets
        Returns:
            list: Generated environment variable strings
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
                env_vars.append(f'export {var_name}="{value}"')
            else:
                mapped_value = mapping['values'].get(value)
                if mapped_value:
                    env_vars.append(f'export {var_name}="{mapped_value}"')
        
        return env_vars

    @staticmethod
    def _generate_nvidia_script_content(nvidia_widgets):
        """
        Generates script content for NVIDIA environment variables.
        Args:
            nvidia_widgets: Dictionary containing NVIDIA settings widgets
        Returns:
            list: Generated environment variable strings
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
                env_vars.append(f'export {var_name}="{extracted_value}"')
            elif mapping.get('convert_to_bytes', False):
                bytes_value = int(value) * 1073741824
                env_vars.append(f'export {var_name}="{bytes_value}"')
            elif mapping.get('direct_value', False):
                env_vars.append(f'export {var_name}="{value}"')
            else:
                mapped_value = mapping['values'].get(value)
                if mapped_value:
                    env_vars.append(f'export {var_name}="{mapped_value}"')
        
        return env_vars

    @staticmethod
    def _write_volt_script(script_content):
        """
        Writes the volt script to the specified path with root permissions.
        Args:
            script_content: Content to write to the script
        Returns:
            str: Path to the written script
        Raises:
            RuntimeError: If script writing fails
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(script_content)
            temp_path = temp_file.name
        
        try:
            subprocess.run([
                "pkexec", "sh", "-c",
                f"cat '{temp_path}' > {GPULaunchManager.VOLT_SCRIPT_PATH} && chmod 755 {GPULaunchManager.VOLT_SCRIPT_PATH}"
            ], check=True)
            
            os.unlink(temp_path)
            return GPULaunchManager.VOLT_SCRIPT_PATH
        except subprocess.CalledProcessError as e:
            os.unlink(temp_path)
            raise RuntimeError(f"Failed to write script: {e}")
        except Exception as e:
            os.unlink(temp_path)
            raise RuntimeError(f"Unexpected error writing script: {e}")

    @staticmethod
    def _write_volt_script_with_all_settings(mesa_widgets, nvidia_widgets):
        """
        Writes a volt script combining all settings (Mesa, NVIDIA, render selector, launch options).
        Args:
            mesa_widgets: Dictionary containing Mesa settings widgets
            nvidia_widgets: Dictionary containing NVIDIA settings widgets
        Returns:
            str: Path to the written script
        """
        mesa_env_vars = []
        if mesa_widgets is not None:
            mesa_env_vars = GPULaunchManager._generate_mesa_script_content(mesa_widgets)
        
        nvidia_env_vars = []
        if nvidia_widgets is not None:
            nvidia_env_vars = GPULaunchManager._generate_nvidia_script_content(nvidia_widgets)
        
        render_env_vars = []
        if GPULaunchManager.render_selector_widgets:
            render_env_vars = GPULaunchManager._generate_render_selector_env_vars(
                GPULaunchManager.render_selector_widgets
            )
            
        launch_options = ""
        if GPULaunchManager.launch_options_widgets and 'launch_options_input' in GPULaunchManager.launch_options_widgets:
            launch_options = GPULaunchManager.launch_options_widgets['launch_options_input'].text().strip()
        
        all_env_vars = mesa_env_vars + nvidia_env_vars + render_env_vars
        
        script_content = "#!/bin/bash\n\n"
        script_content += "\n".join(all_env_vars)
        
        script_content += "\n\n# Handle launch options if present\n"
        if launch_options:
            script_content += f"# Execute the specified program with environment variables\n"
            script_content += f"{launch_options} \"$@\"\n"
        else:
            script_content += "# Launch the specified program with the environment variables\n"
            script_content += "\"$@\"\n"
        
        return GPULaunchManager._write_volt_script(script_content)