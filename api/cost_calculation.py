from sys import stderr

def calculate_estimated_cost_per_row(qep):
    try:
        estimated_cost_per_row = ( qep['Plan']['Startup Cost'] + qep['Plan']['Total Cost'] ) / qep['Plan']['Plan Rows']
    except ZeroDivisionError:
        estimated_cost_per_row = qep['Plan']['Startup Cost'] + qep['Plan']['Total Cost']
    # print('estimated_cost_per_row: ', estimated_cost_per_row, file=stderr)
    return estimated_cost_per_row
