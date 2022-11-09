"""Config manager for the application"""
import logging
import os
from dynaconf import Dynaconf, loaders

logger = logging.getLogger("main")

validators = [
        # Ensure some parameters exists (are required)
    ]


class SettingLoader:
    """Setting loader access through. Use this to access logging"""
    def __init__(self, file_path='settings.toml'):
        if not os.path.exists(file_path):
            logger.fatal("CONFIG FILE DOES NOT EXISTS, please a add settings.toml")
            logger.fatal("More details https://github.com/marcolivierarsenault/tefnut")
            exit()
        self.file_path = file_path
        self.setting_obj = Dynaconf(
                                envvar_prefix="DYNACONF",
                                settings_files=[file_path],
                                validators=validators
                            )

    def save_config(self):
        """Save config file, after they are updated programatically"""
        loaders.write(self.file_path, self.setting_obj.to_dict())

    def set(self, name, value, persist=True):
        """Set a config value from config file

        Parameters:
            name (String): Name of the config value we are looking to set
            value (any): Value you want to store in the config
            persist (Bool): If you want to save the config file, default True
        """
        self.setting_obj.set(name, value)
        if persist:
            self.save_config()

    def get(self, name, default=None):
        """Get a config value from config file

        Parameters:
            name (String): Name of the config value we are looking to get

        Returns:
            String: The value in the config file. Will return None if config
            file does not include the name
        """
        result = self.setting_obj.get(name)
        if result is None and default is None:
            logger.error("Setting config failled, missing setting: %s", name)
        elif result is None:
            logger.warning("Setting config failled, missing setting: %s, using the default value", name)
        return result


settings = SettingLoader('settings.toml')
