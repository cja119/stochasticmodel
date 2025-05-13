"""
This code defines the inequalities used in the optimization model.
"""

from pyomo.environ import Constraint
from math import floor


def obj_bound(self):
    return self.Y >= 1000


def objective_function(self):
    return self.Z


def obj_constraint_2(self):
    return self.Y == (
        (8760 / self.end_time_index)
        * self.amortisation_plant
        * sum(
            sum(
                self.leaf_nodes[s, t, d]
                * self.energy_vector_production_flux[(s_v, t_v, d_v), q]
                * d
                for s, t, d, s_v, t_v, d_v in self.vector_set_time
            )
            / 120
            for q in self.vectors
        )
        / len(self.scenario)
    )


def obj_constraint(self):
    return (
        1000
        * (
            self.CAPEX
            + sum(self.OPEX[s] for s in self.scenario) / len(self.scenario)
        )
        == self.Z * self.Y
    )


def NPV(self):
    return (
        self.Z
        == self.CAPEX
        + sum(self.OPEX[s] for s in self.scenario) / len(self.scenario)
        - self.Y * self.hydrogen_price / 1000
    )


def energy_balance(self, s, t, d, s_v, t_v, d_v):
    bal = 0
    if self.wind:
        bal += (
            self.capacity_number_turbines
            * self.turbine_power[s, t, d]
            * self.turbine_efficiency
        )
    if self.solar:
        bal += self.capacity_solar * self.solar_power[s, t, d] * 0.0036
    if self.grid_wheel:
        bal += self.energy_wheeled[s, t, d]
    bal -= self.energy_curtailed[s, t, d]
    bal -= sum(self.energy_electrolysers[s, t, d, k] for k in self.electrolysers)
    bal -= sum(
        self.energy_penalty_vector_production[(s_v, t_v, d_v), q]
        for q in self.vectors
    )
    bal -= self.energy_compression[s, t, d]
    bal -= sum(
        self.vector_storage_origin[s, t, d, q]
        * self.bol_rate[q]
        * self.bol_energy_penalty[q]
        * 1000
        for q in self.vectors
    )
    bal += self.energy_grid[s, t, d]
    bal += self.energy_HFC[s, t, d]
    return bal == 0


def grid_wheel_lim(self, s, t, d, s0, t0, d0):
    if t % self.wheel_period.value <= t0 % self.wheel_period.value or t == self.end_time_index.value:
        expr = {(0, 0, 1): 0}
        for s_o, t_o, d_o, s0_o, t0_o, d0_o in self.continuity_set:
            if t_o <= t:
                expr[(s_o, t_o, d_o)] = (
                    expr[(s0_o, t0_o, d0_o)]
                    + self.energy_wheeled[s_o, t_o, d_o] * d_o
                )
        return expr[s, t, d] == 0
    else:
        return Constraint.Skip


def fuel_cell_production_curve(self, s, t, d):
    return (
        self.energy_HFC_flux[s, t, d] * self.fuel_cell_efficiency
        - self.energy_HFC[s, t, d]
        == 0
    )


def fuel_cell_capacity(self, s, t, d):
    return self.energy_HFC[s, t, d] - self.capacity_HFC <= 0


def electrolyser_production(self, s, t, d):
    return (
        sum(
            self.energy_electrolysers[s, t, d, k] * self.electrolyser_efficiency[k]
            for k in self.electrolysers
        )
        - self.energy_gH2_flux[s, t, d]
        == 0
    )


def electrolyser_capacity(self, s, t, d, k):
    return self.energy_electrolysers[s, t, d, k] - self.capacity_electrolysers[k] <= 0


def grid_use_balance(self, s):
    expr = {(0, 0, 1): 0}
    for s_o, t_o, d_o, s0_o, t0_o, d0_o in self.continuity_set:
        expr[(s_o, t_o, d_o)] = (
            expr[(s0_o, t0_o, d0_o)] + self.energy_grid[s_o, t_o, d_o] * d_o
        )
    return expr[s, t_o, d_o] == self.net_grid[s]


def grid_use_limit(self, s):
    if self.grid_connection.value:
        return Constraint.Skip
    else:
        return self.net_grid[s] <= 0


def compressor_balance(self, s, t, d):
    return (
        self.energy_compression[s, t, d]
        - sum(
            self.electrolyser_compression_energy[k]
            * (self.electrolyser_efficiency[k] / self.hydrogen_LHV)
            * self.energy_electrolysers[s, t, d, k]
            for k in self.electrolysers
        )
        - sum(
            self.vector_compression_penalty[q]
            / self.hydrogen_LHV
            * self.energy_gh2_use[s, t, d, q]
            for q in self.vectors
        )
        - self.storage_compression_penalty
        * (self.energy_gh2_in_store[s, t, d] / self.hydrogen_LHV)
        == 0
    )


def compression_limit(self, s, t, d):
    return self.energy_compression[s, t, d] - self.compression_capacity <= 0


def influent_hydrogen_balance(self, s, t, d):
    return (
        self.energy_gH2_flux[s, t, d] * self.compressor_effiency
        - self.energy_gh2_in_store[s, t, d]
        - sum(self.energy_gh2_use[s, t, d, q] for q in self.vectors)
        == 0
    )


def hydrogen_storage_balance(self, s, t, d, s_0, t_0, d_0):
    return (
        self.gh2_storage[s, t, d]
        - self.gh2_storage[s_0, t_0, d_0]
        + (
            sum(self.energy_gh2_rem[s, t, d, q] for q in self.vectors)
            + self.energy_HFC_flux[s, t, d]
            - self.energy_gh2_in_store[s, t, d]
        )
        * d
        == 0
    )


def hydrogen_storage_balance_contiguity(self, s):
    return (
        self.gh2_storage[0, 0, 1]
        - self.gh2_storage[s, self.end_time_index.value, 1]
        == 0
    )


def effluent_hydrogen_balance(self, s, t, d, s_v, t_v, d_v, q):
    return (
        self.energy_vector_production_flux[(s_v, t_v, d_v), q]
        / self.vector_synthetic_efficiency[q]
        - self.energy_gh2_rem[s, t, d, q]
        - self.energy_gh2_use[s, t, d, q]
        == 0
    )


def hydrogen_storage_limit(self, s, t, d):
    return self.gh2_storage[s, t, d] - self.capacity_gH2_storage <= 0


def hydrogen_storage_lower_limit(self, s, t, d):
    return 0.2 * self.capacity_gH2_storage - self.gh2_storage[s, t, d] <= 0


def vector_production_energy_balance(self, s, t, d, s_v, t_v, d_v, q):
    return (
        self.energy_vector_production_flux[(s_v, t_v, d_v), q]
        * (self.vector_variable_energy_penalty[q] / self.vector_calorific_value[q])
        * (1 - self.vector_fixed_energy_penalty[q])
        + self.number_active_trains[(s_v, t_v, d_v), q]
        * self.vector_fixed_energy_penalty[q]
        * self.vector_variable_energy_penalty[q]
        * self.single_train_throughput_limit[q]
        - self.energy_penalty_vector_production[(s_v, t_v, d_v), q] == 0
    )


def active_train_limit(self, s, t, d, s_v, t_v, d_v, q):
    return self.number_active_trains[(s_v, t_v, d_v), q] - self.capacity_vector_production[q] <= 0


def vector_lower_production_limit(self, s, t, d, s_v, t_v, d_v, q):
    return (
        self.single_train_throughput_limit[q]
        * self.minimum_process_throughput[q]
        * self.number_active_trains[(s_v, t_v, d_v), q]
        - self.energy_vector_production_flux[(s_v, t_v, d_v), q] / self.vector_calorific_value[q]
        <= 0
    )


def vector_upper_production_limit(self, s, t, d, s_v, t_v, d_v, q):
    if q == "LH2":
        return (
            self.energy_vector_production_flux[(s_v, t_v, d_v), q] / self.vector_calorific_value[q]
            + self.vector_storage_origin[s, t, d, q] * self.bol_rate[q] * self.bol_energy_penalty[q] * 1000
            - self.single_train_throughput_limit[q] * self.number_active_trains[(s_v, t_v, d_v), q]
            <= 0
        )
    else:
        return (
            self.energy_vector_production_flux[(s_v, t_v, d_v), q] / self.vector_calorific_value[q]
            - self.single_train_throughput_limit[q] * self.number_active_trains[(s_v, t_v, d_v), q]
            <= 0
        )


def lower_ramping_limit(
    self, s, t, d, s_0, t_0, d_0, s_v, t_v, d_v, s_v0, t_v0, d_v0, q
):
    if floor(self.time_values[t] / self.vector_operating_duration) == 0:
        return Constraint.Skip
    elif self.relaxed_ramping:
        if self.ramp_down_limit[q] * self.vector_operating_duration * d_v >= 1:
            return Constraint.Skip
        else:
            return (
                self.energy_vector_production_flux[(s_v0, t_v0, d_v0), q]
                - self.energy_vector_production_flux[(s_v, t_v, d_v), q]
            ) / self.vector_calorific_value[q] - (
                self.number_active_trains[(s_v, t_v, d_v), q]
                * self.single_train_throughput_limit[q]
                * self.ramp_down_limit[q]
                * self.vector_operating_duration
                * d
            ) <= 0
    else:
        return (
            self.energy_vector_production_flux[(s_v0, t_v0, d_v0), q]
            - self.energy_vector_production_flux[(s_v, t_v, d_v), q]
        ) / self.vector_calorific_value[q] - (
            self.number_active_trains[(s_v, t_v, d_v), q]
            * self.single_train_throughput_limit[q]
            * self.ramp_down_limit[q]
            * d
        ) <= 0


def upper_ramping_limit(
    self, s, t, d, s_0, t_0, d_0, s_v, t_v, d_v, s_v0, t_v0, d_v0, q
):
    if floor(self.time_values[t] / self.vector_operating_duration) == 0:
        return Constraint.Skip
    elif self.relaxed_ramping:
        if self.ramp_up_limit[q] * self.vector_operating_duration * d_v >= 1:
            return Constraint.Skip
        else:
            return (
                self.energy_vector_production_flux[(s_v, t_v, d_v), q]
                - self.energy_vector_production_flux[(s_v0, t_v0, d_v0), q]
            ) / self.vector_calorific_value[q] - (
                self.capacity_vector_production[q]
                + 1
                - self.number_active_trains[(s_v, t_v, d_v), q]
            ) * (
                self.single_train_throughput_limit[q]
                * self.ramp_up_limit[q]
                * self.vector_operating_duration
                * d
            ) <= 0
    else:
        return (
            self.energy_vector_production_flux[(s_v, t_v, d_v), q]
            - self.energy_vector_production_flux[(s_v0, t_v0, d_v0), q]
        ) / self.vector_calorific_value[q] - (
            self.capacity_vector_production[q]
            + 1
            - self.number_active_trains[(s_v, t_v, d_v), q]
        ) * (
            self.single_train_throughput_limit[q]
            * self.ramp_up_limit[q]
            * d
        ) <= 0


def origin_vector_storage_balance(
    self, s, t, d, s_0, t_0, d_0, s_v, t_v, d_v, s_v0, t_v0, d_v0, q
):
    return (
        (self.vector_storage_origin[s, t, d, q] - self.vector_storage_origin[s_0, t_0, d_0, q])
        * 1000
        + (
            -self.energy_vector_production_flux[(s_v, t_v, d_v), q]
            * self.vector_fugitive_efficiency[q]
            / self.vector_calorific_value[q]
            + self.number_ships_charging[s, t, d, q]
            * (self.ship_storage_capacity[q] / self.loading_time)
        )
        * d
        == 0
    )


def origin_vector_storage_balance_contiguity(self, s, q):
    return (
        self.vector_storage_origin[(0, 0, 1), q]
        - self.vector_storage_origin[(s, self.end_time_index.value, 1), q]
        <= 0
    )


def origin_vector_storage_limit(self, s, t, d, q):
    return self.vector_storage_origin[s, t, d, q] - self.capacity_vector_storage_origin[q] <= 0


def origin_storage_min(self, s, t, d, q):
    return 0.2 * self.capacity_vector_storage_origin[q] - self.vector_storage_origin[s, t, d, q] <= 0


def shipping_balance_charging_t_0(self, q):
    return self.number_ships_charging[0, 0, 1, q] == self.number_ships_start_charging[(0, 0, 1), q]


def shipping_balance_charging(
    self, s, t, d, s_0, t_0, d_0, s_c, t_c, d_c, s_c0, t_c0, d_c0, s_cd, t_cd, d_cd, q
):
    if t == t_c:
        return (
            self.number_ships_charging[s, t, d, q]
            == self.number_ships_charging[s_0, t_0, d_0, q]
            + self.number_ships_start_charging[(s_c, t_c, d_c), q] * d
        )
    if (t - self.loading_time) == t_cd:
        return (
            self.number_ships_charging[s, t, d, q]
            == self.number_ships_charging[s_0, t_0, d_0, q]
            - self.number_ships_start_charging[(s_cd, t_cd, d_cd), q] * d
        )
    else:
        return self.number_ships_charging[s, t, d, q] == self.number_ships_charging[s_0, t_0, d_0, q]


def total_capital_expenditure(self):
    expr = 0
    if self.wind:
        expr += self.turbine_unit_capital_cost * self.capacity_number_turbines * self.amortisation_turbine
    if self.solar:
        expr += self.solar_unit_capital_cost * self.capacity_solar * self.amortisation_solar
    expr += self.fuel_cell_unit_capital_cost * self.capacity_HFC * self.amortisation_fuel_cell
    expr += sum(
        self.electrolyser_unit_capital_cost[k]
        * self.capacity_electrolysers[k]
        * self.amortisation_electrolysers[k]
        for k in self.electrolysers
    )
    expr += (
        self.compression_capacity
        * self.compressor_unit_capital_cost
        * self.amortisation_compressor
        / self.hydrogen_LHV
    )
    expr += (
        self.hydrogen_storage_unit_capital_cost
        / self.hydrogen_LHV
        * self.capacity_gH2_storage
        * self.amortisation_hydrogen_storage
        * self.hydrogen_storage_cost_sf
    )
    expr += sum(
        self.vector_production_unit_capital_cost[q]
        * self.capacity_vector_production[q]
        * self.amortisation_vector_production[q]
        for q in self.vectors
    )
    expr += sum(
        self.capacity_vector_storage_origin[q]
        * self.vector_storage_unit_capital_cost[q]
        * self.amortisation_vector_storage[q]
        for q in self.vectors
    )
    return expr - self.CAPEX <= 0


def total_operating_expenditure(self, s):
    expr = 0
    if self.wind:
        expr += self.turbine_unit_operating_cost * self.capacity_number_turbines * self.amortisation_plant
    if self.solar:
        expr += self.solar_unit_operating_cost * self.capacity_solar * self.amortisation_plant
    expr += self.fuel_cell_unit_operating_cost * self.capacity_HFC * self.amortisation_plant
    if self.grid_connection.value:
        expr += (
            self.net_grid[s]
            * self.grid_energy_factor
            * self.LCAP
            * self.amortisation_plant
            * (8760 / self.end_time_index)
        )
    expr += sum(
        self.electrolyser_unit_operating_cost[k]
        * self.capacity_electrolysers[k]
        * self.amortisation_plant
        for k in self.electrolysers
    )
    expr += (
        self.compression_capacity
        * self.compressor_unit_operating_cost
        * self.amortisation_plant
        / self.hydrogen_LHV
    )
    expr += (
        self.hydrogen_storage_unit_operating_cost
        / self.hydrogen_LHV
        * self.capacity_gH2_storage
        * self.amortisation_plant
        * self.hydrogen_storage_cost_sf
    )
    expr += sum(
        self.vector_production_unit_operating_cost[q]
        * self.capacity_vector_production[q]
        * self.amortisation_plant
        for q in self.vectors
    )
    expr += sum(
        self.capacity_vector_storage_origin[q]
        * self.vector_storage_unit_operating_cost[q]
        for q in self.vectors
    ) * self.amortisation_plant
    return expr - self.OPEX[s] <= 0

def generate_inequalities(model):
    # Energy balance for the energy production of the system
    model.energy_balance = Constraint(model.vector_set_time, rule=energy_balance)
    model.grid_use_balance = Constraint(model.scenario, rule=grid_use_balance)
    model.grid_use_limit = Constraint(model.scenario, rule=grid_use_limit)

    # Electrolysis equations
    model.electrolyser_production = Constraint(
        model.full_set, rule=electrolyser_production
    )
    model.electrolyser_capacity = Constraint(
        model.full_set, model.electrolysers, rule=electrolyser_capacity
    )

    # Gaseous hydrogen storage equations
    model.hydrogen_storage_balance = Constraint(
        model.continuity_set, rule=hydrogen_storage_balance
    )
    model.hydrogen_storage_balance_contiguity = Constraint(
        model.scenario, rule=hydrogen_storage_balance_contiguity
    )
    model.hydrogen_storage_limit = Constraint(
        model.full_set, rule=hydrogen_storage_limit
    )
    model.hydrogen_storage_lower_limit = Constraint(
        model.full_set, rule=hydrogen_storage_lower_limit
    )
    model.influent_hydrogen_balance = Constraint(
        model.full_set, rule=influent_hydrogen_balance
    )
    model.effluent_hydrogen_balance = Constraint(
        model.vector_set_time, model.vectors, rule=effluent_hydrogen_balance
    )

    # Compression equations
    model.compression_limit = Constraint(
        model.full_set, rule=compression_limit
    )
    model.compression_balance = Constraint(
        model.full_set, rule=compressor_balance
    )

    # Vector production equations
    model.vector_production_energy_balance = Constraint(
        model.vector_set_time, model.vectors, rule=vector_production_energy_balance
    )
    model.vector_upper_production_limit = Constraint(
        model.vector_set_time, model.vectors, rule=vector_upper_production_limit
    )
    model.vector_lower_production_limit = Constraint(
        model.vector_set_time, model.vectors, rule=vector_lower_production_limit
    )
    model.active_train_limit = Constraint(
        model.vector_set_time, model.vectors, rule=active_train_limit
    )
    model.lower_ramping_limit = Constraint(
        model.vector_continuity_set, model.vectors, rule=lower_ramping_limit
    )
    model.upper_ramping_limit = Constraint(
        model.vector_continuity_set, model.vectors, rule=upper_ramping_limit
    )

    # Vector storage equations
    model.origin_vector_storage_balance = Constraint(
        model.vector_continuity_set, model.vectors, rule=origin_vector_storage_balance
    )
    model.origin_vector_storage_balance_contiguity = Constraint(
        model.scenario, model.vectors, rule=origin_vector_storage_balance_contiguity
    )
    model.origin_vector_storage_limit = Constraint(
        model.full_set, model.vectors, rule=origin_vector_storage_limit
    )
    model.origin_vector_storage_lower_limit = Constraint(
        model.full_set, model.vectors, rule=origin_storage_min
    )
    model.shipping_balance_charging = Constraint(
        model.shipping_continuity_set, model.vectors, rule=shipping_balance_charging
    )
    model.shipping_balance_charging_t_0 = Constraint(
        model.vectors, rule=shipping_balance_charging_t_0
    )

    # Fuel cell equations
    model.fuel_cell_production_curve = Constraint(
        model.full_set, rule=fuel_cell_production_curve
    )
    model.fuel_cell_capacity = Constraint(
        model.full_set, rule=fuel_cell_capacity
    )

    # Cost equations
    model.total_capital_expenditure = Constraint(
        rule=total_capital_expenditure
    )
    model.total_operating_expenditure = Constraint(
        model.scenario, rule=total_operating_expenditure
    )
    model.obj_constraint_2 = Constraint(rule=obj_constraint_2)

    if model.net_present_value.value:
        model.NPV = Constraint(rule=NPV)
    else:
        model.obj_constraint = Constraint(rule=obj_constraint)

    if model.grid_wheel:
        model.grid_wheel_lim = Constraint(
            model.continuity_set, rule=grid_wheel_lim
        )