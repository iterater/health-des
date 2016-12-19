import pandas as pd
import numpy as np
import simpy
import state_info


def patient(env, patient_id, starting_state, states_pool, surgery_resource, logger):
    """Processing patients through the pool of states with queueing for states N* and I*"""
    state = starting_state
    while not states_pool[state].is_final:
        logger.append({'ID': patient_id, 'TIME': env.now, 'STATE': state,
                       'DIRECTION': 'IN', 'QUEUE_TIME': 0})
        # print(env.now, logger[-1])
        surgery_state = state[0] in ['N', 'I']
        time_before_queue = env.now
        if surgery_state:
            request = surgery_resource.request()
            yield request
        time_in_queue = env.now - time_before_queue
        duration = int(states_pool[state].generate_duration())
        yield env.timeout(duration)
        if surgery_state:
            surgery_resource.release(request)
        logger.append({'ID': patient_id, 'TIME': env.now, 'STATE': state,
                       'DIRECTION': 'OUT', 'QUEUE_TIME': time_in_queue})
        # print(env.now, logger[-1])
        state = states_pool[state].generate_next_state()
    logger.append({'ID': patient_id, 'TIME': env.now, 'STATE': state,
                   'DIRECTION': 'IN', 'QUEUE_TIME': 0})


def background_surgery_process(env, surgery_resource, duration, logger):
    """Processing request to surgery room"""
    logger.append({'ID': -1, 'TIME': env.now, 'STATE': 'IXX',
                   'DIRECTION': 'IN', 'QUEUE_TIME': 0})
    time_before_queue = env.now
    request = surgery_resource.request()
    yield request
    yield env.timeout(duration)
    surgery_resource.release(request)
    logger.append({'ID': -1, 'TIME': env.now, 'STATE': 'IXX',
                   'DIRECTION': 'OUT', 'QUEUE_TIME': env.now - time_before_queue})


def generate_day_sequence(per_day_gen, time_in_day_gen):
    """Generating sequence of requests within 24h"""
    seq = [0, 24*60]
    n = int(per_day_gen.rvs())
    for i in range(n):
        seq.append(int(time_in_day_gen.rvs()))
    seq.sort()
    return seq


def background_emitter(env, surgery_resource, logger):
    """Generating daily activity in surgery room"""
    per_day_gen = state_info.RvFromData(np.loadtxt('data\\total_surgeries_per_day.txt').flatten())
    time_in_day_gen = state_info.RvFromData(np.loadtxt('data\\total_surgeries_time_in_day.txt').flatten())
    duration_gen = state_info.RvFromData(np.loadtxt('data\\total_surgeries_duration.txt').flatten())
    while True:
        seq = generate_day_sequence(per_day_gen, time_in_day_gen)
        print('Background surgery sequence for day: ', seq)
        for i in range(1, len(seq) - 1):
            yield env.timeout(seq[i] - seq[i - 1])
            env.process(background_surgery_process(env, surgery_resource, int(duration_gen.rvs()), logger))
        yield env.timeout(seq[-1] - seq[-2])


def emitter(env, states_pool, surgery_resource, logger):
    """Emitting patients with inter-patients time by span generator"""
    per_day_gen = state_info.RvFromData(np.loadtxt('data\\planned_in_per_day.txt').flatten())
    time_in_day_gen = state_info.RvFromData(np.loadtxt('data\\planned_in_time_in_day.txt').flatten())
    counter = 0
    while True:
        seq = generate_day_sequence(per_day_gen, time_in_day_gen)
        print('Planned sequence for day: ', seq)
        for i in range(1, len(seq) - 1):
            yield env.timeout(seq[i] - seq[i - 1])
            env.process(patient(env, counter, '_01', states_pool, surgery_resource, logger))
            counter += 1
            # print(str(env.now) + ': emitting new patient #' + str(counter) + ' at ' + str(seq[i]))
        yield env.timeout(seq[-1] - seq[-2])


def simulate_patients_flow(n_surgeries, states_pool, simulation_time):
    log_track = []
    env = simpy.Environment()
    res = simpy.Resource(env, capacity=n_surgeries)
    env.process(emitter(env, states_pool, res, log_track))
    env.process(background_emitter(env, res, log_track))
    env.run(until=simulation_time)
    return pd.DataFrame(log_track, columns=['TIME', 'ID', 'STATE', 'DIRECTION', 'QUEUE_TIME'])
