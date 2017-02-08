import pandas as pd
import numpy as np
import state_info
import dept_des
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib

ps = os.path.sep
basic_path = 'data' + ps + 'acs' + ps

# reading paths clusters
clusters = pd.read_csv(basic_path + 'clusters_size.csv', delimiter=';')
n_clusters = len(clusters)
p_clusters = np.array(clusters.CLUSTER_SIZE) / clusters.CLUSTER_SIZE.sum()
# reading states for clusters
states_pools = [state_info.load_state_pool(basic_path + 'Transition_matrix' + str(i) + '.csv',
                                           basic_path + 'Distr_states_' + str(i)) for i in range(n_clusters)]
# creating ACS patients generator
acs_patients_gen = state_info.PatientGenerator(p_clusters, states_pools)
acs_event_gen = state_info.PatientsDayFlowGenerator(basic_path + 'Number_of_patients.txt',
                                                    basic_path + 'Entrance_time.txt')
# creating background patients generator
background_surgery_gen = state_info.PatientsDayFlowGenerator('data' + ps + 'total_surgeries_per_day.txt',
                                                             'data' + ps + 'total_surgeries_time_in_day.txt')
background_surgery_duration_gen = state_info.RvFromData(np.loadtxt('data' + ps + 'total_surgeries_duration.txt').
                                                        flatten())

# single simulation run
# background_scale = 0.1
# surgeries_number = 2
# simulation_time = 365*24*60
# sim_res = dept_des.simulate_patients_flow(acs_patients_gen, acs_event_gen, surgeries_number, background_surgery_gen,
#                                           background_surgery_duration_gen, background_scale, simulation_time,
#                                           use_queueing=False)
# sim_res.to_csv('logs' + ps + 'sim-res-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv')

# plotting LoS
# los_gr = sim_res[(sim_res.ID >= 0) &
#                  (sim_res.STATE.str.contains('E') |
#                   sim_res.STATE.str.contains('F'))].groupby(['ID', 'STATE'])['TIME']
# los = np.array((los_gr.max() - los_gr.min()).sum(level=0), dtype=float)
# sns.distplot(los / (60.0 * 24.0))
# plt.savefig('pics' + ps + 'los-FE-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.png')
# plt.close()
# los_gr = sim_res[sim_res.ID >= 0].groupby('ID')['TIME']
# los = np.array(los_gr.max() - los_gr.min(), dtype=float)
# sns.distplot(los / (60.0 * 24.0))
# plt.savefig('pics' + ps + 'los-ALL-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.png')
# plt.close()


# run series
def single_experiment_run(target_scale, bg_scale, n_surgery, queue, run_id):
    simulation_time = 60 * 24 * 60
    sim_res = dept_des.simulate_patients_flow(acs_patients_gen, acs_event_gen, n_surgery,
                                              background_surgery_gen, background_surgery_duration_gen,
                                              bg_scale, target_scale, simulation_time, use_queueing=queue)
    sim_stats = dept_des.get_queue_statistics(sim_res)
    sim_stats['BG_SCALE'] = bg_scale
    sim_stats['TARGET_SCALE'] = target_scale
    sim_stats['N_SURG'] = n_surgery
    print(run_id, sim_stats)
    return sim_stats

if __name__ == '__main__':
    total_log = []
    for tg_s in [0.5, 1.0, 1.5, 2.0]:
        for bg_s in [0.5, 1.0, 1.5, 2.0]:
            for nps in [1, 2, 3, 4, 5]:
                run_res = joblib.Parallel(n_jobs=6)(joblib.delayed(single_experiment_run)(tg_s, bg_s, nps, True, i_run)
                                                    for i_run in range(100))
                total_log.extend(run_res)
    total_log_df = pd.DataFrame(total_log, columns=total_log[0].keys())
    total_log_df.to_csv('logs' + ps + 'queue-stats-' +
                        datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv')
