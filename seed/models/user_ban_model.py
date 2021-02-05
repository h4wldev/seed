import arrow
import datetime

from sqlalchemy import Column, ForeignKey, CheckConstraint, Text, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from typing import Set

from seed.setting import setting

from .mixin import Base, ModelMixin

from .role_model import RoleModel  # noqa: F401
from .ability_model import AbilityModel  # noqa: F401


class UserBanModel(Base, ModelMixin):
    __tablename__ = 'user_bans'
    __table_args__ = (
        Index('user_id'), Index('role'), Index('ability'),
        CheckConstraint('role IS NOT NULL OR ability IS NOT NULL'),
    )

    _repr_attrs = ('id', 'user_id', 'role', 'ability')

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_ = Column('role', String(20), ForeignKey('roles.role'), nullable=True)
    ability_ = Column('ability', String(20), ForeignKey('abilities.ability'), nullable=True)
    reason = Column(Text)
    until_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now)

    role = relationship(
        'RoleModel',
    )

    ability = relationship(
        'AbilityModel',
    )

    @property
    def is_continue(self) -> bool:
        if self.until_at is None:
            return True

        return self.until_at >= arrow.now(setting.timezone).naive
