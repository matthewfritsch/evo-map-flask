from datetime import datetime
from typing import Any
import attr


@attr.s(kw_only=True)
class Coordinate:
    lat: float = attr.ib()
    lon: float = attr.ib(converter=lambda val: val if val > 0 else 360 + val)

    def to_values(self):
        return [self.lat, self.lon]


@attr.s(kw_only=True)
class TimedCoordinate(Coordinate):
    timestamp: datetime = attr.ib()

    def popup_format(self) -> str:
        return f"{self.timestamp.isoformat()}\n({self.lat},{self.lon})"


def same_coordinate(a: Any, b: Any) -> bool:
    return isinstance(a, Coordinate) and isinstance(b, Coordinate) and a.lat == b.lat and a.lon == b.lon
