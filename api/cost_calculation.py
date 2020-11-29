import numpy as np

qep_optimal = {
    'name': 'qep_optimal',
    'selectivities': {
        'attr1': 0.02,
        'attr2': 0.02,
        'attr3': 0.02,
        'attr4': 0.02
    },
    'Startup Cost': 1000,
    'Total Cost': 160114.59,
    'Plan Rows': 120087,
    'Actual Startup Time': 0.563,
    'Actual Total Time': 7012.146,
    'Actual Rows': 123794,
}

qep1 = {
    'name': 'qep1',
    'selectivities': {
        'attr1': 0.2,
        'attr2': 0.2,
        'attr3': 0.2,
        'attr4': 0.2
    },
    'Startup Cost': 0,
    'Total Cost': 190890.74,
    'Plan Rows': 1200866,
    'Actual Startup Time': 0.722,
    'Actual Total Time': 4978.087,
    'Actual Rows': 1200813,
}


qep2 = {
    'name': 'qep2',
    'selectivities': {
        'attr1': 0.1,
        'attr2': 0.1,
        'attr3': 0.1,
        'attr4': 0.1
    },
    'Startup Cost': 0,
    'Total Cost': 190890.74,
    'Plan Rows': 600470,
    'Actual Startup Time': 0.777,
    'Actual Total Time': 4978.57,
    'Actual Rows': 598028,
}


qep3 = {
    'name': 'qep3',
    'selectivities': {
        'attr1': 0.0,
        'attr2': 0.0,
        'attr3': 0.0,
        'attr4': 0.0
    },
    'Startup Cost': 1000,
    'Total Cost': 148165.89,
    'Plan Rows': 600,
    'Actual Startup Time': 6489.005,
    'Actual Total Time': 6507.625,
    'Actual Rows': 0,
}


qeps = [qep_optimal, qep1, qep2, qep3]

estimated_cost_per_row = []
actual_cost_per_row = []

for qep in qeps:
    try:
        estimated_cost_per_row.append(
            ( qep['Startup Cost'] + qep['Total Cost'] ) / qep['Plan Rows']
        )
    except ZeroDivisionError:
        estimated_cost_per_row.append(
            qep['Startup Cost'] + qep['Total Cost']
        )

    try:
        actual_cost_per_row.append(
            ( qep['Actual Startup Time'] + qep['Actual Total Time'] ) / qep['Actual Rows']
        )
    except ZeroDivisionError:
        actual_cost_per_row.append(
            qep['Actual Startup Time'] + qep['Actual Total Time']
        )

selectivities = [v['selectivities']['attr1'] for v in qeps]
print('selectivity: ', selectivities)
print('estimated_cost_per_row: ', estimated_cost_per_row)
print('actual_cost_per_row: ', actual_cost_per_row)