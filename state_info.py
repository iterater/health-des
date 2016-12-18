import numpy as np
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
