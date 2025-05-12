"""
This code defines the OptimisationModel class, which is used to create and solve an optimisation model using Pyomo.
"""

import time
from os import getcwd, chdir
from sys import exit
from dill import dump, load
from pathlib import Path
from matplotlib import rcParams
from pyomo.environ import (
    AbstractModel, Objective, minimize, SolverFactory, TerminationCondition,
    TransformationFactory, Var, value
)
from .vars.param import generate_parameters
from .funcs.ineq import generate_inequalities, objective_function
from .vars.vars import generate_variables
from .utils import (
    wind_energy, vector_production, hydrogen_production,
    hydrogen_storage_tank_level, origin_storage_tank_levels, grid_energy,
    curtailed_energy, objective_cdf, active_trains, LCOH_contributions
)


class H2Planning:
    instance = None
    """
    This class is used to create and solve an optimisation model using Pyomo.
    It includes methods for setting up the model, generating the objective function,
    building the model, and solving it using a specified solver.
    It also includes methods for generating plots of the results and for handling
    warm starts.

    Attributes:
    .. parameters 
        instance: The Pyomo model instance.
        key: A string used to identify the model.
        solver: The solver used to solve the model.
        results: The results of the optimisation.
        model: The Pyomo model.
        alpha: The transparency level for plots.
        custom_cmap: A list of colors for plots.
        linewidth: The line width for plots.
    .. methods
        __init__(self, parameters, key, probabilities=False):
            Initializes the model with the given parameters and key.
        setup_model(self, parameters, probabilities):
            Sets up the model with the given parameters.
        generate_objective_function(self):
            Generates the objective function for the model.

        build_model(self):
            Builds the model and saves it to a file.
        get_param_dict(file_name):
            Loads the parameters from a file and returns an OptimisationModel instance.
        get_parameters(file_name):
            Loads the parameters from a file and returns them as a dictionary.
        class_solve(cls, unbounded=False, feasibility=1e-2, optimality=1e-8,
            mip_percentage=5, random_seed=42, solver='gurobi', key=None,
            parallel=False, time=None, reinitialise=False):
            Solves the model using the specified solver and parameters.
        get_solve(cls, key, reinitialise=False):
            Loads the model from a file and returns an OptimisationModel instance.
       
         generate_plots(self, all=True, demand=False, storage_tanks=False,
            conversion_process=False, electrolyser_production=False,
            curtailed=False, grid=False, quality=150):
            Generates plots of the results.
        
    """

    def __init__(self, parameters, key, filename, filepath = None):
        self.key = key
        self.filename = filename
        self.filepath = filepath
        start_time = time.time()
        self.setup_model(parameters)
        self.generate_objective_function()
        print(f'[INFO] Setup Model completed in {time.time() - start_time:.2f} seconds')

        start_time = time.time()
        self.build_model()
        print(f'[INFO] Model Built in {time.time() - start_time:.2f} seconds')

    def setup_model(self, parameters):
        self.model = AbstractModel()
        self.model.random_seed = int(parameters['random_seed'])
        generate_parameters(self.model, parameters, self.filename, self.filepath)
        generate_variables(self.model)
        generate_inequalities(self.model)

    def generate_objective_function(self):
        self.model.Obj = Objective(rule=objective_function, sense=minimize)

    def build_model(self):
        self.instance = self.model.create_instance()
        current_dir = Path(__file__).resolve().parent
        presolve_dir = current_dir.parent / "tmp" / 'pre'

        open(presolve_dir/f"{self.key}.pickle", 'a').close()
        with open(presolve_dir/f"{self.key}.pickle", 'wb') as f:
            dump(self.instance, f)
        chdir(current_dir)

    @staticmethod
    def get_param_dict(file_name):
        current_dir = Path(__file__).resolve().parent
        presolve_dir = current_dir.parent.parent / "tmp" / 'pre'
        open(presolve_dir/f"{file_name}.pickle", 'a').close()
        with open(presolve_dir/f"{file_name}.pickle", 'rb') as f:
            parameters = load(f)
        chdir(current_dir)
        return H2Planning(parameters, key=file_name)

    @staticmethod
    def get_parameters(file_name):
        current_dir = Path(__file__).resolve().parent
        presolve_dir = current_dir.parent.parent / "tmp" / 'pre'
        open(presolve_dir/f"{file_name}.pickle", 'a').close()
        with open(presolve_dir/f"{file_name}.pickle" 'rb') as f:
            parameters = load(f)
        chdir(current_dir)
        return parameters

    @classmethod
    def class_solve(
        cls, feasibility=1e-2, optimality=1e-8, mip_percentage=5,
        random_seed=42, solver='gurobi', key=None, parallel=False, time=None,
        reinitialise=False, verbose = True
    ):
        """
        This method solves the optimisation model using the specified solver
        and parameters. It also handles warm starts and saves the results to a file.
        
        Parameters:
        .. feasibility (float): Feasibility tolerance for the solver.
        .. optimality (float): Optimality tolerance for the solver.
        .. mip_percentage (float): MIP gap percentage for the solver.
        .. random_seed (int): Random seed for the solver.
        .. solver (str): The solver to use (default is 'gurobi').
        .. key (str): A string used to identify the model.
        .. parallel (bool): Whether to use parallel processing (default is False).
        .. time (int): Time limit for the solver (default is None).
        .. reinitialise (bool): Whether to reinitialise the model (default is False).

        """
        # Get the current working directory
        current_dir = Path(__file__).resolve().parent
        cls.filename = key

        # Target directory for presolved model
        cache_dir = current_dir.parent / "tmp" 

        # Check if the instance is None or if reinitialisation is required
        if cls.instance is None or reinitialise:
            with open(cache_dir / f"pre/{key}.pickle", 'rb') as f:
                loaded = load(f)
                if isinstance(loaded, dict):
                    print('Loaded recognised as dict')
                    cls = H2Planning.get_param_dict(key)
                else:
                    print('[INFO] Loaded recognised as instance')
                    cls.instance = loaded
                cls.key = key

        # Setting up the solver
        solve_kwargs = {}
        cls.solver = SolverFactory(solver)
        
        if solver == "cbc":
            cls.solver.options['ratioGap'] = mip_percentage / 100
            cls.solver.options['logLevel'] = 1
            cls.solver.options['randomCbcSeed'] = random_seed
            if parallel:
                cls.solver.options['threads'] = 8
            solve_kwargs['tee'] = True
            solve_kwargs['logfile'] = str(cache_dir / f"log/{cls.key}.log")
        elif solver == "gurobi":
            cls.solver.options['FeasibilityTol'] = feasibility
            cls.solver.options['OptimalityTol'] = optimality
            cls.solver.options['MIPGap'] = mip_percentage / 100
            cls.solver.options['LogToConsole'] = 1
            cls.solver.options['LogFile'] = str(cache_dir / f"log/{cls.key}.log")
            solve_kwargs['tee'] = True
            if parallel:
                cls.solver.options['Threads'] = 8
                cls.solver.options['DistributedMIPJobs'] = 2
                
        if verbose is False:
            cls.solver.options['LogToConsole'] = 0
            cls.solver.options.pop('LogFile', None)
            cls.solver.options['OutputFlag'] = 0
            solve_kwargs['tee'] = False


        # Solving the model
        cls.results = cls.solver.solve(cls.instance, **solve_kwargs)
        
        # Saving the results
        if verbose:
            cls.results.write()
        open(cache_dir / f"post/{cls.key}.pickle", 'a').close()
        with open(cache_dir / f"post/{cls.key}.pickle", 'wb') as f:
            dump(cls.instance, f)
        return cls

    @classmethod
    def get_solve(cls, key, reinitialise=False):
        """
        This method loads the model from a file and returns an OptimisationModel instance.
        """
        # Get the current working directory
        current_dir = Path(__file__).resolve().parent

        # Target directory for presolved model
        cache_dir = current_dir.parent.parent / "cache"  
        
        if cls.instance is None or reinitialise:
            with open(cache_dir / f"post/{key}.pickle", 'rb') as f:
                cls.instance = load(f)
                cls.key = key
        return cls

    def generate_plots(
        self, all=True, demand=False, storage_tanks=False, conversion_process=False,
        electrolyser_production=False, curtailed=False, grid=False, quality=150
    ):
        """
        This method generates plots of the results using matplotlib.
        Parameters:
        .. all (bool): If True, generates all plots.
        .. demand (bool): If True, generates demand plots.
        .. storage_tanks (bool): If True, generates storage tank plots.
        .. conversion_process (bool): If True, generates conversion process plots.
        .. electrolyser_production (bool): If True, generates electrolyser production plots.
        .. curtailed (bool): If True, generates curtailed energy plots.
        .. grid (bool): If True, generates grid energy plots.
        .. quality (int): Quality of the plots (default is 150).
        """
        # Set the font properties for the plots
        rcParams['font.family'] = 'serif'
        rcParams['font.serif'] = ['CMU Serif'] + rcParams['font.serif']
        rcParams['figure.dpi'] = quality

        # Set the colors for the plots
        colors = [
            "#232333", "#000080", "#0000CD", "#008080", "#232333", "#C71585",
            "#DC143C", "#006400", "#40E0D0", "#EE82EE", "#7B68EE", "#FF0000",
            "#FF8C00", "#00FF7F", "#F5F5F5", "#00BFFF", "#F0E68C", "#AFEEEE",
            "#FFB6C1", "#E6E6FA", "#FA8072", "#FFA500", "#98FB98"
        ]

        # Set the transparency level and line width for the plots
        self.alpha = 0.75
        self.custom_cmap = colors
        self.linewidth = 1.25

        # Generate the plots based on the specified parameters
        if demand or all:
            wind_energy(self)
        if grid or all:
            grid_energy(self)
        if curtailed or all:
            curtailed_energy(self)
        if storage_tanks or all:
            hydrogen_storage_tank_level(self)
            origin_storage_tank_levels(self)
        if conversion_process or all:
            vector_production(self)
            active_trains(self)
        if electrolyser_production or all:
            hydrogen_production(self)
        objective_cdf(self)
        LCOH_contributions(self, threshold=0.01)
