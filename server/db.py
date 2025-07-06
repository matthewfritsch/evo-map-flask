import os
from contextlib import contextmanager
from datetime import datetime
import libsql

from server.types import TimedCoordinate


COORDINATE_DB = "evomap.db"
WEBPAGE_DB = "webpage.db"

TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")


# def setup_db():
#     with _db(COORDINATE_DB) as database:
#         cmd = """CREATE TABLE COORDINATES (
#             Time TIMESTAMP,
#             Latitude REAL,
#             Longitude REAL);"""
#         try:
#             _ = database.execute(cmd)
#         except Exception:
#             print("COORDINATES already exists. Continuing...")
#
#     with _db(WEBPAGE_DB) as database:
#         cmd = """CREATE TABLE WEBPAGE (
#             Time TIMESTAMP,
#             Name TEXT,
#             Contents CLOB);"""
#         try:
#             _ = database.execute(cmd)
#         except Exception:
#             print("WEBPAGE already exists. Continuing...")


def get_all_coords() -> list[TimedCoordinate]:
    with _db(COORDINATE_DB) as database:
        cmd = """SELECT * from COORDINATES ORDER BY Time ASC;"""
        _ = database.execute(cmd)
        values = database.fetchall()
        return [TimedCoordinate(timestamp=datetime.fromisoformat(t), lat=la, lon=lo) for t, la, lo in values]


def get_newest_coord() -> TimedCoordinate:
    with _db(COORDINATE_DB) as database:
        cmd = """SELECT * from COORDINATES ORDER BY Time DESC LIMIT 1;"""
        _ = database.execute(cmd)
        t, la, lo = database.fetchone()
        return TimedCoordinate(timestamp=datetime.fromisoformat(t), lat=la, lon=lo)


def get_latest_webpage(name: str) -> tuple[str, str]:
    with _db(WEBPAGE_DB) as database:
        cmd = """SELECT * FROM WEBPAGE WHERE Name = (?) ORDER BY Time DESC LIMIT 1;"""
        _ = database.execute(cmd, (name,))
        latest_time, _, latest_webpage = database.fetchone()
        return latest_time, latest_webpage


def submit_webpage(name, webpage):
    with _db(WEBPAGE_DB) as database:
        cmd = """INSERT INTO WEBPAGE VALUES (?, ?, ?);"""
        _ = database.execute(cmd, (datetime.now().isoformat(), name, webpage))


@contextmanager
def _db(db_name):
    global TURSO_URL
    global TURSO_AUTH_TOKEN
    assert None not in [TURSO_AUTH_TOKEN, TURSO_URL]
    # Open the connection to SQLite Cloud
    conn = libsql.connect(db_name, sync_url=TURSO_URL, auth_token=TURSO_AUTH_TOKEN)
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        conn.commit()
        conn.close()
