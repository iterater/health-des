import scipy.stats as stat
import pandas as pd
import numpy as np
import state_info

probMatrix = pd.read_csv('data\\1\\Transition_matrix.csv', sep=';')
statesNames = list(probMatrix.columns[1:])
states = []
for name in statesNames:
    if name == '*01':
        st = state_info.StateInfo(name, transition_names=statesNames, is_final=True)
    elif name == '_01':
        st = state_info.StateInfo(name, transition_names=statesNames)
    else:
        dObservations = np.loadtxt('data\\1\\Distr_states1\\' + name + '.txt', delimiter=',', dtype=float)
        tProb = list(probMatrix[statesNames].iloc[statesNames.index(name)])
        st = state_info.StateInfo(name, transition_names=statesNames, transition_probabilities=tProb,
                                  duration_observations=dObservations)
    states.append(st)

print(states[2].name, states[2].generate_duration(), states[2].generate_next_state())
