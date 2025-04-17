from pyomo.environ import Set, Param
from numpy.random import randint, seed
from math import floor
from os import path, chdir, getcwd
from pickle import load
from PyStochOpt import StochasticGrid
from StochasticScripts.ProbabalisticWeather import ProbabilisticWeatherModel
from pandas import read_pickle, read_csv
from numpy import ones, int64

def extract_values(dictionary, index):
    extracted_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            extracted_dict[key] = extract_values(value, index)
        elif isinstance(value, (tuple, list)):
            extracted_dict[key] = value[index] if index < len(value) else None
        elif isinstance(value, (int, int64, float)):
            extracted_dict[key] = value
        else:
            raise ValueError(f"Values should be tuples, lists, integers, or floats. Your dict contains/is a {type(value)}")
    return extracted_dict

def generate_parameters(model, parameters, probabilities):
    """
    Generates and initializes parameters and sets for a stochastic optimization model.
    Args:
        model: The optimization model to which parameters and sets will be added.
        parameters (dict): A dictionary containing various parameters required for the model.
            - 'booleans': Dictionary of boolean flags for different components.
                - 'vector_choice': Dict indicating which vectors are chosen.
                - 'electrolysers': Dict indicating which electrolysers are chosen.
                - 'grid_connection': Boolean indicating if grid connection is considered.
                - 'wind': Boolean indicating if wind power is considered.
                - 'solar': Boolean indicating if solar power is considered.
            - 'n_stages': Number of stages in the stochastic model.
            - 'stage_duration': Duration of each stage.
            - 'n_stochastics': Number of stochastic scenarios.
            - 'vector_operating_duration': Duration for vector operation.
            - 'relaxed_ramping': Relaxed ramping parameter.
            - 'efficiencies': Dictionary of efficiency parameters.
                - 'fuel_cell': Efficiency of the fuel cell.
                - 'turbine': Efficiency of the turbine.
                - 'compressor': Efficiency of the compressor.
                - 'electrolysers': Dict of efficiencies for each electrolyser.
                - 'vector_calorific_value': Dict of calorific values for each vector.
                - 'vector_fugitive': Dict of fugitive efficiencies for each vector.
                - 'vector_synthesis': Dict of synthesis efficiencies for each vector.
            - 'miscillaneous': Dictionary of miscellaneous parameters.
                - 'electrolyser_compression_energy': Dict of compression energy for each electrolyser.
                - 'storage_compression_penalty': Penalty for storage compression.
                - 'vector_compression_penalty': Dict of compression penalties for each vector.
                - 'hydrogen_LHV': Lower heating value of hydrogen.
                - 'discount_factor': Discount factor for amortization.
            - 'vector_production': Dictionary of vector production parameters.
                - 'single_train_throughput': Dict of single train throughput for each vector.
                - 'minimum_train_throughput': Dict of minimum train throughput for each vector.
                - 'boil_off_energy_penalty': Dict of boil-off energy penalties for each vector.
                - 'boil_off_percentage': Dict of boil-off percentages for each vector.
                - 'fixed_energy_penalty': Dict of fixed energy penalties for each vector.
                - 'variable_energy_penalty': Dict of variable energy penalties for each vector.
                - 'ramp_down_limit': Dict of ramp down limits for each vector.
                - 'ramp_up_limit': Dict of ramp up limits for each vector.
            - 'shipping': Dictionary of shipping parameters.
                - 'journey_time': Journey time for shipping.
                - 'loading_time': Loading time for shipping.
                - 'storage_capacity': Dict of storage capacities for each vector.
            - 'replacement_frequencies': Dictionary of replacement frequencies for equipment.
                - 'system_duration': Duration of the system.
                - 'turbine': Replacement frequency for turbines.
                - 'solar': Replacement frequency for solar panels.
                - 'fuel_cell': Replacement frequency for fuel cells.
                - 'hydrogen_storage': Replacement frequency for hydrogen storage.
                - 'vector_production': Dict of replacement frequencies for vector production.
                - 'electrolysers': Dict of replacement frequencies for electrolysers.
                - 'vector_storage': Dict of replacement frequencies for vector storage.
                - 'compressor': Replacement frequency for compressors.
            - 'capital_costs': Dictionary of capital costs for equipment.
                - 'turbine': Capital cost for turbines.
                - 'solar': Capital cost for solar panels.
                - 'fuel_cell': Capital cost for fuel cells.
                - 'hydrogen_storage': Capital cost for hydrogen storage.
                - 'vector_storage': Dict of capital costs for vector storage.
                - 'vector_production': Dict of capital costs for vector production.
                - 'compressor': Capital cost for compressors.
                - 'electrolysers': Dict of capital costs for electrolysers.
            - 'operating_costs': Dictionary of operating costs for equipment.
                - 'turbine': Operating cost for turbines.
                - 'solar': Operating cost for solar panels.
                - 'fuel_cell': Operating cost for fuel cells.
                - 'hydrogen_storage': Operating cost for hydrogen storage.
                - 'vector_storage': Dict of operating costs for vector storage.
                - 'vector_production': Dict of operating costs for vector production.
                - 'compressor': Operating cost for compressors.
                - 'electrolysers': Dict of operating costs for electrolysers.
                - 'grid_energy_factor': Operating cost factor for grid energy.
            - 'equipment': Dictionary of equipment capacities.
                - 'vector_production': Dict of capacities for vector production.
        probabilities (list): List of probabilities for different scenarios.
    Returns:
        None
    """
    # Set the random seed for reproducibility
    seed(model.random_seed)
    
    # Extract the necessary parameters from the dictionary
    parameters = extract_values(parameters, 1)
        
    # Generate the necessary sets using comprehension of the parameter dictionary
    model.vectors = Set(initialize=[
        key for key, value in parameters['booleans']['vector_choice'].items() if value
    ])
    model.electrolysers = Set(initialize=[
        key for key, value in parameters['booleans']['electrolysers'].items() if value
    ])
    model.time = Set(initialize=range((parameters['n_stages'] + 1) * parameters['stage_duration']))
    model.time.construct()

    # Generate the parameters for the stochastic system
    model.scenario = Set(initialize=range(parameters['n_stochastics'] ** parameters['n_stages']))
    model.stage = Set(initialize=range(parameters['n_stages'] + 1))
    model.vector_operating_duration = Param(initialize=parameters['vector_operating_duration'])
    model.n_stages = Param(initialize=parameters['n_stages'], mutable=False)
    model.n_stochastics = Param(initialize=parameters['n_stochastics'], mutable=False)
    model.stage_duration = Param(initialize=parameters['stage_duration'], mutable=False)
    model.relaxed_ramping = Param(initialize=parameters['relaxed_ramping'], mutable=False)
    model.grid_connection = Param(initialize=parameters['booleans']['grid_connection'], mutable=False)
    model.shipping_decision = Param(initialize=parameters['shipping_decision'], mutable=False)
    model.net_present_value = Param(initialize=parameters['booleans']['net_present_value'], mutable=False)

    # Build the necessary parameters and sets for the system
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
    

    # Generate the nonanticipativity structure for the stochastic system
    repeat_stages = {key: parameters['n_stochastics'] ** parameters['n_stages']/parameters['n_stochastics'] ** (key // parameters['stage_duration']) for key in model.time}
    
    parameters['vector_operating_duration'] = int(parameters['vector_operating_duration'])
    parameters['shipping_decision'] = int(parameters['shipping_decision'])
    model.repeat_stages = Param(model.time, initialize = repeat_stages, mutable=False)
    model.repeat_stages.construct()
    model.wind = Param(initialize=parameters['booleans']['wind'], mutable=False)
    model.solar = Param(initialize=parameters['booleans']['solar'], mutable=False)
    model.solar.construct()
    model.wind.construct()
    model.grid_wheel = Param(initialize=parameters['booleans']['grid_wheel'], mutable=False)
    model.grid_wheel.construct()
    if model.grid_wheel:
        parameters['wheel_period'] = int(parameters['wheel_period'])
        model.wheel_period = Param(initialize=parameters['wheel_period'], mutable=False)
    stochastic_grid = StochasticGrid(parameters['n_stages'], parameters['n_stochastics'], parameters['stage_duration'],model.random_seed)
    if model.wind and not model.solar:
        if model.grid_wheel:
            wind_samples = stochastic_grid.add_dataset('CoastalChile_Wind.csv','WeatherModel/WeatherData/',cluster=True,epsilon=0.001,cluster_points=[(parameters['shipping_decision'],parameters['shipping']['loading_time']),(parameters['wheel_period'],0)])
        else:
            wind_samples = stochastic_grid.add_dataset('CoastalChile_Wind.csv','WeatherModel/WeatherData/',cluster=True,epsilon=0.001,cluster_points=[(parameters['shipping_decision'],parameters['shipping']['loading_time'])])
    else:
        wind_samples = stochastic_grid.add_dataset('CoastalChile_Wind.csv','WeatherModel/WeatherData/',cluster=False)
    model.vector_continuity_set = Set(initialize=zip(stochastic_grid.get_grid(),stochastic_grid.new_grid(1,1),stochastic_grid.new_grid(parameters['vector_operating_duration']),stochastic_grid.new_grid(parameters['vector_operating_duration'],1)),dimen=12)
    
    leaf_nodes = stochastic_grid.leaf_nodes()

    model.vector_set_time =  Set(initialize=zip(stochastic_grid.get_grid(),stochastic_grid.new_grid(parameters['vector_operating_duration'])),dimen=6)
    model.vector_param_set = Set(initialize = stochastic_grid.remove_duplicates(stochastic_grid.new_grid(parameters['vector_operating_duration'])))
    model.shipping_set_time = Set(initialize=zip(stochastic_grid.get_grid(),stochastic_grid.new_grid(parameters['shipping_decision'])) ,dimen=6)
    model.full_set = Set(initialize=stochastic_grid.get_grid(),dimen=3)
    model.continuity_set = Set(initialize=zip(stochastic_grid.get_grid(),stochastic_grid.new_grid(1,1)),dimen=6)
    model.shipping_param_set = Set(initialize=stochastic_grid.remove_duplicates(stochastic_grid.new_grid(parameters['shipping_decision'])))
    model.shipping_continuity_set = Set(initialize=zip(stochastic_grid.get_grid(),stochastic_grid.new_grid(1,1),stochastic_grid.new_grid(parameters['shipping_decision']),stochastic_grid.new_grid(parameters['shipping_decision'],1),stochastic_grid.new_grid(parameters['shipping_decision'],parameters['shipping']['loading_time'])),dimen=15)

    model.full_set.construct()
    model.continuity_set.construct()
    model.vector_param_set.construct()
    
    # Adding other decision variables 
    model.end_time_index = Param(initialize=model.time.at(-1), mutable=False)
    model.time_values = Param(model.time, initialize={key: key for key in model.time}, mutable=False)
    model.leaf_nodes = Param(model.full_set, initialize=leaf_nodes)
    model.leaf_nodes.construct()


   
    # Generate energy related parameters
    n_samp = sum([parameters['n_stochastics'] ** stage for stage in range(parameters['n_stages'] + 2)])
    
    if model.wind:
        model.turbine_power = Param(
                model.full_set, initialize=wind_samples, mutable=False
            )
        model.turbine_power.construct()
    
    if model.solar:
        solar_samples = stochastic_grid.add_dataset('CoastalChile_Solar.csv','WeatherModel/WeatherData/')
        model.solar_power = Param(
            model.full_set, initialize=solar_samples, mutable=False
        )
        model.solar_power.construct()
    
    model.fuel_cell_efficiency = Param(initialize=parameters['efficiencies']['fuel_cell'], mutable=False)
    model.turbine_efficiency = Param(initialize=parameters['efficiencies']['turbine'], mutable=False)
    model.compressor_effiency = Param(initialize=parameters['efficiencies']['compressor'], mutable=False)
    model.electrolyser_compression_energy = Param(
        model.electrolysers, initialize={
            key: parameters['miscillaneous']['electrolyser_compression_energy'][key]
            for key, value in parameters['booleans']['electrolysers'].items() if value
        }, mutable=False
    )
    model.storage_compression_penalty = Param(initialize=parameters['miscillaneous']['storage_compression_penalty'], mutable=False)
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

    model.hydrogen_LHV = Param(initialize=parameters['miscillaneous']['hydrogen_LHV'], mutable=False)

    # Generate vector related parameters
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

    model.minimum_process_throughput = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['minimum_train_throughput'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    model.bol_energy_penalty = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['boil_off_energy_penalty'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    model.bol_rate = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['boil_off_percentage'][key] / 100
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    model.vector_fixed_energy_penalty = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['fixed_energy_penalty'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    model.vector_variable_energy_penalty = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['variable_energy_penalty'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    model.vector_fugitive_efficiency = Param(
        model.vectors, initialize={
            key: parameters['efficiencies']['vector_fugitive'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    model.vector_synthetic_efficiency = Param(
        model.vectors, initialize={
            key: parameters['efficiencies']['vector_synthesis'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    model.ramp_down_limit = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['ramp_down_limit'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
    model.ramp_up_limit = Param(
        model.vectors, initialize={
            key: parameters['vector_production']['ramp_up_limit'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Add shipping related parameters
    model.journey_time = Param(initialize=parameters['shipping']['journey_time'], mutable=False)
    model.loading_time = Param(initialize=parameters['shipping']['loading_time'], mutable=False)
    model.ship_storage_capacity = Param(
        model.vectors, initialize={
            key: parameters['shipping']['storage_capacity'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )

    # Adding the amortisation factor for the OPEX and adding the net annual demand function (kg(H2)) these are used in calculation of the LCOH
    equipment_lives = ones(parameters['replacement_frequencies']['system_duration'] + 20)

    # This calculates the amortised cost of having to replace equipment during the lifetime of the plant i is equpment replacement age, j is the year of operation
    for i in range(1, parameters['replacement_frequencies']['system_duration']):
        for j in range(1, parameters['replacement_frequencies']['system_duration']):
            if j % i == 0:
                equipment_lives[i - 1] += (1 / (1 + parameters['miscillaneous']['discount_factor'])) ** (j - 1)

    # Adding the amortised costs for each piece of equpment to the model
    model.amortisation_turbine = Param(initialize=equipment_lives[floor(parameters['replacement_frequencies']['turbine'] - 1)], mutable=False)
    model.amortisation_solar = Param(initialize=equipment_lives[floor(parameters['replacement_frequencies']['solar'] - 1)], mutable=False)
    model.amortisation_fuel_cell = Param(initialize=equipment_lives[floor(parameters['replacement_frequencies']['fuel_cell'] - 1)], mutable=False)
    model.amortisation_hydrogen_storage = Param(initialize=equipment_lives[floor(parameters['replacement_frequencies']['hydrogen_storage'] - 1)], mutable=False)
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
    model.amortisation_compressor = Param(initialize=equipment_lives[floor(parameters['replacement_frequencies']['compressor'] - 1)], mutable=False)
    model.amortisation_plant = Param(initialize=equipment_lives[0], mutable=False)
    
    model.hydrogen_price = Param(initialize=parameters['hydrogen_price'] )
    
    LCOAP = []
    if model.wind:
        LCOWP = ((parameters['capital_costs']['turbine'] * equipment_lives[parameters['replacement_frequencies']['turbine'] - 1] + (parameters['operating_costs']['turbine'] * equipment_lives[0])) /
                 ((8760 * parameters['efficiencies']['turbine'] * equipment_lives[0] / int(model.time.at(-1) + 1) * sum([model.turbine_power[s,t,d] * d * model.leaf_nodes[s,t,d] for s,t,d in model.full_set])/ parameters['n_stochastics'] ** parameters['n_stages']))) 
        model.LCOWP = Param(initialize=LCOWP, mutable=False)
        LCOAP.append(LCOWP)
    if model.solar:
        LCOSP =  ((parameters['capital_costs']['solar'] * equipment_lives[parameters['replacement_frequencies']['solar'] - 1] + (parameters['operating_costs']['solar'] * equipment_lives[0])) /
                 ((8760 * equipment_lives[0] / int(model.time.at(-1) + 1) * 0.0036 * sum([model.solar_power[s,t,d] *d* model.leaf_nodes[s,t,d] for s,t,d in model.full_set])/ parameters['n_stochastics'] ** parameters['n_stages']))) 
        model.LCOSP = Param(initialize=LCOSP, mutable=False)
        LCOAP.append(LCOSP)
    
    model.LCAP = Param(initialize=sum(LCOAP) / len(LCOAP), mutable=False)

    # Adding cost parameters
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
            key: parameters['capital_costs']['vector_production'][key] * (parameters['vector_production']['single_train_throughput'][key]) ** (2 / 3)
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
    model.vector_production_unit_operating_cost = Param(
        model.vectors, initialize={
            key: parameters['operating_costs']['vector_production'][key] * (parameters['vector_production']['single_train_throughput'][key]) ** (2 / 3)
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
    model.hydrogen_storage_cost_sf = Param(initialize=parameters['hydrogen_storage_cost_sf'])
    model.hydrogen_storage_unit_capital_cost = Param(initialize=parameters['capital_costs']['hydrogen_storage'], mutable=False)
    model.hydrogen_storage_unit_operating_cost = Param(initialize=parameters['operating_costs']['hydrogen_storage'], mutable=False)
    model.fuel_cell_unit_capital_cost = Param(initialize=parameters['capital_costs']['fuel_cell'], mutable=False)
    model.fuel_cell_unit_operating_cost = Param(initialize=parameters['operating_costs']['fuel_cell'], mutable=False)
    model.turbine_unit_capital_cost = Param(initialize=parameters['capital_costs']['turbine'], mutable=False)
    model.turbine_unit_operating_cost = Param(initialize=parameters['operating_costs']['turbine'], mutable=False)
    model.solar_unit_capital_cost = Param(initialize=parameters['capital_costs']['solar'], mutable=False)
    model.solar_unit_operating_cost = Param(initialize=parameters['operating_costs']['solar'], mutable=False)
    model.compressor_unit_capital_cost = Param(initialize=parameters['capital_costs']['compressor'], mutable=False)
    model.compressor_unit_operating_cost = Param(initialize=parameters['operating_costs']['compressor'], mutable=False)
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
    model.grid_energy_factor = Param(initialize=parameters['grid_energy_factor'], mutable=True)
    
    model.capacity_vector_production = Param(
        model.vectors, initialize={
            key: parameters['equipment']['vector_production'][key]
            for key, value in parameters['booleans']['vector_choice'].items() if value
        }, mutable=False
    )
    pass
