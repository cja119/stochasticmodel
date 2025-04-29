from pathlib import Path
import json

class DefaultParams:
    def __init__(self,name = 'default'):
        self.path = Path(__file__).resolve().parent / f"{name}.json"
        
        with open(self.path, 'r') as f:
            self.formulation_parameters = json.load(f)

        self.formulation_parameters.update({'shipping_regularity': 168,
                                        'ramping_frequency': 1,
                                        'hydrogen_storage_cost_sf': 1,
                                        'grid_energy_factor': 2.5})
        pass

    def __enter__(self):
        return self.formulation_parameters
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass