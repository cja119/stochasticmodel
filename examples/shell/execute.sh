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

python -m examples.models.compile "$n_stages" "$n_branches" "$vector" "$random_seed" "$stage_duration" "$renewables" "$grid_connection" "$key"
python -m examples.models.solve "$key" "$feasibility" "$optimality" "$mip_percentage" "$random_seed"
