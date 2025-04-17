"""
This code builds Pareto fronts for a given optimization model.
"""

import sys
from stochasticmodel.algorithms import Pareto

Pareto.build_fronts(sys.argv[1])

