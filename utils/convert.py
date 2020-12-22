import typing


def int2bitfield(value: int) -> typing.List[bool]:
    return list(reversed([
        bool(int(digit)) \
        for digit in bin(value)[2:]
    ]))


def bitfield2int(value: typing.List[bool]) -> int:
    result: int = 0

    for i, v in enumerate(value):
        result += int(v) * (2 ** i)

    return result
