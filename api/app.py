from flask import Flask, request

from constant.constants import (
    var_prefix_to_table,
    equality_comparators,
    range_comparators,
)

from sys import stderr
import ast
import numpy as np

# import sqlparse
import string
import re
from datetime import date


# our own python scripts
from database_query_helper import *
from generate_predicate_varies_values import *
from postorder_qep import *
from sqlparser import *
from query_visualizer import *


# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Load Flask config
app = Flask(__name__)
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

    print(request_data, file=stderr)

    # Gets the query execution plan (qep) recommended by postgres for this query
    qep_sql_string = (
        "EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON) "
        + request_data["query"]
    )

    # Get the optimal qep
    optimal_qep = query(qep_sql_string, explain=True)
    optimal_qep = json.dumps(ast.literal_eval(str(optimal_qep)))

    # explanation = postorder_qep(optimal_qep)
    explanation = json.dumps(visualize_query(optimal_qep))
    optimal_qep = json.loads(optimal_qep)

    # Get the selectivity variation of this qep.
    if len(request_data["predicates"]) != 0:
        get_selectivities(request_data["query"], request_data["predicates"])

    return json.dumps({"output": optimal_qep, "explanation": explanation})


""" #################################################################### 
Calculates the specific selectivities of each predicate in the query.
#################################################################### """

# def histogram(): # should be made into a class for clarity
#     statement = "SELECT histogram_bounds FROM pg_stats WHERE tablename='{}' AND attname='{}';".format(
#                 predicate_table, predicate_attribute
#             )

#     # Query for the histogram
#     stats = query(statement)


# def most_common_value(): # should be made into a class for clarity
#     # Use most common values (MSV) to determine selectivity requirement
#     statement = "SELECT null_frac, n_distinct, most_common_vals, most_common_freqs FROM pg_stats WHERE tablename='{}' AND attname='{}';".format(
#         predicate_table, predicate_attribute
#     )

#     # Query for the MSV
#     stats = query(statement)


def get_selectivities(sql_string, predicates):
    sqlparser = SQLParser()
    sqlparser.parse_query(sql_string)

    for predicate in predicates:
        relation = var_prefix_to_table[predicate.split("_")[0]]

        conditions = sqlparser.comparison[predicate]
        print("conditions: ", conditions, file=stderr)

        if conditions == []:
            pass
        elif conditions[0][0] in equality_comparators:
            # required_histogram_values = most_common_value()
            pass
        else:
            print("=" * 50, file=stderr)
            required_histogram_values = get_histogram(relation, predicate, conditions)
            print(required_histogram_values, file=stderr)
            print(sql_string, file=stderr)

            for condition in required_histogram_values["conditions"]:
                # print(type(condition[0]), file=stderr)
                # print(type(condition[1]), file=stderr)
                # print(f"{required_histogram_values['attribute']}\s*{condition[0]}\s*{condition[1]}", file=stderr)
                print("condition: ", condition, file=stderr)
                print(
                    required_histogram_values["conditions"][condition][
                        "histogram_bounds"
                    ],
                    file=stderr,
                )

                for new_selectivity in required_histogram_values["conditions"][
                    condition
                ]["histogram_bounds"]:
                    print(
                        "new_selectivity: ",
                        new_selectivity,
                        required_histogram_values["conditions"][condition][
                            "histogram_bounds"
                        ][new_selectivity],
                        file=stderr,
                    )

                sql_string = re.sub(
                    rf"{required_histogram_values['attribute']}\s*{condition[0]}\s*{condition[1]}",
                    f"{required_histogram_values['attribute']} {condition[0]} {condition[1]}",
                    sql_string,
                )
                print("sql_string modified: ", sql_string, file=stderr)

            print("=" * 50, file=stderr)

    return


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
