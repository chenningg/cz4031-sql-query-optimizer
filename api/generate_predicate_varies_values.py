
from sys import stderr
from datetime import date
from database_query_helper import *



""" #################################################################### 
convert postgresql returned value that is dict-like to a list
#################################################################### """
def dict_like_to_list(dict_like, output_type):
    if output_type == 'float':
        # print("float output", dict_like, file=stderr)
        output = dict_like[1:-1]
        output = output.split(',')
        cleaned_output = [float(i) for i in output]
    if output_type == 'integer':
        # print("integer output", dict_like, file=stderr)
        output = dict_like[1:-1]
        output = output.split(',')
        cleaned_output = [int(i) for i in output]        
    if output_type == 'date':
        # print("date output", dict_like, file=stderr)
        output = dict_like[1:-1]
        output = output.split(',')
        cleaned_output = [date.fromisoformat(i) for i in output]
    return cleaned_output


""" #################################################################### 
used to get the datatype of the attribute 
#################################################################### """
def get_attribute_datatype(relation, attribute):
    # print(relation, file=stderr)
    # print(attribute, file=stderr)
    
    # retrieve a histogram
    sql_string = f"SELECT data_type FROM information_schema.columns WHERE table_name = '{relation}' AND column_name = '{attribute}';"
    result = query(sql_string)
    result = result[0]
    
    return result

""" #################################################################### 
used to get the histgram for a specific attribute from a table 
#################################################################### """
def get_histogram(relation, attribute, conditions):
    operators, attribute_values, attribute_datatypes = [], [], []
    predicate_datatype = ""
    for condition in conditions:
        operators.append(condition[0])
        datatype = get_attribute_datatype(relation, attribute)
        attribute_datatypes.append(datatype)
        
        if datatype == 'integer':
            attribute_values.append(int(condition[1]))
        if datatype == 'numeric':
            attribute_values.append(float(condition[1]))
            predicate_datatype = "numeric"
        elif datatype == 'date':
            attribute_values.append(date.fromisoformat(condition[1][1:-1]))
            predicate_datatype = "date"
        else:
            attribute_values.append(condition[1])
            predicate_datatype = "string"

    
    if len(operators) == 0:
        return "ERROR - please give at least one valid predicate to explore"
    
    # print(operators, file=stderr)
    # print(attribute_values, file=stderr)
    # print(attribute_datatypes, file=stderr)
    

    return_values = {
        'relation': relation,
        'attribute': attribute,
        'datatype': predicate_datatype,
        'conditions': {}
    }

    for i in range(len(operators)):
        operator = operators[i]
        attribute_value = attribute_values[i]
        attribute_datatype = attribute_datatypes[i]
        condition = conditions[i]

        # retrieve a histogram
        sql_string = f"SELECT histogram_bounds FROM pg_stats WHERE tablename = '{relation}' AND attname = '{attribute}';"
        result = query(sql_string)
        result = result[0]
        # print("result", result, file=stderr)

        print("datatype: ", attribute_datatype, file=stderr)
        if attribute_datatype == 'numeric':
            histogram = dict_like_to_list(result, 'float')
        if attribute_datatype == 'integer':
            histogram = dict_like_to_list(result, 'integer')            
        if attribute_datatype == 'date':
            histogram = dict_like_to_list(result, 'date')
        
        num_buckets = len(histogram) - 1

        # print(histogram, file=stderr)
        # print(type(histogram), file=stderr)
        # print(len(histogram), file=stderr)
        # print(list(histogram), file=stderr)

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
        # print("selectivity of query: ", selectivity, file=stderr)

        # print(len(histogram), file=stderr)
        # for i in range(0, len(histogram), 10):
        #     print(histogram[i], file=stderr)
        
        
        # get 20% below until 20% above, in 10% intervals
        selectivities = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        
        lower = [v for v in selectivities if v <= selectivity]
        higher = [v for v in selectivities if v >= selectivity]
        lower.sort()
        higher.sort()

        selectivities_required = []
        
        
        if len(lower) != 0:
            lower_leftbound = max(len(lower) - 2, 0)
            # print('lower_leftbound, ', lower_leftbound, file=stderr)
            for i in lower[lower_leftbound:]:
                selectivities_required.append(i)

        if len(higher) != 0:
            higher_rightbound = min( len(higher), 2)
            # print('higher_rightbound, ', higher_rightbound, file=stderr)
            for i in higher[:higher_rightbound]:
                selectivities_required.append(i)
        
        selectivities_required.sort()
        selectivities_required = list(set(selectivities_required))

        values_required = {}
        for i in selectivities_required:
            index = int(i * num_buckets)

            if operator in ["<=", "<"]:
                values_required[i] = histogram[index]
            elif operator in [">=", ">"]:
                values_required[1-i] = histogram[index]
        
        # craft return value 
        return_value = {    
            'queried_selectivity': selectivity,
            'histogram_bounds': values_required
        }
        
                
        # print(return_value, file=stderr)

        # print("condition: ", condition, file=stderr)
        return_values['conditions'][condition] = return_value

    # print(return_values, file=stderr)
    return return_values


# """ #################################################################### 
# used to get the most common values for a specific attribute from a table 
# #################################################################### """
# def get_mcv():
#     # dummy values for coding first. assume we are doing a less-than query 
#     relation = 'lineitem'
#     # attribute = 'l_shipmode'
#     attribute = 'l_extendedprice'
#     attribute_value = 1501.51
#     # attribute_value = 923
#     # attribute_value = 'DELIVER IN PERSON'
#     operator = '='

#     attribute_datatype = get_attribute_datatype(relation, attribute)
#     print(attribute_datatype, file=stderr)

    
#     # retrieve a MCV table
#     sql_string = f"SELECT null_frac, n_distinct, most_common_vals, most_common_freqs FROM pg_stats WHERE tablename='{relation}' AND attname='{attribute}';"
#     result = query(sql_string)
#     print(result, file=stderr)

#     null_frac, n_distinct, most_common_vals, most_common_freqs = result[0], result[1], result[2], result[3]

#     print("="*50, file=stderr)
#     print(null_frac, file=stderr)
#     print(n_distinct, file=stderr)
#     print(most_common_vals, file=stderr)
#     print(most_common_freqs, file=stderr)


#     if attribute_datatype == 'character':
#         most_common_vals = dict_like_to_list(most_common_vals, 'string')
#     if attribute_datatype == 'numeric':
#         most_common_vals = dict_like_to_list(most_common_vals, 'float')
    
#     print("="*50, file=stderr)

#     print(null_frac, file=stderr)
#     print(n_distinct, file=stderr)
#     print(most_common_vals, file=stderr)
#     print(most_common_freqs, file=stderr)

#     if attribute_value in most_common_vals:
#         index = most_common_vals.index(attribute_value)
#         selectivity = most_common_freqs[index]
#         print(selectivity, file=stderr)
#     else:
#         selectivity = (1 - sum(most_common_freqs)) / (n_distinct - len(most_common_vals))
        


        
        
        
#         # result = result[0]
#         # histogram = result[1:-2]
#         # histogram = histogram.split(',')
#         # histogram = [float(i) for i in histogram]
#         # num_buckets = len(histogram) - 1

#         # print(histogram, file=stderr)
#         # print(type(histogram), file=stderr)
#         # print(len(histogram), file=stderr)
#         # print(list(histogram), file=stderr)

    

