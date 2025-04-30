"""
This script is used to build Pareto fronts for the grid wheeling scenario.
"""

import sys
from h2_plan.algs import Pareto
from h2_plan.opt import OptimisationModel
from data.default import DefaultParams

booleans = {
        'vector_choice': {
                'LH2': sys.argv[2] == 'LH2',
                'NH3': sys.argv[2] == 'NH3',
        },
        'electrolysers': {
                'alkaline': True,
                'PEM': True,
                'SOFC': True,
        },
        'grid_connection': sys.argv[4] == 'True',
        'wind': sys.argv[6] in ['Wind', 'Both'],
        'solar': sys.argv[6] in ['Solar', 'Both'],
        'net_present_value': True,
        'grid_wheel': True,
}

parameters = DefaultParams().formulation_parameters
parameters.update({
        'booleans': booleans,
        'stage_duration': 168,
        'n_stages': 3,
        'n_stochastics': 3,
        'random_seed': 42,
        'relaxed_ramping': True,
        'hydrogen_price': 5,  # $/kg
        'vector_operating_duration': 1,
        'shipping_decision': 168,
        'wheel_period': 24,
})

key = sys.argv[1]
model = OptimisationModel(parameters, key=key)
pareto = Pareto(model, sys.argv[3], [float(x) for x in sys.argv[5].split(',')])
pareto.build_models(parameters)
