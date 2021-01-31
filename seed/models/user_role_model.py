import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from typing import Set

from .mixin import Base, ModelMixin

from .role_model import RoleModel  # noqa: F401


class UserRoleModel(Base, ModelMixin):
    __tablename__ = 'user_roles'
    __table_args__ = (
        Index('user_id'), Index('role'),
    )

    _repr_attrs = ('id', 'user_id')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_ = Column('role', String(20), ForeignKey('roles.role'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    role = relationship(
        'RoleModel',
    )

    @property
    def abilities(self) -> Set[str]:
        return set(map(lambda a: a.ability_, self.role.abilities))
