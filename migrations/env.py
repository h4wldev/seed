import os
import sys

from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)  # noqa: E501

from db import make_database_url
from seed.models import Base
from seed.models.user_model import UserModel  # noqa: F401
from seed.models.user_login_history_model import UserLoginHistoryModel  # noqa: F401
from seed.models.user_meta_model import UserMetaModel  # noqa: F401
from seed.models.user_profile_model import UserProfileModel  # noqa: F401
from seed.models.user_social_account_model import UserSocialAccountModel  # noqa: F401
from setting import setting


config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

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
