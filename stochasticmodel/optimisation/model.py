from pyomo.environ import AbstractModel, Objective, minimize, SolverFactory, TerminationCondition
from OptimisationScripts.parameters import generate_parameters
from OptimisationScripts.inequalities import generate_inequalities, objective_function
from OptimisationScripts.OptimisationVariables import generate_variables
from OptimisationScripts.OptimisationPlots import (
    wind_energy, vector_production, hydrogen_production, hydrogen_storage_tank_level,
    origin_storage_tank_levels, grid_energy, curtailed_energy, objective_cdf, active_trains,LCOH_contributions
)
from matplotlib import rcParams
from pyomo.environ import TransformationFactory, Var, value
from os import getcwd, chdir
from dill import dump, load
from sys import exit
import time


class OptimModel:
    instance = None

    def __init__(self, parameters, key, probabilities=False):
        self.key = key
        start_time = time.time()
        self.setup_model(parameters, probabilities)
        self.generate_objective_function()
        print(f'Setup Model completed in {time.time() - start_time:.2f} seconds')
        
        start_time = time.time()
        self.build_model()
        print(f'Model Built in {time.time() - start_time:.2f} seconds')

    def setup_model(self, parameters, probabilities):
        self.model = AbstractModel()
        self.model.random_seed = int(parameters['random_seed'])
        generate_parameters(self.model, parameters, probabilities=False)
        generate_variables(self.model)
        generate_inequalities(self.model)

    def generate_objective_function(self):
        self.model.Obj = Objective(rule=objective_function, sense=minimize)

    def build_model(self):
        self.instance = self.model.create_instance()
        dir = getcwd()
        chdir(dir + '/PreSolvedModels')
        open(self.key + '.pickle', 'a').close()
        with open(self.key + '.pickle', 'wb') as f:
            dump(self.instance, f)
        chdir(dir)

    @staticmethod
    def get_param_dict(file_name):
        dir = getcwd()
        chdir(dir + '/PreSolvedModels')
        open(file_name + '.pickle', 'a').close()
        with open(file_name + '.pickle', 'rb') as f:
            parameters = load(f)
        chdir(dir)
        return OptimModel(parameters,key=file_name)
    
    @staticmethod
    def get_parameters(file_name):
        dir = getcwd()
        chdir(dir + '/PreSolvedModels')
        open(file_name + '.pickle', 'a').close()
        with open(file_name + '.pickle', 'rb') as f:
            parameters = load(f)
        chdir(dir)
        return parameters

    @classmethod
    def class_solve(cls, unbounded=False, feasibility=1e-2, optimality=1e-8, mip_percentage=5, random_seed=42, solver='gurobi', key=None, parallel=False,time=None,reinitialise=False):
        dir = getcwd()
        if cls.instance is None or reinitialise:
            chdir(dir + '/PreSolvedModels')
            with open(key + '.pickle', 'rb') as f:
                loaded = load(f)
                if isinstance(loaded,dict):
                    print('loaded recognised as dict')
                    chdir(dir)
                    cls = OptimModel.get_param_dict(key)
                    print(type(cls.instance))
                    chdir(dir + '/PreSolvedModels')
                else:
                    print('loaded recognised as instance')
                    cls.instance = loaded
                cls.key = key
            chdir(dir)
        print(type(cls.instance))
        chdir(dir + '/SolverLogs')
        cls.solver = SolverFactory(solver)
        cls.solver.options['FeasibilityTol'] = feasibility
        cls.solver.options['Seed'] = random_seed
        cls.solver.options['OptimalityTol'] = optimality
        cls.solver.options['MIPGap'] = mip_percentage / 100
        cls.solver.options['LogToConsole'] = 1
        cls.solver.options['LogFile'] = cls.key + '.log'
        
        if parallel:
            cls.solver.options['Threads'] = 8
            cls.solver.options['DistributedMIPJobs'] = 2
        if time is not None:
            cls.solver.options['TimeLimit'] = time
            cls.solver.options['ResultFile'] = cls.key+'_progress.mst'
            cls.solver.options['warmstart'] = 1
            try:
                cls.solver.options['MIPStart'] = cls.key+'_progress.mst'
            except:
                pass
            try:
                chdir(dir)
                chdir(dir + '/WarmStarts')
                with open(cls.key+'_warmstart.pickle', 'rb') as f:
                    variable_values = load(f)
                chdir(dir+ '/SolverLogs') 
                    
                print('Warmstart Found')
                for v in cls.instance.component_objects(Var, active=True):
                    if v.is_indexed():
                        for index in v:
                            var_name = f"{v.name}[{index}]"
                            if var_name in variable_values:
                                v[index].value = variable_values[var_name]
                    else:
                        if v.name in variable_values:
                            v.value = variable_values[v.name]
                print('Warmstart Loaded')
                cls.results = cls.solver.solve(cls.instance, tee=True,warmstart=True)
            except:
                chdir(dir+ '/SolverLogs')
                cls.results = cls.solver.solve(cls.instance, tee=True)
            

            if cls.results.solver.termination_condition == TerminationCondition.optimal:
                print("Optimal solution found. Exiting...")
                cls.results.write()
                chdir(dir)
                chdir(dir + '/SolvedModels')
                open(cls.key + '.pickle', 'a').close()
                with open(cls.key + '.pickle', 'wb') as f:
                    dump(cls.instance, f)
                chdir(dir)
                return cls  
            elif cls.results.solver.termination_condition in [TerminationCondition.maxTimeLimit]:
                print("Suboptimal solution found. Preparing warm start...")

                # Save variable values for warm start
                
                variable_values = {}
                for var in cls.instance.component_objects(Var, active=True):
                    if var.is_indexed():
                        # Loop over all scalar variables in the IndexedVar
                        for idx in var:
                            if var[idx].value is None:
                                pass
                            else:
                                variable_values[f"{var.name}[{idx}]"] = value(var[idx])
                    else:
                        if var.value is None:
                            pass
                        else:
                            variable_values[var.name] = value(var)
                chdir(dir)
                chdir(dir + '/WarmStarts')
                with open(cls.key+'_warmstart.pickle', 'wb') as f:
                    dump(variable_values, f)
                chdir(dir)
                exit(2)
                
        else:
            cls.results = cls.solver.solve(cls.instance, tee=True)
            cls.results.write()
            chdir(dir)
            chdir(dir + '/SolvedModels')
            open(cls.key + '.pickle', 'a').close()
            with open(cls.key + '.pickle', 'wb') as f:
                dump(cls.instance, f)
            chdir(dir)
            return cls
            

        

    @classmethod
    def get_solve(cls, key, reinitialise=False):
        dir = getcwd()
        if cls.instance is None or reinitialise:
            chdir(dir + '/SolvedModels')
            with open(key + '.pickle', 'rb') as f:
                cls.instance = load(f)
                cls.key = key
        chdir(dir)
        return cls

    def generate_plots(self, all=True, demand=False, storage_tanks=False, conversion_process=False, electrolyser_production=False, curtailed=False, grid=False, quality=150):
        # Initializing some global matplotlib parameters
        rcParams['font.family'] = 'serif'
        rcParams['font.serif'] = ['CMU Serif'] + rcParams['font.serif']
        rcParams['figure.dpi'] = quality

        # These colours are imperial's new brand colours... using these for plots
        colors = [
            "#232333", "#000080", "#0000CD", "#008080", "#232333", "#C71585",
            "#DC143C", "#006400", "#40E0D0", "#EE82EE", "#7B68EE", "#FF0000",
            "#FF8C00", "#00FF7F", "#F5F5F5", "#00BFFF", "#F0E68C", "#AFEEEE",
            "#FFB6C1", "#E6E6FA", "#FA8072", "#FFA500", "#98FB98"
        ]
        # Setting other global parameters relating to line_width
        self.alpha = 0.75
        self.custom_cmap = colors
        self.linewidth = 1.25

        # Generating the plots, in accordance with user chosen boolean values
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
        LCOH_contributions(self,threshold=0.01)
