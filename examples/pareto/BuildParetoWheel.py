import sys
import os

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from StochasticScripts.ParetoFronts import ParetoFront
from PreOptimisationDataStore.DefaultParameters import Default_Params
from OptimisationScripts.model import OptimModel

booleans = {'vector_choice':{'LH2':True if sys.argv[2] == 'LH2' else False,
                                'NH3':True if sys.argv[2] == 'NH3' else False
                                },
                'electrolysers':{'alkaline':True,
                                'PEM':True,
                                'SOFC':True
                                },
                'grid_connection':True if sys.argv[4]=='True' else False,
                'wind':sys.argv[6] in ['Wind', 'Both'],
                'solar':sys.argv[6] in ['Solar', 'Both'],
                'net_present_value': True,
		'grid_wheel':True}
                

parameters = Default_Params().formulation_parameters
parameters['booleans'] = booleans
parameters['stage_duration'] = 168
parameters['n_stages'] = 3
parameters['n_stochastics'] = 3
parameters['random_seed'] = 42
parameters['relaxed_ramping'] = True
parameters['hydrogen_price'] = 5 #$/kg
parameters['vector_operating_duration']= 1
parameters['shipping_decision']=168
parameters['wheel_period']=24
key = sys.argv[1]
model = OptimModel(parameters, key=key)
pareto = ParetoFront(model,sys.argv[3],[float(x) for x in sys.argv[5].split(',')])
pareto.build_models(parameters)
