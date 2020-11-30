import psycopg2
import os
from sys import stderr
from custom_errors import *

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


""" #################################################################### 
establish connection to database
#################################################################### """


def connect():
    """ Connect to the PostgreSQL database server """
    try:
        # connection details. either use environemtn variable if set up, or use default values
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "TPC-H"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            port=os.getenv("DB_PORT", 5432),
        )
        cur = conn.cursor()

        return conn, cur

    except CustomError as e:
        raise CustomError(str(e))
    except:
        if conn is not None:
            conn.close()
        raise CustomError("Error in connect() - Database connection error.")


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

        if explain:
            return data[0][0][0]
        else:
            return data[0]
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in query() - Database has a problem executing query, check your SQL syntax."
        )


""" #################################################################### 
gets the estimated cost of a plan, normalized by rows. If rows returned is zero, just return total cost
#################################################################### """


def calculate_estimated_cost_per_row(qep):
    try:
        try:
            estimated_cost_per_row = (
                qep["Plan"]["Startup Cost"] + qep["Plan"]["Total Cost"]
            ) / qep["Plan"]["Plan Rows"]
        except ZeroDivisionError:
            estimated_cost_per_row = (
                qep["Plan"]["Startup Cost"] + qep["Plan"]["Total Cost"]
            )
        return estimated_cost_per_row
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in calculate_estimated_cost_per_row() - Unable to calculate estimated costs."
        )
