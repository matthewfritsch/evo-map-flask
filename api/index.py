from flask import Flask

from server.map_class import read_all_map, read_ant_map, read_current_map

app = Flask(__name__)

# run_map_update_thread()


@app.route("/current")
def show_map():
    return read_current_map()


@app.route("/all")
def show_all_map():
    return read_all_map()


@app.route("/")
@app.route("/ant")
def show_ant_map():
    return read_ant_map()
