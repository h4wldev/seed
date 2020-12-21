from dynaconf import Dynaconf


setting: Dynaconf = Dynaconf(
    environments=True,
    settings_files=[
        'settings/settings.toml',
        'settings/.secrets.settings.toml',
    ],
)
