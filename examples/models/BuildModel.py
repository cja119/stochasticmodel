
import sys
import os

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from OptimisationScripts.model import OptimModel
from PreOptimisationDataStore.DefaultParameters import Default_Params
import numpy as np

booleans = {'vector_choice':{'LH2':True if sys.argv[3] == 'LH2' else False,
                                'NH3':True if sys.argv[3] == 'NH3' else False
                                },
                'electrolysers':{'alkaline':True,
                                'PEM':True,
                                'SOFC':True
                                },
               'grid_connection':True if sys.argv[7]=='True' else False,
                'wind':sys.argv[6] in ['Wind', 'Both'],
                'solar':sys.argv[6] in ['Solar', 'Both'],
                'net_present_value': True,
                'grid_wheel':False
             }

parameters = Default_Params().formulation_parameters
parameters['booleans'] = booleans

parameters['wheel_period']=24
parameters['stage_duration'] = int(sys.argv[5])
parameters['n_stages'] = int(sys.argv[1])
parameters['n_stochastics'] = int(sys.argv[2])
parameters['hydrogen_price'] = 5 #$/kg
parameters['random_seed'] = int(sys.argv[4])
parameters['relaxed_ramping'] = True
parameters['vector_operating_duration'] = 1
parameters['shipping_decision'] = 168

model = OptimModel(parameters, key=sys.argv[8])

    
