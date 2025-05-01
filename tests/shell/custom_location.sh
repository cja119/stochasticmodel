#!/bin/bash

# This loads in the credentials for the Earthdata login
script_dir=$(dirname "$0")
if [ -f "$script_dir/_creds.sh" ]; then
    chmod +x "$script_dir/_creds.sh"
    source "$script_dir/_creds.sh"
    echo "[INFO] Earthdata credentials loaded successfully"
fi

# These variables can be changed subject to the chosen location 
vector="NH3"
grid_connection="False"
n_stages=3
n_branches=3
stage_duration=168
renewables=Wind
key='weather_test'
random_seed=42
feasibility=1e-6
optimality=1e-8
mip_percentage=5
random_seed=42

# These two scripts are used to build the weather data and solve the model
python tests/models/weather_build.py "$n_stages" "$n_branches" "$vector" "$random_seed" "$stage_duration" "$renewables" "$grid_connection" "$key"
python tests/models/solve.py "$key" "$feasibility" "$optimality" "$mip_percentage" "$random_seed"
