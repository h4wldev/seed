"""Create tables

Revision ID: c6457970ac13
Revises: 
Create Date: 2021-01-11 22:24:16.601528+09:00

"""
import os
import sys
import sqlalchemy as sa

from alembic import op
from typing import Any, List, Dict

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
)

from seed.models import (
    AbilityModel,
    UserModel,
    UserBanModel,
    UserRoleModel,
    UserLoginHistoryModel,
    UserMetaModel,
    UserProfileModel,
    UserSocialAccountModel,
    RoleModel,
    RoleAbilityModel
)
from seed.models.mixin import Base


revision = 'c6457970ac13'
down_revision = None
branch_labels = None
depends_on = None


def table_args(model: Base) -> None:
    def create_new_column(column: sa.Column) -> sa.Column:
        attributes: List[str] = [
            'name',
            'type',
            'key',
            'primary_key',
            'nullable',
            'default',
            'server_default',
            'server_onupdate',
            'index',
            'unique',
            'system',
            'doc',
            'onupdate',
            'autoincrement',
            'comment',
        ]

        kwargs: Dict[str, Any] = {
            a: getattr(column, a, None) for a in attributes
        }
        kwargs['type_']: 'TypeEngine' = kwargs.get('type', None)
        del kwargs['type']

        return sa.Column(**kwargs)
        
    columns: List[sa.Column] = list(map(
        create_new_column,
        model.__table__.columns.values()
    ))

    return (
        model.__tablename__,
        *columns,
    )


models: List[Base] = [
    AbilityModel,
    RoleModel,
    RoleAbilityModel,
    UserModel,
    UserBanModel,
    UserRoleModel,
    UserLoginHistoryModel,
    UserMetaModel,
    UserProfileModel,
    UserSocialAccountModel,
]


def upgrade() -> None:
    for model in models:
        op.create_table(*table_args(model))


def downgrade() -> None:
    for model in reversed(models):
        op.drop_table(model.__tablename__)
