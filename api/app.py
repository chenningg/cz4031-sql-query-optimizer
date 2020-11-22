from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Load Flask config
app.config.from_object("config.Config")


@app.route("/")
def hello():
    return "Hey, you're not supposed to come here! But if you find this, please give us extra marks, thanks! (:"


@app.route("/generate", methods=["POST"])
def get_plans():
    # Gets the SQL query from the frontend
    data = request.json

    # Connect to database
    db_url = ""

    if len(data["dbUrl"]) > 0:
        db_url = data["dbUrl"]
    else:
        db_url = os.getenv("DB_URL")

    return data
