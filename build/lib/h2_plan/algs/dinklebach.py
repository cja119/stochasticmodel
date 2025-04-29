"""
This module implements the Dinkelbach algorithm for optimizing the levelized cost of hydrogen (LCOH).
"""

from numpy import abs
import pandas as pd
from copy import deepcopy
from pathlib import Path
from h2_plan.opt import H2Planning
import time


class Dinkelbach:
    instance = None

    def __init__(self, key, tolerance=0.05, initial_guess=5, model=None):
        """
        Initialize the Dinkelbach class.

        Args:
            key (str): Unique identifier for the instance.
            tolerance (float): Convergence tolerance for the algorithm.
            initial_guess (float): Initial guess for the LCOH value.
            model (object): Optional model instance.
        """
        self.key = key
        self.tolerance = tolerance
        self.initial_guess = initial_guess
        self.instance = model

    @classmethod
    def warm_start(cls, key, original_parameters, initial_guess=5, tolerance=0.05, max_price=10, time_lim=None):
        """
        Perform a warm start for the Dinkelbach algorithm.

        Args:
            key (str): Unique identifier for the instance.
            original_parameters (dict): Original parameters for the optimization model.
            initial_guess (float): Initial guess for the LCOH value.
            tolerance (float): Convergence tolerance for the algorithm.
            max_price (float): Maximum allowable price for hydrogen.
            time_lim (float): Optional time limit for the optimization process.
        """
        hydrogen_price = max_price
        break_out = False
        LCOH = initial_guess
        start_time = time.time()

        # Get the current working directory
        current_dir = Path(__file__).resolve().parent

        # Target directory for presolved model
        cache_dir = current_dir.parent.parent / 'cache' 

        # Iterate until the difference between hydrogen_price and LCOH is within tolerance
        while abs(hydrogen_price - LCOH) > tolerance * hydrogen_price:

            try:
                df = pd.read_csv(cache_dir / f'dinklebach/{key}.csv')
                if not df.empty:
                    # Retrieve the last row of the log file
                    last_row = df.iloc[-1]
                    hydrogen_price = last_row['Hydrogen Price']
                    LCOH = last_row['LCOH']
                    break_out = last_row['Break Out']
                else:
                    # Initialize the log file if empty
                    df = pd.DataFrame(columns=['Hydrogen Price', 'LCOH', 'Break Out'])
                    new_row = pd.DataFrame([{
                        'Hydrogen Price': hydrogen_price,
                        'LCOH': LCOH,
                        'Break Out': break_out
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(cache_dir / f'dinklebach/{key}.csv', index=False)
            except FileNotFoundError:
                # Create a new log file if it does not exist
                df = pd.DataFrame(columns=['Hydrogen Price', 'LCOH', 'Break Out'])
                new_row = pd.DataFrame([{
                    'Hydrogen Price': hydrogen_price,
                    'LCOH': LCOH,
                    'Break Out': break_out
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(cache_dir / f'dinklebach/{key}.csv', index=False)

            if not break_out:
                # Adjust LCOH if it exceeds the maximum price
                if LCOH > max_price:
                    LCOH = max_price

                # Update parameters with the current hydrogen price
                parameters = deepcopy(original_parameters)
                hydrogen_price = LCOH
                parameters['hydrogen_price'] = LCOH

                # Solve the optimization model
                H2Planning(parameters, key)
                current_time = time.time()
                if time_lim is not None:
                    instance = H2Planning.class_solve(
                        key=key,
                        time=time_lim - (current_time - start_time),
                        reinitialise=True
                    ).instance
                else:
                    instance = H2Planning.class_solve(
                        key=key,
                        reinitialise=True
                    ).instance

                # Calculate the discounted demand
                discounted_demand = (
                    (8760 / instance.end_time_index * instance.amortisation_plant *
                     sum(
                         sum(
                             (instance.leaf_nodes[s, t, d]) *
                             instance.energy_vector_production_flux[(s_v, t_v, d_v), q].value * d
                             for s, t, d, s_v, t_v, d_v in instance.vector_set_time
                         ) / 120
                         for q in instance.vectors
                     )) / len(instance.scenario.data())
                )

                # Update LCOH based on the new discounted demand
                LCOH = (
                    (10**3) * sum(instance.OPEX[s].value / len(instance.scenario) for s in instance.scenario) +
                    (10**3) * instance.CAPEX.value
                ) / discounted_demand

                # Check for convergence
                if abs(hydrogen_price - LCOH) < tolerance * hydrogen_price:
                    break_out = True

                # Log the updated values
                new_row = pd.DataFrame([{
                    'Hydrogen Price': hydrogen_price,
                    'LCOH': LCOH,
                    'Break Out': break_out
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(cache_dir / f'dinklebach/{key}.csv', index=False)
