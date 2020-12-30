import datetime

from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime

from . import Base, ModelMixin


class UserLoginHistoryModel(Base, ModelMixin):
    __tablename__ = 'user_login_histories'

    _repr_attrs = ('id', 'user_id', 'success')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    success = Column(Boolean, default=False)
    ip = Column(String, nullable=False)
    provider = Column(String)
    device = Column(String)
    os = Column(String)
    browser = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)


UserLoginHistory = sqlalchemy_to_pydantic(UserLoginHistoryModel)
