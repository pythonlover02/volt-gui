import os
import configparser
from pathlib import Path
from kernel import KernelManager
from disk import DiskManager


class ConfigManager:
    """
    Handles saving and loading of application configuration settings.
    """
    
    @staticmethod
    def get_config_path(profile_name="Default"):
        """
        Get the configuration file path, creating directories if needed.
        """
        config_dir = Path(os.path.expanduser("~/.config/volt-gui"))
        config_dir.mkdir(parents=True, exist_ok=True)
        if profile_name == "Default":
            return config_dir / "volt-config.ini"
        else:
            return config_dir / f"volt-config-{profile_name}.ini"
    
    @staticmethod
    def get_available_profiles():
        """
        Get list of available profile names.
        """
        config_dir = Path(os.path.expanduser("~/.config/volt-gui"))
        profiles = ["Default"]
        
        if config_dir.exists():
            for config_file in config_dir.glob("volt-config-*.ini"):
                profile_name = config_file.stem.replace("volt-config-", "")
                profiles.append(profile_name)
        
        return profiles
    
    @staticmethod
    def save_config(cpu_widgets, gpu_manager, kernel_widgets, disk_widgets, profile_name="Default"):
        """
        Save all widget settings to the configuration file.
        """
        config = configparser.ConfigParser()
        
        config['CPU'] = {
            'governor': cpu_widgets['gov_combo'].currentText(),
            'scheduler': cpu_widgets['sched_combo'].currentText()
        }
        
        config['Mesa'] = {}
        for widget_key, widget in gpu_manager.mesa_widgets.items():
            if hasattr(widget, 'currentText') and widget_key != 'mesa_apply_button':
                config['Mesa'][widget_key] = widget.currentText()
        
        config['NVIDIA'] = {}
        for widget_key, widget in gpu_manager.nvidia_widgets.items():
            if hasattr(widget, 'currentText') and widget_key != 'nvidia_apply_button':
                config['NVIDIA'][widget_key] = widget.currentText()
        
        config['RenderSelector'] = {}
        for widget_key, widget in gpu_manager.render_selector_widgets.items():
            if hasattr(widget, 'currentText') and widget_key != 'render_selector_apply_button':
                config['RenderSelector'][widget_key] = widget.currentText()
        
        config['FrameControl'] = {}
        for widget_key, widget in gpu_manager.frame_control_widgets.items():
            if hasattr(widget, 'currentText') and widget_key != 'frame_control_apply_button':
                config['FrameControl'][widget_key] = widget.currentText()
            
        if 'launch_options_input' in gpu_manager.launch_options_widgets:
            launch_options = gpu_manager.launch_options_widgets['launch_options_input'].text().replace('%', '%%')
            config['LaunchOptions'] = {'launch_options': launch_options}
            
        if kernel_widgets:
            kernel_config = {}
            for setting_name in KernelManager.KERNEL_SETTINGS.keys():
                value = kernel_widgets[f'{setting_name}_input'].text().strip()
                if value:
                    kernel_config[setting_name] = value
            if kernel_config:
                config['Kernel'] = kernel_config
        
        if disk_widgets and 'disk_combos' in disk_widgets:
            disk_config = {}
            for disk_name, scheduler_combo in disk_widgets['disk_combos'].items():
                disk_config[disk_name] = scheduler_combo.currentText()
            if disk_config:
                config['Disk'] = disk_config
        
        with open(ConfigManager.get_config_path(profile_name), 'w') as configfile:
            config.write(configfile)
    
    @staticmethod
    def load_config(cpu_widgets, gpu_manager, kernel_widgets, disk_widgets, profile_name="Default"):
        """
        Load settings from configuration file and apply to widgets.
        """
        config = configparser.ConfigParser()
        config_path = ConfigManager.get_config_path(profile_name)
        
        if not config_path.exists():
            return False
        
        config.read(config_path)
        
        if 'CPU' in config:
            cpu_widgets['gov_combo'].setCurrentText(config['CPU'].get('governor', 'unset'))
            cpu_widgets['sched_combo'].setCurrentText(config['CPU'].get('scheduler', 'unset'))
        
        if 'Mesa' in config:
            for widget_key, value in config['Mesa'].items():
                if widget_key in gpu_manager.mesa_widgets and hasattr(gpu_manager.mesa_widgets[widget_key], 'setCurrentText'):
                    gpu_manager.mesa_widgets[widget_key].setCurrentText(value)
        
        if 'NVIDIA' in config:
            for widget_key, value in config['NVIDIA'].items():
                if widget_key in gpu_manager.nvidia_widgets and hasattr(gpu_manager.nvidia_widgets[widget_key], 'setCurrentText'):
                    gpu_manager.nvidia_widgets[widget_key].setCurrentText(value)
        
        if 'RenderSelector' in config:
            for widget_key, value in config['RenderSelector'].items():
                if widget_key in gpu_manager.render_selector_widgets and hasattr(gpu_manager.render_selector_widgets[widget_key], 'setCurrentText'):
                    gpu_manager.render_selector_widgets[widget_key].setCurrentText(value)
    
        if 'FrameControl' in config:
            for widget_key, value in config['FrameControl'].items():
                if widget_key in gpu_manager.frame_control_widgets and hasattr(gpu_manager.frame_control_widgets[widget_key], 'setCurrentText'):
                    gpu_manager.frame_control_widgets[widget_key].setCurrentText(value)
                
        if 'LaunchOptions' in config and 'launch_options_input' in gpu_manager.launch_options_widgets:
            launch_options = config['LaunchOptions'].get('launch_options', '').replace('%%', '%')
            gpu_manager.launch_options_widgets['launch_options_input'].setText(launch_options)
                
        if kernel_widgets and 'Kernel' in config:
            for setting_name, value in config['Kernel'].items():
                if setting_name in KernelManager.KERNEL_SETTINGS:
                    input_widget = kernel_widgets[f'{setting_name}_input']
                    input_widget.setText(value)
        
        if disk_widgets and 'disk_combos' in disk_widgets and 'Disk' in config:
            for disk_name, scheduler in config['Disk'].items():
                if disk_name in disk_widgets['disk_combos']:
                    disk_widgets['disk_combos'][disk_name].setCurrentText(scheduler)
        
        return True
    
    @staticmethod
    def delete_profile(profile_name):
        """
        Delete a profile configuration file.
        """
        if profile_name == "Default":
            return False
        
        config_path = ConfigManager.get_config_path(profile_name)
        if config_path.exists():
            config_path.unlink()
            return True
        
        return False

    @staticmethod
    def save_current_profile_preference(profile_name):
        """
        Save the currently selected profile as the last used profile.
        """
        config_dir = Path(os.path.expanduser("~/.config/volt-gui"))
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_path = config_dir / "volt-session.ini"
        config = configparser.ConfigParser()
        
        if config_path.exists():
            try:
                config.read(config_path)
            except:
                pass
        
        if not config.has_section('Session'):
            config.add_section('Session')
        
        config.set('Session', 'last_profile', profile_name)
        
        try:
            with open(config_path, 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"Warning: Failed to save session config: {e}")

    @staticmethod
    def load_current_profile_preference():
        """
        Load the last used profile from session config.
        """
        config_path = Path(os.path.expanduser("~/.config/volt-gui/volt-session.ini"))
        
        if not config_path.exists():
            return "Default"
        
        config = configparser.ConfigParser()
        try:
            config.read(config_path)
            if config.has_section('Session') and config.has_option('Session', 'last_profile'):
                last_profile = config.get('Session', 'last_profile')
                available_profiles = ConfigManager.get_available_profiles()
                if last_profile in available_profiles:
                    return last_profile
        except Exception as e:
            print(f"Warning: Failed to load session config: {e}")
        
        return "Default"

    @staticmethod
    def load_options_settings():
        """
        Load options settings from configuration file.
        """
        options_path = Path(os.path.expanduser("~/.config/volt-gui/volt-options.ini"))
        use_system_tray = True
        start_minimized = False

        if not options_path.exists():
            return use_system_tray, start_minimized

        config = configparser.ConfigParser()
        try:
            config.read(options_path)

            if 'SystemTray' in config and 'run_in_tray' in config['SystemTray']:
                use_system_tray = config['SystemTray']['run_in_tray'] == 'enable'

            if 'StartupBehavior' in config and 'start_minimized' in config['StartupBehavior']:
                if use_system_tray:
                    start_minimized = config['StartupBehavior'].get('start_minimized', 'disable') == 'enable'
                else:
                    start_minimized = False

        except Exception as e:
            print(f"Warning: Failed to load options settings: {e}")

        return use_system_tray, start_minimized