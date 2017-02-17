# Discrete-event simulation of patients flow

## General description

Experiments with discrete-event simulation (DES) of patients flow passing through the group of key departments (GKD). Stochastic flow of patients, transitions between states, and length of stay (LoS) in states, as well as queueing for selected states (reflecting limited facilities  like surgery rooms) are supported. Two flows are considered: (1) target flow with detailed simulation, multiple classes, individual transitions and LoS in different states for each classes; (2) background flow with reduced paths limited to queueing facilities.

## Implementation details

![DES implementation](/pics/des_implementation.png)

Implementation is based on [SimPy](http://simpy.readthedocs.org/) with processes for flow generation and patients states transition presented by processes (see `target_emitter(...)`, `background_emitter(...)`, `background_surgery_process(...)`, and `patient(...)` in [dept_des.py](dept_des.py)). Other routins in [dept_des.py](dept_des.py):

- `generate_day_sequence(...)` - generating daily sequence of delays for incoming patients (with scale)
- `simulate_patients_flow(...)` - run single simulation
- `get_queue_statistics(...)` - basic statistics on queueing from simulation results


All stochastic parameters and datasets are generated with the help of [SciPy](http://scipy.org/) (see `RvFromData`, `PatientsDayFlowGenerator`, and `PatientGenerator` in [state_info.py](state_info.py)). Other routins in [state_info.py](state_info.py):

- `StateInfo` - basic class for handling state information (states, transition matrices, LoS generation) and processing with states
- `load_state_pool(...)` - load set of states for different classes

To run simulation in parallel [JobLib](http://pythonhosted.org/joblib/) is used. Data storing and processing were implemented using [NumPy](http://www.numpy.org/) and [Pandas](http://pandas.pydata.org/).

## Experiments

- [Experiment #1: ACS patients flow with classification](/docs/experiment_01_acs.md)
- [Experiment #2: ACS patients flow without classification](/docs/experiment_02_acs_no_clusters.md)
