import pandas as pd
import numpy as np
import os
from scipy.stats import rv_discrete, rv_continuous


class RvFromData(rv_continuous):
    """Distribution generated from data"""

    data = np.sort(np.random.rand(100))

    def __init__(self, initdata, *args):
        self.data = np.sort(initdata)
        super().__init__(args)

    def _cdf(self, x, *args):
        idx = int((self.data < x).sum())
        if idx == 0:
            return 0.0
        if idx >= len(self.data):
            return 1.0
        return (idx - 1.0 + (x - self.data[idx - 1]) / (self.data[idx] - self.data[idx - 1])) / len(self.data)


class PatientsDayFlowGenerator:
    """Generating patients flow for day"""

    def __init__(self, events_per_day_file, events_time_file):
        self.per_day_gen = RvFromData(np.loadtxt(events_per_day_file).flatten())
        self.time_in_day_gen = RvFromData(np.loadtxt(events_time_file).flatten())

    def generate_day_sequence(self, scale=1.0):
        seq = [0, 24 * 60]
        n = self.per_day_gen.rvs()
        for i in range(int(n * scale)):
            seq.append(int(self.time_in_day_gen.rvs()))
        seq.sort()
        return seq


class StateInfo:
    """Generating state information"""

    duration_generator = None
    transition_generator = None

    def __init__(self, name, transition_names,
                 transition_probabilities=None, duration_observations=None, is_final=False):
        self.name = name
        self.transition_names = transition_names
        self.is_final = is_final
        if transition_probabilities is not None:
            self.transition_generator = rv_discrete(values=(np.arange(len(transition_probabilities)),
                                                            transition_probabilities))
        if duration_observations is not None:
            self.duration_generator = RvFromData(initdata=duration_observations)

    def generate_next_state(self):
        if self.is_final or self.transition_generator is None:
            return self.name
        else:
            return self.transition_names[self.transition_generator.rvs()]

    def generate_duration(self):
        if self.is_final or self.duration_generator is None:
            return 0.0
        else:
            return self.duration_generator.rvs()


def load_state_pool(transition_matrix_file_path, states_time_dir_path, filtering=True):
    """Load set of states form matrix and directory"""
    prob_matrix = pd.read_csv(transition_matrix_file_path, sep=';')
    states_names = list(prob_matrix.columns[1:])
    states = {}
    for name in states_names:
        if name.startswith('*'):
            st = StateInfo(name, transition_names=states_names, is_final=True)
        elif name.startswith('_'):
            st = StateInfo(name, transition_names=states_names,
                           transition_probabilities=list(prob_matrix[states_names].iloc[states_names.index(name)]))
        else:
            # observations = np.loadtxt(os.path.join(states_time_dir_path, name + '.txt'), delimiter=',', dtype=float)
            f = open(os.path.join(states_time_dir_path, name + '.txt'))
            s = f.readlines()[-1].replace('[', '').replace(']', '').replace(' ', '')
            f.close()
            observations = np.array(list(map(float, s.split(','))), dtype=float)
            if filtering:
                # filtering zeros
                observations = observations[observations > 0]
                # filtering outliers with Tukey's test
                # q1 = np.percentile(observations, 25)
                # q3 = np.percentile(observations, 75)
                # k = 2.0
                # acceptable_range = (q1 - k * (q3 - q1), q3 + k * (q3 - q1))
                # observations = observations[(observations > acceptable_range[0]) &
                #                             (observations < acceptable_range[1])]
            t_prob = list(prob_matrix[states_names].iloc[states_names.index(name)])
            st = StateInfo(name, transition_names=states_names, transition_probabilities=t_prob,
                           duration_observations=observations)
        states[st.name] = st
    return states


class PatientGenerator:
    """Generate patient with initial state"""
    def __init__(self, types_p, types_state_pool):
        self.generator = rv_discrete(values=(np.arange(len(types_p)), types_p))
        self.types_state_pool = types_state_pool

    def get_patient(self):
        type_id = self.generator.rvs()
        return '_01', self.types_state_pool[type_id], type_id
