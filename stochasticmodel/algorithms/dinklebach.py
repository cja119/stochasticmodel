from numpy import abs
import pandas as pd
from OptimisationScripts.model import OptimModel
from copy import deepcopy
import time

class Dinkelbach:
    instance = None
    def __init__(self,key, tolerance=0.05, intial_guess = 5,model=None):
        self.key = key
        self.tolerance = tolerance
        self.intial_guess = intial_guess
        self.instance = model
        
    
    @classmethod
    def warm_start(cls,key,original_parameters,initial_guess=5,tolerance=0.05,max_price = 10,time_lim=None):
        hydrogen_price = max_price
        break_out = False
        LCOH = initial_guess
        start_time = time.time()
        while abs(hydrogen_price - LCOH) > tolerance * hydrogen_price:
            try:
                df = pd.read_csv(f'SolverLogs/{key}_Dinkelbach.csv')
                if not df.empty:
                    last_row = df.iloc[-1]
                    hydrogen_price = last_row['Hydrogen Price']
                    LCOH = last_row['LCOH']
                    break_out = last_row['Break Out']
                else:
                    df = pd.DataFrame(columns=['Hydrogen Price','LCOH','Break Out'])
                    new_row = pd.DataFrame([{'Hydrogen Price': hydrogen_price, 'LCOH': LCOH, 'Break Out': break_out}])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(f'SolverLogs/{key}_Dinkelbach.csv', index=False)
            except FileNotFoundError:
                df = pd.DataFrame(columns=['Hydrogen Price','LCOH','Break Out'])
                new_row = pd.DataFrame([{'Hydrogen Price': hydrogen_price, 'LCOH': LCOH, 'Break Out': break_out}])
                df = pd.concat([df, new_row], ignore_index=True)                
                df.to_csv(f'SolverLogs/{key}_Dinkelbach.csv', index=False)
            
            if not break_out:
                if LCOH > max_price:
                    LCOH = max_price
                parameters = deepcopy(original_parameters)
                hydrogen_price = LCOH
                parameters['hydrogen_price'] = LCOH
                OptimModel(parameters,key)
                current_time = time.time()
                if time_lim is not None:
                    instance = OptimModel.class_solve(key=key,time=time_lim - (current_time-start_time),reinitialise=True).instance
                else:
                    instance = OptimModel.class_solve(key=key,reinitialise=True).instance
                discounted_demand  = (8760 / (instance.end_time_index) * instance.amortisation_plant * sum(
                        sum((instance.leaf_nodes[s,t,d]) * 
                                instance.energy_vector_production_flux[(s_v, t_v,d_v), q].value * d
                                for s,t,d,s_v,t_v,d_v in instance.vector_set_time)/ 120
                                    for q in instance.vectors
                                )) / len(instance.scenario.data())
                
                LCOH = ((10**3)*sum(instance.OPEX[s].value/len(instance.scenario) for s in instance.scenario) + (10**3)*instance.CAPEX.value) / discounted_demand
                if abs(hydrogen_price - LCOH) < tolerance * hydrogen_price:
                    break_out = True

                new_row = pd.DataFrame([{'Hydrogen Price': hydrogen_price, 'LCOH': LCOH, 'Break Out': break_out}])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(f'SolverLogs/{key}_Dinkelbach.csv', index=False)
            
            
