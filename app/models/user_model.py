import datetime

from sqlalchemy import text, Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from typing import Any

from seed.setting import setting

from seed.model import Base, ModelMixin

from .user_role_model import UserRoleModel  # noqa: F401
from .user_login_history_model import UserLoginHistoryModel  # noqa: F401
from .user_meta_model import UserMetaModel  # noqa: F401
from .user_profile_model import UserProfileModel  # noqa: F401
from .user_social_account_model import UserSocialAccountModel  # noqa: F401


class UserModel(Base, ModelMixin):
    __tablename__ = 'users'
    __table_args__ = (
        Index('email', 'username'),
    )

    _repr_attrs = ('id', 'email', 'username')

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    created_at = Column(DateTime, default=datetime.datetime.now)

    profile = relationship(
        'UserProfileModel',
        backref='user',
        cascade='all,delete',
        uselist=False,
    )

    meta = relationship(
        'UserMetaModel',
        backref='user',
        cascade='all,delete',
        uselist=False,
    )

    social_accounts = relationship(
        'UserSocialAccountModel',
        backref='user',
        cascade='all,delete',
    )

    login_histories = relationship(
        'UserLoginHistoryModel',
        backref='user',
        cascade='all,delete',
    )

    roles = relationship(
        'UserRoleModel',
        backref='user',
        cascade='all,delete',
    )

    @property
    def key_field(self) -> Any:
        return getattr(self, setting.user_key_field)
