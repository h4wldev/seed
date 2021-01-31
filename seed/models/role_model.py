import datetime

from sqlalchemy import Column, Text, String, DateTime
from sqlalchemy.orm import relationship

from .mixin import Base, ModelMixin

from .role_ability_model import RoleAbilityModel  # noqa: F401


class RoleModel(Base, ModelMixin):
    __tablename__ = 'roles'

    _repr_attrs = ('role',)

    role = Column(String(20), primary_key=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)

    abilities = relationship(
        'RoleAbilityModel',
        backref='role',
        cascade='all,delete',
    )
