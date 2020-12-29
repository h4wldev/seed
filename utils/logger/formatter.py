import logging

from typing import Dict

from setting import setting


class Formatter:
    def stdout_format(self, record: logging.LogRecord) -> str:
        extra_headers: Dict[str, str] = {}

        if record['extra'].get('uuid', None):
            extra_headers['uuid'] = record['extra']['uuid']

        record['extra']['headers'] = ''.join(map(
            lambda i: f'[{i[0]}={i[1]}]', extra_headers.items()
        ))

        return setting.logging.format + '\n{exception}'
