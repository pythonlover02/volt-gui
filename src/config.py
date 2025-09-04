import os
import configparser
from pathlib import Path
from kernel import KernelManager


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
    def save_config(cpu_widgets, gpu_widgets, kernel_widgets, disk_widgets, profile_name="Default"):
        """
        Save all widget settings to the configuration file.
        """
        config = configparser.ConfigParser()
        
        config['CPU'] = {
            'governor': cpu_widgets['gov_combo'].currentText(),
            'max_freq': cpu_widgets['max_freq_combo'].currentText(),
            'min_freq': cpu_widgets['min_freq_combo'].currentText(),
            'scheduler': cpu_widgets['sched_combo'].currentText()
        }
        
        config['Mesa'] = {}
        for widget_key, widget in gpu_widgets['mesa'].items():
            if hasattr(widget, 'currentText') and widget_key != 'mesa_apply_button':
                config['Mesa'][widget_key] = widget.currentText()
        
        config['NVIDIA'] = {}
        for widget_key, widget in gpu_widgets['nvidia'].items():
            if hasattr(widget, 'currentText') and widget_key != 'nvidia_apply_button':
                config['NVIDIA'][widget_key] = widget.currentText()
        
        config['RenderSelector'] = {}
        for widget_key, widget in gpu_widgets['render_selector'].items():
            if hasattr(widget, 'currentText') and widget_key != 'render_selector_apply_button':
                config['RenderSelector'][widget_key] = widget.currentText()
        
        config['RenderPipeline'] = {}
        for widget_key, widget in gpu_widgets['render_pipeline'].items():
            if hasattr(widget, 'currentText') and widget_key != 'render_pipeline_apply_button':
                config['RenderPipeline'][widget_key] = widget.currentText()
            
        if 'launch_options_input' in gpu_widgets['launch_options']:
            launch_options = gpu_widgets['launch_options']['launch_options_input'].text().replace('%', '%%')
            config['LaunchOptions'] = {'launch_options': launch_options}
            
        if kernel_widgets:
            kernel_config = {}
            for category in KernelManager.KERNEL_SETTINGS_CATEGORIES.values():
                for setting_name in category.keys():
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
    def load_config(cpu_widgets, gpu_widgets, kernel_widgets, disk_widgets, profile_name="Default"):
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
            cpu_widgets['max_freq_combo'].setCurrentText(config['CPU'].get('max_freq', 'unset'))
            cpu_widgets['min_freq_combo'].setCurrentText(config['CPU'].get('min_freq', 'unset'))
            cpu_widgets['sched_combo'].setCurrentText(config['CPU'].get('scheduler', 'unset'))
        
        if 'Mesa' in config and 'mesa' in gpu_widgets:
            for widget_key, value in config['Mesa'].items():
                if widget_key in gpu_widgets['mesa'] and hasattr(gpu_widgets['mesa'][widget_key], 'setCurrentText'):
                    gpu_widgets['mesa'][widget_key].setCurrentText(value)
        
        if 'NVIDIA' in config and 'nvidia' in gpu_widgets:
            for widget_key, value in config['NVIDIA'].items():
                if widget_key in gpu_widgets['nvidia'] and hasattr(gpu_widgets['nvidia'][widget_key], 'setCurrentText'):
                    gpu_widgets['nvidia'][widget_key].setCurrentText(value)
        
        if 'RenderSelector' in config and 'render_selector' in gpu_widgets:
            for widget_key, value in config['RenderSelector'].items():
                if widget_key in gpu_widgets['render_selector'] and hasattr(gpu_widgets['render_selector'][widget_key], 'setCurrentText'):
                    gpu_widgets['render_selector'][widget_key].setCurrentText(value)
    
        if 'RenderPipeline' in config and 'render_pipeline' in gpu_widgets:
            for widget_key, value in config['RenderPipeline'].items():
                if widget_key in gpu_widgets['render_pipeline'] and hasattr(gpu_widgets['render_pipeline'][widget_key], 'setCurrentText'):
                    gpu_widgets['render_pipeline'][widget_key].setCurrentText(value)
                
        if 'LaunchOptions' in config and 'launch_options' in gpu_widgets and 'launch_options_input' in gpu_widgets['launch_options']:
            launch_options = config['LaunchOptions'].get('launch_options', '').replace('%%', '%')
            gpu_widgets['launch_options']['launch_options_input'].setText(launch_options)
                
        if kernel_widgets and 'Kernel' in config:
            for setting_name, value in config['Kernel'].items():
                for category in KernelManager.KERNEL_SETTINGS_CATEGORIES.values():
                    if setting_name in category:
                        input_widget = kernel_widgets[f'{setting_name}_input']
                        input_widget.setText(value)
                        break
        
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