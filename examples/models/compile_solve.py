import sys
import time
from os import getcwd, chdir, environ, popen, system
from dill import dump
import numpy as np
from stochasticmodel.optimisation import OptimisationModel
from data.default import DefaultParams
from stochasticmodel.algorithms import *

start_time = time.time()

booleans = {
    'vector_choice': {
        'LH2': sys.argv[3] == 'LH2',
        'NH3': sys.argv[3] == 'NH3'
    },
    'electrolysers': {
        'alkaline': True,
        'PEM': True,
        'SOFC': True
    },
    'grid_connection': False,
    'wind': sys.argv[6] in ['Wind', 'Both'],
    'solar': sys.argv[6] in ['Solar', 'Both'],
    'net_present_value': True
}

parameters = DefaultParams().formulation_parameters
parameters['booleans'] = booleans
parameters['stage_duration'] = int(sys.argv[5])
parameters['n_stages'] = int(sys.argv[1])
parameters['n_stochastics'] = int(sys.argv[2])
parameters['hydrogen_price'] = 5  # $/kg
parameters['random_seed'] = int(sys.argv[4])
parameters['relaxed_ramping'] = True
parameters['vector_operating_duration'] = 1
parameters['shipping_decision'] = 168

model = OptimisationModel(parameters, key=sys.argv[7])
time_elapsed = time.time() - start_time

model = OptimisationModel.class_solve(
    key=sys.argv[7],
    time=int(sys.argv[8]) - time_elapsed
)
