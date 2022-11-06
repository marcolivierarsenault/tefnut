"""Config manager for the application"""
import logging
from dynaconf import Dynaconf, loaders

logger = logging.getLogger("main")


class SettingLoader:
    """Setting loader access through. Use this to access logging"""
    def __init__(self, file_path='settings.toml'):
        self.file_path = file_path
        self.setting_obj = Dynaconf(
                                envvar_prefix="DYNACONF",
                                settings_files=[file_path]
                            )

    def save_config(self):
        """Save config file, after they are updated programatically"""
        loaders.write(self.file_path, self.setting_obj.to_dict())

    def get(self, name):
        """Get a config value from config file

        Parameters:
            name (String): Name of the config value we are looking to get

        Returns:
            String: The value in the config file. Will return None if config
            file does not include the name
        """
        result = self.setting_obj.get(name)
        if result is None:
            logger.error("Setting config failled, missing setting: %s", name)
        return result


settings = SettingLoader('settings.toml')
