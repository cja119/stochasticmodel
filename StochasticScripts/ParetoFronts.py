import os
import csv
import numpy as np
import matplotlib.pyplot as plot
from os import chdir, getcwd
from dill import dump, load
from pyomo.environ import value as pyomo_value
from OptimisationScripts.OptimisationModel import OptimModel
from copy import deepcopy
from numpy import floor

def save_csv(array, title, folder='PreOptimisationDataStore'):
    if isinstance(array, dict):
        data = array
    else:
        data = {i: value for i, value in enumerate(array)}

    csv_file = os.path.join(folder, title)
    os.makedirs(folder, exist_ok=True)

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Key', 'Value'])
        for key, value in data.items():
            writer.writerow([key, value])


class ParetoFront:
    instance = None

    def __init__(self, model, parameter_name, values_list):
        self.instance = model.instance
        self.parameter_name = parameter_name
        self.values_list = values_list
        self.label = model.key

    def build_models(self,original_parameters):
        with open(f'SolverLogs/{self.label}_Pareto.log', 'w') as file:
            file.write('')
            for count, value in enumerate(self.values_list):
                if self.parameter_name != 'WeatherFactor':
                    parameters = deepcopy(original_parameters)
                    parameters[self.parameter_name] = value
                dir = getcwd()
                chdir(dir + '/PreSolvedModels')
                open(self.label + f'_{count}_' + '.pickle', 'a').close()
                with open(self.label + f'_{count}_' + '.pickle', 'wb') as f:
                    dump(parameters, f)
                chdir(dir)

                with open(f'SolverLogs/{self.label}_Pareto.log', 'a') as file:
                    file.write(f'{self.label}_{count}_' + '\n')

        dir = getcwd()
        chdir(dir + '/PreSolvedModels')
        open(f'{self.label}_Pareto.pickle', 'a').close()
        with open(f'{self.label}_Pareto.pickle', 'wb') as f:
            dump(self, f)
        chdir(dir)

    @classmethod
    def build_fronts(cls, key):
        cls.label = key
        if cls.instance is None:
            dir = getcwd()
            chdir(dir + '/PreSolvedModels')
            print(key + '_Pareto.pickle')
            with open(key + '_Pareto.pickle', 'rb') as f:
                cls = load(f)
            chdir(dir)

        obj_dict = {}
        dir = getcwd()
        for count, value in enumerate(cls.values_list):
            chdir(dir)
            try:
                key = f'{cls.label}_{count}_'

                solve = OptimModel.get_solve(key=key, reinitialise=True)

                cumulative_demand = {(0,0,1):0}
                for s,t,d,s_0,t_0,d_0,s_v,t_v,d_v,s_v0,t_v0,d_v0 in solve.instance.vector_continuity_set:
                    cumulative_demand[(s,t,d)] = cumulative_demand[(s_0,t_0,d_0)] + (8760 / (solve.instance.end_time_index) * solve.instance.amortisation_plant \
                                             * sum(solve.instance.energy_vector_production_flux[(s_v, t_v,d_v), q].value * d\
                                                   / 120 for q in solve.instance.vectors))
                
                
                production_vector = []
                for s in solve.instance.scenario:
                    if cumulative_demand[s,solve.instance.end_time_index.value,1] != 0:
                        production_vector.append(1000*(solve.instance.CAPEX.value+ solve.instance.OPEX[s].value) / cumulative_demand[s,solve.instance.end_time_index.value,1])
                    else:
                        production_vector.append(('No Production'))
                    obj_dict[(cls.parameter_name, value)] = production_vector
            except Exception as e:
                    print(f'Failed Solve {cls.parameter_name} {value}: {e}')
                    obj_dict[(cls.parameter_name, value)] = ['Failed Solve']
                    continue
        chdir(dir)
        os.makedirs(dir+'/DataAnalysis', exist_ok=True)
        with open(dir+f'/DataAnalysis/{cls.label}_Pareto.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            for key, values in obj_dict.items():
                if isinstance(values, list):
                    writer.writerow([key] + list(map(str, values)))
                else:
                    writer.writerow([key, str(values)])

    @classmethod
    def plot_pareto_front(cls, filename, axis_labels=('Varied Parameter', 'Objective Value'), normaliser=(1, 1),times_time = False,aspect=(10,8),existing=None):
        folder = 'DataAnalysis'
        csv_file = os.path.join(folder, filename)
        with open(csv_file, mode='r') as file:
            n_lines = sum(1 for _ in file)
        arrays = [[] for _ in range(n_lines)]
        first_column = []
        x_values = []
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            for count, row in enumerate(reader):
                try:
                    first_column.append(row[0])
                    for j in row[1:]:
                        if float(j) !=float(j):
                            break
                        arrays[count].append(float(j))
                except:
                    continue
        for count in range(len(arrays) - 1, -1, -1):
            if len(arrays[count]) == 0:
                arrays.pop(count)
                first_column.pop(count)
        
        for item in first_column:
            start_idx = item.find('(')
            end_idx = item.find(')')
            if start_idx != -1 and end_idx != -1:
                tuple_str = item[start_idx + 1:end_idx]
                tuple_elements = tuple_str.split(',')
            x_values.append(float(tuple_elements[1].strip()) / normaliser[0])
        
    
        if times_time:
            arrays = [np.array(arrays[count]) * x_values[count] / normaliser[1] for count in range(len(arrays))]
        else:
            arrays = [np.array(arr) / normaliser[1] for arr in arrays]

        means = [np.mean(arr) for arr in arrays]
        stds = [np.std(arr) for arr in arrays]

        confidence_intervals = np.logspace(np.log(1), np.log(0.01), 20, base=10)
        if existing is not None:
            plt = existing
            color='#00509E'
        else:
            color='black'
            plt=plot
            plt.figure(figsize=aspect)
        
        plt.plot(x_values, means, marker='o', linestyle='-', color=color, label=filename[:3])

        for ci in confidence_intervals:
            ci_label = f'{int(ci * 100)}% CI'
            lower_bounds = [mean - ci * std for mean, std in zip(means, stds)]
            upper_bounds = [mean + ci * std for mean, std in zip(means, stds)]
            plt.fill_between(x_values, lower_bounds, upper_bounds, color=color, alpha=(1 - ci) * 0.75)
        plt.ylim((0,max(upper_bounds)*1.25))
        plt.xlabel(axis_labels[1])
        plt.ylabel(axis_labels[0])
        plt.title('Pareto Front')
        plt.grid(False)
        return plt
