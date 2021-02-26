import os

from dynaconf import Dynaconf


_root_path: str = os.path.dirname(os.path.abspath(__file__))

setting: Dynaconf = Dynaconf(
    env=os.environ.get('ENV', 'development').lower(),
    envvar_prefix='SEED',
    environments=True,
    settings_files=[
        os.path.join(_root_path, './settings/secrets/.secrets.default.toml'),
        os.path.join(_root_path, './settings/setting.default.toml'),
        os.path.join(_root_path, './settings/secrets/.secrets.testing.toml'),
        os.path.join(_root_path, './settings/setting.testing.toml')
    ]
)
