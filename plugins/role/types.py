import typing

from utils.convert import (
    int2bitfield,
    bitfield2int,
)
from setting import setting


class Flag:
    def __init__(
        self,
        value: int,
        mapping: typing.List[str] = []
    ) -> None:
        self.mapping: typing.Dict[int, str] = {
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
        *names: typing.List[str],
        any_: bool = False
    ) -> bool:
        method: typing.Callable[typing.List[str], bool] = all

        if any_:
            method = any

        return method([self.get(n) for n in names])

    def has_any(
        self,
        *names: typing.List[str]
    ) -> bool:
        return self.has(*names, any_=True)

    def get_all(self) -> typing.Dict[str, bool]:
        return {
            k: self.bitfield[v] \
            for k, v in self.mapping.items()
        }

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
        value: typing.List[bool],
        mapping: typing.List[str] = []
    ) -> 'Flag':
        return cls(bitfield2int(value), mapping)

    def _set_bitfield(self, value: int) -> typing.List[bool]:
        bitfield: typing.List[bool] = int2bitfield(value)
        size_diff: int = len(self.mapping) - len(bitfield)

        if size_diff > 0: 
            bitfield += [False] * size_diff
        elif size_diff < 0:
            bitfield = bitfield[:len(self.mapping)]

        self.bitfield = bitfield

        return self.bitfield

    def __repr__(self) -> str:
        attr_string: str = ''
        flags: typing.List[str] = []

        for k, v in self.get_all().items():
            if v: flags.append(k)

        return f'<{self.__class__.__name__} flags=[{",".join(flags)}]>'


class Role(Flag):
    def __init__(
        self,
        value: int,
        mapping: typing.Optional[typing.List[str]] = None
    ) -> None:
        if not mapping:
            mapping = setting.plugin.role.roles

        super().__init__(value, mapping)


class Permission(Flag):
    def __init__(
        self,
        value: int,
        mapping: typing.Optional[typing.List[str]] = None
    ) -> None:
        if not mapping:
            mapping = setting.plugin.role.permissions

        super().__init__(value, mapping)
