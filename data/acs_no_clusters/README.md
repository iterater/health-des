# ACS patients paths (no clustering)

## General description

Pathways for ACS patients without clustering (see [clustered dataset](/data/acs/)). Paths are described with a states, transition probabilities, observed LoS for states.
  
### States naming convention

- `_` - initial state
- `*` - final state
- `A` - reception
- `D` - reception for transfer to further treatment
- `E` - cardiological department
- `F` - intensive care department
- `I` - surgery
- `N` - coronarography


## Files

- `Transition_matrix.csv` - transition matrix (probability of transition from state to state) for all available states (csv, headers in first row and column)
- `X.txt` - set of observed data for length of stay in state `X`

Here `X` is states (can be obtained from transition matrices). 
