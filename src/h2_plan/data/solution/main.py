"""
This module takes an instance of the solved model and extracts the results in regards
to the planning.
"""

from __future__ import annotations
from h2_plan.opt import H2Planning
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

    def evaluate_total_capex_terms(self):
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
