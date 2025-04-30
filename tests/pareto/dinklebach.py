"""
This script demonstrates how to use the Dinkelbach algorithm for optimization.
"""

import sys
import time
from h2_plan.opt import OptimisationModel
from h2_plan.algs import Dinkelbach

# Record the start time of the script
start_time = time.time()

# Retrieve optimization parameters from the input file provided as the first argument
parameters = OptimisationModel.get_parameters(sys.argv[1])

# Calculate the time elapsed since the script started
time_elapsed = time.time() - start_time

# Perform the warm start for the Dinkelbach algorithm
# The time limit is adjusted by subtracting the elapsed time from the provided time limit
Dinkelbach.warm_start(
    sys.argv[1],
    parameters,
    time_lim=int(sys.argv[2]) - time_elapsed
)
