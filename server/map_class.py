from copy import deepcopy
import folium
import folium.plugins as plugins
import io

from datetime import datetime, timedelta, UTC
from server.buffers import read_all
from server.constants import (
    ANT_MAP,
    MAP_BOUNDS,
    MAP_CENTER,
    CURRENT_MAP,
    ALL_MAP,
    SHIP_ICON,
    UPDATE_INTERVAL_MS,
)
from server.db import (
    get_all_coords,
    get_latest_webpage,
    get_newest_coord,
    submit_webpage,
)
from server.types import Coordinate, TimedCoordinate

last_coord: Coordinate | None = None


def update_map(mapname: str) -> str:
    now = datetime.now()

    latest_map_time, latest_map_content = get_latest_webpage(mapname)
    if datetime.fromisoformat(latest_map_time) + timedelta(minutes=20) >= now.astimezone(UTC):
        return latest_map_content

    current_coord = get_newest_coord()

    msg = f"{now}\n({current_coord.lat},{current_coord.lon})"
    map_obj = folium.Map(location=MAP_CENTER.to_values(), zoom_start=3)
    _ = folium.Marker(current_coord.to_values(), popup=msg, icon=SHIP_ICON).add_to(map_obj)
    map_obj.fit_bounds(MAP_BOUNDS)

    coords = get_all_coords()
    webpages = {
        **build_current_coords_map(map_obj),
        **build_all_coords_map(deepcopy(map_obj), coords, current_coord),
        **build_antpath_map(deepcopy(map_obj), coords),
    }

    for name, content in webpages.items():
        submit_webpage(name, content)

    print(type(webpages[mapname]))
    return webpages[mapname]


def build_current_coords_map(map_obj) -> dict[str, str]:
    buf = io.BytesIO()
    map_obj.save(buf, close_file=False)
    return {CURRENT_MAP: add_timeout(buf)}


def build_all_coords_map(map_obj, coords: list[TimedCoordinate], current_coord: TimedCoordinate) -> dict[str, str]:
    last_added: TimedCoordinate | None = None
    coords.remove(current_coord)

    for coord_to_add in coords:
        popup = coord_to_add.popup_format()
        location = coord_to_add.to_values()
        if last_added and within_hour(last_added.timestamp, coord_to_add.timestamp):
            continue
        print("Adding {} stating {}")
        _ = folium.Marker(location=location, popup=popup).add_to(map_obj)
        last_added = coord_to_add
    buf = io.BytesIO()
    map_obj.save(buf, close_file=False)
    return {ALL_MAP: add_timeout(buf)}


def build_antpath_map(map_obj, coords) -> dict[str, str]:
    real_coords = list(map(lambda x: x.to_values(), coords))
    plugins.AntPath(locations=real_coords, dash_array=[20, 30]).add_to(map_obj)
    buf = io.BytesIO()
    map_obj.save(buf, close_file=False)
    return {ANT_MAP: add_timeout(buf)}


def within_hour(a: datetime, b: datetime) -> bool:
    greater = max(a, b)
    lesser = min(a, b)
    return greater - lesser < timedelta(hours=1)


def add_timeout(webpage: io.BytesIO) -> str:
    lines = read_all(webpage).split("\n")
    print(lines[:3])
    added_lines = [
        "setInterval(function() {",
        "    location.reload();",
        f"}}, {UPDATE_INTERVAL_MS});",
    ]
    lines = "\n".join([*lines[:-2], *added_lines, *lines[-2:]])
    return lines


def read_current_map():
    return update_map(CURRENT_MAP)


def read_all_map():
    return update_map(ALL_MAP)


def read_ant_map():
    return update_map(ANT_MAP)


# def auto_update_map():
#     setup_db()
#     update_map()
#     while True:
#         time.sleep(UPDATE_INTERVAL_MS / 1000)  # Sleep for 1 hour (3600 seconds)
#         print(f"Updating map at {datetime.now().strftime('%H:%M:%S')}")
#         update_map()
