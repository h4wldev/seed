import datetime

from sqlalchemy import text, Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from typing import Any, Optional, Set, Dict

from seed.db import db
from seed.schemas.user_schemas import RegisterSchema, SocialInfoSchema
from seed.setting import setting

from .mixin import Base, ModelMixin

from .user_ban_model import UserBanModel  # noqa: F401
from .user_login_history_model import UserLoginHistoryModel  # noqa: F401
from .user_meta_model import UserMetaModel  # noqa: F401
from .user_profile_model import UserProfileModel  # noqa: F401
from .user_social_account_model import UserSocialAccountModel  # noqa: F401
from .user_role_model import UserRoleModel  # noqa: F401


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

    bans = relationship(
        'UserBanModel',
        backref='user',
        cascade='all,delete',
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

    @classmethod
    def create(
        cls,
        register_fields: RegisterSchema,
        social_info_fields: SocialInfoSchema,
        roles: Set[str] = set()
    ) -> 'UserModel':
        roles.update(setting.role.roles)

        user: 'UserModel' = cls(
            email=register_fields.email,
            username=register_fields.username,
        )
        db.session.add(user)
        db.session.flush()

        user_profile: UserProfileModel = UserProfileModel(
            user_id=user.id,
            display_name=register_fields.display_name,
        )

        user_meta: UserMetaModel = UserMetaModel(
            user_id=user.id,
            email_promotion=register_fields.email_promotion,
            email_notification=register_fields.email_notification
        )

        user_social_account: UserSocialAccountModel = UserSocialAccountModel(
            user_id=user.id,
            social_id=social_info_fields.social_id,
            provider=social_info_fields.provider
        )

        roles: List[UserRoleModel] = list(map(
            lambda r: UserRoleModel(user_id=user.id, role_=r),
            roles
        ))

        db.session.add(user_profile)
        db.session.add(user_meta)
        db.session.add(user_social_account)
        db.session.add(user_profile)
        db.session.bulk_save_objects(roles)


    @classmethod
    def q_email_or_username(
        cls,
        email: str,
        username: str
    ) -> 'Query':
        return cls.q()\
            .filter(
                (
                    cls.email == email,
                    cls.username == username
                )
            )
