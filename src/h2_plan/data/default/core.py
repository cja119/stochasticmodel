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
    
        

    def filter_params(self,key):
        """
        Performs a depth search to find the key in the dictionary and picks the value based on the key.
        """
        def recursive_filter(d, key):
            if isinstance(d, dict):
                if key in d:
                    return d[key]
                return {k: recursive_filter(v, key) for k, v in d.items()}
            elif isinstance(d, list):
                return [recursive_filter(item, key) for item in d]
            return d

        self.formulation_parameters = recursive_filter(self.formulation_parameters, key)

    def __enter__(self):
        return self.formulation_parameters
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass