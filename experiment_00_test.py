import pandas as pd
import numpy as np
import datetime
import state_info
import dept_des

# reading probabilities
states = state_info.load_state_pool('data\\1\\Transition_matrix.csv', 'data\\1\\Distr_states1')

total_log = []
# running simulation
# iterations: background-flow scale, number of parallel surgeries, multiple runs
for bgf_scale in np.arange(0.5, 3.0, 0.5):
    for nps in [1, 2, 3]:
        for i_run in range(10):
            sim_res = dept_des.simulate_patients_flow(nps, states, 30*24*60, bgf_scale)
            sim_stats = dept_des.get_queue_statistics(sim_res)
            sim_stats['SCALE'] = bgf_scale
            sim_stats['N_SURG'] = nps
            print(sim_stats)
            total_log.append(sim_stats)
total_log_df = pd.DataFrame(total_log, columns=total_log[0].keys())
total_log_df.to_csv('logs\\queue-stats-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv')

# NB: Old and incompatible version of simulation
