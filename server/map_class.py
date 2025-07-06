import folium
import time

from datetime import datetime, timedelta
from server.constants import (
    MAP_BOUNDS,
    MAP_CENTER,
    CURRENT_MAP_LOC,
    ALL_MAP_LOC,
    SHIP_ICON,
    UPDATE_INTERVAL_MS,
)
from server.db import (
    get_all_coords,
    setup_db,
)
from server.types import Coordinate, TimedCoordinate, same_coordinate

last_coord: Coordinate | None = None


def update_map():
    current_coord = get_newest_coord()
    now = datetime.now().isoformat()

    if not current_coord:
        print(f"{now} -> Could not connect to sqlite cloud!")
        return

    msg = f"{now}\n({current_coord.lat},{current_coord.lon})"
    map_obj = folium.Map(location=MAP_CENTER.to_values(), zoom_start=3)
    _ = folium.Marker(current_coord.to_values(), popup=msg, icon=SHIP_ICON).add_to(map_obj)
    map_obj.fit_bounds(MAP_BOUNDS)
    map_obj.save(CURRENT_MAP_LOC)  # type: ignore

    added_count = 0
    total_count = 0
    last_added: TimedCoordinate | None = None

    coords, _ = get_all_coords()
    for coord_to_add in coords:
        total_count += 1
        if last_added and within_hour(last_added.timestamp, coord_to_add.timestamp):
            continue
        if same_coordinate(coord_to_add, current_coord):
            continue
        _ = folium.Marker(coord_to_add.to_values(), popup=coord_to_add.popup_format()).add_to(map_obj)
        last_added = coord_to_add
        added_count += 1

    print(f"Displaying {added_count + 1} of a total {total_count + 1} markers")

    map_obj.save(ALL_MAP_LOC)
    add_timeout(CURRENT_MAP_LOC)
    add_timeout(ALL_MAP_LOC)


def is_unique(coord: Coordinate | None) -> bool:
    global last_coord
    if not coord:
        return False
    return not same_coordinate(coord, last_coord)


def within_hour(a: datetime, b: datetime) -> bool:
    greater = max(a, b)
    lesser = min(a, b)
    return greater - lesser < timedelta(hours=1)


def get_newest_coord() -> TimedCoordinate | None:
    newest = None
    coords, success = get_all_coords()
    if not success:
        return None
    for coord in coords:
        if not newest or coord.timestamp > newest.timestamp:
            newest = coord
    return newest


def add_timeout(location: str):
    with open(location, "r") as f:
        lines = f.readlines()
    added_lines = [
        "setInterval(function() {",
        "    location.reload();",
        f"}}, {UPDATE_INTERVAL_MS});",
    ]
    lines = [*lines[:-2], *added_lines, *lines[-2:]]
    with open(location, "w") as f:
        f.writelines(lines)


def auto_update_map(cloud_url: str):
    setup_db(cloud_url)
    update_map()
    while True:
        time.sleep(UPDATE_INTERVAL_MS / 1000)  # Sleep for 1 hour (3600 seconds)
        print(f"Updating map at {datetime.now().strftime('%H:%M:%S')}")
        update_map()
