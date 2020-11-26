import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables
load_dotenv()


class Config(object):
    # General config
    SECRET_KEY = os.getenv("SECRET_KEY", "CZ4031DatabaseSystemPrinciples2020!")
    FLASK_APP = os.getenv("FLASK_APP", "app.py")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")


class ProductionConfig(Config):
    FLASK_ENV = "production"
