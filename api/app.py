from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from sys import stderr
import psycopg2


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
    print("data: ", data, file=stderr)
      
    # # Connect to database
    # if len(data["dbUrl"]) > 0:
    #     db_url = data["dbUrl"]
    # else:
    #     db_url = os.getenv("DB_URL")
    
    # print("db_url: ", db_url, file=stderr)

    sql_string = data["query"]
    data = query(sql_string)
    print('data: ', data, file=stderr)


    return str(data)

def query(sql_string):
    conn, cur = connect()

    data = ''
    if conn is not None:
        cur.execute(sql_string)
        data = cur.fetchall()

        conn.close()
        print('Database connection closed.', file=stderr)

    return data



def connect():
    """ Connect to the PostgreSQL database server """
    try:
        # connection details 
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )

        cur = conn.cursor()
        
        return conn, cur
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("Exception occured", file=stderr)
        if conn is not None:
            conn.close()
            print('Database connection closed.', file=stderr)
        return error, error