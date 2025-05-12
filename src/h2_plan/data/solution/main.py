"""
This module takes an instance of the solved model and extracts the results in regards
to the planning.
"""

from __future__ import annotations
from h2_plan.opt import H2Planning
from typing import Optional
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
                sum(mi.capacity_vector_production[q].value for q in mi.vectors)
            ),
            "capex": mi.CAPEX.value,
            "opex": sum(mi.OPEX[s].value for s in mi.scenario)
        }
        if targ is None:
            targ = Path(__file__).parent.parent.parent / "tmp/yml"
        else:
            targ = Path(targ)
            
        if not targ.exists():
            targ.mkdir(parents=True, exist_ok=True)
            
        with open(targ / self.filename, "w") as file:
            yaml.dump(self._res, file)

        return self._res