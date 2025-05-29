"""
This module takes an instance of the solved model and extracts the results in regards
to the planning.
"""

from __future__ import annotations
from h2_plan.opt import H2Planning
from collections import defaultdict
from typing import Optional
from pyomo import value
from pathlib import Path
import yaml


class PlanningResults:
    """
    
    """
    def __init__(self, model: H2Planning):
        """
        Initialize the PlanningResults object with the given model.

        Args:
            model (H2Planning): The H2Planning model instance.
        """
        self.model = model
        self.results = None

    def extract_results(self, targ = Optional[str]):
        """
        Extracts the results from the model, including ranges for all variables.
        """

        mi = self.model.instance

        self._res = {
            "renewable_energy_capacity": (
                mi.capacity_solar.value if mi.solar 
                else mi.capacity_number_turbines.value if mi.wind 
                else 0
            ),
            "hydrogen_storage_capacity": mi.capacity_gH2_storage.value,
            "fuelcell_capacity": mi.capacity_HFC.value,
            "compression_capacity": mi.compression_capacity.value,
            "electrolyser_capacity": sum(mi.capacity_electrolysers[k].value for k in mi.electrolysers),
            "conversion_trains_number": (
                sum(mi.capacity_vector_production[q] for q in mi.vectors)
            ),
            "vector_storage_capacity": (
                sum(mi.capacity_vector_storage_origin[q].value for q in mi.vectors)
            ),
            "capex": mi.CAPEX.value,
            "opex": sum(mi.OPEX[s].value for s in mi.scenario) / len(mi.scenario),
            "vector": mi.vectors.at(1),
            'renewables': 'solar' if mi.solar else 'wind' if mi.wind else 'none',
        }
        if targ is None:
            targ = Path(__file__).parent.parent.parent / "tmp/yml"
        else:
            targ = Path(targ)
            
        if not targ.exists():
            targ.mkdir(parents=True, exist_ok=True)
            
        with open(targ / (self.model.filename + '.yml'), "w") as file:
            yaml.dump(self._res, file)

        return self._res

    def capex(self):
        results = {}
        model = self.model.instance
        # Wind CAPEX
        if value(model.wind):
            wind_capex = (
                value(model.turbine_unit_capital_cost)
                * value(model.capacity_number_turbines)
                * value(model.amortisation_turbine)
            )
            results["wind_capex"] = wind_capex
        else:
            results["wind_capex"] = 0.0
    
        # Solar CAPEX
        if value(model.solar):
            solar_capex = (
                value(model.solar_unit_capital_cost)
                * value(model.capacity_solar)
                * value(model.amortisation_solar)
            )
            results["solar_capex"] = solar_capex
        else:
            results["solar_capex"] = 0.0
    
        # Fuel cell CAPEX
        fuel_cell_capex = (
            value(model.fuel_cell_unit_capital_cost)
            * value(model.capacity_HFC)
            * value(model.amortisation_fuel_cell)
        )
        results["fuel_cell_capex"] = fuel_cell_capex
    
        # Electrolysers CAPEX
        electrolyser_capex = 0.0
        for k in model.electrolysers:
            term = (
                value(model.electrolyser_unit_capital_cost[k])
                * value(model.capacity_electrolysers[k])
                * value(model.amortisation_electrolysers[k])
            )
            electrolyser_capex += term
        results["electrolyser_capex"] = electrolyser_capex
    
        # Compressor CAPEX
        compressor_capex = (
            value(model.compression_capacity)
            * value(model.compressor_unit_capital_cost)
            * value(model.amortisation_compressor)
            / value(model.hydrogen_LHV)
        )
        results["compressor_capex"] = compressor_capex
    
        # H2 Storage CAPEX
        hydrogen_storage_capex = (
            value(model.hydrogen_storage_unit_capital_cost)
            / value(model.hydrogen_LHV)
            * value(model.capacity_gH2_storage)
            * value(model.amortisation_hydrogen_storage)
            * value(model.hydrogen_storage_cost_sf)
        )
        results["hydrogen_storage_capex"] = hydrogen_storage_capex
    
        # Vector Production CAPEX
        vector_production_capex = 0.0
        for q in model.vectors:
            term = (
                value(model.vector_production_unit_capital_cost[q])
                * value(model.capacity_vector_production[q])
                * value(model.amortisation_vector_production[q])
            )
            vector_production_capex += term
        results["vector_production_capex"] = vector_production_capex
    
        # Vector Storage CAPEX
        vector_storage_capex = 0.0
        for q in model.vectors:
            term = (
                value(model.capacity_vector_storage_origin[q])
                * value(model.vector_storage_unit_capital_cost[q])
                * value(model.amortisation_vector_storage[q])
            )
            vector_storage_capex += term
        results["vector_storage_capex"] = vector_storage_capex
    
        # Total CAPEX
        total = sum(results.values())
        results["total_CAPEX"] = total
        results["CAPEX_constraint_rhs"] = value(model.CAPEX)
    
        return results
        
    def opex(self):
        model = self.model.instance
        
        # Initialize accumulator for each component
        accum = defaultdict(float)
        count = 0
    
        for s in model.S:  # or replace `model.S` with your actual set
            count += 1
    
            # Wind
            if value(model.wind):
                accum["wind_opex"] += (
                    value(model.turbine_unit_operating_cost)
                    * value(model.capacity_number_turbines)
                    * value(model.amortisation_plant)
                )
    
            # Solar
            if value(model.solar):
                accum["solar_opex"] += (
                    value(model.solar_unit_operating_cost)
                    * value(model.capacity_solar)
                    * value(model.amortisation_plant)
                )
    
            # Fuel Cell
            accum["fuel_cell_opex"] += (
                value(model.fuel_cell_unit_operating_cost)
                * value(model.capacity_HFC)
                * value(model.amortisation_plant)
            )
    
            # Grid
            if value(model.grid_connection):
                accum["grid_opex"] += (
                    value(model.net_grid[s])
                    * value(model.grid_energy_factor)
                    * value(model.LCAP)
                    * value(model.amortisation_plant)
                    * (8760 / value(model.end_time_index))
                )
    
            # Electrolyser
            for k in model.electrolysers:
                accum["electrolyser_opex"] += (
                    value(model.electrolyser_unit_operating_cost[k])
                    * value(model.capacity_electrolysers[k])
                    * value(model.amortisation_plant)
                )
    
            # Compressor
            accum["compressor_opex"] += (
                value(model.compression_capacity)
                * value(model.compressor_unit_operating_cost)
                * value(model.amortisation_plant)
                / value(model.hydrogen_LHV)
            )
    
            # H2 Storage
            accum["hydrogen_storage_opex"] += (
                value(model.hydrogen_storage_unit_operating_cost)
                / value(model.hydrogen_LHV)
                * value(model.capacity_gH2_storage)
                * value(model.amortisation_plant)
                * value(model.hydrogen_storage_cost_sf)
            )
    
            # Vector production
            for q in model.vectors:
                accum["vector_production_opex"] += (
                    value(model.vector_production_unit_operating_cost[q])
                    * value(model.capacity_vector_production[q])
                    * value(model.amortisation_plant)
                )
    
            # Vector storage
            for q in model.vectors:
                accum["vector_storage_opex"] += (
                    value(model.capacity_vector_storage_origin[q])
                    * value(model.vector_storage_unit_operating_cost[q])
                ) * value(model.amortisation_plant)
    
        # Compute averages
        averaged = {k: v / count for k, v in accum.items()}
        averaged["average_total_OPEX"] = sum(averaged.values())
    
        return averaged
