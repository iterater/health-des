# Experiment #1: ACS patients flow with classification

Implemented in [experiment_01_acs.py](experiment_01_acs.py)

## Experiment description

Simulation of patients with two flows: ACS patients from [ACS clustered data](/data/acs/) and background flow for surgery facilities load with [surgery flow data](/data/surgeries/). Parameters variation:

- Target (ACS) flow scaling: 0.5, 1.0, 1.5, 2.0
- Background (surgery) flow scaling: 0.5, 1.0, 1.5, 2.0
- Number of parallel surgeries facilities: 1, 2, 3, 4, 5

Every combination of three parameters is executed 100 times with simulation of 60 days (4*4*5*100=8.000 runs in total). Executed in parallel.

## Simulation results

![Simulation results](/pics/SiH_paper_fig_10.png)

(a) - QQ-plot for total LoS for all cases and top-3 clusters; (b) - percentage of cases where waiting in queue was detected for different background scales; (c) mean waiting time for different background scales

Additional visualization (Jupyter notebooks):

- [LoS plotting](/docs/plotting_los.ipynb) 
- [Queueing analysis and plotting](/docs/plotting_stats_multiple_scales.ipynb)
- [Queueing analysis and plotting (old version)](/docs/plotting_stats.ipynb)
