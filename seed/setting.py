import os

from dynaconf import Dynaconf


setting: Dynaconf = Dynaconf(
    env=os.environ.get('ENV', 'development').lower(),
    envvar_prefix='SEED',
    environments=True,
    settings_files=[
        'settings/secrets/.secrets.default.toml',
        'settings/secrets/.secrets.development.toml',
        'settings/secrets/.secrets.testing.toml',

        'settings/setting.default.toml',
        'settings/setting.development.toml',
        'settings/setting.testing.toml',
    ],
)
