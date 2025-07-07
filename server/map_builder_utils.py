import io
import folium
import folium.plugins as plugins

from datetime import datetime, timedelta
from server.buffers import read_all, write
from server.constants import ALL_MAP, ANT_MAP, CURRENT_MAP, UPDATE_INTERVAL_MS
from server.db import get_all_coords, get_ant_coords
from server.types import TimedCoordinate


def build_current_coords_map(map_obj) -> dict[str, str]:
    buf = io.BytesIO()
    map_obj.save(buf, close_file=False)
    return {CURRENT_MAP: add_extras(buf)}


def build_all_coords_map(map_obj, current_coord: TimedCoordinate) -> dict[str, str]:
    last_added: TimedCoordinate | None = None
    coords = get_all_coords()
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
    return {ALL_MAP: add_extras(buf)}


def build_antpath_map(map_obj) -> dict[str, str]:
    ant_coords = list(map(lambda c: c.to_values(), get_ant_coords()))
    plugins.AntPath(locations=ant_coords, dash_array=[20, 30]).add_to(map_obj)
    buf = io.BytesIO()
    map_obj.save(buf, close_file=False)
    return {ANT_MAP: add_extras(buf)}


def add_extras(buf: io.BytesIO) -> str:
    buf = add_timeout(buf)
    buf = add_banner(buf)
    return read_all(buf)


def add_timeout(webpage: io.BytesIO) -> io.BytesIO:
    lines = read_all(webpage).split("\n")
    added_lines = [
        "setInterval(function() {",
        "    location.reload();",
        f"}}, {UPDATE_INTERVAL_MS});",
    ]
    combined = "\n".join([*lines[:-2], *added_lines, *lines[-2:]])
    result = write(combined, as_bytes=True)
    assert isinstance(result, io.BytesIO)
    return result


def add_banner(webpage: io.BytesIO) -> io.BytesIO:
    lines = read_all(webpage).split("\n")
    added_lines = [
    '  <div style="background-color: #f0f0f0; padding: 10px; text-align: center; font-family: sans-serif; font-size: 18px;">',
    '    Thank you <a href="https://navapi.com/" target="_blank" style="color: #333; text-decoration: underline;">NavAPI</a> for live vessel tracking!',
    '  </div>',
    ]
    idx = lines.index('<body>')
    combined = "\n".join([*lines[:idx+1], *added_lines, *lines[idx+1:]])
    result = write(combined, as_bytes=True)
    assert isinstance(result, io.BytesIO)
    return result


def within_hour(a: datetime, b: datetime) -> bool:
    greater = max(a, b)
    lesser = min(a, b)
    return greater - lesser < timedelta(hours=1)
