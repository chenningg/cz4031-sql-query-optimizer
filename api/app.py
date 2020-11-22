from flask import Flask, request, jsonify
from os.path import dirname, abspath
from subprocess import call
import time

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/test", methods=["POST"])
def get_plans():
    # Gets the SQL query from the frontend
    data = request.json
    query = data["query"]

    # Absolute filepath to run Picasso command line utility from
    filepath = (
        dirname(dirname(abspath(__file__)))
        + "\picasso2.1\PicassoRun\Windows\PicassoCmd"
    )

    return query
