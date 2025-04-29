#!/bin/bash


vector="NH3"
grid_connection="False"
n_stages=3
n_branches=3
stage_duration=168
renewables=Wind
key='test_model'
random_seed=42
feasibility=1e-6
optimality=1e-8
mip_percentage=5
random_seed=42

python tests/models/compile.py "$n_stages" "$n_branches" "$vector" "$random_seed" "$stage_duration" "$renewables" "$grid_connection" "$key"
python tests/models/solve.py "$key" "$feasibility" "$optimality" "$mip_percentage" "$random_seed"
