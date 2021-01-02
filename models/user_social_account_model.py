from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Index

from . import Base, ModelMixin


class UserSocialAccountModel(Base, ModelMixin):
    __tablename__ = 'user_social_accounts'
    __table_args__ = (
        Index('user_id'),
    )

    _repr_attrs = ('id', 'user_id')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    social_id = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    access_token = Column(String)
    updated_at = Column(DateTime)


UserSocialAccount = sqlalchemy_to_pydantic(UserSocialAccountModel)
