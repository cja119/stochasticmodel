"""
This code runs the Dinkelbach algorithm for optimizing the levelized cost of hydrogen (LCOH) in a stochastic model.
"""

import sys
import time
from os import getcwd, chdir, environ, popen, system
from dill import dump
import numpy as np

from data.default import DefaultParams
from stochasticmodel.algorithms import Dinkelbach

# Record the start time of the script
start_time = time.time()

# Define boolean flags based on input arguments
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

# Load default parameters and update them with user inputs
parameters = DefaultParams().formulation_parameters
parameters.update({
    'booleans': booleans,
    'stage_duration': int(sys.argv[5]),  # Duration of each stage
    'n_stages': int(sys.argv[1]),  # Number of stages
    'n_stochastics': int(sys.argv[2]),  # Number of stochastic scenarios
    'hydrogen_price': 5,  # $/kg
    'random_seed': int(sys.argv[4]),  # Random seed for reproducibility
    'relaxed_ramping': True,  # Enable relaxed ramping
    'vector_operating_duration': 1,  # Operating duration of vectors
    'shipping_decision': 168  # Shipping decision interval (hours)
})

# Calculate elapsed time
time_elapsed = time.time() - start_time

# Run the Dinkelbach algorithm with a warm start
Dinkelbach.warm_start(
    sys.argv[7],  # Input file or configuration
    parameters,  # Model parameters
    time_lim=int(sys.argv[8]) - time_elapsed  # Time limit for the algorithm
)
