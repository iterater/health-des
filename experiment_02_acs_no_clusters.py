import pandas as pd
import numpy as np
import state_info
import dept_des
import datetime
import os
import joblib

ps = os.path.sep
basic_path = 'data' + ps + 'acs_no_clusters' + ps
add_path = 'data' + ps + 'acs' + ps
surg_path = 'data' + ps + 'surgeries' + ps

# reading paths clusters
n_clusters = 1
p_clusters = np.full(1, 1.0, dtype=float)
# reading states for clusters
states_pools = [state_info.load_state_pool(basic_path + 'Transition_matrix.csv', basic_path)]
# creating ACS patients generator
acs_patients_gen = state_info.PatientGenerator(p_clusters, states_pools)
acs_event_gen = state_info.PatientsDayFlowGenerator(add_path + 'Number_of_patients.txt',
                                                    add_path + 'Entrance_time.txt')
# creating background patients generator
background_surgery_gen = state_info.PatientsDayFlowGenerator(surg_path + 'total_surgeries_per_day.txt',
                                                             surg_path + 'total_surgeries_time_in_day.txt')
background_surgery_duration_gen = state_info.RvFromData(np.loadtxt(surg_path + 'total_surgeries_duration.txt').
                                                        flatten())


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
