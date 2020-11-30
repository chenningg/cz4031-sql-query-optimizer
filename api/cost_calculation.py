from sys import stderr
from custom_errors import *

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
