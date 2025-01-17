#!/bin/bash


vector="NH3"
grid_connection="False"
n_stages=3
n_branches=3
stage_duration=168
renewables=Wind
key='SampleModel'
random_seed=42


python ExecutionScripts/BuildModel.py "$n_stages" "$n_stochastics" "$vector" "$random_seed" "$stage_duration" "$renewables" "$grid_connection" "$key"
python ExecutionScripts/SolvePareto.py "$key" 
