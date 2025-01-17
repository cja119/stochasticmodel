
import sys
import os

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from OptimisationScripts.OptimisationModel import OptimModel
from PreOptimisationDataStore.DefaultParameters import Default_Params
import numpy as np

booleans = {'vector_choice':{'LH2':True if sys.argv[3] == 'LH2' else False,
                                'NH3':True if sys.argv[3] == 'NH3' else False
                                },
                'electrolysers':{'alkaline':True,
                                'PEM':True,
                                'SOFC':True
                                },
                'grid_connection':False,
                'wind':True,
                'solar':False,
                'net_present_value': True,
                'grid_wheel':False
             }

parameters = Default_Params().formulation_parameters
parameters['booleans'] = booleans
parameters['stage_duration'] = 168
parameters['n_stages'] = 39
parameters['n_stochastics'] = 1
parameters['random_seed'] = 42
parameters['relaxed_ramping'] = True
parameters['hydrogen_price'] = 5 #$/kg
parameters['vector_operating_duration']= 1
parameters['shipping_decision']=168
parameters['wheel_period']=24

model = OptimModel(parameters, key=sys.argv[6])

    
