"""
This module generates the parameters for the stochastic optimization model.
It is messy and needs to be cleaned up.
"""


from pyomo.environ import Set, Param
from numpy.random import randint, seed
from math import floor
from os import path, chdir, getcwd
from pickle import load
from pathlib import Path
from PyStochOpt import StochasticGrid
from pandas import read_pickle, read_csv
from numpy import ones, int64


def extract_values(dictionary, index):
    """
    Recursively extracts values from a nested dictionary based on the given index.
    Args:
        dictionary (dict): The input dictionary.
        index (int): The index to extract values from lists or tuples.
    Returns:
        dict: A dictionary with extracted values.
    """
    extracted_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            extracted_dict[key] = extract_values(value, index)
        elif isinstance(value, (tuple, list)):
            extracted_dict[key] = value[index] if index < len(value) else None
        elif isinstance(value, (int, int64, float)):
            extracted_dict[key] = value
        else:
            raise ValueError(
                f"Values should be tuples, lists, integers, or floats. "
                f"Your dict contains/is a {type(value)}"
            )
    return extracted_dict


def generate_parameters(model, parameters):
    """
    Generates and initializes parameters and sets for a stochastic optimization model.
    Args:
        model: The optimization model to which parameters and sets will be added.
        parameters (dict): A dictionary containing various parameters required for the model.
    Returns:
        None
    """
    # Set the random seed for reproducibility
    seed(model.random_seed)

    # Extract the necessary parameters from the dictionary
    parameters = extract_values(parameters, 1)

    # Generate sets for vectors and electrolysers
    model.vectors = Set(initialize=[
        key for key, value in parameters['booleans']['vector_choice'].items() if value
    ])
    model.electrolysers = Set(initialize=[
        key for key, value in parameters['booleans']['electrolysers'].items() if value
    ])
    model.time = Set(initialize=range(
        (parameters['n_stages'] + 1) * parameters['stage_duration']
    ))
    model.time.construct()

    # Generate parameters for the stochastic system
    model.scenario = Set(initialize=range(
        parameters['n_stochastics'] ** parameters['n_stages']
    ))
    model.stage = Set(initialize=range(parameters['n_stages'] + 1))
    model.vector_operating_duration = Param(
        initialize=parameters['vector_operating_duration']
    )
    model.n_stages = Param(initialize=parameters['n_stages'], mutable=False)
    model.n_stochastics = Param(initialize=parameters['n_stochastics'], mutable=False)
    model.stage_duration = Param(initialize=parameters['stage_duration'], mutable=False)
    model.relaxed_ramping = Param(initialize=parameters['relaxed_ramping'], mutable=False)
    model.grid_connection = Param(
        initialize=parameters['booleans']['grid_connection'], mutable=False
    )
    model.shipping_decision = Param(
        initialize=parameters['shipping_decision'], mutable=False
    )
    model.net_present_value = Param(
        initialize=parameters['booleans']['net_present_value'], mutable=False
    )

    # Construct sets and parameters
    model.vectors.construct()
    model.electrolysers.construct()
    model.n_stages.construct()
    model.n_stochastics.construct()
    model.stage_duration.construct()
    model.shipping_decision.construct()
    model.vector_operating_duration.construct()
    model.scenario.construct()
    model.stage.construct()
    model.net_present_value.construct()

    # Generate non-anticipativity structure for the stochastic system
    repeat_stages = {
        key: parameters['n_stochastics'] ** parameters['n_stages'] /
             parameters['n_stochastics'] ** (key // parameters['stage_duration'])
        for key in model.time
    }

    parameters['vector_operating_duration'] = int(parameters['vector_operating_duration'])
    parameters['shipping_decision'] = int(parameters['shipping_decision'])
    model.repeat_stages = Param(
        model.time, initialize=repeat_stages, mutable=False
    )
    model.repeat_stages.construct()
    model.wind = Param(initialize=parameters['booleans']['wind'], mutable=False)
    model.solar = Param(initialize=parameters['booleans']['solar'], mutable=False)
    model.solar.construct()
    model.wind.construct()
    model.grid_wheel = Param(
        initialize=parameters['booleans']['grid_wheel'], mutable=False
    )
    model.grid_wheel.construct()

    if model.grid_wheel:
        parameters['wheel_period'] = int(parameters['wheel_period'])
        model.wheel_period = Param(initialize=parameters['wheel_period'], mutable=False)

    # Initialize stochastic grid
    stochastic_grid = StochasticGrid(
        parameters['n_stages'], parameters['n_stochastics'],
        parameters['stage_duration'], model.random_seed
    )

    weather_path = Path(__file__).parent.parent.parent / "weathermodel/data/"

    # Add wind dataset
    if model.wind and not model.solar:
        if model.grid_wheel:
            wind_samples = stochastic_grid.add_dataset(
                'CoastalChile_Wind.csv', str(weather_path),
                cluster=True, epsilon=0.001,
                cluster_points=[
                    (parameters['shipping_decision'], parameters['shipping']['loading_time']),
                    (parameters['wheel_period'], 0)
                ]
            )
        else:
            wind_samples = stochastic_grid.add_dataset(
                'CoastalChile_Wind.csv', str(weather_path),
                cluster=True, epsilon=0.001,
                cluster_points=[
                    (parameters['shipping_decision'], parameters['shipping']['loading_time'])
                ]
            )
    else:
        wind_samples = stochastic_grid.add_dataset(
            'CoastalChile_Wind.csv', str(weather_path), cluster=False
        )

    # Generate sets for vector continuity and shipping
    model.vector_continuity_set = Set(
        initialize=zip(
            stochastic_grid.get_grid(),
            stochastic_grid.new_grid(1, 1),
            stochastic_grid.new_grid(parameters['vector_operating_duration']),
            stochastic_grid.new_grid(parameters['vector_operating_duration'], 1)
        ),
        dimen=12
    )

    leaf_nodes = stochastic_grid.leaf_nodes()

    model.vector_set_time = Set(
        initialize=zip(
            stochastic_grid.get_grid(),
            stochastic_grid.new_grid(parameters['vector_operating_duration'])
        ),
        dimen=6
    )
    model.vector_param_set = Set(
        initialize=stochastic_grid.remove_duplicates(
            stochastic_grid.new_grid(parameters['vector_operating_duration'])
        )
    )
    model.shipping_set_time = Set(
        initialize=zip(
            stochastic_grid.get_grid(),
            stochastic_grid.new_grid(parameters['shipping_decision'])
        ),
        dimen=6
    )
    model.full_set = Set(initialize=stochastic_grid.get_grid(), dimen=3)
    model.continuity_set = Set(
        initialize=zip(
            stochastic_grid.get_grid(),
            stochastic_grid.new_grid(1, 1)
        ),
        dimen=6
    )
    model.shipping_param_set = Set(
        initialize=stochastic_grid.remove_duplicates(
            stochastic_grid.new_grid(parameters['shipping_decision'])
        )
    )
    model.shipping_continuity_set = Set(
        initialize=zip(
            stochastic_grid.get_grid(),
            stochastic_grid.new_grid(1, 1),
            stochastic_grid.new_grid(parameters['shipping_decision']),
            stochastic_grid.new_grid(parameters['shipping_decision'], 1),
            stochastic_grid.new_grid(
                parameters['shipping_decision'], parameters['shipping']['loading_time']
            )
        ),
        dimen=15
    )

    model.full_set.construct()
    model.continuity_set.construct()
    model.vector_param_set.construct()

    # Add other decision variables
    model.end_time_index = Param(initialize=model.time.at(-1), mutable=False)
    model.time_values = Param(
        model.time, initialize={key: key for key in model.time}, mutable=False
    )
    model.leaf_nodes = Param(model.full_set, initialize=leaf_nodes)
    model.leaf_nodes.construct()

    # Generate energy-related parameters
    n_samp = sum([
        parameters['n_stochastics'] ** stage
        for stage in range(parameters['n_stages'] + 2)
    ])

    if model.wind:
        model.turbine_power = Param(
            model.full_set, initialize=wind_samples, mutable=False
        )
        model.turbine_power.construct()

    if model.solar:
        solar_samples = stochastic_grid.add_dataset(
            'CoastalChile_Solar.csv', str(weather_path),
        )
        model.solar_power = Param(
            model.full_set, initialize=solar_samples, mutable=False
        )
        model.solar_power.construct()

    model.fuel_cell_efficiency = Param(
        initialize=parameters['efficiencies']['fuel_cell'], mutable=False
    )
    model.turbine_efficiency = Param(
        initialize=parameters['efficiencies']['turbine'], mutable=False
    )
    model.compressor_effiency = Param(
        initialize=parameters['efficiencies']['compressor'], mutable=False
    )
    model.electrolyser_compression_energy = Param(
        model.electrolysers, initialize={
            key: parameters['miscillaneous']['electrolyser_compression_energy'][key]
            for key, value in parameters['booleans']['electrolysers'].items() if value
        }, mutable=False
    )
    model.storage_compression_penalty = Param(
        initialize=parameters['miscillaneous']['storage_compression_penalty'], mutable=False
    )
    model.vector_compression_penalty = Param(
        model.vectors, initialize={
            key: parameters['miscillaneous']['vector_compression_penalty'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    model.electrolyser_efficiency = Param(
        model.electrolysers, initialize={
            key: parameters['efficiencies']['electrolysers'][key]
            for key, value in parameters['booleans']['electrolysers'].items() if value
        }, mutable=False
    )

    model.hydrogen_LHV = Param(
        initialize=parameters['miscillaneous']['hydrogen_LHV'], mutable=False
    )

    # Generate vector-related parameters
    model.single_train_throughput_limit = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['single_train_throughput'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    model.vector_calorific_value = Param(
        model.vectors, initialize={
            key: parameters['efficiencies']['vector_calorific_value'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
    # Define the minimum process throughput for each vector
    model.minimum_process_throughput = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['minimum_train_throughput'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Define the boil-off energy penalty for each vector
    model.bol_energy_penalty = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['boil_off_energy_penalty'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Define the boil-off rate (percentage) for each vector
    model.bol_rate = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['boil_off_percentage'][key] / 100
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Define the fixed energy penalty for each vector
    model.vector_fixed_energy_penalty = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['fixed_energy_penalty'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Define the variable energy penalty for each vector
    model.vector_variable_energy_penalty = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['variable_energy_penalty'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Define the fugitive efficiency for each vector
    model.vector_fugitive_efficiency = Param(
        model.vectors, initialize={
            key: parameters['efficiencies']['vector_fugitive'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Define the synthetic efficiency for each vector
    model.vector_synthetic_efficiency = Param(
        model.vectors, initialize={
            key: parameters['efficiencies']['vector_synthesis'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Define the ramp-down limit for each vector
    model.ramp_down_limit = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['ramp_down_limit'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Define the ramp-up limit for each vector
    model.ramp_up_limit = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['ramp_up_limit'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Add shipping-related parameters
    model.journey_time = Param(
        initialize=parameters['shipping']['journey_time'], mutable=False
    )
    model.loading_time = Param(
        initialize=parameters['shipping']['loading_time'], mutable=False
    )
    model.ship_storage_capacity = Param(
        model.vectors, initialize={
            key: parameters['shipping']['storage_capacity'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Calculate the amortisation factor for equipment replacement
    equipment_lives = ones(parameters['replacement_frequencies']['system_duration'] + 20)

    # Compute amortised costs for equipment replacement during the plant's lifetime
    for i in range(1, parameters['replacement_frequencies']['system_duration']):
        for j in range(1, parameters['replacement_frequencies']['system_duration']):
            if j % i == 0:
                equipment_lives[i - 1] += (1 / (1 + parameters['miscillaneous']['discount_factor'])) ** (j - 1)

    # Add amortised costs for each piece of equipment to the model
    model.amortisation_turbine = Param(
        initialize=equipment_lives[floor(parameters['replacement_frequencies']['turbine'] - 1)], mutable=False
    )
    model.amortisation_solar = Param(
        initialize=equipment_lives[floor(parameters['replacement_frequencies']['solar'] - 1)], mutable=False
    )
    model.amortisation_fuel_cell = Param(
        initialize=equipment_lives[floor(parameters['replacement_frequencies']['fuel_cell'] - 1)], mutable=False
    )
    model.amortisation_hydrogen_storage = Param(
        initialize=equipment_lives[floor(parameters['replacement_frequencies']['hydrogen_storage'] - 1)], mutable=False
    )
    model.amortisation_vector_production = Param(
        model.vectors, initialize={
            key: equipment_lives[floor(parameters['replacement_frequencies']['vector_production'][key] - 1)]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
    model.amortisation_electrolysers = Param(
        model.electrolysers, initialize={
            key: equipment_lives[floor(parameters['replacement_frequencies']['electrolysers'][key] - 1)]
            for key, value in parameters['booleans']['electrolysers'].items() if value
        }, mutable=False
    )
    model.amortisation_vector_storage = Param(
        model.vectors, initialize={
            key: equipment_lives[floor(parameters['replacement_frequencies']['vector_storage'][key] - 1)]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
    model.amortisation_compressor = Param(
        initialize=equipment_lives[floor(parameters['replacement_frequencies']['compressor'] - 1)], mutable=False
    )
    model.amortisation_plant = Param(initialize=equipment_lives[0], mutable=False)

    # Define hydrogen price
    model.hydrogen_price = Param(initialize=parameters['hydrogen_price'])

    # Calculate Levelized Cost of Energy (LCOE) for wind and solar
    lcoap = []
    if model.wind:
        lcowp = (
            (parameters['capital_costs']['turbine'] * equipment_lives[parameters['replacement_frequencies']['turbine'] - 1] +
             (parameters['operating_costs']['turbine'] * equipment_lives[0])) /
            ((8760 * parameters['efficiencies']['turbine'] * equipment_lives[0] /
              int(model.time.at(-1) + 1) *
              sum([model.turbine_power[s, t, d] * d * model.leaf_nodes[s, t, d] for s, t, d in model.full_set]) /
              parameters['n_stochastics'] ** parameters['n_stages']))
        )
        model.LCOWP = Param(initialize=lcowp, mutable=False)
        lcoap.append(lcowp)

    if model.solar:
        lcos = (
            (parameters['capital_costs']['solar'] * equipment_lives[parameters['replacement_frequencies']['solar'] - 1] +
             (parameters['operating_costs']['solar'] * equipment_lives[0])) /
            ((8760 * equipment_lives[0] / int(model.time.at(-1) + 1) * 0.0036 *
              sum([model.solar_power[s, t, d] * d * model.leaf_nodes[s, t, d] for s, t, d in model.full_set]) /
              parameters['n_stochastics'] ** parameters['n_stages']))
        )
        model.LCOSP = Param(initialize=lcos, mutable=False)
        lcoap.append(lcos)

    # Calculate average Levelized Cost of Energy (LCOE)
    model.LCAP = Param(initialize=sum(lcoap) / len(lcoap), mutable=False)

    # Add cost parameters for various components
    model.vector_storage_unit_capital_cost = Param(
        model.vectors, initialize={
            key: parameters['capital_costs']['vector_storage'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
    model.vector_storage_unit_operating_cost = Param(
        model.vectors, initialize={
            key: parameters['operating_costs']['vector_storage'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
    model.vector_production_unit_capital_cost = Param(
        model.vectors, initialize={
            key: parameters['capital_costs']['vector_production'][key] *
                 (parameters['vector_production']['single_train_throughput'][key]) ** (2 / 3)
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
    model.vector_production_unit_operating_cost = Param(
        model.vectors, initialize={
            key: parameters['operating_costs']['vector_production'][key] *
                 (parameters['vector_production']['single_train_throughput'][key]) ** (2 / 3)
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
    model.hydrogen_storage_cost_sf = Param(
        initialize=parameters['hydrogen_storage_cost_sf']
    )
    model.hydrogen_storage_unit_capital_cost = Param(
        initialize=parameters['capital_costs']['hydrogen_storage'], mutable=False
    )
    model.hydrogen_storage_unit_operating_cost = Param(
        initialize=parameters['operating_costs']['hydrogen_storage'], mutable=False
    )
    model.fuel_cell_unit_capital_cost = Param(
        initialize=parameters['capital_costs']['fuel_cell'], mutable=False
    )
    model.fuel_cell_unit_operating_cost = Param(
        initialize=parameters['operating_costs']['fuel_cell'], mutable=False
    )
    model.turbine_unit_capital_cost = Param(
        initialize=parameters['capital_costs']['turbine'], mutable=False
    )
    model.turbine_unit_operating_cost = Param(
        initialize=parameters['operating_costs']['turbine'], mutable=False
    )
    model.solar_unit_capital_cost = Param(
        initialize=parameters['capital_costs']['solar'], mutable=False
    )
    model.solar_unit_operating_cost = Param(
        initialize=parameters['operating_costs']['solar'], mutable=False
    )
    model.compressor_unit_capital_cost = Param(
        initialize=parameters['capital_costs']['compressor'], mutable=False
    )
    model.compressor_unit_operating_cost = Param(
        initialize=parameters['operating_costs']['compressor'], mutable=False
    )
    model.electrolyser_unit_capital_cost = Param(
        model.electrolysers, initialize={
            key: parameters['capital_costs']['electrolysers'][key]
            for key, value in parameters['booleans']['electrolysers'].items() if value
        }, mutable=False
    )
    model.electrolyser_unit_operating_cost = Param(
        model.electrolysers, initialize={
            key: parameters['operating_costs']['electrolysers'][key]
            for key, value in parameters['booleans']['electrolysers'].items() if value
        }, mutable=False
    )
    model.grid_energy_factor = Param(
        initialize=parameters['grid_energy_factor'], mutable=True
    )

    # Define the capacity for vector production
    model.capacity_vector_production = Param(
        model.vectors, initialize={
            key: parameters['equipment']['vector_production'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
