import datetime

from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship

from depends.role.column_types import MutableRole, Role, Permission

from . import Base, ModelMixin
from .user_profile_model import UserProfileModel  # noqa: F401
from .user_meta_model import UserMetaModel  # noqa: F401
from .user_social_account_model import UserSocialAccountModel  # noqa: F401


class UserModel(Base, ModelMixin):
    __tablename__ = 'users'
    __table_args__ = (
        Index('email', 'username'),
    )

    _repr_attrs = ('id', 'email', 'username')

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    role = Column(MutableRole.as_mutable(Role), default=0, nullable=False)
    permission = Column(MutableRole.as_mutable(Permission), default=0, nullable=False)
    updated_at = Column(DateTime)
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


User = sqlalchemy_to_pydantic(UserModel)
