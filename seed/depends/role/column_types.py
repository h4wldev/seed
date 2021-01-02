import sqlalchemy.types as atypes

from sqlalchemy.ext.mutable import Mutable
from typing import Any, List

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

    def _set_bitfield(self, *args, **kwargs) -> List[bool]:
        self.changed()

        return super()._set_bitfield(*args, **kwargs)

    def __repr__(self) -> str:
        return self._class.__repr__()


class Role(atypes.TypeDecorator):
    impl: atypes.TypeEngine = atypes.Integer
    type_: FlagType = RoleType

    def process_bind_param(
        self,
        value: Any,
        dialect: 'SQLAlchemyDialect'
    ) -> int:
        try:
            return value.value
        except Exception:
            pass

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
