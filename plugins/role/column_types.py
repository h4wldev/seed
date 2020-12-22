import typing

import sqlalchemy.types as atypes

from sqlalchemy.sql import operators
from sqlalchemy.ext.mutable import Mutable

from .types import (
    Flag as FlagType,
    Role as RoleType,
    Permission as PermissionType,
)


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
    def coerce(
        cls,
        key: str,
        value: FlagType
    ) -> 'MutableRole':
        return MutableRole(value)

    def set(self, *args, **kwargs) -> None:
        self.changed()

        return super().set(*args, **kwargs)

    def __repr__(self) -> str:
        return self._class.__repr__()


class Role(atypes.TypeDecorator):
    impl: atypes.TypeEngine = atypes.Integer
    type_: FlagType = RoleType

    def process_bind_param(
        self,
        value: typing.Any,
        dialect: 'SQLAlchemyDialect'
    ) -> int:
        try:
            if issubclass(value.__class__, FlagType.__class__):
                return value.value
        except: pass

        return value

    def process_result_value(
        self,
        value: int,
        dialect: 'SQLAlchemyDialect'
    ) -> FlagType:
        if isinstance(value, int):
            return self.type_(value)
        
        return value


class Permission(Role):
    type_: FlagType = PermissionType
