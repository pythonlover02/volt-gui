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
    def get_config_path():
        """
        Get the path to the configuration file.
        Returns:
            Path: Path object pointing to the config file
        """
        config_dir = Path(os.path.expanduser("~/.config/volt-gui"))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "volt-config.ini"
    
    @staticmethod
    def save_settings(cpu_widgets, gpu_manager, kernel_widgets, disk_widgets):
        """
        Save current settings to the configuration file.
        Args:
            cpu_widgets: Dictionary of CPU settings widgets
            gpu_manager: GPULaunchManager instance
            kernel_widgets: Dictionary of kernel settings widgets
            disk_widgets: Dictionary of disk settings widgets
        """
        config = configparser.ConfigParser()
        
        # Save CPU settings
        config['CPU'] = {
            'governor': cpu_widgets['gov_combo'].currentText(),
            'scheduler': cpu_widgets['sched_combo'].currentText()
        }
        
        # Save Mesa settings
        config['Mesa'] = {}
        for widget_key, widget in gpu_manager.mesa_widgets.items():
            if hasattr(widget, 'currentText'):
                config['Mesa'][widget_key] = widget.currentText()
        
        # Save NVIDIA settings
        config['NVIDIA'] = {}
        for widget_key, widget in gpu_manager.nvidia_widgets.items():
            if hasattr(widget, 'currentText'):
                config['NVIDIA'][widget_key] = widget.currentText()
        
        # Save render selector settings
        config['RenderSelector'] = {}
        for widget_key, widget in gpu_manager.render_selector_widgets.items():
            if hasattr(widget, 'currentText'):
                config['RenderSelector'][widget_key] = widget.currentText()
            
        # Save launch options
        if 'launch_options_input' in gpu_manager.launch_options_widgets:
            launch_options = gpu_manager.launch_options_widgets['launch_options_input'].text().replace('%', '%%')
            config['LaunchOptions'] = {'launch_options': launch_options}
            
        # Save kernel settings if provided
        if kernel_widgets:
            kernel_settings = {}
            # Handle all kernel settings from the unified dictionary
            for setting_name in KernelManager.KERNEL_SETTINGS.keys():
                value = kernel_widgets[f'{setting_name}_input'].text().strip()
                if value:
                    kernel_settings[setting_name] = value
            if kernel_settings:
                config['Kernel'] = kernel_settings
        
        # Save disk settings if provided
        if disk_widgets:
            disk_settings = {}
            # Save disk scheduler settings
            for disk_id, scheduler_combo in disk_widgets.items():
                if disk_id.endswith('_scheduler') and hasattr(scheduler_combo, 'currentText'):
                    disk_name = disk_id.replace('_scheduler', '')
                    disk_settings[disk_name] = scheduler_combo.currentText()
            if disk_settings:
                config['Disk'] = disk_settings
        
        # Write config to file
        with open(ConfigManager.get_config_path(), 'w') as configfile:
            config.write(configfile)
    
    @staticmethod
    def load_settings(cpu_widgets, gpu_manager, kernel_widgets, disk_widgets):
        """
        Load settings from the configuration file.
        Args:
            cpu_widgets: Dictionary of CPU settings widgets to update
            gpu_manager: GPULaunchManager instance
            kernel_widgets: Dictionary of kernel settings widgets to update
            disk_widgets: Dictionary of disk settings widgets to update
        Returns:
            bool: True if settings were loaded successfully, False otherwise
        """
        config = configparser.ConfigParser()
        config_path = ConfigManager.get_config_path()
        
        if not config_path.exists():
            return False
        
        config.read(config_path)
        
        # Load CPU settings
        if 'CPU' in config:
            cpu_widgets['gov_combo'].setCurrentText(config['CPU'].get('governor', 'unset'))
            cpu_widgets['sched_combo'].setCurrentText(config['CPU'].get('scheduler', 'unset'))
        
        # Load Mesa settings
        if 'Mesa' in config:
            for widget_key, value in config['Mesa'].items():
                if widget_key in gpu_manager.mesa_widgets and hasattr(gpu_manager.mesa_widgets[widget_key], 'setCurrentText'):
                    gpu_manager.mesa_widgets[widget_key].setCurrentText(value)
        
        # Load NVIDIA settings
        if 'NVIDIA' in config:
            for widget_key, value in config['NVIDIA'].items():
                if widget_key in gpu_manager.nvidia_widgets and hasattr(gpu_manager.nvidia_widgets[widget_key], 'setCurrentText'):
                    gpu_manager.nvidia_widgets[widget_key].setCurrentText(value)
        
        # Load render selector settings
        if 'RenderSelector' in config:
            for widget_key, value in config['RenderSelector'].items():
                if widget_key in gpu_manager.render_selector_widgets and hasattr(gpu_manager.render_selector_widgets[widget_key], 'setCurrentText'):
                    gpu_manager.render_selector_widgets[widget_key].setCurrentText(value)
                
        # Load launch options
        if 'LaunchOptions' in config and 'launch_options_input' in gpu_manager.launch_options_widgets:
            launch_options = config['LaunchOptions'].get('launch_options', '').replace('%%', '%')
            gpu_manager.launch_options_widgets['launch_options_input'].setText(launch_options)
                
        # Load kernel settings
        if kernel_widgets and 'Kernel' in config:
            for setting_name, value in config['Kernel'].items():
                # Check if the setting exists in the unified kernel settings
                if setting_name in KernelManager.KERNEL_SETTINGS:
                    input_widget = kernel_widgets[f'{setting_name}_input']
                    input_widget.setText(value)
        
        # Load disk settings
        if disk_widgets and 'Disk' in config:
            for disk_name, scheduler in config['Disk'].items():
                scheduler_widget_key = f'{disk_name}_scheduler'
                if scheduler_widget_key in disk_widgets and hasattr(disk_widgets[scheduler_widget_key], 'setCurrentText'):
                    disk_widgets[scheduler_widget_key].setCurrentText(scheduler)
        
        return True