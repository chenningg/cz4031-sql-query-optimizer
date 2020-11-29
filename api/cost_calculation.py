from sys import stderr

def calculate_estimated_cost_per_row(qep):
    try:
        try:
            estimated_cost_per_row = ( qep['Plan']['Startup Cost'] + qep['Plan']['Total Cost'] ) / qep['Plan']['Plan Rows']
        except ZeroDivisionError:
            estimated_cost_per_row = qep['Plan']['Startup Cost'] + qep['Plan']['Total Cost']
        return estimated_cost_per_row
    except:
        raise Exception("Error in calculate_estimated_cost_per_row() - unable to calculate estimated costs")