from geolite2 import geolite2
from typing import Optional, Dict


class GeoIP:
    _reader: 'Reader' = geolite2.reader()

    def __init__(
        self,
        ip: str
    ) -> None:
        self.ip: str = ip

        self.match: Dict = self._reader.get(self.ip)

    @property
    def country(self) -> Optional[Dict]:
        if self.match is None:
            return None

        return self.match.get('country', None)

    @property
    def city(self) -> Optional[Dict]:
        if self.match is None:
            return None

        return self.match.get('city', None)
