from contextlib import contextmanager
from datetime import datetime
import sqlitecloud
from sqlitecloud.exceptions import SQLiteCloudOperationalError

from server.types import TimedCoordinate


server_url: str | None = None


def setup_db(cloud_url: str):
    global server_url
    server_url = cloud_url
    with _db() as database:
        cmd = """CREATE TABLE COORDINATES (
            Time TIMESTAMP,
            Latitude REAL,
            Longitude REAL);"""
        try:
            _ = database.execute(cmd)
        except SQLiteCloudOperationalError:
            print("COORDINATES already exists. Continuing...")


def get_all_coords() -> tuple[list[TimedCoordinate], bool]:
    try:
        with _db() as database:
            cmd = """SELECT * from COORDINATES;"""
            _ = database.execute(cmd)
            values = database.fetchall()
            return [TimedCoordinate(timestamp=datetime.fromisoformat(t), lat=la, lon=lo) for t, la, lo in values], True
    except SQLiteCloudOperationalError:
        return [], False


@contextmanager
def _db():
    global server_url
    assert server_url is not None
    # Open the connection to SQLite Cloud
    conn = sqlitecloud.connect(server_url)
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        conn.commit()
        conn.close()
