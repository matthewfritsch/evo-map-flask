import folium
from server.types import Coordinate


def _as_milliseconds(hours: int = 0, minutes: int = 0, seconds: int = 0) -> int:
    minutes += hours * 60
    seconds += minutes * 60
    return seconds * 1000


AISSTREAM_BBOXES = [
    [
        [41.3, 114.4],
        [18.5, 242.8],
    ]
]
MAP_BOUNDS = list(
    map(
        lambda x: x.to_values(),
        [
            Coordinate(lat=41.18, lon=142.0),
            Coordinate(lat=30.3, lon=120.9),
            Coordinate(lat=41.8, lon=-115),
            Coordinate(lat=32.2, lon=-123.6),
        ],
    )
)
MAP_CENTER = Coordinate(lat=36.55, lon=-171.99)
CURRENT_MAP = "current"
ALL_MAP = "all"
ANT_MAP = "ant"
ICON_SCALE = 0.15
SHIP_ICON = folium.CustomIcon(
    icon_image="server/icons/ship_icon.png",
    icon_size=(int(355 * ICON_SCALE), int(161 * ICON_SCALE)),
)
UPDATE_INTERVAL_MS = _as_milliseconds(minutes=60)
