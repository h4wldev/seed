from typing import List


def int2bitfield(value: int) -> List[bool]:
    return list(reversed([
        bool(int(digit)) \
        for digit in bin(value)[2:]
    ]))


def bitfield2int(value: List[bool]) -> int:
    result: int = 0

    for i, v in enumerate(value):
        result += int(v) * (2 ** i)

    return result


def units2seconds(value: str) -> int:
    if isinstance(value, int):
        return value
    
    if value.isnumeric():
        return int(value)

    unit_map: Dict[str, Callable[..., int]] = {
        's': lambda t: t,
        'm': lambda t: t * 60,
        'h': lambda t: t * 60 * 60,
        'd': lambda t: t * 60 * 60 * 24,
        'w': lambda t: t * 60 * 60 * 24 * 7,
        'M': lambda t: t * 60 * 60 * 24 * 30,
        'q': lambda t: t * 60 * 60 * 24 * 30 * 4,
        'y': lambda t: t * 60 * 60 * 24 * 365
    }
    result: int = 0

    for token in value.split():
        time: int = int(token[:-1])
        unit: str = token[-1]

        result += unit_map[unit](time)

    return result
