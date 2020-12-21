from dynaconf import Dynaconf


setting = Dynaconf(
    environments=True,
    settings_files=[
        'settings/settings.toml',
        'settings/.secrets.settings.toml',
    ],
)
