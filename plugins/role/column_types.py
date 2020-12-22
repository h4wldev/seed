import sqlalchemy.types as atypes

from sqlalchemy.ext.mutable import Mutable

from .types import (
    Flag as FlagType,
    Role as RoleType,
    Permission as PermissionType,
)

import sys
sys.tracebacklimit = 0


class MutableRole(Mutable, FlagType):
    def __init__(
        self,
        value: FlagType
    ) -> None:
        self._class: FlagType = value

        super().__init__(
            self._class.value,
            self._class.mapping
        )

    @classmethod
    def coerce(cls, key, value):
        return MutableRole(value)

    def set(self, *args, **kwargs) -> None:
        self.changed()

        return super().set(*args, **kwargs)

    def __repr__(self) -> str:
        return self._class.__repr__()


class Role(atypes.TypeDecorator):
    impl: atypes.TypeEngine = atypes.Integer

    def process_bind_param(self, value, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return RoleType(value)


class Permission(atypes.TypeDecorator):
    impl: atypes.TypeEngine = atypes.Integer

    def process_bind_param(self, value, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return PermissionType(value)
