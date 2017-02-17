# ACS patients paths

## General description

Classification of pathways for ACS patients. Ten classes were identified according to clustering of observed paths. Each class is described with a states, transition probabilities, observed LoS for states.
  
### States naming convention

- `_01` - initial state
- `*01` - final state
- `Axx` - reception
- `Dxx` - reception for transfer to further treatment
- `Exx` - cardiological department
- `Fxx` - intensive care department
- `Ixx` - surgery
- `Nxx` - coronarography

Here `xx` is two-digit ID of state within a group. 

## Files

### Clusters

For each of 10 clusters (named by cluster ID in a range [0..9]):

- `Transition_matrixN.csv` - transition matrix (probability of transition from state to state) for all available states (csv, headers in first row and column)
- `Distr_statesN/XXX.txt` - set of observed data for length of stay in state `XXX`

Here `N` is cluster ID, `XXX` is states (can be obtained from transition matrices). 

### Flow of patients

- `Number_of_patients.txt` - number of patients per day (1 column, no header)
- `Entrance_time.txt` - time of patients arrival starting from the beginning of the day in minutes (1 column, no header)

### Clustering data

- `LoS.txt` - LoS claimed in EHR in conclusion (1 column, no header)
- `LoS for clusters.csv` - LoS extracted from EHR (csv with header, columns: `Cluster` - cluster ID, `Case` - case ID;`LoS` - LoS in minutes)
- `clusters_size.csv` - number of cases in clusters (csv with header, columns: `CLUSTER_ID` - cluster ID, `CLUSTER_SIZE` - number of cases)
