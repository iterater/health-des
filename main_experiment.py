import pandas as pd
import numpy as np
import scipy.stats.mstats
import datetime
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


def get_queue_statistics(sim_res):
    """Basic stats for queue witing time"""
    mask = [st[0] in ['N', 'I'] for st in sim_res.STATE] & (sim_res.DIRECTION == 'OUT') & (sim_res.ID >= 0)
    mask_with_queue = mask & (sim_res.QUEUE_TIME > 0)
    qq = scipy.stats.mstats.mquantiles(sim_res[mask_with_queue].QUEUE_TIME)
    return {'PART': mask_with_queue.sum() / mask.sum(),
            'MIN': sim_res[mask_with_queue].QUEUE_TIME.min(),
            'MAX': sim_res[mask_with_queue].QUEUE_TIME.max(),
            'AVG': np.average(sim_res[mask_with_queue].QUEUE_TIME),
            'Q1': qq[0], 'Q2': qq[1], 'Q3': qq[2],
            'MAX_QUEUE_LENGTH': sim_res[mask_with_queue].QUEUE_LENGTH.max()}

total_log = []
# running simulation
# iterations: background-flow scale, number of parallel surgeries, multiple runs
for bgf_scale in np.arange(0.5, 3.0, 0.5):
    for nps in [1, 2, 3]:
        for i_run in range(10):
            sim_res = dept_des.simulate_patients_flow(nps, states, 30*24*60, bgf_scale)
            sim_stats = get_queue_statistics(sim_res)
            sim_stats['SCALE'] = bgf_scale
            sim_stats['N_SURG'] = nps
            print(sim_stats)
            total_log.append(sim_stats)
total_log_df = pd.DataFrame(total_log, columns=total_log[0].keys())
total_log_df.to_csv('logs\\queue-stats-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv')
