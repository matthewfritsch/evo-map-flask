import os
from flask import Flask
from server.constants import CURRENT_MAP_LOC, ALL_MAP_LOC
from server.update_thread import run_map_update_thread

app = Flask(__name__)

run_map_update_thread(os.environ["SQLITE_CLOUD_URL"])


@app.route("/")
@app.route("/current")
def show_map():
    with open(CURRENT_MAP_LOC, "r") as f:
        return f.read()


@app.route("/all")
def show_refresh_map():
    with open(ALL_MAP_LOC, "r") as f:
        return f.read()
