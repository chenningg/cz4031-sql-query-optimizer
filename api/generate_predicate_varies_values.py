from sys import stderr
from datetime import date
from database_query_helper import *
from custom_errors import *


""" #################################################################### 
convert postgresql returned value that is dict-like to a list
#################################################################### """


def dict_like_to_list(dict_like, output_type):
    try:
        if output_type == "float":
            output = dict_like[1:-1]
            output = output.split(",")
            cleaned_output = [float(i) for i in output]
        if output_type == "integer":
            output = dict_like[1:-1]
            output = output.split(",")
            cleaned_output = [int(i) for i in output]
        if output_type == "date":
            output = dict_like[1:-1]
            output = output.split(",")
            cleaned_output = [date.fromisoformat(i) for i in output]
        return cleaned_output
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in dict_like_to_list() - Unable to convert dictionary-like object to a list."
        )


""" #################################################################### 
used to get the datatype of the attribute 
#################################################################### """


def get_attribute_datatype(relation, attribute):
    try:
        # retrieve a histogram
        sql_string = f"SELECT data_type FROM information_schema.columns WHERE table_name = '{relation}' AND column_name = '{attribute}';"
        result = query(sql_string)
        result = result[0]
        return result
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in get_attribute_datatype() - Unable to get the datatype of an attribute."
        )


""" #################################################################### 
used to get the histgram for a specific attribute from a table 
#################################################################### """


def get_histogram(relation, attribute, conditions):
    try:
        operators, attribute_values, attribute_datatypes = [], [], []
        predicate_datatype = ""

        # recreate the data in the correct type
        for condition in conditions:
            operators.append(condition[0])
            datatype = get_attribute_datatype(relation, attribute)
            attribute_datatypes.append(datatype)

            if datatype == "integer":
                attribute_values.append(int(condition[1]))
            if datatype == "numeric":
                attribute_values.append(float(condition[1]))
                predicate_datatype = "numeric"
            elif datatype == "date":
                attribute_values.append(date.fromisoformat(condition[1][1:-1]))
                predicate_datatype = "date"
            else:
                attribute_values.append(condition[1])
                predicate_datatype = "string"

        # fail condition
        if len(operators) == 0:
            return "ERROR - Please give at least one valid predicate to explore."

        # dictionary object to store return result
        return_values = {
            "relation": relation,
            "attribute": attribute,
            "datatype": predicate_datatype,
            "conditions": {},
        }

        # do for every condition
        for i in range(len(operators)):
            operator = operators[i]
            attribute_value = attribute_values[i]
            attribute_datatype = attribute_datatypes[i]
            condition = conditions[i]

            # retrieve a histogram
            sql_string = f"SELECT histogram_bounds FROM pg_stats WHERE tablename = '{relation}' AND attname = '{attribute}';"
            result = query(sql_string)
            result = result[0]

            if attribute_datatype == "numeric":
                histogram = dict_like_to_list(result, "float")
            if attribute_datatype == "integer":
                histogram = dict_like_to_list(result, "integer")
            if attribute_datatype == "date":
                histogram = dict_like_to_list(result, "date")

            num_buckets = len(histogram) - 1

            # get the selectivity for the given attribute value
            leftbound = 0
            for i in range(num_buckets):
                if attribute_value > histogram[i]:
                    leftbound = i

            selectivity = (
                leftbound
                + (attribute_value - histogram[leftbound])
                / (histogram[leftbound + 1] - histogram[leftbound])
            ) / num_buckets

            # inverse logic for the >= and > operators, since prior logic assumes a <= or < operator
            if operator in ["<=", "<"]:
                pass
            elif operator in [">=", ">"]:
                selectivity = 1 - selectivity

            # set floor and ceiling
            if selectivity <= 0:
                selectivity = 0
            if selectivity >= 1:
                selectivity = 1

            # get 20% below until 20% above, in 10% intervals
            selectivities = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

            lower = [v for v in selectivities if v <= selectivity]
            higher = [v for v in selectivities if v >= selectivity]
            lower.sort()
            higher.sort()

            selectivities_required = []

            if len(lower) != 0:
                lower_leftbound = max(len(lower) - 2, 0)
                for i in lower[lower_leftbound:]:
                    selectivities_required.append(i)

            if len(higher) != 0:
                higher_rightbound = min(len(higher), 2)
                for i in higher[:higher_rightbound]:
                    selectivities_required.append(i)

            selectivities_required.sort()
            selectivities_required = list(set(selectivities_required))

            # get the corresponding values to the selectivity that we want from the histogram
            values_required = {}
            for i in selectivities_required:
                if operator in ["<=", "<"]:
                    pass
                elif operator in [">=", ">"]:
                    i = 1 - i

                index = int(i * num_buckets)

                if operator in ["<=", "<"]:
                    values_required[i] = histogram[index]
                elif operator in [">=", ">"]:
                    values_required[1 - i] = histogram[index]

            # craft return value
            return_value = {
                "queried_selectivity": selectivity,
                "histogram_bounds": values_required,
            }

            return_values["conditions"][condition] = return_value

        return return_values
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in get_histogram() - Unable to obtain histogram for the attribute."
        )
