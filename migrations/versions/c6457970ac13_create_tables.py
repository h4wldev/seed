"""Create tables

Revision ID: c6457970ac13
Revises: 
Create Date: 2021-01-11 22:24:16.601528+09:00

"""
import os
import sys
import sqlalchemy as sa

from alembic import op
from typing import List

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
)

from migrations.utils import table_args

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
    UserSocialAccountModel
]


def upgrade() -> None:
    for model in models:
        op.create_table(*table_args(model))


def downgrade() -> None:
    for model in reversed(models):
        op.drop_table(model.__tablename__)
