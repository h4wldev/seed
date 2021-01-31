import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship

from .mixin import Base, ModelMixin

from .ability_model import AbilityModel  # noqa: F401


class RoleAbilityModel(Base, ModelMixin):
    __tablename__ = 'role_abilities'
    __table_args__ = (
        Index('role'), Index('ability'),
    )

    _repr_attrs = ('id', 'role', 'ability')

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_ = Column('role', String(20), ForeignKey('roles.role'), nullable=False)
    ability_ = Column('ability', String(20), ForeignKey('abilities.ability'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    ability = relationship(
        'AbilityModel',
    )
