import psycopg2
import os
from sys import stderr

from dotenv import load_dotenv
# Load environment variables
load_dotenv()


""" #################################################################### 
establish connection to database
#################################################################### """
def connect():
    """ Connect to the PostgreSQL database server """
    try:
        # connection details
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "TPC-H"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            port=os.getenv("DB_PORT", 5432),
        )
        cur = conn.cursor()

        return conn, cur

    except:
        print("Exception occured", file=stderr)
        if conn is not None:
            conn.close()
            print("Database connection closed.", file=stderr)
        raise Exception("Error in connect() - database connection error")


""" #################################################################### 
helper that processes a query and returns the data
#################################################################### """
def query(sql_string, explain=False):
    conn, cur = connect()

    try:
        data = ""
        if conn is not None:
            cur.execute(sql_string)
            data = cur.fetchall()

            conn.close()
            print("Database connection closed.", file=stderr)

        if explain:
            return data[0][0][0]
        else:
            return data[0]
    except:
        raise Exception ("Error in query() - database has problem executing query, check your SQL syntax")
