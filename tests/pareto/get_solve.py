"""
This code builds Pareto fronts for a given optimization model.
"""

import sys
from h2_plan.algs import Pareto

Pareto.build_fronts(sys.argv[1])

