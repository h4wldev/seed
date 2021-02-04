from figures import figures
from typing import Any, Dict, Optional, List


class LogLevel:
    def __init__(
        self,
        name: str,
        level: int,
        icon: str = '  ',
        color: Optional[str] = None,
        exists: bool = True,
    ) -> None:
        self.name = name.upper()
        self.level = level
        self.icon = icon
        self.color = color
        self.exists = exists

    @property
    def kwargs(self) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            'icon': self.icon,
            'color': self.color
        }

        if not self.exists:
            kwargs['no'] = self.level

        return kwargs


LOG_LEVELS: List[LogLevel] = [
    LogLevel(name='CRITICAL', level=50, icon=figures('cross'), color='<red>'),
    LogLevel(name='ERROR', level=40, icon=figures('cross'), color='<red>'),
    LogLevel(name='WARNING', level=30, icon=figures('warning'), color='<yellow>'),
    LogLevel(name='INFO', level=20, icon=figures('info'), color='<blue>'),
    LogLevel(name='DEBUG', level=10, icon=figures('bullets'), color='<light-black>'),
]
