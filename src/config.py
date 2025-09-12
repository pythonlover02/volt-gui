import os, configparser
from pathlib import Path
from kernel import KernelManager
from cpu import CPUManager
from disk import DiskManager
from gpu_launch import GPULaunchManager

class ConfigManager:

    @staticmethod
    def get_config_path(profile_name="Default"):
        """
        Get the configuration file path for a given profile.
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
        Get a list of all available configuration profiles.
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
        Save configuration settings to a profile file.
        """
        config = configparser.ConfigParser()

        cpu_config = {}
        for setting_key in CPUManager.CPU_SETTINGS.keys():
            if setting_key in cpu_widgets and hasattr(cpu_widgets[setting_key], 'currentText'):
                cpu_config[setting_key] = cpu_widgets[setting_key].currentText()
        if cpu_config:
            config['CPU'] = cpu_config

        gpu_config = {}
        for setting_key in GPULaunchManager.GPU_SETTINGS.keys():
            for category_name, category_widgets in gpu_widgets.items():
                if category_name != 'LaunchOptions' and setting_key in category_widgets:
                    if hasattr(category_widgets[setting_key], 'currentText'):
                        gpu_config[setting_key] = category_widgets[setting_key].currentText()
                    break
        if gpu_config:
            config['GPU'] = gpu_config

        if 'LaunchOptions' in gpu_widgets and 'launch_options_input' in gpu_widgets['LaunchOptions']:
            launch_options = gpu_widgets['LaunchOptions']['launch_options_input'].text().replace('%', '%%')
            config['LaunchOptions'] = {'launch_options': launch_options}

        kernel_config = {}
        for setting_key in KernelManager.KERNEL_SETTINGS.keys():
            widget_key = f'{setting_key}_input'
            if widget_key in kernel_widgets:
                value = kernel_widgets[widget_key].text().strip()
                if value:
                    kernel_config[setting_key] = value
        if kernel_config:
            config['Kernel'] = kernel_config

        disk_config = {}
        for disk_name, disk_widgets_dict in disk_widgets['disk_settings'].items():
            for setting_key in DiskManager.DISK_SETTINGS.keys():
                if setting_key in disk_widgets_dict:
                    disk_config[f"{disk_name}_{setting_key}"] = disk_widgets_dict[setting_key].currentText()
        if disk_config:
            config['Disk'] = disk_config

        with open(ConfigManager.get_config_path(profile_name), 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def load_config(cpu_widgets, gpu_widgets, kernel_widgets, disk_widgets, profile_name="Default"):
        """
        Load configuration settings from a profile file.
        """
        config = configparser.ConfigParser()
        config_path = ConfigManager.get_config_path(profile_name)

        if not config_path.exists():
            return False

        config.read(config_path)

        if 'CPU' in config:
            for setting_key in CPUManager.CPU_SETTINGS.keys():
                if setting_key in config['CPU'] and setting_key in cpu_widgets:
                    cpu_widgets[setting_key].setCurrentText(config['CPU'][setting_key])

        if 'GPU' in config:
            for setting_key in GPULaunchManager.GPU_SETTINGS.keys():
                if setting_key in config['GPU']:
                    for category_name, category_widgets in gpu_widgets.items():
                        if category_name != 'LaunchOptions' and setting_key in category_widgets:
                            category_widgets[setting_key].setCurrentText(config['GPU'][setting_key])
                            break

        if 'LaunchOptions' in config and 'LaunchOptions' in gpu_widgets and 'launch_options_input' in gpu_widgets['LaunchOptions']:
            launch_options = config['LaunchOptions'].get('launch_options', '').replace('%%', '%')
            gpu_widgets['LaunchOptions']['launch_options_input'].setText(launch_options)

        if kernel_widgets and 'Kernel' in config:
            for setting_key in KernelManager.KERNEL_SETTINGS.keys():
                if setting_key in config['Kernel']:
                    widget_key = f'{setting_key}_input'
                    if widget_key in kernel_widgets:
                        kernel_widgets[widget_key].setText(config['Kernel'][setting_key])

        if disk_widgets and 'disk_settings' in disk_widgets and 'Disk' in config:
            for config_key, value in config['Disk'].items():
                if '_' in config_key:
                    disk_name, setting_key = config_key.rsplit('_', 1)
                    if disk_name in disk_widgets['disk_settings'] and setting_key in disk_widgets['disk_settings'][disk_name]:
                        disk_widgets['disk_settings'][disk_name][setting_key].setCurrentText(value)

        return True

    @staticmethod
    def delete_profile(profile_name):
        """
        Delete a configuration profile. Cannot delete the Default profile.
        """
        if profile_name == "Default":
            return False

        config_path = ConfigManager.get_config_path(profile_name)
        if config_path.exists():
            config_path.unlink()
            return True

        return False
