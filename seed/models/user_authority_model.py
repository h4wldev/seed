import datetime

from sqlalchemy import text, Column, ForeignKey, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship

from . import Base, ModelMixin
from .authority_model import AuthorityModel


class UserAuthorityModel(Base, ModelMixin):
    __tablename__ = 'user_authorities'
    __table_args__ = (
        Index('user_id'), Index('authority'),
    )

    _repr_attrs = ('id', 'user_id')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    authority = relationship(
        'AuthorityModel',
        back_populates='users',
        cascade='all,delete',
    )
