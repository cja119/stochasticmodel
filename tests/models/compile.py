"""
This script is used to compile the stochastic model for the hydrogen supply chain.
"""

import sys
import numpy as np
from h2_plan.opt import H2Planning
from h2_plan.data.default import DefaultParams

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
   'grid_connection': sys.argv[7] == 'True',
   'wind': sys.argv[6] in ['Wind', 'Both'],
   'solar': sys.argv[6] in ['Solar', 'Both'],
   'net_present_value': True,
   'grid_wheel': False
}

parameters = DefaultParams().formulation_parameters
parameters.update({
   'booleans': booleans,
   'wheel_period': 24,
   'stage_duration': int(sys.argv[5]),
   'n_stages': int(sys.argv[1]),
   'n_stochastics': int(sys.argv[2]),
   'hydrogen_price': 5,  # $/kg
   'random_seed': int(sys.argv[4]),
   'relaxed_ramping': True,
   'vector_operating_duration': 1,
   'shipping_decision': 168
})

model = H2Planning(parameters, key=sys.argv[8],filename = 'CoastalChile_15-20_Wind.csv', filepath = None )
