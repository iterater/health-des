# Planned stenting patients paths

## General description

Classification of pathways for planned stenting (PCI). Two classes were identified: for 1 and 2 PCIs. Each class is described with a states, transition probabilities, observed LoS for states.
  
### States naming convention

- `_01` - initial state
- `*01` - final state
- `Axx` - reception
- `Exx` - cardiological department
- `Fxx` - intensive care department
- `Ixx` - surgery
- `Nxx` - coronarography

Here `xx` is two-digit ID of state within a group. 

## Files

### Clusters

For each two clusters (directories `1` and `2`, named by number of PCIs in path):

- `N/Transition_matrixN.csv` - transition matrix (probability of transition from state to state) for all available states (csv, headers in first row and column)
- `N/Distr_statesN/XXX.txt` - set of observed data for length of stay in state `XXX`
- `N/labelN.png` - plotted labeled graph for states in cluster
- `N/Noper.png` - plotted length of stay for different states

Here `N` is number of PCIs, `XXX` is states (can be obtained from transition matrices). 

### Flow of patients

- `planned_in_per_day.txt` - number of patients per day (1 column, no header)
- `planned_in_time_in_day.txt` - time of patients arrival starting from the beginning of the day in minutes (1 column, no header)
