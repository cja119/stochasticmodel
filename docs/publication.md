# Reproducing Publication Results

In order to reproduce the results of the scenario analyses, in a terminal run:
```
bash  test/shell/exexute.sh
```
Then modify the following by coding in **one** of the values in each brackets, to create the eight different scneario permutations. It is reccomended to modify the key parameter value to ensure saved runs don't override eachother:
```
vector=("LH2","NH3")
grid_connection=("True","False")
grid_connection=("True","False")
n_stages=(1,2,3,4,5...)
n_branches=(1,2,3,4,5...)
stage_duration=(1,2,3,4,5...)
renewables=("Wind","Solar")
key='SampleModel'
random_seed=42
```
Run the scripts, using the following command:
```
bash SolveModel.sh
```
## Parametric Modification
In order to manually change parameters, head to the pre-optimisation datastore and change the values of the parameters in the middle of the upper and lower bounds. These are taken as default values for the model when solving. Other, formulation specific, parameters can be found in the 'Executionscripts/BuildModel.py' file, this is accessed prior to each model solution. 


## Pareto Fronts

The files to generate the pareto fronts are present, but the executions shell scripts are omitted, as they were solved on a HPC cluster and, as such, are coded in a proprietary manner. Any user wishing to perform these solves is encouraged to produce a suitable shell script that can parallelise the solves for their system. The global sensitivity scripts are coded in such a manner that they solve in three stages: 
  1) The first stage builds the models and saves them in the 'PreSolvedModelsFolder'. This step is computed serially.
  2) On completion of the first stage, the second stage access a list of model names from the SolverLogs folder, and accesses these using an 'array index' of the hpc clusters multisolve capability. This step is computed in parallel.
  3) For the final stage, once the parallel solves are complete, the final stage calculates the LCOH values and stores them in the DataAnalysis Folder.
  4) The StochasticScripts.ParetoFronts.ParetoFront.plot_pareto_front(FileName) will then visualise the results.
