import pandas as pd
import numpy as np
import state_info
import dept_des

# reading probabilities
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

# running simulation
sim_res = dept_des.simulate_patients_flow(2, states, 30*24*60)

# queueing analysis in log
mask = [st[0] in ['N', 'I'] for st in sim_res.STATE] & (sim_res.DIRECTION == 'OUT')
print(sim_res[sim_res.QUEUE_TIME > 0].head(30))
print(str((sim_res.QUEUE_TIME > 0).sum()) + ' (' +
      str(np.round((sim_res.QUEUE_TIME > 0).sum() / mask.sum() * 100, 1)) +
      '%) cases with queue time > 0 with average waiting time ' +
      str(np.average(sim_res[sim_res.QUEUE_TIME > 0].QUEUE_TIME)))
