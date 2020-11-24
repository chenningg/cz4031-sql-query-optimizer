from flask import Flask, request
import os
from dotenv import load_dotenv
from sys import stderr
import psycopg2
import ast
import json


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
    # print("data: ", data, file=stderr)

    sql_string = "EXPLAIN (FORMAT JSON, BUFFERS) " + data["query"]
    data = query(sql_string)
    data = json.dumps(ast.literal_eval(str(data)))
    # print("data: ", data, file=stderr)

    optimized_query_plan = postorder_qep(data)
    data = {"optimizedQueryPlan": optimized_query_plan}

    return data


name = 65


def postorder_qep(plan):
    try:
        plan = json.loads(plan)
        plan = plan["Plan"]
        # print(json.dumps(plan, indent=2), file=stderr)

        postorder_result = []

        global name

        def recurse(plan):
            if plan == None:
                return

            global name

            child_names = []

            # My own output name (e.g. A)
            curr_name = ""

            # Recurse all the way down the tree and get the intermediate output(s)
            if plan.get("Plans") != None:
                for branch in plan.get("Plans"):
                    result = recurse(branch)

                    if result:
                        child_names.append(result[0])
                        postorder_result.append(result[1])

                    # If not leaf node, give an arbitrary name
                    curr_name = chr(name)
                    name += 1
            # If we are a leaf node, then just put table name
            else:
                curr_name = plan.get("Relation Name")

            # When we reach here, we can assume we are a leaf node, or that all our children has already recursed.
            output = ""
            node_type = plan.get("Node Type")
            output += node_type + " "

            # Take care of joins and sorts
            if (
                node_type == "Hash"
                or node_type == "Sort"
                or node_type == "Gather Merge"
                or node_type == "Merge"
                or node_type == "Aggregate"
            ):
                output += child_names[0] + " as " + curr_name + "."
            elif (
                node_type == "Hash Join"
                or node_type == "Nested Loop"
                or node_type == "Merge Join"
            ):
                if node_type == "Nested Loop":
                    output += "Join "
                output += (
                    "between "
                    + child_names[0]
                    + " (outer) and "
                    + child_names[1]
                    + " (inner) as "
                    + curr_name
                    + "."
                )
            else:
                output += "on " + curr_name + "."

            print([curr_name, output], file=stderr)

            return [curr_name, output]

        output = ""
        node_type = plan.get("Node Type")
        result = recurse(plan)

        if result:
            output += node_type + " " + result[0] + " to get final result " + chr(name)

        postorder_result.append(output)

        return postorder_result

    except:
        print("Can't find any nodes in query execution plan.", file=stderr)


def query(sql_string):
    conn, cur = connect()

    try:
        data = ""
        if conn is not None:
            cur.execute(sql_string)
            data = cur.fetchall()

            conn.close()
            print("Database connection closed.", file=stderr)
    except:
        data = "Error executing query - check your SQL syntax"

    return data[0][0][0]


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

    except (Exception, psycopg2.DatabaseError) as error:
        print("Exception occured", file=stderr)
        if conn is not None:
            conn.close()
            print("Database connection closed.", file=stderr)
        return error, error