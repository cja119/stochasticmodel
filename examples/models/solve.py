"""
This script is used to solve a stochastic optimisation problem.
"""

import sys
from stochasticmodel.optimisation import OptimisationModel

solve = OptimisationModel.class_solve(
    key=sys.argv[1],
    feasibility = float(sys.argv[2]),
    optimality = float(sys.argv[3]),
    mip_percentage = int(sys.argv[4]),
    random_seed=sys.argv[5],
    parallel=False
    )

solve.generate_plots(solve)