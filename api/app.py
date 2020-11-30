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
from sqlparser import *
from generator import Generator
from query_visualizer_explainer import *
from custom_errors import *


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
    try:
        # Gets the request data from the frontend
        request_data = request.json
        sql_query = request_data["query"]

        # Gets the query execution plan (qep) recommended by postgres for this query and also the graph and explanation
        qep_sql_string = create_qep_sql(sql_query)
        original_qep, original_graph, original_explanation = execute_plan(
            qep_sql_string
        )

        # Get the values and selectivity of various attributes for the original query
        original_predicate_selectivity_data = []

        for predicate_data in get_selectivities(sql_query, request_data["predicates"]):
            attribute = predicate_data["attribute"]

            for operator in predicate_data["conditions"]:
                queried_selectivity = predicate_data["conditions"][operator][
                    "queried_selectivity"
                ]
                queried_value = predicate_data["conditions"][operator][
                    "histogram_bounds"
                ][queried_selectivity]

                original_predicate_selectivity_data.append(
                    {
                        "attribute": attribute,
                        "operator": operator,
                        "queried_value": queried_value,
                        "new_value": None,
                        "queried_selectivity": queried_selectivity,
                        "new_selectivity": None,
                    }
                )

        # Add the original query and its details into the dictionary that will contain all queries
        all_generated_plans = {
            0: {
                "qep": original_qep,
                "graph": original_graph,
                "explanation": original_explanation,
                "predicate_selectivity_data": original_predicate_selectivity_data,
                "estimated_cost_per_row": calculate_estimated_cost_per_row(
                    original_qep
                ),
            }
        }

        # Get the selectivity variation of this qep.
        # if len(request_data["predicates"]) != 0:
        if len(original_predicate_selectivity_data) != 0:

            new_selectivities = get_selectivities(sql_query, request_data["predicates"])

            # array of (new_queries, predicate_selectivity_data)
            new_plans = Generator().generate_plans(new_selectivities, sql_query)

            # loop through every potential new plan and fire off a query, then get the result and save to our result dictionary
            for index, (new_query, predicate_selectivity_data) in enumerate(new_plans):
                predicate_selectivity_combination = []

                # predicate_selectivity_data format: n tuples of format (attribute, operator, old value, new value, old selectivity, new selectivity)
                for i in range(len(predicate_selectivity_data)):
                    predicate_selectivity = {
                        "attribute": predicate_selectivity_data[i][0],
                        "operator": predicate_selectivity_data[i][1],
                        "queried_value": predicate_selectivity_data[i][2],
                        "new_value": predicate_selectivity_data[i][3],
                        "queried_selectivity": predicate_selectivity_data[i][4],
                        "new_selectivity": predicate_selectivity_data[i][5],
                    }
                    predicate_selectivity_combination.append(predicate_selectivity)

                qep_sql_string = create_qep_sql(new_query)
                qep, graph, explanation = execute_plan(qep_sql_string)
                all_generated_plans[index + 1] = {
                    "qep": qep,
                    "graph": graph,
                    "explanation": explanation,
                    "predicate_selectivity_data": predicate_selectivity_combination,
                    "estimated_cost_per_row": calculate_estimated_cost_per_row(qep),
                }

        # get the best plan out of all the generated plans
        best_plan_id = get_best_plan_id(all_generated_plans)

        # clean out the date objects for json serializability
        data = {
            "data": all_generated_plans,
            "best_plan_id": best_plan_id,
            "status": "Successfully executed query.",
            "error": False,
        }
        clean_json(data)

        return data
    except CustomError as e:
        return {"status": str(e), "error": True}
    except Exception as e:
        print(str(e), file=stderr)
        return {
            "status": "Error in get_plans() - Unable to get plans for the query.",
            "error": True,
        }


""" #################################################################### 
used to clean a json dictionary 
#################################################################### """


def clean_json(d):
    try:
        if isinstance(d, dict):
            for v in d.values():
                yield from clean_json(v)
        elif isinstance(d, list):
            for v in d:
                yield from clean_json(v)
        else:
            # change date types to string
            if type(d) == date:
                d = d.strftime("%Y-%m-%d")
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError("Error in clean_json() - Unable to clean JSON dictionary.")


""" #################################################################### 
used to get the qep, graph and explanation for a given query string
#################################################################### """


def execute_plan(qep_sql_string):
    try:
        # Get the optimal qep
        qep = query(qep_sql_string, explain=True)
        qep = json.dumps(ast.literal_eval(str(qep)))

        graph, explanation = visualize_explain_query(qep)
        # explanation = postorder_qep(qep)
        qep = json.loads(qep)
        return qep, graph, explanation
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in execute_plan() - Unable to get QEP, graph, explanation."
        )


def create_qep_sql(sql_query):
    try:
        return "EXPLAIN (COSTS, VERBOSE, BUFFERS, FORMAT JSON) " + sql_query
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in create_qep_sql() - Unable to create sql_query string."
        )


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
            if conditions and conditions[0][0] not in equality_comparators:
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
        return predicate_selectivities
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in get_selectivities() - Unable to get the different selectivities for predicates."
        )


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
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in get_selective_qep() - Unable to parse the sql_string for 'WHERE' clause."
        )


""" #################################################################### 
get the best plan id in terms of cost, and the plan must be different from original plan
#################################################################### """


def get_best_plan_id(all_generated_plans):
    try:
        best_plan_id_cost = all_generated_plans[0]["estimated_cost_per_row"]
        best_plan_id = 0

        for plan_id in all_generated_plans:

            # ignore the original plan
            if plan_id != 0:

                # if the estimated cost per row is lower, the plan might be better
                if (
                    all_generated_plans[plan_id]["estimated_cost_per_row"]
                    < best_plan_id_cost
                ):

                    # if the plan is not the same plan as original plan
                    if (
                        all_generated_plans[plan_id]["explanation"]
                        != all_generated_plans[0]["explanation"]
                    ):
                        best_plan_id_cost = all_generated_plans[plan_id][
                            "estimated_cost_per_row"
                        ]
                        best_plan_id = plan_id

        return best_plan_id
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in get_best_plan_id() - Unable to get the lowest cost plan."
        )
