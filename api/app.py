from flask import Flask, request
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

    # Gets the query execution plan (qep) recommended by postgres for this query
    qep_sql_string = "EXPLAIN (FORMAT JSON, BUFFERS) " + request_data["query"]

    # Get the optimal qep
    optimal_qep = query(qep_sql_string, explain=True)
    optimal_qep = json.dumps(ast.literal_eval(str(optimal_qep)))

    explanation = postorder_qep(optimal_qep)
    optimal_qep = json.loads(optimal_qep)

    # Get the selectivity variation of this qep.
    get_selectivities(request_data["query"], request_data["predicates"])

    # JUST FOR TESTING AT THE MOMENT
    # GET A HISTOGRAM
    get_histogram()

    return json.dumps({"output": optimal_qep, "explanation": explanation})


""" #################################################################### 
Calculates the specific selectivities of each predicate in the query.
#################################################################### """


def get_selectivities(sql_string, predicates):
    try:
        # Find the place in query to add additional clauses for selectivity
        where_index = sql_string.find("where")

        # If there is a where statement, pull all conditions from it
        if where_index != -1:
            # Go to start of where statement
            where_index += 6

            # Get where clauses to find predicates
            clauses = sql_string[where_index:].split("\n")
            conditions = []

            # Pull the where conditions from the query
            for clause in clauses:
                # Check if it's a where comparative clause
                if any(i in clause for i in ">=<!"):
                    clean_clause = "".join(clause.split("\t"))
                    clean_clause = "".join(clean_clause.split("and "))
                    conditions.append(clean_clause)

            # Get the tablename and attribute name for querying pg_stats to get histogram
            # We only care about predicates the user wants to vary
            for predicate in predicates:
                predicate_values = predicate.split("_")
                table_names = {
                    "r": "region",
                    "n": "nation",
                    "s": "supplier",
                    "c": "customer",
                    "p": "part",
                    "ps": "partsupp",
                    "o": "orders",
                    "l": "lineitem",
                }
                predicate_table = table_names[predicate_values[0]]
                predicate_attribute = predicate
                predicate_condition = ""

                # Get condition for predicate
                for condition in conditions:
                    if predicate in condition:
                        predicate_condition = condition
                        break

                # If no predicate among conditions, ignore it
                if predicate_condition == "":
                    continue

                predicate_comparator = ""
                comparators = ["<=", ">=", "!=", ">", "<", "="]
                for comparator in comparators:
                    if predicate_condition.find(comparator) != -1:
                        predicate_comparator = comparator
                        break

                predicate_conditions = re.split(">=|<=|!=|<|>|=", predicate_condition)

                predicate_condition = {
                    "left": predicate_conditions[0].strip(" "),
                    "comparator": predicate_comparator,
                    "right": predicate_conditions[1].strip(" "),
                }

                print(predicate_condition, file=stderr)

                # Get statistics from DBMS on predicate's desired selectivity
                # If it's an equality comparator, use MCV
                if (
                    predicate_condition["comparator"] == "="
                    or predicate_condition["comparator"] == "!="
                ):
                    # Use most common values (MSV) to determine selectivity requirement
                    statement = "SELECT null_frac, n_distinct, most_common_vals, most_common_freqs FROM pg_stats WHERE tablename='{}' AND attname='{}';".format(
                        predicate_table, predicate_attribute
                    )

                    # Query for the MSV
                    stats = query(statement)
                    print(stats, file=stderr)
                # Else if it's a range comparator, we use the histogram bounds to determine selectivity
                else:
                    statement = "SELECT histogram_bounds FROM pg_stats WHERE tablename='{}' AND attname='{}';".format(
                        predicate_table, predicate_attribute
                    )

                    # Query for the histogram
                    stats = query(statement)
                    print(stats, file=stderr)

        # No where clause, we just assume 100% for selectivity
        else:
            print("No where clause", file=stderr)
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
            output += node_type + " " + result[0] + " to get final result " + chr(name)

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


# """ #################################################################### 
# get the cost of performing scans on relations
# #################################################################### """


# def get_scan_cost(qep_sql_string):
#     # various scan settings. Only enable one (one-hot)
#     scan_types = [
#         "enable_bitmapscan",
#         "enable_indexscan",
#         "enable_seqscan",
#         "enable_tidscan",
#     ]
#     scan_types_qeps = []

#     for scan_type_on in scan_types:
#         scan_type_sql_string = reset_connection_settings_string(
#             "join"
#         )  # make sure joins are all enabled

#         # create the one-hot scan type query
#         for scan_type_inner in scan_types:
#             if scan_type_inner == scan_type_on:
#                 scan_type_sql_string = (
#                     scan_type_sql_string + f"SET {scan_type_inner} = ON;"
#                 )
#             else:
#                 scan_type_sql_string = (
#                     scan_type_sql_string + f"SET {scan_type_inner} = OFF;"
#                 )
#         scan_type_sql_string = scan_type_sql_string + qep_sql_string

#         print(scan_type_sql_string, file=stderr)
#         print("*" * 50, file=stderr)

#         # get the qep for the one-hot scan type
#         scan_type_on_qep = query(scan_type_sql_string, explain=True)
#         scan_type_on_qep = json.dumps(ast.literal_eval(str(scan_type_on_qep)))
#         scan_type_on_qep = json.loads(scan_type_on_qep)

#         scan_types_qeps.append(scan_type_on_qep)

#     # reset the types of scans enabled to ON
#     reset_scan_type_sql_string = ""
#     for scan_type in scan_types:
#         reset_scan_type_sql_string = (
#             reset_scan_type_sql_string + f"SET {scan_type} = ON;"
#         )
#     query(reset_scan_type_sql_string)

#     # get the cost of scanning various relations
#     scan_types_qep_relations_costs = []
#     for i, scan_types_qep in enumerate(scan_types_qeps):

#         queried_relations = []

#         def recurse(qep):
#             if type(qep) is not dict:
#                 return
#             if "Relation Name" in qep.keys():
#                 queried_relations.append(qep)
#             if "Plan" in qep.keys():
#                 recurse(qep["Plan"])
#             if "Plans" in qep.keys():
#                 for plan in qep["Plans"]:
#                     recurse(plan)

#         recurse(scan_types_qep)

#         scan_types_qep_relations_costs.append({scan_types[i]: queried_relations})

#     # just get the information that we are interested in
#     for scan_types_qep_relations_cost in scan_types_qep_relations_costs:
#         print(scan_types_qep_relations_cost.keys(), "\n", file=stderr)

#         for key in scan_types_qep_relations_cost.keys():
#             for item in scan_types_qep_relations_cost[key]:
#                 for item_key in list(item):
#                     if item_key not in [
#                         "Node Type",
#                         "Relation Name",
#                         "Startup Cost",
#                         "Total Cost",
#                     ]:
#                         del item[item_key]
#                     if item_key == "Node Type":
#                         if item[item_key] == "Bitmap Heap Scan":
#                             item[item_key] = "Bitmap Scan"

#     print(scan_types_qep_relations_costs, file=stderr)
#     for scan_type in scan_types_qep_relations_costs:
#         print(scan_type.keys(), file=stderr)

#         for relation in scan_type.values():
#             print(relation, "\n", file=stderr)
#         print("\n\n", file=stderr)
#     return scan_types_qep_relations_costs


# """ #################################################################### 
# used to create the reset_sql_string to enable all types of joins and scans (to conduct a normal query)
# #################################################################### """


# def reset_connection_settings_string(reset_type):
#     reset_sql_string = ""

#     scan_types = [
#         "enable_bitmapscan",
#         "enable_indexscan",
#         "enable_seqscan",
#         "enable_tidscan",
#     ]
#     join_types = ["enable_hashjoin", "enable_mergejoin", "enable_nestloop"]

#     if reset_type == "all":
#         for scan_type in scan_types:
#             reset_sql_string = reset_sql_string + f"SET {scan_type} = ON;"
#         for join_type in join_types:
#             reset_sql_string = reset_sql_string + f"SET {join_type} = ON;"
#     if reset_type == "join":
#         for join_type in join_types:
#             reset_sql_string = reset_sql_string + f"SET {join_type} = ON;"
#     if reset_type == "scan":
#         for scan_type in scan_types:
#             reset_sql_string = reset_sql_string + f"SET {scan_type} = ON;"

#     return reset_sql_string


""" #################################################################### 
used to get the histgram for a specific attribute from a table 
#################################################################### """
def get_histogram():
    print("hello", file=stderr)

    # dummy values for coding first. assume we are doing a less-than query 
    relation = 'lineitem'
    attribute = 'l_extendedprice'
    # attribute_value = 1501.51
    # attribute_value = 923
    attribute_value = 51011.8
    operator = '>='




    # retrieve a histogram
    sql_string = f"SELECT histogram_bounds FROM pg_stats WHERE tablename = '{relation}' AND attname = '{attribute}';"
    result = query(sql_string)
    result = result[0]
    histogram = result[1:-2]
    histogram = histogram.split(',')
    histogram = [float(i) for i in histogram]
    num_buckets = len(histogram) - 1

    print(histogram, file=stderr)
    print(type(histogram), file=stderr)
    print(len(histogram), file=stderr)
    print(list(histogram), file=stderr)


    # get the selectivity for the given attribute value
    leftbound = 0
    for i in range(num_buckets):
        if attribute_value > histogram[i]:
            leftbound = i


    selectivity = (leftbound + (attribute_value - histogram[leftbound])/(histogram[leftbound+1] - histogram[leftbound])) / num_buckets
    
    if operator in ["<=", "<"]:
        pass
    elif operator in [">=", ">"]:
        selectivity = 1 - selectivity
    print("selectivity of query: ", selectivity, file=stderr)

    print(len(histogram), file=stderr)
    for i in range(0, len(histogram), 10):
        print(histogram[i], file=stderr)
    
    
    # get 20% below until 20% above, in 10% intervals
    selectivities = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    lower = [v for v in selectivities if v <= selectivity]
    higher = [v for v in selectivities if v >= selectivity]
    lower.sort()
    higher.sort()

    selectivities_required = []
    
    if len(lower) != 0:
        lower_leftbound = max(len(lower) - 2, 0)
        print('lower_leftbound, ', lower_leftbound, file=stderr)
        for i in lower[lower_leftbound:]:
            selectivities_required.append(i)

    if len(higher) != 0:
        higher_rightbound = min( len(higher), 2)
        print('higher_rightbound, ', higher_rightbound, file=stderr)
        for i in higher[:higher_rightbound]:
            selectivities_required.append(i)
    
    selectivities_required.sort()
    selectivities_required = list(set(selectivities_required))

    values_required = {}
    for i in selectivities_required:
        index = int(i * 100)

        if operator in ["<=", "<"]:
            values_required[f"{i}"] = histogram[index]
        elif operator in [">=", ">"]:
            values_required[f"{1-i}"] = histogram[index]

        

    
    # craft return value 
    return_value = {    
        'relation': relation,
        'attribute': attribute,
        'attribute_value': attribute_value,
        'queried_selectivity': selectivity,
        'histogram_bounds': values_required
    }
    
            
    print(return_value, file=stderr)

    return