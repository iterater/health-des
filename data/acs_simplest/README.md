# ACS patients simplest states (no clustering, minimum states)

## General description

Simple patients simulation: only three states (surgery, intensive care, regular department), no clustering, no variation in states (see [clustered dataset](/data/acs/) for full flow). Paths are described with a states, transition probabilities, observed LoS for states.
  
### States naming convention

- `_` - initial state
- `*` - final state
- `F` - intensive care department
- `I` - surgery
- `E` - regular departments (including cardiological department)


## Files

- `Transition_matrix.csv` - transition matrix (probability of transition from state to state) for all available states (csv, headers in first row and column)
- `X.txt` - set of observed data for length of stay in state `X`

Here `X` is states (can be obtained from transition matrices). 
