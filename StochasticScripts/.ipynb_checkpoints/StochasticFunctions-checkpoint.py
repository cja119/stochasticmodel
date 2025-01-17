from csv import DictReader
from math import floor
from os import path
from numpy.random import randint
from pyomo.environ import Constraint
from functools import lru_cache


def wrapper(func):
    def inner(*args):
        # Check if the master branch is active
        if args[0].master_branches[args[1], floor(args[2] / args[0].stage_duration)] == 1:
            result = func(*args)
        else:
            # Skip the constraint if the master branch is inactive
            def skip(*args):
                return Constraint.Skip
            result = skip(*args)
        return result
    return inner


def generate_nonanticipativity_structure(n_stages, n_stochastics):
    master_branches = {}
    for w in range(n_stages + 1):
        for s in range(n_stochastics ** n_stages):
            if s % (n_stochastics ** (n_stages - w)) == 0:
                master_branches[(s, w)] = 1
            else:
                master_branches[(s, w)] = 0
    return master_branches


def generate_samples(wind_power, full_set):
    samples = {}
    complete_set = {}
    incumbent = 0
    counter = 0
    first = True
    lengths = []
    bookends = []
    for i in full_set:
        if first:
            first_val = i[1]
            first = False
        if i[0] == incumbent and i != full_set[-1]:
            counter += 1
        else:
            lengths.append(counter)
            incumbent = i[0]
            counter = 1
            last_val = i[1]
            bookends.append((first_val, last_val))
            first = True


    for count,length in enumerate(lengths):
        start_index = randint(0, len(wind_power) - length)
        complete_set[count] = wind_power.iloc[start_index:start_index + length].reset_index(drop=True)
    
    for count,val in enumerate(full_set):  
        samples[val] = complete_set[val[0]].iloc[val[1] - bookends[val[0]][0]].iloc[0]
        
    return samples


def extract_values(dictionary, index):
    extracted_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            extracted_dict[key] = extract_values(value, index)
        elif isinstance(value, (tuple, list)):
            extracted_dict[key] = value[index] if index < len(value) else None
        elif isinstance(value, (int, float)):
            extracted_dict[key] = value
        else:
            raise ValueError("Values should be tuples, lists, integers, or floats")
    return extracted_dict


def grab_from_store(title, folder='PreOptimisationDataStore'):
    data = {}
    csv_file = path.join(folder, title)

    # Open and read the CSV file
    with open(csv_file, 'r') as file:
        reader = DictReader(file)
        for row in reader:
            key = int(row['Key'])
            try:
                value = float(row['Value'])
            except:
                value = row['Value']
            data[key] = value
    return data


def general_nonanticipativity_constraint(var, weeks=False,stage=False):
    def inner(*args):
        model = args[0]
        master_branches = model.master_branches
        stage_duration = model.stage_duration
        vector_operating_duration = model.vector_operating_duration


        if weeks:
            i, j, *rest = args[1:]
            if master_branches[i, floor(j * vector_operating_duration/stage_duration)] == 1:
                return Constraint.Skip
            else:
                args_1 = (i, j) + tuple(rest)
                args_2 = (i - 1, j) + tuple(rest)
                return getattr(model, var)[args_1] == getattr(model, var)[args_2]
        elif stage:
            i, j, *rest = args[1:]
            if master_branches[i, floor(j)] == 1:
                return Constraint.Skip
            else:
                args_1 = (i, j) + tuple(rest)
                args_2 = (i - 1, j) + tuple(rest)
                return getattr(model, var)[args_1] == getattr(model, var)[args_2]
        else:
            i, j, *rest = args[1:]
            if master_branches[i, floor(j / stage_duration)] == 1:
                return Constraint.Skip
            else:
                args_1 = (i, j) + tuple(rest)
                args_2 = (i - 1, j) + tuple(rest)
                return getattr(model, var)[args_1] == getattr(model, var)[args_2]
    return inner

def build_stochastic_tree(n_branches, n_stages, stage_duration, other_grids = None, other_continuities = None):
    full_set = []
    continuity_set = []
    if other_grids is not None:
        grid_set = [[] for _ in range(len(other_grids))]
        overlapping_sets = [[] for _ in range(len(other_grids))]
        other_grid_branches = [0 for _ in range(len(other_grids))]
        complete_continuity_set = [[] for _ in range(len(other_grids))]
    if other_continuities is not None:
        other_continuity_sets = [[] for _ in range(len(other_continuities))]
        

    for time in range(stage_duration*(n_stages+1)):
        stage = time // stage_duration
        
        
        for branch in range(n_branches**stage):
            full_set.append((branch,time))
            
            if other_grids is not None:
                for grid in range(len(other_grids)):
                    if time % other_grids[grid] == 0:
                        grid_value = time / other_grids[grid]
                        other_grid_branches[grid] = n_branches**stage
                        grid_set[grid].append((branch,grid_value))
                        
                    largest_inherited_branch = other_grid_branches[grid]
                    num_stages_passed = n_branches**stage // (largest_inherited_branch*n_branches)
                    parent = branch // (n_branches**num_stages_passed)
                    overlapping_sets[grid].append(((branch,time),(int(parent), int(time // other_grids[grid]))))
            
                    
        if (time+1) % stage_duration == 0:
            for branch in range(n_branches**(stage+1)):
                parent = branch // n_branches
                if time + 1 < stage_duration*(n_stages+1):
                    continuity_set.append(((branch,(stage+1)*stage_duration),(parent,(stage+1)*stage_duration-1)))
                
                for count,continuity in enumerate(other_continuities):
                    for ct_count,cont_tup in enumerate(other_continuity_sets[count]):
                        if cont_tup[0][0] == branch and cont_tup[0][1] == time+1:
                            other_continuity_sets[count][ct_count] = (cont_tup[0], (parent,(stage+1)*stage_duration-1),cont_tup[1])
        else:
            for branch in range(n_branches**stage):
                if time + 1 < stage_duration*(n_stages+1):
                    continuity_set.append(((branch,time+1),(branch,time)))
        
                for count,continuity in enumerate(other_continuities):
                    for ct_count,cont_tup in enumerate(other_continuity_sets[count]):
                        if cont_tup[0][0] == branch and cont_tup[0][1] == time+1:
                            other_continuity_sets[count][ct_count] = (cont_tup[0], (branch,time),cont_tup[1])
        
        
        
        for count,continuity in enumerate(other_continuities):
            if (time + continuity[1]) % stage_duration < continuity[1]:
                stage_skip = continuity[1] // stage_duration
                for branch in range(n_branches**(stage + 1 + stage_skip)):
                    parent = branch // (n_branches**(stage_skip + 1))
                    if time + continuity[1] < stage_duration*(n_stages + 1 + stage_skip):
                                other_continuity_sets[count].append(((branch,time + continuity[1]),(parent,time)))
                    
            else:
                for branch in range(n_branches**stage):
                    if time + 1 < stage_duration*(n_stages+1):
                        other_continuity_sets[count].append(((branch,time + continuity[1]),(branch,time)))
                        

        
        
    
    
    full_set = sorted(full_set, key=lambda x: x[0])
    
    
    for count,continuity in enumerate(other_grids):
        
        for j,i in enumerate(continuity_set):

            current_point = [q[1] for q in overlapping_sets[count] if q[0] == i[0]]
            previous_point =  [q[1] for q in overlapping_sets[count] if q[0] == i[1]]

            if count == 0:
                complete_continuity_set[count].append((i[0],i[1],*current_point,*previous_point))
            else:
                additional_point = []
                for q in other_continuity_sets[0]:
                    if q[0] == i[0]:
                        additional_point = [a[1] for a in overlapping_sets[count] if a[0] == q[2]]
                    else:
                        pass
                if additional_point == []:
                    additional_point = [(0,0)]
                
                complete_continuity_set[count].append((i[0],i[1],*current_point,*previous_point,*additional_point))
   
    
    if other_grids is None:
        return full_set, continuity_set
    else:
        if other_continuities is None:
            return full_set, continuity_set, grid_set, overlapping_sets, complete_continuity_set
        else:
            return full_set, continuity_set, grid_set, overlapping_sets,complete_continuity_set, other_continuity_sets
