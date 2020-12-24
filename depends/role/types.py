import types

from typing import Dict, List, Optional

from utils.convert import (
    int2bitfield,
    bitfield2int,
)
from setting import setting


class Flag:
    def __init__(
        self,
        value: int,
        mapping: List[str] = []
    ) -> None:
        self.mapping: Dict[int, str] = {
            m: i for i, m in enumerate(mapping)
        }
        self._set_bitfield(value)

    def get(
        self,
        name: str
    ) -> bool:
        if name not in self.mapping:
            return False

        return self.bitfield[self.mapping[name]]

    def has(
        self,
        *names: List[str],
        any_: bool = False
    ) -> bool:
        method: Callable[List[str], bool] = all

        if any_:
            method = any

        return method([self.get(n) for n in names])

    def has_any(
        self,
        *names: List[str]
    ) -> bool:
        return self.has(*names, any_=True)

    def get_all(self) -> Dict[str, bool]:
        return {
            k: self.bitfield[v] \
            for k, v in self.mapping.items()
        }

    def reset(self) -> None:
        self._set_bitfield(0)

    def set(
        self,
        name: str,
        value: bool
    ) -> None:
        if name not in self.mapping:
            raise KeyError(f"'{name}' not in mapping dict")

        self.bitfield[self.mapping[name]] = bool(value)

    @property
    def value(self) -> int:
        return bitfield2int(self.bitfield)
    
    @value.setter
    def value(self, value: int) -> None:
        self._set_bitfield(value)

    @classmethod
    def from_bitfield(
        cls,
        value: List[bool],
        mapping: List[str] = []
    ) -> 'Flag':
        return cls(bitfield2int(value), mapping)

    def _set_bitfield(self, value: int) -> List[bool]:
        bitfield: List[bool] = int2bitfield(value)
        size_diff: int = len(self.mapping) - len(bitfield)

        if size_diff > 0: 
            bitfield += [False] * size_diff
        elif size_diff < 0:
            bitfield = bitfield[:len(self.mapping)]

        self.bitfield = bitfield

        return self.bitfield

    def __repr__(self) -> str:
        attr_string: str = ''
        flags: List[str] = []

        for k, v in self.get_all().items():
            if v: flags.append(k)

        return f'<{self.__class__.__name__} flags=[{",".join(flags)}]>'

    def __eq__(
        self,
        other: 'Flag'
    ) -> bool:
        try:
            if issubclass(other.__class__, self.__class__):
                return self.value == other.value
        except: pass

        return False


class Role(Flag):
    _default_mapping: List[str] = setting.plugin.role.roles

    def __init__(
        self,
        value: int,
        mapping: Optional[List[str]] = None
    ) -> None:
        if not mapping:
            mapping = self._default_mapping

        super().__init__(value, mapping)


class Permission(Role):
    _default_mapping: List[str] = setting.plugin.role.permissions
