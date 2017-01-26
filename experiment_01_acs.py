import pandas as pd
import numpy as np
import scipy.stats.mstats
import datetime
import state_info
import dept_des

# reading paths clusters
clusters = pd.read_csv('data\\acs\\clusters_size.csv', delimiter=';')
n_clusters = len(clusters)
p_clusters = np.array(clusters.CLUSTER_SIZE) / clusters.CLUSTER_SIZE.sum()

# reading states for clusters
states_pools = [state_info.load_state_pool('data\\acs\\Transition_matrix' + str(i) + '.csv',
                                           'data\\acs\\Distr_states_' + str(i)) for i in range(n_clusters)]
