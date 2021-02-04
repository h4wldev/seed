import re


def camelcase_to_underscore(string: str) -> str:
    pattern: 'Pattern' = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')

    return pattern.sub(r'_\1', string).lower()


def units_to_seconds(value: str) -> int:
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
