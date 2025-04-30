"""
This script is used to compile the stochastic model for the hydrogen supply chain.
"""

import sys
import numpy as np
from h2_plan.opt import H2Planning
from h2_plan.data.default import DefaultParams


import sys
from numpy import datetime64
from meteor_py import WeatherData, RenewableEnergy

start_date   =  datetime64('2022-01-01', 'ns') 
end_date     = datetime64('2023-01-01', 'ns') 

weatherdata = WeatherData(
    date=(start_date, end_date),
    location='Coastal Chile',
    wind=True,
    solar=False,
    interval=3600,
    n_samp=100,
    sample_type="Structured",
    latitudes=(sys.argv[0], sys.argv[1]),
    longitudes=(sys.argv[2], sys.argv[3])
)

renewableenergy = RenewableEnergy(
    weatherdata,
    [
        (0, 0.0),       # These are points along the power curve.
        (3, 0.0),       # are used in the output curve.
        (4, 0.648),     # Wind speeds are in [m/s].
        (5, 1.4832),
        (6, 2.736),
        (7, 4.4676),
        (8, 6.7104),
        (9, 9.3168),
        (10, 11.2392),
        (11, 11.8008),
        (12, 11.8728),
        (13, 11.88),
        (30, 11.88),
    ]
)

RenewableEnergy(weatherdata).export_power(weatherdata,name=sys.argv[8], dates=True)


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

model = H2Planning(parameters, key=sys.argv[8],filename = sys.argv[8], filepath = None )
