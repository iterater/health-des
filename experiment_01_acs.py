import pandas as pd
import numpy as np
import state_info
import dept_des
import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# reading paths clusters
clusters = pd.read_csv('data\\acs\\clusters_size.csv', delimiter=';')
n_clusters = len(clusters)
p_clusters = np.array(clusters.CLUSTER_SIZE) / clusters.CLUSTER_SIZE.sum()
# reading states for clusters
states_pools = [state_info.load_state_pool('data\\acs\\Transition_matrix' + str(i) + '.csv',
                                           'data\\acs\\Distr_states_' + str(i)) for i in range(n_clusters)]
# creating ACS patients generator
acs_patients_gen = state_info.PatientGenerator(p_clusters, states_pools)
acs_event_gen = state_info.PatientsDayFlowGenerator('data\\acs\\Number_of_patients.txt',
                                                    'data\\acs\\Entrance_time.txt')
# creating background patients generator
background_surgery_gen = state_info.PatientsDayFlowGenerator('data\\total_surgeries_per_day.txt',
                                                             'data\\total_surgeries_time_in_day.txt')
background_surgery_duration_gen = state_info.RvFromData(np.loadtxt('data\\total_surgeries_duration.txt').flatten())

# simulation run
total_log = []
background_scale = 0.7
surgeries_number = 2
simulation_time = 120*24*60
sim_res = dept_des.simulate_patients_flow(acs_patients_gen, acs_event_gen, surgeries_number, background_surgery_gen,
                                          background_surgery_duration_gen, background_scale, simulation_time)
# counting LoS
sim_res.to_csv('logs\\sim-res-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv')
los_gr = sim_res[(sim_res.ID >= 0) &
                 (sim_res.STATE.str.contains('E') |
                  sim_res.STATE.str.contains('F'))].groupby(['ID', 'STATE'])['TIME']
los = np.array((los_gr.max() - los_gr.min()).sum(level=0), dtype=float)
sns.distplot(los / (60.0 * 24.0))
plt.savefig('pics\\los-FE-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.png')
plt.close()
los_gr = sim_res[sim_res.ID >= 0].groupby('ID')['TIME']
los = np.array(los_gr.max() - los_gr.min(), dtype=float)
sns.distplot(los / (60.0 * 24.0))
plt.savefig('pics\\los-ALL-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.png')
plt.close()
# saving stats
sim_stats = dept_des.get_queue_statistics(sim_res)
sim_stats['SCALE'] = background_scale
sim_stats['N_SURG'] = surgeries_number
print(sim_stats)
total_log.append(sim_stats)

# writing total log
# total_log_df = pd.DataFrame(total_log, columns=total_log[0].keys())
# total_log_df.to_csv('logs\\queue-stats-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv')

