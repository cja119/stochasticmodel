import sys
import os

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from OptimisationScripts.OptimisationModel import OptimModel
from PreOptimisationDataStore.DefaultParameters import Default_Params
from StochasticScripts.ParetoFronts import ParetoFront
from StochasticScripts.Dinkelbach import Dinkelbach

import numpy as np
from os import getcwd, chdir, environ, popen,system
from dill import dump   
import time

start_time = time.time()

parameters = OptimModel.get_parameters(sys.argv[1])

time_elapsed = time.time() - start_time

Dinkelbach.warm_start(sys.argv[1],parameters,time_lim = int(sys.argv[2]) - (time_elapsed))


