
# Installation Guide

## Dependencies [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3124/) [![Conda 24.5.0](https://img.shields.io/badge/conda-24.5.0-green.svg)](https://anaconda.org/anaconda/conda/files?page=1&type=conda&version=24.5.0) [![Gurobi 11.03](https://img.shields.io/badge/gurobi-11.0.3-red.svg)](https://www.gurobi.com/downloads/gurobi-optimizer-release-notes-v11-0-3/)
In order to run this model, a licence for [gurobi](https://www.gurobi.com/) is required, as is an installation of [conda](https://docs.anaconda.com/miniconda/). 

## Quick Start
For a quick start, it is first necessary to install PystochOpt, following the instructions available in that repository. Then run the folliwng command to clone this repository to your local machine:
```
pip3 install git@https://github.com/cja119/stochasticmodel.git
```

To run the sample formulation, execute the bash script as follows

```
bash /tests/shell/execute.sh
```

## Weather Data and TimeSeries Clustering

The weatherdata csv can be found in the 'meteor_py/data' folder, along with the appropriatley clustered demand signal and timeseries datasets. Running the shell script at tests/shell/custom_location.sh will grab the weatherdata files from the NASA Merra-2 database. This is achieved using the [EarthAccess Library](https://earthaccess.readthedocs.io/en/latest/) (N.B., this will require an [EarthData](https://urs.earthdata.nasa.gov/) account, with 'NASA GESDISC DATA ARCHIVE' activated under the applications tab). Once set up, save your username and password as environment variables using the following shell commands:

Save these lines in a _creds.sh file in the /tests/shell folder to automate the finding of the variables:

```
export EARTHDATA_USERNAME="Your_Username"
export EARTHDATA_PASSWORD="Your_Password"
```