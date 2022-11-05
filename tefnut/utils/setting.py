from dynaconf import Dynaconf, loaders

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['config/settings.toml'],
)

def save_config():
    loaders.write('config/settings.toml', settings.to_dict())
