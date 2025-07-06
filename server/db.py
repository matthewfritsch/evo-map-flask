import os
from easydict import EasyDict
from contextlib import contextmanager
from datetime import UTC, datetime
from server.types import TimedCoordinate
from supabase import create_client, Client

__supabase_client: Client | None = None


def get_all_coords() -> list[TimedCoordinate]:
    with _db() as database:
        response = database.table("coordinates").select("*").order("time", desc=False).execute()
        easy = [EasyDict(val) for val in response.data]
        return [
            TimedCoordinate(timestamp=datetime.fromisoformat(e.time), lat=e.latitude, lon=e.longitude) for e in easy
        ]


def get_ant_coords() -> list[TimedCoordinate]:
    with _db() as database:
        response = (
            database.table("coordinates")
            .select("*")
            .order("time", desc=False)
            .gt("time", datetime(year=2025, month=7, day=6, tzinfo=UTC).isoformat())
            .execute()
        )
        easy = [EasyDict(val) for val in response.data]
        return [
            TimedCoordinate(timestamp=datetime.fromisoformat(e.time), lat=e.latitude, lon=e.longitude) for e in easy
        ]


def get_newest_coord() -> TimedCoordinate:
    with _db() as database:
        response = database.table("coordinates").select("*").order("time", desc=True).limit(1).execute()
        entry = EasyDict(response.data[0])
        t, la, lo = entry.time, entry.latitude, entry.longitude
        return TimedCoordinate(timestamp=datetime.fromisoformat(t), lat=la, lon=lo)


def get_latest_webpage(name: str) -> tuple[str, str]:
    with _db() as database:
        response = (
            database.table("webpages").select("*").match({"name": name}).order("time", desc=True).limit(1).execute()
        )
        latest_time: str = response.data[0]["time"]
        latest_webpage: str = response.data[0]["webpage"]
        return latest_time, latest_webpage


def submit_webpage(name, webpage):
    with _db() as database:
        database.table("webpages").insert({"name": name, "webpage": webpage}).execute()


@contextmanager
def _db():
    global __supabase_client
    if not __supabase_client:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        assert url
        assert key
        __supabase_client = create_client(url, key)
    yield __supabase_client
