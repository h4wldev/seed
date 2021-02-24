import os

from dynaconf import Dynaconf


setting: Dynaconf = Dynaconf(
    env=os.environ.get('ENV', 'development').lower(),
    envvar_prefix='SEED',
    environments=True,
    settings_files=[
        'seed/settings/.secrets.default.toml',
        'seed/settings/setting.default.toml'
    ],
    DYNACONF_INCLUDE=[
        '../../settings/*.toml',
        '../../settings/secrets/.secrets.*.toml'
    ]
)
