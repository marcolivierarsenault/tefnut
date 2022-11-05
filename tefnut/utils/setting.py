from dynaconf import Dynaconf, loaders

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.toml'],
)

def save_config():
    loaders.write('settings.toml', settings.to_dict())
