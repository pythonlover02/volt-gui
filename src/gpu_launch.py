import os, glob, tempfile
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTabWidget, QScrollArea, QSizePolicy, QLineEdit, QFileDialog
from PySide6.QtCore import Qt, QProcess
from workarounds import WorkaroundManager

class GPULaunchManager:

    SEARCH_PATHS = ["/usr/bin/", "/usr/local/bin/"]

    GPU_SETTINGS_CATEGORIES = {
        "Mesa": {
            'mesa_gl_vsync': {
                'label': "OpenGL Vsync:",
                'text': "OpenGL vertical synchronization.",
                'items': ["unset", "program decides (default)", "default interval 0", "default interval 1", "on", "off"],
                'env_mapping': {
                    'var_names': ['vblank_mode'],
                    'values': {'default interval 0': '1', 'default interval 1': '2', 'on': '3', 'off': '0'}
                }
            },
            'mesa_gl_thread_opt': {
                'label': "OpenGL Thread Optimizations:",
                'text': "Multi-threaded OpenGL command processing. Might improve or worsen OpenGL performance depending on the program being run.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['mesa_glthread'],
                    'values': {'on': 'true'}
                }
            },
            'mesa_gl_dither': {
                'label': "OpenGL Texture Dithering:",
                'text': "OpenGL color dithering on low-depth framebuffers. Reduces color banding on displays with limited color depth at minimal performance cost.",
                'items': ["unset", "on (default)", "off"],
                'env_mapping': {
                    'var_names': ['MESA_NO_DITHER'],
                    'values': {'off': '1'}
                }
            },
            'mesa_gl_msaa': {
                'label': "OpenGL MSAA:",
                'text': "Multisample anti-aliasing in OpenGL. Smooths jagged edges by sampling multiple points per pixel, improving image quality with performance impact.",
                'items': ["unset", "on (default)", 'off'],
                'env_mapping': {
                    'var_names': ['DRI_NO_MSAA'],
                    'values': {'off': '1'}
                }
            },
            'mesa_gl_error_check': {
                'label': "OpenGL Error Checking:",
                'text': "OpenGL error checking. Validates API calls for correctness; disable for performance in stable applications.",
                'items': ["unset", "on (default)", "off"],
                'env_mapping': {
                    'var_names': ['MESA_NO_ERROR'],
                    'values': {'off': '1'}
                }
            },
            'mesa_gl_fake': {
                'label': "OpenGL Version Spoofing:",
                'text': "Report a different OpenGL version to applications. Useful for running games that check version numbers but don't need newer features.",
                'items': ["unset", "off (default)", "3.3", "3.3compat", "4.6", "4.6compat"],
                'env_mapping': {
                    'var_names': ['MESA_GL_VERSION_OVERRIDE'],
                    'direct_value': True
                }
            },
            'mesa_glsl_fake': {
                'label': "GLSL Version Spoofing:",
                'text': "Report a different GLSL version to applications. Works with OpenGL version spoofing for compatibility workarounds.",
                'items': ["unset", "off (default)", "330", "460"],
                'env_mapping': {
                    'var_names': ['MESA_GLSL_VERSION_OVERRIDE'],
                    'direct_value': True
                }
            },
            'mesa_vk_vsync': {
                'label': "Vulkan Vsync:",
                'text': "Vulkan vertical synchronization.",
                'items': ["unset", "program decides (default)", "mailbox", "adaptive vsync", "on", "off"],
                'env_mapping': {
                    'var_names': ['MESA_VK_WSI_PRESENT_MODE'],
                    'values': {'mailbox': 'mailbox', 'adaptive vsync': 'relaxed', 'on': 'fifo', 'off': 'immediate'}
                }
            },
            'mesa_vk_submit_thread': {
                'label': "Vulkan Submit Thread:",
                'text': "Dedicated thread for Vulkan command submission. Separates command submission from command recording, might reduce CPU overhead.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['MESA_VK_ENABLE_SUBMIT_THREAD'],
                    'values': {'on': '1'}
                }
            },
            'mesa_vk_fake': {
                'label': "Vulkan Version Spoofing:",
                'text': "Report a different Vulkan version to applications. Bypasses version checks for games that artificially restrict compatibility.",
                'items': ["unset", "off (default)", "1.1", "1.2", "1.3", "1.4"],
                'env_mapping': {
                    'var_names': ['MESA_VK_VERSION_OVERRIDE'],
                    'direct_value': True
                }
            },
            'mesa_shader_cache': {
                'label': "Shader Cache:",
                'text': "Disk-based shader caching. Stores compiled shaders to disk to eliminate compilation stuttering on subsequent launches.",
                'items': ["unset", "on (default)", "off"],
                'env_mapping': {
                    'var_names': ['MESA_SHADER_CACHE_DISABLE', 'MESA_GLSL_CACHE_DISABLE'],
                    'values': {'off': 'true'}
                }
            },
            'mesa_cache_size': {
                'label': "Shader Cache Size (GB):",
                'text': "Maximum size for the shader cache. Larger caches store more compiled shaders but consume more disk space.",
                'items': ["unset", "program decides (default)"] + [str(i) for i in range(1, 11)] + [str(i) for i in [25, 50, 75, 100]],
                'env_mapping': {
                    'var_names': ['MESA_SHADER_CACHE_MAX_SIZE', 'MESA_GLSL_CACHE_MAX_SIZE'],
                    'direct_value': True
                }
            },
            'radeonsi_no_infinite_interp': {
                'label': "RadeonSI Disable Infinite Interpolation:",
                'text': "Disable infinite interpolation in RadeonSI. Workaround for rendering bugs in some games on AMD GPUs.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['radeonsi_no_infinite_interp'],
                    'values': {'on': 'true'}
                }
            },
            'radeonsi_clamp_div_by_zero': {
                'label': "RadeonSI Clamp Division by Zero:",
                'text': "Clamp division by zero results in RadeonSI. Prevents crashes or visual glitches from shader math errors on AMD GPUs.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['radeonsi_clamp_div_by_zero'],
                    'values': {'on': 'true'}
                }
            },
            'radeonsi_zerovram': {
                'label': "RadeonSI Clear VRAM to Zero:",
                'text': "Clear all allocated VRAM to zero before usage in RadeonSI. Might fix rendering corruptions on AMD GPUs.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['radeonsi_zerovram'],
                    'values': {'on': 'true'}
                }
            },
            'radv_anisotropic_filtering': {
                'label': "RADV Anisotropic Filtering:",
                'text': "Anisotropic filtering level for RADV. Improves texture quality at oblique angles with minimal performance impact on modern AMD GPUs.",
                'items': ["unset", "program decides (default)"] + [str(i) for i in range(0, 17)],
                'env_mapping': {
                    'var_names': ['RADV_TEX_ANISO'],
                    'direct_value': True
                }
            },
            'radv_profile_pstate': {
                'label': "RADV Profile Pstate:",
                'text': "Performance state profiling in RADV. Forces specific GPU clock levels for consistent performance or power testing on AMD GPUs.",
                'items': [
                    "unset",
                    "program decides (default)",
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
            'radv_vrs': {
                'label': "RADV Variable Rate Shading (GFX10.3+):",
                'text': "Variable rate shading in RADV (GFX10.3+). Renders different screen areas at different resolutions to improve performance with minimal quality loss.",
                'items': ["unset", "program decides (default)", "2x2", "1x2", "2x1", "1x1"],
                'env_mapping': {
                    'var_names': ['RADV_FORCE_VRS'],
                    'direct_value': True
                }
            },
            'intel_precise_trig': {
                'label': "Intel Driver Preference on Trigonometric Functions:",
                'text': "Precision vs performance tradeoff for trigonometric functions on Intel GPUs. Accuracy mode ensures correct results; performance mode may have minor errors but runs faster.",
                'items': ["unset", "accuracy", "performance (default)"],
                'env_mapping': {
                    'var_names': ['INTEL_PRECISE_TRIG'],
                    'values': {'accuracy': 'true'}
                }
            },
            'hasvk_always_bindless': {
                'label': "HASVK Bindless Descriptors:",
                'text': "Bindless descriptors in HASVK. Modern descriptor management technique that can improve performance on Intel GPUs.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['HASVK_ALWAYS_BINDLESS'],
                    'values': {'on': 'true'}
                }
            },
            'hasvk_userspace_relocs': {
                'label': "HASVK Userspace Relocations:",
                'text': "Userspace relocations in HASVK. Handles GPU memory address patching in userspace instead of kernel for reduced overhead on older Intel GPUs.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['HASVK_USERSPACE_RELOCS'],
                    'values': {'on': 'true'}
                }
            },
            'anv_sparse': {
                'label': "ANV Sparse Resources (Tiger Lake+):",
                'text': "Sparse resources in ANV (Tiger Lake+). Allows partial allocation of large textures to save memory.",
                'items': ["unset", "on (default)", "off"],
                'env_mapping': {
                    'var_names': ['ANV_SPARSE'],
                    'values': {'off': 'false'}
                }
            },
            'anv_sparse_implementation': {
                'label': "ANV Sparse Implementation (Lunar Lake+):",
                'text': "Sparse resource implementation in ANV (Lunar Lake+). TRTT is the older method, Xe is the newer hardware-accelerated approach.",
                'items': ["unset", "TRTT", "Xe (default)"],
                'env_mapping': {
                    'var_names': ['ANV_SPARSE_USE_TRTT'],
                    'values': {'TRTT': 'true'}
                }
            },
            'nvk_broken_driver': {
                'label': "NVK for Experimental/Untested GPUs:",
                'text': "Experimental NVK driver support for untested GPUs. Enables the open-source Vulkan driver on NVIDIA GPUs that lack official support; may be unstable.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['NVK_I_WANT_A_BROKEN_VULKAN_DRIVER'],
                    'values': {'on': 'true'}
                }
            }
        },
        "NVIDIA": {
            'nvidia_gl_vsync': {
                'label': "OpenGL Vsync:",
                'text': "OpenGL vertical synchronization.",
                'items': ["unset", "program decides (default)", "on", "off"],
                'env_mapping': {
                    'var_names': ['__GL_SYNC_TO_VBLANK'],
                    'values': {'on': '1', 'off': '0'}
                }
            },
            'nvidia_gl_gsync': {
                'label': "OpenGL G-SYNC:",
                'text': "OpenGL G-SYNC/Variable Refresh Rate (VRR). Adaptive sync, that eliminates tearing without the latency penalty of fixed vsync.",
                'items': ["unset", "program decides (default)", "on", "off"],
                'env_mapping': {
                    'var_names': ['__GL_VRR_ALLOWED', '__GL_GSYNC_ALLOWED'],
                    'values': {'on': '1', 'off': '0'}
                }
            },
            'nvidia_gl_thread_opt': {
                'label': "OpenGL Thread Optimizations:",
                'text': "Multi-threaded OpenGL command processing. Might improve or worsen OpenGL performance depending on the program being run.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['__GL_THREADED_OPTIMIZATIONS'],
                    'values': {'on': '1'}
                }
            },
            'nvidia_gl_yield': {
                'label': "OpenGL Yield Behavior:",
                'text': "NVIDIA driver yields CPU time during OpenGL operations. Controls how the driver waits for GPU, affecting CPU usage and responsiveness.",
                'items': ["unset", "call sched_yield() (default)", "never yield", "call usleep(0) to yield"],
                'env_mapping': {
                    'var_names': ['__GL_YIELD'],
                    'values': {'never yield': 'NOTHING', 'call usleep(0) to yield': 'USLEEP'}
                }
            },
            'nvidia_gl_texture_quality': {
                'label': "OpenGL Texture Quality:",
                'text': "Texture quality vs performance tradeoff in OpenGL. Quality uses better filtering, performance uses faster methods with potential visual degradation.",
                'items': ["unset", "program decides (default)", "quality", "mixed", "performance"],
                'env_mapping': {
                    'var_names': ['__GL_OpenGLImageSettings'],
                    'values': {'quality': '1', 'mixed': '2', 'performance': '3'}
                }
            },
            'nvidia_gl_fsaa': {
                'label': "OpenGL Full Scene Antialiasing:",
                'text': "Full scene anti-aliasing level in OpenGL. Reduces jagged edges using multisampling (ms) and coverage sampling (cs/ss) with significant performance cost at higher levels.",
                'items': [
                    "unset", "program decides (default)", "0 - off", "1 - 2x (2xms)", "5 - 4x (4xms)",
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
            'nvidia_gl_fxaa': {
                'label': "OpenGL FXAA:",
                'text': "Fast approximate anti-aliasing in OpenGL. Post-process AA that smooths edges with minimal performance cost but may blur textures. FXAA must first be enabled in NVIDIA Control Panel.",
                'items': ["unset", "on (default)", "off"],
                'env_mapping': {
                    'var_names': ['__GL_ALLOW_FXAA_USAGE'],
                    'values': {'off': '0'}
                }
            },
            'nvidia_gl_aniso': {
                'label': "OpenGL Anisotropic Filtering:",
                'text': "Anisotropic filtering level in OpenGL. Improves texture sharpness at oblique viewing angles; higher levels look better but impact performance.",
                'items': [
                    "unset", "program decides (default)", "0 - no anisotropic filtering",
                    "1 - 2x anisotropic filtering", "2 - 4x anisotropic filtering",
                    "3 - 8x anisotropic filtering", "4 - 16x anisotropic filtering"
                ],
                'env_mapping': {
                    'var_names': ['__GL_LOG_MAX_ANISO'],
                    'extract_prefix': True
                }
            },
            'nvidia_smooth_motion': {
                'label': "Smooth Motion (RTX 40 Series+):",
                'text': "Smooth motion feature (RTX 40 Series+). Optical flow frame interpolation that generates intermediate frames for smoother motion. Vulkan only.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['NVPRESENT_ENABLE_SMOOTH_MOTION'],
                    'values': {'on': '1'}
                }
            },
            'nvidia_max_prerendered_frames': {
                'label': "Maximum Pre-rendered Frames:",
                'text': "Maximum number of pre-rendered frames. Lower values reduce input lag but may hurt frame rate consistency; higher values do the opposite.",
                'items': ["unset", "program decides (default)"] + [str(i) for i in range(1, 5)],
                'env_mapping': {
                    'var_names': ['__GL_MaxFramesAllowed'],
                    'direct_value': True
                }
            },
            'nvidia_sharpen_denoising_enable': {
                'label': "Enable NVIDIA Image Sharpening and Denoising:",
                'text': "Enable NVIDIA Image Sharpening and Denoising. Post-processing filters that enhance image clarity and reduce noise artifacts.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['__GL_SHARPEN_ENABLE'],
                    'values': {'on': '1'}
                }
            },
            'nvidia_image_sharpening': {
                'label': "Image Sharpening:",
                'text': "Image sharpening. Enhances texture and edge definition; higher values increase sharpness but may introduce artifacts.",
                'items': ["unset", "program decides (default)"] + [str(i) for i in range(0, 101)],
                'env_mapping': {
                    'var_names': ['__GL_SHARPEN_VALUE'],
                    'direct_value': True
                }
            },
            'nvidia_image_denoising': {
                'label': "Image Denoising",
                'text': "Image denoising. Reduces film grain and noise; higher values preserve more texture detail but may keep more noise.",
                'items': ["unset", "program decides (default)"] + [str(i) for i in range(0, 101)],
                'env_mapping': {
                    'var_names': ['__GL_SHARPEN_IGNORE_FILM_GRAIN'],
                    'direct_value': True
                }
            },
            'nvidia_shader_cache': {
                'label': "Shader Cache:",
                'text': "Disk-based shader caching. Stores compiled shaders to disk to eliminate compilation stuttering on subsequent launches.",
                'items': ["unset", "on (default)", "off"],
                'env_mapping': {
                    'var_names': ['__GL_SHADER_DISK_CACHE'],
                    'values': {'off': '0'}
                }
            },
            'nvidia_shader_cache_size': {
                'label': "Shader Cache Size (GB):",
                'text': "Maximum size for the shader cache. Larger caches store more compiled shaders but consume more disk space.",
                'items': ["unset", "program decides (default)"] + [str(i) for i in range(1, 11)] + [str(i) for i in [25, 50, 75, 100]],
                'env_mapping': {
                    'var_names': ['__GL_SHADER_DISK_CACHE_SIZE'],
                    'convert_to_bytes': True
                }
            },
            'nvidia_glsl_ext_requirements': {
                'label': "Ignore GLSL Extensions Requirements:",
                'text': "Ignore GLSL extension requirements. Allows GLSL shaders to compile without proper #extension directives or compatibility profile declarations. Fixes shader compilation errors in some games.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['__GL_IGNORE_GLSL_EXT_REQS'],
                    'values': {'on': '1'}
                }
            },
            'nvidia_glx_unofficial_protocol': {
                'label': "Unofficial GLX Protocol:",
                'text': "Unofficial GLX protocol. Enables extensions that aren't part of the official GLX specification.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['__GL_ALLOW_UNOFFICIAL_PROTOCOL'],
                    'values': {'on': '1'}
                }
            },
            'nvidia_experimental_perf': {
                'label': "Experimental Performance Strategy:",
                'text': "Experimental GPU clock boost management. Allows the driver to more aggressively reduce GPU clocks after boost periods, potentially reducing power consumption.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['__GL_ExperimentalPerfStrategy'],
                    'values': {'on': '1'}
                }
            }
        },
        "RenderSelector": {
            'render_gl_device': {
                'label': "Select OpenGL Device:",
                'text': "OpenGL device to use.",
                'items': ["unset", "program decides (default)"]
            },
            'render_vk_device': {
                'label': "Select Vulkan Device:",
                'text': "Vulkan device to use.",
                'items': ["unset", "program decides (default)"]
            }
        },
        "MangoHud": {
            'mangohud_enable': {
                'label': "Enable MangoHud:",
                'text': "Enable MangoHud.",
                'items': ["unset", "on", "off (default)"]
            },
            'mangohud_display': {
                'label': "Display Elements:",
                'text': "Elements displayed in MangoHud overlay.",
                'items': ["unset", "program decides (default)", "no hud", "fps only", "horizontal", "extended", "detailed"],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'values': {'no hud': '0', 'fps only': '1', 'horizontal': '2', 'extended': '3', 'detailed': '4'},
                    'prefix': 'preset='
                }
            },
            'mangohud_gl_vsync': {
                'label': "OpenGL Vsync:",
                'text': "OpenGL vertical synchronization mode when using MangoHud.",
                'items': ["unset", "program decides (default)", "adaptive vsync", "on", "off"],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'values': {'adaptive vsync': '-1', 'on': '1', 'off': '0'},
                    'prefix': 'gl_vsync='
                }
            },
            'mangohud_vk_vsync': {
                'label': "Vulkan Vsync:",
                'text': "Vulkan vertical synchronization mode when using MangoHud.",
                'items': ["unset", "program decides (default)", "mailbox", "adaptive vsync", "on", "off"],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'values': {'mailbox': '2', 'adaptive vsync': '0', 'on': '3', 'off': '1'},
                    'prefix': 'vsync='
                }
            },
            'mangohud_fps_limit': {
                'label': "Fps Limit:",
                'text': "FPS limit when using MangoHud.",
                'items': ["unset", "program decides (default)", "unlimited", "10", "15", "20", "24", "25", "30", "35", "40", "45", "48", "50", "55", "60", "70", "72", "75", "85", "90", "100", "110", "120", "144", "165", "180", "200", "240", "280", "300", "360", "480"],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'values': {'unlimited': '0'},
                    'direct_value': True,
                    'prefix': 'fps_limit='
                }
            },
            'mangohud_fps_method': {
                'label': "Fps Limit Method:",
                'text': "MangoHud FPS limiting implementation.",
                'items': ["unset", "program decides (default)", "early - smoothest frametimes", "late - lowest latency"],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'values': {'early - smoothest frametimes': 'early', 'late - lowest latency': 'late'},
                    'prefix': 'fps_limit_method='
                }
            },
            'mangohud_texture_filter': {
                'label': "Texture Filtering:",
                'text': "Texture filtering method when using MangoHud. Vulkan Only.",
                'items': ["unset", "program decides (default)", "bicubic", "retro", "trilinear"],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'values': {'bicubic': 'bicubic', 'retro': 'retro', 'trilinear': 'trilinear'}
                }
            },
            'mangohud_mipmap_lod_bias': {
                'label': "Mipmap LOD Bias:",
                'text': "Mipmap level-of-detail bias when using MangoHud. Negative values sharpen textures, positive values blur them; affects performance and visual quality. Vulkan Only.",
                'items': ["unset", "program decides (default)"] + [str(i) for i in range(-16, 17)],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'direct_value': True,
                    'prefix': 'picmip='
                }
            },
            'mangohud_anisotropic_filtering': {
                'label': "Anisotropic Filtering:",
                'text': "Anisotropic filtering level when using MangoHud. Improves texture quality at angles; 16x is maximum quality with minimal modern GPU impact. Vulkan Only.",
                'items': ["unset", "program decides (default)"] + [str(i) for i in range(0, 17)],
                'env_mapping': {
                    'var_names': ['MANGOHUD_CONFIG'],
                    'direct_value': True,
                    'prefix': 'af='
                }
            }
        },
        "LSFrameGen": {
            'lsfg_enable': {
                'label': "Enable LSFG-VK:",
                'text': "Enable LSFG-VK. Vulkan Only.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['LSFG_LEGACY'],
                    'values': {'on': '1'}
                }
            },
            'lsfg_dll_path': {
                'label': "Lossless.dll Path:",
                'text': "Path to the Lossless Scaling frame generation DLL file (Lossless.dll).",
                'path': True,
                'env_mapping': {
                    'var_names': ['LSFG_DLL_PATH'],
                    'direct_value': True
                }
            },
            'lsfg_multiplier': {
                'label': "FPS Multiplier:",
                'text': "Frame generation multiplier. Generates additional frames between real frames.",
                'items': ["unset", "program decides (default)", "2", "3", "4"],
                'env_mapping': {
                    'var_names': ['LSFG_MULTIPLIER'],
                    'direct_value': True
                }
            },
            'lsfg_flow_scale': {
                'label': "Motion Estimation Quality:",
                'text': "Motion estimation quality. Lower values improve performance at the cost of quality.",
                'items': ["unset", "program decides (default)", "0.25", "0.50", "0.75", "1.0"],
                'env_mapping': {
                    'var_names': ['LSFG_FLOW_SCALE'],
                    'direct_value': True
                }
            },
            'lsfg_performance_mode': {
                'label': "Performance Mode:",
                'text': "Performance mode which reduces quality for higher frame rates.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['LSFG_PERFORMANCE_MODE'],
                    'values': {'on': '1'}
                }
            },
            'lsfg_hdr_mode': {
                'label': "HDR Mode:",
                'text': "HDR support in frame generation.",
                'items': ["unset", "on", "off (default)"],
                'env_mapping': {
                    'var_names': ['LSFG_HDR_MODE'],
                    'values': {'on': '1'}
                }
            },
            'lsfg_vk_present_mode': {
                'label': "Vulkan Vsync:",
                'text': "Vulkan vertical synchronization mode when using lsfg-vk.",
                'items': ["unset", "program decides (default)", "mailbox", "adaptive vsync", "on", "off"],
                'env_mapping': {
                    'var_names': ['LSFG_EXPERIMENTAL_PRESENT_MODE'],
                    'values': {'mailbox': 'mailbox', 'adaptive vsync': 'relaxed', 'on': 'fifo', 'off': 'immediate'}
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
    def get_available(program_name, search_flatpak):
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
        return GPULaunchManager.get_available("vulkaninfo", False)

    @staticmethod
    def get_available_glxinfo():
        """
        Check if glxinfo is available.
        """
        return GPULaunchManager.get_available("glxinfo", False)

    @staticmethod
    def get_available_mangohud():
        """
        Check if MangoHUD is available.
        """
        return GPULaunchManager.get_available("mangohud", True)

    @staticmethod
    def get_available_lsfg():
        """
        Check if lsfg-vk is available.
        """
        return GPULaunchManager.get_available("lsfg", True)

    @staticmethod
    def get_opengl_device_options():
        """
        Get available OpenGL device options from glxinfo.
        """
        devices = []
        device_map = {}

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
                device_map[name] = env_vars

            options = ["unset"] + list(fixed_options.keys())
            return options, device_map

        try:
            process = QProcess()
            WorkaroundManager.setup_clean_process(process)
            env = process.environment()
            env.append("__GLX_VENDOR_LIBRARY_NAME=nvidia")
            process.setEnvironment(env)
            process.start("glxinfo")

            if process.waitForFinished(10000):
                output = process.readAllStandardOutput().data().decode()
                for line in output.split('\n'):
                    if "OpenGL renderer string:" in line:
                        device_name = line.split(':', 1)[1].strip()
                        device_name = GPULaunchManager.truncate_name(device_name)
                        device_name = device_name.lower()

                        if device_name not in device_map:
                            devices.append(device_name)
                            device_map[device_name] = {"__GLX_VENDOR_LIBRARY_NAME": "nvidia"}
                        break
        except Exception:
            pass

        index = 0
        while index < 5:
            try:
                process = QProcess()
                WorkaroundManager.setup_clean_process(process)
                env = process.environment()
                env.append("__GLX_VENDOR_LIBRARY_NAME=mesa")
                env.append(f"DRI_PRIME={index}")
                process.setEnvironment(env)
                process.start("glxinfo")

                if process.waitForFinished(10000):
                    output = process.readAllStandardOutput().data().decode()

                    renderer_found = False
                    for line in output.split('\n'):
                        if "OpenGL renderer string:" in line:
                            device_name = line.split(':', 1)[1].strip()
                            device_name = GPULaunchManager.truncate_name(device_name)
                            device_name = device_name.lower()

                            if "llvmpipe" in device_name or device_name in device_map:
                                break

                            devices.append(device_name)
                            device_map[device_name] = {
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
            device_map[name] = env_vars

        options = devices + list(fixed_options.keys())

        return options, device_map

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
    def create_gpu_settings_tabs():
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
        mangohud_tab, mangohud_widgets = GPULaunchManager.create_category_tab("MangoHud")
        ls_frame_gen_tab, ls_frame_gen_widgets = GPULaunchManager.create_category_tab("LSFrameGen")

        gpu_subtabs.addTab(mesa_tab, "Mesa")
        gpu_subtabs.addTab(nvidia_tab, "NVIDIA (Proprietary)")
        gpu_subtabs.addTab(render_selector_tab, "Render Selector")
        gpu_subtabs.addTab(mangohud_tab, "MangoHud")
        gpu_subtabs.addTab(ls_frame_gen_tab, "LS Frame Gen")
        gpu_layout.addWidget(gpu_subtabs)

        widgets = {
            'Mesa': mesa_widgets,
            'NVIDIA': nvidia_widgets,
            'RenderSelector': render_selector_widgets,
            'MangoHud': mangohud_widgets,
            'LSFrameGen': ls_frame_gen_widgets
        }

        return gpu_tab, widgets

    @staticmethod
    def create_path_widget(setting_info):
        """
        Create a path selection widget with browse and clear buttons.
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        path_input = QLineEdit()
        path_input.setPlaceholderText("No file selected")
        path_input.setReadOnly(True)
        path_input.setToolTip(setting_info['text'])
        layout.addWidget(path_input)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addStretch(1)

        browse_button = QPushButton("...")
        browse_button.clicked.connect(lambda: GPULaunchManager.browse_file(path_input))
        button_layout.addWidget(browse_button)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(lambda: path_input.clear())
        button_layout.addWidget(clear_button)

        layout.addLayout(button_layout)

        return container, path_input, browse_button, clear_button

    @staticmethod
    def browse_file(path_input):
        """
        Open a file dialog to select a file and set the path to the input field.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select File",
            "",
            "All Files (*)"
        )
        if file_path:
            path_input.setText(file_path)

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

            if setting_info.get('path', False):
                path_widget, path_input, browse_button, clear_button = GPULaunchManager.create_path_widget(setting_info)
                widgets[setting_key] = path_input
                widgets[f"{setting_key}_browse"] = browse_button
                widgets[f"{setting_key}_clear"] = clear_button
                layout.addWidget(label)
                layout.addWidget(path_widget)
            else:
                widgets[setting_key] = QComboBox()
                widgets[setting_key].addItems(setting_info['items'])
                widgets[setting_key].setCurrentText("unset")
                widgets[setting_key].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                widgets[setting_key].setToolTip(setting_info['text'])
                layout.addWidget(label)
                layout.addWidget(widgets[setting_key])

            scroll_layout.addLayout(layout)

        if category_name == "RenderSelector":
            if GPULaunchManager.get_available_glxinfo():
                opengl_devices, device_map = GPULaunchManager.get_opengl_device_options()
                default_items = GPULaunchManager.GPU_SETTINGS_CATEGORIES["RenderSelector"]['render_gl_device']['items']
                opengl_options = default_items + opengl_devices
                widgets['render_gl_device'].clear()
                widgets['render_gl_device'].addItems(opengl_options)
                widgets['render_gl_device'].device_map = device_map
            else:
                widgets['render_gl_device'].setEnabled(False)
                widgets['render_gl_device'].setToolTip("glxinfo not available - OpenGL device selection disabled")

            if GPULaunchManager.get_available_vulkaninfo():
                vulkan_devices, device_map = GPULaunchManager.get_vulkan_device_options()
                default_items = GPULaunchManager.GPU_SETTINGS_CATEGORIES["RenderSelector"]['render_vk_device']['items']
                vulkan_options = default_items + vulkan_devices
                widgets['render_vk_device'].clear()
                widgets['render_vk_device'].addItems(vulkan_options)
                widgets['render_vk_device'].device_map = device_map
            else:
                widgets['render_vk_device'].setEnabled(False)
                widgets['render_vk_device'].setToolTip("vulkaninfo not available - Vulkan device selection disabled")

        if category_name == "MangoHud":
            if not GPULaunchManager.get_available_mangohud():
                for widget_key, widget in widgets.items():
                    if hasattr(widget, 'setEnabled'):
                        widget.setEnabled(False)
                        widget.setToolTip("MangoHUD not available - MangoHUD options disabled")

        if category_name == "LSFrameGen":
            if not GPULaunchManager.get_available_lsfg():
                for widget_key, widget in widgets.items():
                    if hasattr(widget, 'setEnabled'):
                        widget.setEnabled(False)
                        widget.setToolTip("lsfg-vk not available - lsfg-vk options disabled")
                    elif isinstance(widget, QLineEdit):
                        widget.setEnabled(False)
                        widget.setToolTip("lsfg-vk not available - lsfg-vk options disabled")
                        browse_key = f"{widget_key}_browse"
                        clear_key = f"{widget_key}_clear"
                        if browse_key in widgets:
                            widgets[browse_key].setEnabled(False)
                            widgets[browse_key].setToolTip("lsfg-vk not available - All lsfg-vk options disabled")
                        if clear_key in widgets:
                            widgets[clear_key].setEnabled(False)
                            widgets[clear_key].setToolTip("lsfg-vk not available - All lsfg-vk options disabled")

        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        GPULaunchManager.create_gpu_apply_button(main_layout, widgets, f"{category_name.lower()}_apply_button")

        return tab, widgets

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

        launch_options_input = QLineEdit()
        launch_options_input.setPlaceholderText("enter launch options")
        launch_options_input.setToolTip("Additional programs and environment variables to launch with the game.\nExample: gamemoderun PROTON_USE_WINED3D=1")
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
        unset_vars = []

        if category_name == "MangoHud":
            mangohud_parts = []
            has_non_default_settings = False

            for setting_key, widget in widgets.items():
                if setting_key.endswith('_apply_button') or setting_key.endswith('_browse') or setting_key.endswith('_clear'):
                    continue

                if setting_key == 'mangohud_enable':
                    continue

                setting_info = GPULaunchManager.GPU_SETTINGS_CATEGORIES[category_name][setting_key]

                if setting_info.get('path', False):
                    value = widget.text().strip()
                    if not value:
                        continue
                else:
                    value = widget.currentText()
                    if value == "unset":
                        continue
                    elif "(default)" in value:
                        continue
                    else:
                        has_non_default_settings = True

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

            if mangohud_parts and has_non_default_settings:
                config_value = ','.join(mangohud_parts)
                env_vars.append(f'MANGOHUD_CONFIG={config_value}')
            elif not has_non_default_settings:
                unset_vars.append('MANGOHUD_CONFIG')
        else:
            for setting_key, widget in widgets.items():
                if setting_key.endswith('_apply_button') or setting_key.endswith('_browse') or setting_key.endswith('_clear'):
                    continue

                setting_info = GPULaunchManager.GPU_SETTINGS_CATEGORIES[category_name][setting_key]

                if setting_info.get('path', False):
                    value = widget.text().strip()
                    if not value:
                        continue
                else:
                    value = widget.currentText()
                    if value == "unset":
                        continue
                    elif "(default)" in value and 'env_mapping' in setting_info:
                        mapping = setting_info['env_mapping']
                        unset_vars.extend(mapping['var_names'])
                        continue

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

        return env_vars, unset_vars

    @staticmethod
    def generate_render_selector_env_vars(render_widgets):
        """
        Generate environment variables for render selector settings.
        """
        env_vars = []
        unset_vars = []

        if 'render_gl_device' in render_widgets:
            selected = render_widgets['render_gl_device'].currentText()
            if "(default)" in selected:
                unset_vars.extend(["__GLX_VENDOR_LIBRARY_NAME", "LIBGL_ALWAYS_SOFTWARE", "MESA_LOADER_DRIVER_OVERRIDE", "LIBGL_KOPPER_DRI2", "DRI_PRIME"])
            elif selected != "unset":
                device_map = getattr(render_widgets['render_gl_device'], 'device_map', {})
                env_dict = device_map.get(selected, {})
                for var, value in env_dict.items():
                    env_vars.append(f"{var}={value}")

        if 'render_vk_device' in render_widgets:
            vulkan_selection = render_widgets['render_vk_device'].currentText()
            if "(default)" in vulkan_selection:
                unset_vars.extend(["MESA_VK_DEVICE_SELECT", "VK_DRIVER_FILES", "VK_ICD_FILENAMES"])
            elif vulkan_selection != "unset":
                device_map = getattr(render_widgets['render_vk_device'], 'device_map', {})
                device_key = device_map.get(vulkan_selection)
                if device_key:
                    env_vars.append(f"MESA_VK_DEVICE_SELECT={device_key}!")

        return env_vars, unset_vars

    @staticmethod
    def write_settings_file(mesa_widgets, nvidia_widgets, render_selector_widgets, mangohud_widgets, ls_frame_gen_widgets, launch_options_widgets):
        """
        Write all settings to a temporary configuration file.
        """
        mesa_env_vars, mesa_unset = GPULaunchManager.generate_env_vars(mesa_widgets, "Mesa")
        nvidia_env_vars, nvidia_unset = GPULaunchManager.generate_env_vars(nvidia_widgets, "NVIDIA")
        render_env_vars, render_unset = GPULaunchManager.generate_render_selector_env_vars(render_selector_widgets)
        mangohud_env_vars, mangohud_unset = GPULaunchManager.generate_env_vars(mangohud_widgets, "MangoHud")
        ls_frame_gen_env_vars, lsfg_unset = GPULaunchManager.generate_env_vars(ls_frame_gen_widgets, "LSFrameGen")

        launch_options = ""
        if 'launch_options_input' in launch_options_widgets:
            launch_options = launch_options_widgets['launch_options_input'].text().strip()

        mangohud_enabled = ('mangohud_enable' in mangohud_widgets and mangohud_widgets['mangohud_enable'].currentText() == "on")

        if mangohud_enabled and launch_options:
            launch_options = f"mangohud {launch_options}"
        elif mangohud_enabled and not launch_options:
            launch_options = "mangohud"

        all_env_vars = mesa_env_vars + nvidia_env_vars + render_env_vars + mangohud_env_vars + ls_frame_gen_env_vars
        all_unset_vars = mesa_unset + nvidia_unset + render_unset + mangohud_unset + lsfg_unset

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as temp_file:
            for env_var in all_env_vars:
                temp_file.write(f"{env_var}\n")

            for unset_var in all_unset_vars:
                temp_file.write(f"unset:{unset_var}\n")

            if launch_options:
                temp_file.write(f"launch_options={launch_options}\n")

            return temp_file.name
