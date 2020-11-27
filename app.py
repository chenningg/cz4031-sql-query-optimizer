from flask import Flask, request
from pipeline.sqlparser import SQLParser
from constant.constants import var_prefix_to_table, equality_comparators, range_comparators
import os
from dotenv import load_dotenv
from sys import stderr
import psycopg2
import ast
import json
import numpy as np
import sqlparse
import string
import re

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Load Flask config
app.config.from_object("config.Config")


@app.route("/")
def hello():
    return "Hey, you're not supposed to come here! But if you find this, please give us extra marks, thanks! (:"


""" #################################################################### 
used to generate a query plan based on the provided query
#################################################################### """


@app.route("/generate", methods=["POST"])
def get_plans():
    # Gets the request data from the frontend
    request_data = request.json

    print(request_data)

    # Gets the query execution plan (qep) recommended by postgres for this query
    qep_sql_string = "EXPLAIN (FORMAT JSON, BUFFERS) " + request_data["query"]

    clean_qep_sql_string = (
        reset_connection_settings_string("all") + qep_sql_string
    )  # make sure that all joins and scans are enabled

    # Get the optimal qep
    optimal_qep = query(clean_qep_sql_string, explain=True)
    optimal_qep = json.dumps(ast.literal_eval(str(optimal_qep)))

    explanation = postorder_qep(optimal_qep)
    optimal_qep = json.loads(optimal_qep)
    print('explanation ', explanation)
    print('optimalqep ', optimal_qep)

    # get the different scanning cost for this variations of this qep
    get_scan_cost(qep_sql_string)

    # Get the selectivity variation of this qep.
    get_selectivities(request_data["query"], request_data["predicates"])

    return json.dumps({"output": optimal_qep, "explanation": explanation})


""" #################################################################### 
Calculates the specific selectivities of each predicate in the query.
#################################################################### """

def histogram(): # should be made into a class for clarity 
    statement = "SELECT histogram_bounds FROM pg_stats WHERE tablename='{}' AND attname='{}';".format(
                predicate_table, predicate_attribute
            )

    # Query for the histogram
    stats = query(statement)


def most_common_value(): # should be made into a class for clarity 
    # Use most common values (MSV) to determine selectivity requirement
    statement = "SELECT null_frac, n_distinct, most_common_vals, most_common_freqs FROM pg_stats WHERE tablename='{}' AND attname='{}';".format(
        predicate_table, predicate_attribute
    )

    # Query for the MSV
    stats = query(statement)


def get_selectivities(sql_string, predicates):
    try:
        sqlparser = SQLParser()
        sqlparser.parse_query(sql_string)
        
        for predicate in predicates: 
            conditions = sqlparser.comparison[predicate]

            if conditions[0][0] in equality_comparators:
                some_returned_json = most_common_value()
            else: 
                some_returned_json = histogram()
        
        return some_returned_json
            
    except:
        print("Error", file=stderr)


""" #################################################################### 
Get optimal query plan for a given query by adding selectivities for each predicate.
Selectivity must have same number of keys as predicates.
#################################################################### """


def get_selective_qep(sql_string, selectivities, predicates):
    try:
        # Find the place in query to add additional clauses for selectivity
        where_index = sql_string.find("where")

        # If there is a where statement, just add selectivity clause in where statement
        if where_index != -1:
            # Go to start of where statement
            where_index += 6
            for i in range(0, len(predicates)):
                predicate = str(predicates[i])
                selectivity = str(selectivities[i])
                sql_string = (
                    sql_string[:where_index]
                    + " {} < {} and ".format(predicate, selectivity)
                    + sql_string[where_index:]
                )

            print(sql_string, file=stderr)
        else:
            print("No where clause", file=stderr)
    except:
        print("ERROR!", file=stderr)


""" #################################################################### 
Prints out a query plan 
#################################################################### """

# Output name of intermediate output
name = 65


def postorder_qep(plan):
    try:
        plan = json.loads(plan)
        plan = plan["Plan"]
        # print(json.dumps(plan, indent=2), file=stderr)

        postorder_result = []

        global name
        name = 65

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
            output += node_type + " " + \
                result[0] + " to get final result " + chr(name)

        postorder_result.append(output)

        return postorder_result

    except:
        print("Can't find any nodes in query execution plan.", file=stderr)


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
    except:
        data = "Error executing query - check your SQL syntax"

    if explain:
        return data[0][0][0]
    else:
        return data[0]


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

    except (Exception, psycopg2.DatabaseError) as error:
        print("Exception occured", file=stderr)
        if conn is not None:
            conn.close()
            print("Database connection closed.", file=stderr)
        return error, error


""" #################################################################### 
get the cost of performing scans on relations
#################################################################### """


def get_scan_cost(qep_sql_string):
    # various scan settings. Only enable one (one-hot)
    scan_types = [
        "enable_bitmapscan",
        "enable_indexscan",
        "enable_seqscan",
        "enable_tidscan",
    ]
    scan_types_qeps = []

    for scan_type_on in scan_types:
        scan_type_sql_string = reset_connection_settings_string(
            "join"
        )  # make sure joins are all enabled

        # create the one-hot scan type query
        for scan_type_inner in scan_types:
            if scan_type_inner == scan_type_on:
                scan_type_sql_string = (
                    scan_type_sql_string + f"SET {scan_type_inner} = ON;"
                )
            else:
                scan_type_sql_string = (
                    scan_type_sql_string + f"SET {scan_type_inner} = OFF;"
                )
        scan_type_sql_string = scan_type_sql_string + qep_sql_string

        print(scan_type_sql_string, file=stderr)
        print("*" * 50, file=stderr)

        # get the qep for the one-hot scan type
        scan_type_on_qep = query(scan_type_sql_string, explain=True)
        scan_type_on_qep = json.dumps(ast.literal_eval(str(scan_type_on_qep)))
        scan_type_on_qep = json.loads(scan_type_on_qep)

        scan_types_qeps.append(scan_type_on_qep)

    # reset the types of scans enabled to ON
    reset_scan_type_sql_string = ""
    for scan_type in scan_types:
        reset_scan_type_sql_string = (
            reset_scan_type_sql_string + f"SET {scan_type} = ON;"
        )
    query(reset_scan_type_sql_string)

    # get the cost of scanning various relations
    scan_types_qep_relations_costs = []
    for i, scan_types_qep in enumerate(scan_types_qeps):

        queried_relations = []

        def recurse(qep):
            if type(qep) is not dict:
                return
            if "Relation Name" in qep.keys():
                queried_relations.append(qep)
            if "Plan" in qep.keys():
                recurse(qep["Plan"])
            if "Plans" in qep.keys():
                for plan in qep["Plans"]:
                    recurse(plan)

        recurse(scan_types_qep)

        scan_types_qep_relations_costs.append(
            {scan_types[i]: queried_relations})

    # just get the information that we are interested in
    for scan_types_qep_relations_cost in scan_types_qep_relations_costs:
        print(scan_types_qep_relations_cost.keys(), "\n", file=stderr)

        for key in scan_types_qep_relations_cost.keys():
            for item in scan_types_qep_relations_cost[key]:
                for item_key in list(item):
                    if item_key not in [
                        "Node Type",
                        "Relation Name",
                        "Startup Cost",
                        "Total Cost",
                    ]:
                        del item[item_key]
                    if item_key == "Node Type":
                        if item[item_key] == "Bitmap Heap Scan":
                            item[item_key] = "Bitmap Scan"

    print(scan_types_qep_relations_costs, file=stderr)
    for scan_type in scan_types_qep_relations_costs:
        print(scan_type.keys(), file=stderr)

        for relation in scan_type.values():
            print(relation, "\n", file=stderr)
        print("\n\n", file=stderr)
    return scan_types_qep_relations_costs


""" #################################################################### 
used to create the reset_sql_string to enable all types of joins and scans (to conduct a normal query)
#################################################################### """


def reset_connection_settings_string(reset_type):
    reset_sql_string = ""

    scan_types = [
        "enable_bitmapscan",
        "enable_indexscan",
        "enable_seqscan",
        "enable_tidscan",
    ]
    join_types = ["enable_hashjoin", "enable_mergejoin", "enable_nestloop"]

    if reset_type == "all":
        for scan_type in scan_types:
            reset_sql_string = reset_sql_string + f"SET {scan_type} = ON;"
        for join_type in join_types:
            reset_sql_string = reset_sql_string + f"SET {join_type} = ON;"
    if reset_type == "join":
        for join_type in join_types:
            reset_sql_string = reset_sql_string + f"SET {join_type} = ON;"
    if reset_type == "scan":
        for scan_type in scan_types:
            reset_sql_string = reset_sql_string + f"SET {scan_type} = ON;"

    return reset_sql_string
