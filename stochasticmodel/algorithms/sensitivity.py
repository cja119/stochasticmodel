from os import chdir, getcwd, makedirs
from copy import deepcopy
from OptimisationScripts.model import OptimModel
import csv

def get_weather_sensitivity(label, n_solve):
    obj_dict = {}
    dir = getcwd()
    for count in range(1,n_solve+1):
        chdir(dir)
        print(count)
        try:
            key = f'{label}{count}'

            solve = OptimModel.get_solve(key=key, reinitialise=True)

            cumulative_demand = {(0,0):0}
            for s,t,s_0,t_0,s_v,t_v,s_v0,t_v0 in solve.instance.vector_continuity_set:
                cumulative_demand[(s,t)] = cumulative_demand[(s_0,t_0)] + (8760 / (solve.instance.end_time_index) * solve.instance.amortisation_plant \
                                             * sum(solve.instance.energy_vector_production_flux[(s_v, t_v), q].value\
                                                   / 120 for q in solve.instance.vectors))
                
                
            production_vector = []
            for s in solve.instance.scenario:
                if cumulative_demand[s,solve.instance.end_time_index.value] != 0:
                    production_vector.append(1000*(solve.instance.CAPEX.value+ solve.instance.OPEX[s].value) / cumulative_demand[s,solve.instance.end_time_index.value])
                else:
                    production_vector.append(('No Production'))
                obj_dict[(count)] = production_vector
        except Exception as e:
                print(f'Failed Solve {count}: {e}')
                obj_dict[(count)] = ['Failed Solve']
                continue
    chdir(dir)
    makedirs(dir+'/DataAnalysis', exist_ok=True)
    with open(dir+f'/DataAnalysis/{label}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for key, values in obj_dict.items():
            if isinstance(values, list):
                writer.writerow([key] + list(map(str, values)))
            else:
                writer.writerow([key, str(values)])