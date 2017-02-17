# Experiment #2: ACS patients flow without classification

## Experiment description

Simulation of patients with two flows: ACS patients from [ACS data without clustering](/data/acs_no_clusters/) and background flow for surgery facilities load with [surgery flow data](/data/surgeries/). To be compared with [Experiment #1](/docs/experiment_02_acs_no_clusters.md). Parameters variation:

- Target (ACS) flow scaling: 0.5, 1.0, 1.5, 2.0
- Background (surgery) flow scaling: 0.5, 1.0, 1.5, 2.0
- Number of parallel surgeries facilities: 1, 2, 3, 4, 5

Every combination of three parameters is executed 100 times with simulation of 60 days (4*4*5*100=8.000 runs in total). Executed in parallel.

## Simulation results

TBD