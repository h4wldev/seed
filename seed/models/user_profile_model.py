from sqlalchemy import text, Column, ForeignKey, Integer, String, DateTime, Index

from .mixin import Base, ModelMixin


class UserProfileModel(Base, ModelMixin):
    __tablename__ = 'user_profiles'
    __table_args__ = (
        Index('user_id'),
    )

    _repr_attrs = ('id', 'user_id')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    display_name = Column(String(50), unique=True, nullable=False)
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
