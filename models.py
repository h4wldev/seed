import datetime

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime, Index, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///seed.db", echo=True)
Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'users'

    _repr_attrs = ('id', 'email', 'username')

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    role = Column(Integer, default=0, nullable=False)
    permission = Column(Integer, default=0, nullable=False)
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


class UserProfileModel(Base):
    __tablename__ = 'user_profiles'

    _repr_attrs = ('id', 'user_id')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    display_name = Column(String, unique=True, nullable=False)
    updated_at = Column(DateTime)


class UserMetaModel(Base):
    __tablename__ = 'user_meta'

    _repr_attrs = ('id', 'user_id')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    email_promotion = Column(Boolean, default=False)
    email_notification = Column(Boolean, default=False)
    is_certified = Column(Boolean, default=False)
    updated_at = Column(DateTime)


class UserSocialAccountModel(Base):
    __tablename__ = 'user_social_accounts'

    _repr_attrs = ('id', 'user_id')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    social_id = Column(Integer, nullable=False)
    provider = Column(String, nullable=False)
    access_token = Column(String)
    updated_at = Column(DateTime)


Base.metadata.create_all(engine)