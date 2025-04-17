"""
This file contains a function to calculate weather sensitivity for a given label and number of solves.
"""
import csv
from os import chdir, getcwd, makedirs
from copy import deepcopy
from pathlib import Path
from stochasticmodel.optimisation import OptimisationModel


def get_weather_sensitivity(label, n_solve):
    """
    Calculate weather sensitivity for a given label and number of solves.

    Args:
        label (str): Label for the sensitivity analysis.
        n_solve (int): Number of solves to perform.

    Returns:
        None: Writes results to a CSV file.
    """

     # Get the current working directory
    current_dir = Path(__file__).resolve().parent()
    
    # Target directory for presolved model
    data_dir = current_dir.parent.parent / 'data' 
    
    obj_dict = {}
      # Get the current working directory

    for count in range(1, n_solve + 1):
        try:
            key = f'{label}{count}'

            # Retrieve the solve instance
            solve = OptimisationModel.get_solve(key=key, reinitialise=True)

            # Initialize cumulative demand dictionary
            cumulative_demand = {(0, 0): 0}

            # Calculate cumulative demand
            for s, t, s_0, t_0, s_v, t_v, s_v0, t_v0 in solve.instance.vector_continuity_set:
                cumulative_demand[(s, t)] = (
                    cumulative_demand[(s_0, t_0)]
                    + (
                        8760
                        / solve.instance.end_time_index
                        * solve.instance.amortisation_plant
                        * sum(
                            solve.instance.energy_vector_production_flux[(s_v, t_v), q].value / 120
                            for q in solve.instance.vectors
                        )
                    )
                )

            # Calculate production vector
            production_vector = []
            for s in solve.instance.scenario:
                if cumulative_demand[s, solve.instance.end_time_index.value] != 0:
                    production_vector.append(
                        1000
                        * (solve.instance.CAPEX.value + solve.instance.OPEX[s].value)
                        / cumulative_demand[s, solve.instance.end_time_index.value]
                    )
                else:
                    production_vector.append('No Production')

                # Store results in the dictionary
                obj_dict[count] = production_vector

        except Exception as e:
            print(f'Failed Solve {count}: {e}')
            obj_dict[count] = ['Failed Solve']
            continue

    # Write results to a CSV file


    with open(data_dir / f'{label}_sensitivity.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for key, values in obj_dict.items():
            if isinstance(values, list):
                writer.writerow([key] + list(map(str, values)))
            else:
                writer.writerow([key, str(values)])