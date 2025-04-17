"""
This code defines the variables used in the optimization model.
"""
from pyomo.environ import NonNegativeIntegers, NonNegativeReals, Var, Reals


def generate_variables(model):
    # Starting with all energy-related variables
    if model.grid_wheel:
        model.energy_wheeled = Var(model.full_set, within=Reals)
    model.energy_curtailed = Var(model.full_set, within=NonNegativeReals)
    model.energy_electrolysers = Var(
        model.full_set, model.electrolysers, within=NonNegativeReals
    )
    model.energy_gH2_flux = Var(model.full_set, within=NonNegativeReals)
    model.energy_penalty_vector_production = Var(
        model.vector_param_set, model.vectors, within=NonNegativeReals
    )
    model.energy_vector_production_flux = Var(
        model.vector_param_set, model.vectors, within=NonNegativeReals
    )
    model.energy_vector_consumption_flux = Var(
        model.vector_param_set, model.vectors, within=NonNegativeReals
    )

    # Adding compression and GH2 balance variables
    model.energy_compression = Var(model.full_set, within=NonNegativeReals)
    model.energy_gh2_use = Var(
        model.full_set, model.vectors, within=NonNegativeReals
    )
    model.energy_gh2_rem = Var(
        model.full_set, model.vectors, within=NonNegativeReals
    )
    model.energy_gh2_in_store = Var(model.full_set, within=NonNegativeReals)
    model.energy_grid = Var(model.full_set, within=NonNegativeReals)

    # Generating accumulation-related variables
    model.gh2_storage = Var(model.full_set, within=NonNegativeReals)
    model.vector_storage_origin = Var(
        model.full_set, model.vectors, within=NonNegativeReals
    )

    # Generating equipment size-related variables
    model.number_active_trains = Var(
        model.vector_param_set, model.vectors, within=NonNegativeIntegers
    )

    # Generating shipping scheduling-related variables
    model.number_ships_start_charging = Var(
        model.shipping_param_set, model.vectors, within=NonNegativeIntegers
    )
    model.number_ships_charging = Var(
        model.full_set, model.vectors, within=NonNegativeReals
    )

    model.energy_HFC = Var(model.full_set, within=NonNegativeReals)
    model.energy_HFC_flux = Var(model.full_set, within=NonNegativeReals)

    # Generating capacity variables
    model.compression_capacity = Var(within=NonNegativeReals)
    model.capacity_HFC = Var(within=NonNegativeReals)
    model.capacity_gH2_storage = Var(within=NonNegativeReals)
    model.capacity_solar = Var(within=NonNegativeReals)
    model.capacity_vector_storage_origin = Var(
        model.vectors, within=NonNegativeReals
    )
    model.capacity_electrolysers = Var(
        model.electrolysers, within=NonNegativeReals
    )
    model.capacity_number_turbines = Var(within=NonNegativeReals)
    model.net_grid = Var(model.scenario, within=NonNegativeReals)
    model.CAPEX = Var(within=NonNegativeReals)
    model.OPEX = Var(model.scenario, within=NonNegativeReals)
    model.Z = Var(within=Reals)
    model.Y = Var(within=Reals)