import datetime

from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship

from models import Base, ModelMixin


class UserProfileModel(Base, ModelMixin):
    __tablename__ = 'user_profiles'
    __table_args__ = (
        Index('user_id'),
    )

    _repr_attrs = ('id', 'user_id')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    display_name = Column(String, unique=True, nullable=False)
    updated_at = Column(DateTime)


UserProfile = sqlalchemy_to_pydantic(UserProfileModel)
