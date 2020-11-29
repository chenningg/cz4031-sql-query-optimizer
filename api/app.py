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

    original_qep, original_graph, original_explanation = execute_plan(qep_sql_string)

    original_predicate_selectivity_data = []


    print("=" * 100, file=stderr)
    for predicate_data in get_selectivities(sql_query, request_data["predicates"]):
        attribute = predicate_data['attribute']

        for operator in predicate_data['conditions']:
            queried_selectivity = predicate_data['conditions'][operator]['queried_selectivity']
            queried_value = predicate_data['conditions'][operator]['histogram_bounds'][queried_selectivity]
            
            original_predicate_selectivity_data.append({
                'attribute': attribute,
                'operator': operator,
                'queried_value': queried_value,
                'new_value': None,
                'queried_selectivity': queried_selectivity,
                'new_selectivity': None                
            })

    # print("a: ", a, file=stderr)
    # print("=" * 100, file=stderr)


    all_generated_plans = {
        0: {
            "qep": original_qep,
            "graph": original_graph,
            "explanation": original_explanation,
            "predicate_selectivity_data": original_predicate_selectivity_data,
            "estimated_cost_per_row": calculate_estimated_cost_per_row(original_qep),
        }
    }
    # Get the selectivity variation of this qep.
    if len(request_data["predicates"]) != 0:
        new_selectivities = get_selectivities(sql_query, request_data["predicates"])
        print("new selectivities: ", new_selectivities, file=stderr)

        new_plans = Generator().generate_plans(
            new_selectivities, sql_query
        )  # array of (new_queries, predicate_selectivity_data)
        
        # predicate_selectivity_data format: n tuples of format (attribute, operator, old value, new value, old selectivity, new selectivity)
        for index, (new_query, predicate_selectivity_data) in enumerate(new_plans):

            predicate_selectivity_combination = []

            for i in range(len(predicate_selectivity_data)):
                predicate_selectivity = {
                        'attribute': predicate_selectivity_data[i][0],
                        'operator': predicate_selectivity_data[i][1],
                        'queried_value': predicate_selectivity_data[i][2],
                        'new_value': predicate_selectivity_data[i][3],
                        'queried_selectivity': predicate_selectivity_data[i][4],
                        'new_selectivity': predicate_selectivity_data[i][5]
                    }
                predicate_selectivity_combination.append(predicate_selectivity)

            # print("predicate_selectivity_combination", predicate_selectivity_combination, file=stderr)

            qep_sql_string = create_qep_sql(new_query)
            qep, graph, explanation = execute_plan(qep_sql_string)
            all_generated_plans[index + 1] = {
                "qep": qep,
                "graph": graph,
                "explanation": explanation,
                "predicate_selectivity_data": predicate_selectivity_combination,
                "estimated_cost_per_row": calculate_estimated_cost_per_row(qep),
            }
    
    data = {"data": all_generated_plans}
    clean_json(data)

    return data


def clean_json(d):
    if isinstance(d, dict):
        for v in d.values():
            yield from clean_json(v)
    elif isinstance(d, list):
        for v in d:
            yield from clean_json(v)
    else:
        if type(d) == date:
            d = d.strftime("%Y-%m-%d")


def execute_plan(qep_sql_string):
    # Get the optimal qep
    qep = query(qep_sql_string, explain=True)
    qep = json.dumps(ast.literal_eval(str(qep)))

    graph = visualize_query(qep)
    explanation = postorder_qep(qep)
    qep = json.loads(qep)
    return qep, graph, explanation


def create_qep_sql(sql_query):
    return "EXPLAIN (COSTS, VERBOSE, BUFFERS, FORMAT JSON) " + sql_query


""" #################################################################### 
Calculates the specific selectivities of each predicate in the query.
#################################################################### """
def get_selectivities(sql_string, predicates):
    try:
        sqlparser = SQLParser()
        sqlparser.parse_query(sql_string)

        predicate_selectivities = []
        for predicate in predicates:
            relation = var_prefix_to_table[predicate.split("_")[0]]

            conditions = sqlparser.comparison[predicate]

            if conditions[0][0] in equality_comparators:
                # some_returned_json = most_common_value()
                pass
            else:
                histogram_data = get_histogram(relation, predicate, conditions)
                res = {}
                for k, v in histogram_data["conditions"].items():  # k is like ('<', 5)
                    if len(k) == 2:
                        operator = k[0]
                        new_v = {kk: vv for kk, vv in v.items()}
                        cur_selectivity = new_v["queried_selectivity"]
                        new_v["histogram_bounds"][cur_selectivity] = (
                            k[1]
                            if histogram_data["datatype"] != "date"
                            else date.fromisoformat(k[1][1:-1])
                        )
                        res[operator] = new_v
                histogram_data["conditions"] = dict(
                    sorted(res.items())
                )  # make sure that < always comes first

                # histogram_data returns the histogram bounds for a single predicate
                predicate_selectivities.append(histogram_data)

        print("predicate_selectivities", predicate_selectivities)
        return predicate_selectivities

        # single res example
        # {'relation': 'orders', 'attribute': 'o_orderdate', 'datatype': 'date', 'conditions': {'<': {'queried_selectivity': 0.3060869565217391, 'histogram_bounds': {'0.2': datetime.date(1993, 4, 16), '0.4': datetime.date(1994, 8, 15), '0.3': datetime.date(1993, 12, 18), '0.5': datetime.date(1995, 4, 13), '0.3060869565217391': datetime.date(1994, 1, 1)}}, '>=': {'queried_selectivity': 0.7303999999999999, 'histogram_bounds': {'0.4': datetime.date(1995, 12, 8), '0.30000000000000004': datetime.date(1996, 8, 8), '0.19999999999999996': datetime.date(1997, 4, 11), '0.09999999999999998': datetime.date(1997, 12, 8), '0.7303999999999999': datetime.date(1993, 10, 1)}}}}

        # sql_string_replaced = sql_string.replace(conditions[0][1], "{{" + str(predicate) + "}}")
        # some_returned_json['jinja_query'] = sql_string_replaced
        # res.append(some_returned_json)

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
