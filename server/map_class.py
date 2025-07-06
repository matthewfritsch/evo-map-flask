from copy import deepcopy
import folium

from datetime import datetime, timedelta, UTC
from server.constants import (
    ANT_MAP,
    MAP_BOUNDS,
    MAP_CENTER,
    CURRENT_MAP,
    ALL_MAP,
    SHIP_ICON,
)
from server.db import (
    get_latest_webpage,
    get_newest_coord,
    submit_webpage,
)
from server.map_builder_utils import build_all_coords_map, build_antpath_map, build_current_coords_map


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

    webpages = {
        **build_current_coords_map(map_obj),
        **build_all_coords_map(deepcopy(map_obj), current_coord),
        **build_antpath_map(deepcopy(map_obj)),
    }

    for name, content in webpages.items():
        submit_webpage(name, content)

    print(type(webpages[mapname]))
    return webpages[mapname]


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
