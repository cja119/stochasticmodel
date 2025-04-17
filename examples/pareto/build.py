"""
This script builds a Pareto front for the given optimisation model.
"""
import sys
from data.default import DefaultParams
from stochasticmodel.optimisation import OptimisationModel
from stochasticmodel.algorithms import Pareto

# Parse command-line arguments
vector_choice = sys.argv[2]
grid_connection = sys.argv[4]
wind_solar_choice = sys.argv[6]

booleans = {
        'vector_choice': {
                'LH2': vector_choice == 'LH2',
                'NH3': vector_choice == 'NH3',
        },
        'electrolysers': {
                'alkaline': True,
                'PEM': True,
                'SOFC': True,
        },
        'grid_connection': grid_connection == 'True',
        'wind': wind_solar_choice in ['Wind', 'Both'],
        'solar': wind_solar_choice in ['Solar', 'Both'],
        'net_present_value': True,
        'grid_wheel': False,
}

parameters = DefaultParams().formulation_parameters
parameters.update({
        'booleans': booleans,
        'stage_duration': 168,
        'n_stages': 39,
        'n_stochastics': 1,
        'random_seed': 42,
        'relaxed_ramping': True,
        'hydrogen_price': 5,  # $/kg
        'vector_operating_duration': 1,
        'shipping_decision': 168,
        'wheel_period': 24,
})

key = sys.argv[1]
model = OptimisationModel(parameters, key=key)

pareto = Pareto(
        model,
        sys.argv[3],
        [float(x) for x in sys.argv[5].split(',')]
)
pareto.build_models(parameters)
