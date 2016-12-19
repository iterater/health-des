import pandas as pd
import numpy as np
import state_info
import dept_des

probMatrix = pd.read_csv('data\\1\\Transition_matrix.csv', sep=';')
statesNames = list(probMatrix.columns[1:])
states = {}
for name in statesNames:
    if name == '*01':
        st = state_info.StateInfo(name, transition_names=statesNames, is_final=True)
    elif name == '_01':
        st = state_info.StateInfo(name, transition_names=statesNames,
                                  transition_probabilities=list(probMatrix[statesNames].iloc[statesNames.index(name)]))
    else:
        dObservations = np.loadtxt('data\\1\\Distr_states1\\' + name + '.txt', delimiter=',', dtype=float)
        tProb = list(probMatrix[statesNames].iloc[statesNames.index(name)])
        st = state_info.StateInfo(name, transition_names=statesNames, transition_probabilities=tProb,
                                  duration_observations=dObservations)
    states[st.name] = st


span_generator = state_info.RvFromData([20, 10, 20, 40, 50])

sim_res = dept_des.simulate_patients_flow(2, states, span_generator, 24*60)

print(sim_res.head())
