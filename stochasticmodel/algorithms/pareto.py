"""
This module contains the ParetoFront class, which is used to build and plot Pareto fronts for optimization problems.
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plot
from pathlib import Path
from os import chdir, getcwd
from dill import dump, load
from pyomo.environ import value as pyomo_value
from stochasticmodel.optimisation.model import OptimisationModel
from copy import deepcopy
from numpy import floor


def save_csv(array, title, folder='PreOptimisationDataStore'):
    """
    Save a dictionary or list as a CSV file.

    Args:
        array (dict or list): Data to save.
        title (str): Name of the CSV file.
        folder (str): Folder to save the file in.
    """
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


class Pareto:
    """
    Class to build and plot Pareto fronts for optimization problems.
    """
    instance = None

    def __init__(self, model, parameter_name, values_list):
        """
        Initialize the ParetoFront instance.

        Args:
            model: Optimization model instance.
            parameter_name (str): Name of the parameter to vary.
            values_list (list): List of parameter values.
        """
        self.instance = model.instance
        self.parameter_name = parameter_name
        self.values_list = values_list
        self.label = model.key

    def build_models(self, original_parameters):
        """
        Build and save models for each parameter value.

        Args:
            original_parameters (dict): Original model parameters.
        """
        # Get the current working directory
        current_dir = Path(__file__).resolve().parent

        # Target directory for presolved model
        cache_dir = current_dir.parent.parent / 'cache' 

        with open(cache_dir / f'pareto/{self.label}.log', 'w') as file:
            file.write('')
            for count, value in enumerate(self.values_list):
                if self.parameter_name != 'WeatherFactor':
                    parameters = deepcopy(original_parameters)
                    parameters[self.parameter_name] = value

                open(cache_dir / f'pre/{self.label}_{count}.pickle', 'a').close()
                with open(cache_dir / f'pre/{self.label}_{count}.pickle', 'wb') as f:
                    dump(parameters, f)

                with open(cache_dir / f'pareto/{self.label}.log', 'a') as file:
                    file.write(f'{self.label}_{count}_' + '\n')

        open(cache_dir / f'pareto/{self.label}.pickle', 'a').close()
        with open(cache_dir / f'pareto/{self.label}.pickle', 'wb') as f:
            dump(self, f)

    @classmethod
    def build_fronts(cls, key):
        """
        Build Pareto fronts by solving models for each parameter value.

        Args:
            key (str): Key to identify the Pareto front.
        """

        # Get the current working directory
        current_dir = Path(__file__).resolve().parent

        # Target directory for presolved model
        cache_dir = current_dir.parent.parent / 'cache' 

        cls.label = key
        if cls.instance is None:
            with open(cache_dir / f'pareto/{cls.label}.pickle', 'rb') as f:
                cls = load(f)

        obj_dict = {}
        for count, value in enumerate(cls.values_list):
            try:
                key = f'{cls.label}_{count}'

                solve = OptimisationModel.get_solve(key=key, reinitialise=True)

                cumulative_demand = {(0, 0, 1): 0}
                for s, t, d, s_0, t_0, d_0, s_v, t_v, d_v, s_v0, t_v0, d_v0 in solve.instance.vector_continuity_set:
                    cumulative_demand[(s, t, d)] = cumulative_demand[(s_0, t_0, d_0)] + (
                        8760 / solve.instance.end_time_index
                        * solve.instance.amortisation_plant
                        * sum(
                            solve.instance.energy_vector_production_flux[(s_v, t_v, d_v), q].value * d / 120
                            for q in solve.instance.vectors
                        )
                    )

                production_vector = []
                for s in solve.instance.scenario:
                    if cumulative_demand[s, solve.instance.end_time_index.value, 1] != 0:
                        production_vector.append(
                            1000 * (solve.instance.CAPEX.value + solve.instance.OPEX[s].value)
                            / cumulative_demand[s, solve.instance.end_time_index.value, 1]
                        )
                    else:
                        production_vector.append('No Production')
                    obj_dict[(cls.parameter_name, value)] = production_vector
            except Exception as e:
                print(f'Failed Solve {cls.parameter_name} {value}: {e}')
                obj_dict[(cls.parameter_name, value)] = ['Failed Solve']
                continue
        with open(cache_dir / f'pareto/{cls.label}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            for key, values in obj_dict.items():
                if isinstance(values, list):
                    writer.writerow([key] + list(map(str, values)))
                else:
                    writer.writerow([key, str(values)])

    @classmethod
    def plot_pareto_front(cls, filename, axis_labels=('Varied Parameter', 'Objective Value'),
                          normaliser=(1, 1), times_time=False, aspect=(10, 8), existing=None):
        """
        Plot the Pareto front from a CSV file.

        Args:
            filename (str): Name of the CSV file.
            axis_labels (tuple): Labels for the axes.
            normaliser (tuple): Normalization factors for x and y axes.
            times_time (bool): Whether to multiply by time.
            aspect (tuple): Aspect ratio of the plot.
            existing: Existing plot object to add to.
        """
        
        # Get the current working directory
        current_dir = Path(__file__).resolve().parent

        # Target directory for presolved model
        cache_dir = current_dir.parent.parent / 'cache' 

        csv_file = os.path.join(cache_dir / 'pareto', filename)

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
                        if float(j) != float(j):
                            break
                        arrays[count].append(float(j))
                except ValueError:
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
            color = '#00509E'
        else:
            color = 'black'
            plt = plot
            plt.figure(figsize=aspect)

        plt.plot(x_values, means, marker='o', linestyle='-', color=color, label=filename[:3])

        for ci in confidence_intervals:
            ci_label = f'{int(ci * 100)}% CI'
            lower_bounds = [mean - ci * std for mean, std in zip(means, stds)]
            upper_bounds = [mean + ci * std for mean, std in zip(means, stds)]
            plt.fill_between(x_values, lower_bounds, upper_bounds, color=color, alpha=(1 - ci) * 0.75)
        plt.ylim((0, max(upper_bounds) * 1.25))
        plt.xlabel(axis_labels[1])
        plt.ylabel(axis_labels[0])
        plt.title('Pareto Front')
        plt.grid(False)
        return plt
