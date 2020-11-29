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
from generator import Generator
from query_visualizer import *
from cost_calculation import *


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
    sql_query = request_data["query"]
    # Gets the query execution plan (qep) recommended by postgres for this query
    qep_sql_string = create_qep_sql(sql_query)

    optimal_qep, explanation = execute_plan(qep_sql_string)

    # print(request_data, file=stderr)

    all_generated_plans = {0: {"data": {"optimal_qep": optimal_qep, "explanation": explanation}}}
    # Get the selectivity variation of this qep.
    if len(request_data["predicates"]) != 0:
        new_selectivities = get_selectivities(sql_query, request_data["predicates"])
        new_plans = Generator().generate_plans(new_selectivities, sql_query) # array of (new_queries, predicate_selectivity_data)

        
        for index, (new_query, predicate_selectivity_data) in enumerate(new_plans):
            qep_sql_string = create_qep_sql(new_query)
            optimal_qep, explanation = execute_plan(qep_sql_string)
            all_generated_plans[index+1] = {"data": {"optimal_qep": optimal_qep, "explanation": explanation}}
    print(all_generated_plans)
    return json.dumps({"output": optimal_qep, "explanation": explanation})


def execute_plan(qep_sql_string):
    # Get the optimal qep
    optimal_qep = query(qep_sql_string, explain=True)
    optimal_qep = json.dumps(ast.literal_eval(str(optimal_qep)))

    # explanation = postorder_qep(optimal_qep)
    explanation = json.dumps(visualize_query(optimal_qep))
    optimal_qep = json.loads(optimal_qep)
    return optimal_qep, explanation

def create_qep_sql(sql_query): 
    return "EXPLAIN (COSTS, VERBOSE, BUFFERS, FORMAT JSON) " + sql_query


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
    try:
        sqlparser = SQLParser()
        sqlparser.parse_query(sql_string)

        predicate_selectivities = []
        for predicate in predicates:
            relation = var_prefix_to_table[predicate.split('_')[0]]
            
            conditions = sqlparser.comparison[predicate]
                        
            if conditions[0][0] in equality_comparators:
                # some_returned_json = most_common_value()
                pass
            else:
                histogram_data = get_histogram(relation, predicate, conditions)
                res = {}
                for k, v in histogram_data['conditions'].items(): # k is like ('<', 5)
                    if len(k) == 2: 
                        operator = k[0]
                        new_v = {kk: vv for kk, vv in v.items()}
                        cur_selectivity = new_v['queried_selectivity']
                        new_v['histogram_bounds'][cur_selectivity] = k[1] if histogram_data['datatype'] != "date" else date.fromisoformat(k[1][1:-1]) 
                        res[operator] = new_v
                histogram_data['conditions'] = dict(sorted(res.items())) # make sure that < always comes first
                
                # histogram_data returns the histogram bounds for a single predicate 
                predicate_selectivities.append(histogram_data)

        print('predicate_selectivities', predicate_selectivities)
        return predicate_selectivities
        
        # single res example 
        # {'relation': 'orders', 'attribute': 'o_orderdate', 'datatype': 'date', 'conditions': {'<': {'queried_selectivity': 0.3060869565217391, 'histogram_bounds': {'0.2': datetime.date(1993, 4, 16), '0.4': datetime.date(1994, 8, 15), '0.3': datetime.date(1993, 12, 18), '0.5': datetime.date(1995, 4, 13), '0.3060869565217391': datetime.date(1994, 1, 1)}}, '>=': {'queried_selectivity': 0.7303999999999999, 'histogram_bounds': {'0.4': datetime.date(1995, 12, 8), '0.30000000000000004': datetime.date(1996, 8, 8), '0.19999999999999996': datetime.date(1997, 4, 11), '0.09999999999999998': datetime.date(1997, 12, 8), '0.7303999999999999': datetime.date(1993, 10, 1)}}}}

                

                # sql_string_replaced = sql_string.replace(conditions[0][1], "{{" + str(predicate) + "}}")
                # some_returned_json['jinja_query'] = sql_string_replaced
                # res.append(some_returned_json)
        
            
    except:
        print("Error", file=stderr)

#     sqlparser = SQLParser()
#     sqlparser.parse_query(sql_string)

#     for predicate in predicates:
#         relation = var_prefix_to_table[predicate.split("_")[0]]

#         conditions = sqlparser.comparison[predicate]
#         print("conditions: ", conditions, file=stderr)

#         if conditions == []:
#             pass
#         # elif conditions[0][0] in equality_comparators:
#         #     # required_histogram_values = most_common_value()
#         #     pass
#         else:
#             conditions = [v for v in conditions if v[0][0] not in equality_comparators]

#             print("=" * 50, file=stderr)
#             required_histogram_values = get_histogram(relation, predicate, conditions)
#             print(required_histogram_values, file=stderr)
#             print(sql_string, file=stderr)

#             for condition in required_histogram_values["conditions"]:
#                 # print(type(condition[0]), file=stderr)
#                 # print(type(condition[1]), file=stderr)
#                 # print(f"{required_histogram_values['attribute']}\s*{condition[0]}\s*{condition[1]}", file=stderr)
#                 print("condition: ", condition, file=stderr)
#                 print(
#                     required_histogram_values["conditions"][condition][
#                         "histogram_bounds"
#                     ],
#                     file=stderr,
#                 )

#                 for new_selectivity in required_histogram_values["conditions"][
#                     condition
#                 ]["histogram_bounds"]:
#                     print(
#                         "new_selectivity: ",
#                         new_selectivity,
#                         required_histogram_values["conditions"][condition][
#                             "histogram_bounds"
#                         ][new_selectivity],
#                         file=stderr,
#                     )

#                 sql_string = re.sub(
#                     rf"{required_histogram_values['attribute']}\s*{condition[0]}\s*{condition[1]}",
#                     f"{required_histogram_values['attribute']} {condition[0]} {condition[1]}",
#                     sql_string,
#                 )
#                 print("sql_string modified: ", sql_string, file=stderr)

#             print("=" * 50, file=stderr)

#     return


# {'relation': 'lineitem', 'attribute': 'l_extendedprice', 'attribute_value': 51011.8, 'queried_selectivity': 0.30000000000000004, 'histogram_bounds': {'0.8': 15143.76, '0.6': 29445.06, '0.7': 22372.5, '0.5': 36378.45}}

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
