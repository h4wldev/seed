import datetime

from sqlalchemy import text, Column, ForeignKey, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship

from .mixin import Base, ModelMixin
from .ability_model import AbilityModel


class UserAbilityModel(Base, ModelMixin):
    __tablename__ = 'user_abilities'
    __table_args__ = (
        Index('user_id'), Index('ability'),
    )

    _repr_attrs = ('id', 'user_id')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ability_ = Column('ability', String(20), ForeignKey('abilities.ability'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    ability = relationship(
        'AbilityModel',
    )
