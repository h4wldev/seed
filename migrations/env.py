import os
import sys

from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool
from typing import List

from alembic import context

root_path: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.insert(0, root_path)  # noqa: E501

from seed.models import (
    UserModel,
    UserLoginHistoryModel,
    UserMetaModel,
    UserProfileModel,
    UserSocialAccountModel
)  # noqa: F401
from seed.models.mixin import Base
from seed.utils.database import make_database_url
from seed.setting import setting


setting_files: List[str] = [
    './settings/*.toml',
    './settings/secrets/.secrets.*.toml'
]


config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata
setting.load_file(path=list(map(lambda p: os.path.join(root_path, p), setting_files)))

database_url: str = make_database_url(**{
    **setting.database,
    **{'password': setting.password.database_password}
})


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.z
    """
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
